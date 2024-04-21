import streamlit as st
import pandas as pd
from funclib import connect_to_database, create_db_cursor, access_loggedout, is_user_banned
from login_page import menu
from datetime import datetime

mydb = connect_to_database()
maincursor = create_db_cursor(mydb)

# Function to insert data into the coach table
def insert_coach_data(maincursor, connection, coach_id, name, sport_taught, experience, salary):
    sql = "INSERT INTO coach (coach_id, name, sport_taught, experience, salary) VALUES (%s, %s, %s, %s, %s)"
    val = (coach_id, name, sport_taught, experience, salary)
    maincursor.execute(sql, val)
    connection.commit()

# Function to fetch all coaches
def fetch_all_coaches():
    query = "SELECT * FROM coach"
    maincursor.execute(query)
    coaches = maincursor.fetchall()
    return coaches

# Function to delete selected coach
def delete_coach(coach_id):
    query = "DELETE FROM coach WHERE coach_id = %s"
    maincursor.execute(query, (coach_id,))
    mydb.commit()

# Function to update experience or salary of coach
def update_coach_attribute(coach_id, attribute, value):
    query = f"UPDATE coach SET {attribute} = %s WHERE coach_id = %s"
    maincursor.execute(query, (value, coach_id))
    mydb.commit()

# Function to ban a student
def ban_student(roll_num):
    mydb = connect_to_database()
    if mydb:
        mycursor = create_db_cursor(mydb)
        query = "UPDATE users SET is_banned_unavailable = True WHERE username = %s"
        mycursor.execute(query, (roll_num,))
        mydb.commit()
        st.write(f"Student with ID {roll_num} has been banned.")

    if mydb and mydb.is_connected():
        mycursor.close()
        mydb.close()

# Function to unban a student
def unban_student(roll_num):
    mydb = connect_to_database()
    if mydb:
        mycursor = create_db_cursor(mydb)
        query = "UPDATE users SET is_banned_unavailable = False WHERE username = %s"
        mycursor.execute(query, (roll_num,))
        mydb.commit()
        st.write(f"Student with ID {roll_num} has been unbanned.")

def fetch_all_student_roll_numbers(mycursor):
    query = "SELECT roll_num FROM student"
    mycursor.execute(query)
    roll_numbers = [row[0] for row in mycursor.fetchall()]
    return roll_numbers

def unban_all_students(mycursor):
    # Execute SQL query to unban all students
    query = "UPDATE users SET is_banned_unavailable = 0 WHERE role = 'student'"
    mycursor.execute(query)
    mydb.commit()
    st.experimental_rerun()
    # st.success("All students have been unbanned successfully.")

def fetch_all_banned_students(mycursor):
    # Execute SQL query to fetch all unbanned students
    query = """
    SELECT s.roll_num, s.firstname, s.lastname, s.dept, s.year, s.email_id
    FROM student s
    INNER JOIN users u ON s.roll_num = u.username
    WHERE u.role = 'student' AND u.is_banned_unavailable = 1
    """
    mycursor.execute(query)
    unbanned_students = mycursor.fetchall()
    return unbanned_students

# Function to display the "Ban/Unban Student" section
def ban_unban_student_section():
    st.title("Ban/Unban Student")

    selection_method = st.radio("Select Student by:", ("Dropdown", "Roll Number"))
    if selection_method == "Dropdown":
        # Fetch all roll numbers from the student table
        all_roll_numbers = fetch_all_student_roll_numbers(maincursor)
        # Display dropdown to select student
        selected_student = st.selectbox("Select Student Roll Number:", all_roll_numbers)
    else:
        # Input field to enter roll number
        roll_number = st.number_input("Enter Roll Number:", step=1, value=0, format="%d")
        selected_student = roll_number

    # Display button based on student ban status
    if is_user_banned(maincursor, str(selected_student)):
        if st.button("Unban Student"):
            unban_student(str(selected_student))
            mydb.commit()
    else:
        if st.button("Ban Student"):
            ban_student(str(selected_student))
            mydb.commit()

    # Display all banned students
    st.title("All Banned Students")
    banned_students = fetch_all_banned_students(maincursor)

    if banned_students:
        st.write("List of Banned Students:")
        banned_students_df = pd.DataFrame(banned_students, columns=["Roll Number", "First Name", "Last Name", "Department", "Year", "Email"])
        banned_students_df_styled = banned_students_df.style.set_properties(**{'text-align': 'center'}).set_table_styles([{
            'selector': 'th',
            'props': [('text-align', 'center')]
        }])

        # Display the styled DataFrame
        st.write(banned_students_df_styled)
        
        # Button to unban all students
        if st.button("Unban All"):
            unban_all_students(maincursor)
            mydb.commit()
            st.success("All students have been unbanned.")
    else:
        st.write("No students are currently banned.")

# Function to display the "Add Coach" and "All Coaches" section
def add_coach_all_coaches_section():
    st.title("Add Coach")

    # Display the form to add a new coach
    with st.form(key='add_coach_form'):
        # Form fields for adding a new coach
        coach_id = st.number_input('Coach ID', step=1, min_value=0)
        name = st.text_input('Name')
        sport_taught = st.text_input('Sport Taught')
        experience = st.number_input('Experience', step=1, min_value=0)
        salary = st.number_input('Salary', step=0.01, min_value=0.00)
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            # Insert the coach data into the database
            insert_coach_data(maincursor, mydb, coach_id, name, sport_taught, experience, salary)
            st.success("Coach information submitted successfully.")

    # Display all coaches and delete options in expander
    with st.expander("All Coaches and Options", expanded=True):
        # Fetch all coaches
        coaches = fetch_all_coaches()
        if coaches:
            # Convert the list of tuples to a DataFrame
            coaches_df = pd.DataFrame(coaches, columns=["Coach ID", "Name", "Sport Taught", "Experience", "Salary"])

            # Display the DataFrame
            st.dataframe(coaches_df)

            # Display radio buttons to select coach to delete
            selected_coach_id_delete = st.radio("Select Coach to Delete", [coach[0] for coach in coaches])
            if st.button("Delete Coach"):
                delete_coach(selected_coach_id_delete)
                st.success("Coach deleted successfully.")

            # Display dropdown to select attribute to update
            st.write("Update Experience or Salary:")
            selected_coach_id_update = st.selectbox("Select Coach", [coach[0] for coach in coaches])
            update_attribute = st.selectbox("Select Attribute to Update", ["Experience", "Salary"])
            new_value = st.number_input(f"Enter New {update_attribute}", step=1)

            # Button to update coach attribute
            if st.button("Update"):
                update_coach_attribute(selected_coach_id_update, update_attribute.lower(), new_value)
                st.success(f"{update_attribute} updated successfully.")
        else:
            st.write("No coaches found.")

# Function to fetch bookings from the database
def fetch_bookings(mycursor):
    # Execute SQL query to fetch bookings
    query = """
    SELECT s.a_id, s.booked_by, s.start_time, s.end_time
    FROM slot s
    INNER JOIN student st ON s.booked_by = st.roll_num
    ORDER BY s.start_time
    """
    mycursor.execute(query)
    bookings = mycursor.fetchall()
    return bookings

# Define delete_bookings function to delete selected bookings from the database
def delete_bookings(mycursor, bookings_to_delete):
    for booking in bookings_to_delete:
        # Execute SQL query to delete booking
        query = """
        DELETE FROM slot
        WHERE a_id = %s AND booked_by = %s AND start_time = %s AND end_time = %s
        """
        mycursor.execute(query, booking)
    st.success("Selected bookings have been deleted successfully.")

def delete_bookings(mycursor, bookings_to_delete):
    for booking in bookings_to_delete:
        # Execute SQL query to delete booking
        query = """
        DELETE FROM slot
        WHERE a_id = %s AND booked_by = %s AND start_time = %s AND end_time = %s
        """
        mycursor.execute(query, booking)
    st.success("Selected bookings have been deleted successfully.")

# Define booking_section function to display bookings and provide delete functionality
def booking_section(mycursor):
    st.title("Booking Section")

    # Create a form to choose how to view the bookings
    view_options = ["All Bookings", "By Time", "By User", "By Date", "By Area"]
    view_option = st.selectbox("View Bookings By:", view_options)

    # Fetch bookings from the database
    bookings = fetch_bookings(mycursor)

    if bookings:
        # Convert bookings to DataFrame
        bookings_df = pd.DataFrame(bookings, columns=["Area ID", "Booked By", "Start Time", "End Time"])

        # Format datetime columns
        bookings_df["Start Time"] = pd.to_datetime(bookings_df["Start Time"])
        bookings_df["End Time"] = pd.to_datetime(bookings_df["End Time"])

        # Display bookings based on selected view option
        if view_option == "All Bookings":
            st.write("All Bookings:")
            st.dataframe(bookings_df.style.set_properties(**{'background-color': '#f5f5f5', 'color': 'black'}))
        elif view_option == "By Time":
            # Display bookings by time
            selected_time = st.time_input("Select Time:")
            filtered_bookings = bookings_df[(bookings_df["Start Time"].dt.time == selected_time) | (bookings_df["End Time"].dt.time == selected_time)]
            if not filtered_bookings.empty:
                st.dataframe(filtered_bookings.style.set_properties(**{'background-color': '#f5f5f5', 'color': 'black'}))
            else:
                st.write("No bookings found for the selected time.")
        elif view_option == "By User":
            # Display bookings by user
            selected_user = st.selectbox("Select User:", bookings_df["Booked By"].unique())
            filtered_bookings = bookings_df[bookings_df["Booked By"] == selected_user]
            if not filtered_bookings.empty:
                st.dataframe(filtered_bookings.style.set_properties(**{'background-color': '#f5f5f5', 'color': 'black'}))
            else:
                st.write("No bookings found for the selected user.")
        elif view_option == "By Date":
            # Display bookings by date
            selected_date = st.date_input("Select Date:")
            filtered_bookings = bookings_df[(bookings_df["Start Time"].dt.date == selected_date) | (bookings_df["End Time"].dt.date == selected_date)]
            if not filtered_bookings.empty:
                st.dataframe(filtered_bookings.style.set_properties(**{'background-color': '#f5f5f5', 'color': 'black'}))
            else:
                st.write("No bookings found for the selected date.")
        elif view_option == "By Area":
            # Display bookings by area
            selected_area = st.selectbox("Select Area:", bookings_df["Area ID"].unique())
            filtered_bookings = bookings_df[bookings_df["Area ID"] == selected_area]
            if not filtered_bookings.empty:
                st.dataframe(filtered_bookings.style.set_properties(**{'background-color': '#f5f5f5', 'color': 'black'}))
            else:
                st.write("No bookings found for the selected area.")

        # # Add a button to delete selected bookings
        # if st.button("Delete Selected Bookings"):
        #     selected_bookings = []
        #     for index, row in bookings_df.iterrows():
        #         selected = st.checkbox(f"Booking ID: {index}", key=index)
        #         if selected:
        #             selected_bookings.append((row["Area ID"], row["Booked By"], row["Start Time"], row["End Time"]))
        #     if selected_bookings:
        #         delete_bookings(mycursor, selected_bookings)

        with st.form(key='delete_form'):
            st.write("Specify deletion criteria:")
            area_id = st.number_input("Area ID:", step=1)
            booked_by = st.number_input("Booked By (User ID):", step=1)
            start_time = st.date_input("Start Time:")
            end_time = st.date_input("End Time:")
            submit_button = st.form_submit_button(label='Delete Bookings')

        # Delete bookings based on specified criteria
        if submit_button:
            # Execute SQL query to delete bookings based on specified criteria
            query = """
            DELETE FROM slot
            WHERE a_id = %s AND booked_by = %s AND start_time = %s AND end_time = %s
            """
            mycursor.execute(query, (area_id, booked_by, start_time, end_time))
            st.success("Selected bookings have been deleted successfully.")

    else:
        st.write("No bookings found.")

# Function to fetch booked slots
def fetch_booked_slots():
    query = "SELECT * FROM booked_slots"
    maincursor.execute(query)
    slots = maincursor.fetchall()
    return slots

# Function to fetch available slots
def fetch_available_slots():
    query = "SELECT * FROM available_slots"
    maincursor.execute(query)
    slots = maincursor.fetchall()
    return slots

# Function to insert data into the available_slots table
def insert_available_slot(area_id, start_time, end_time):
    sql = "INSERT INTO available_slots (area_id, start_time, end_time) VALUES (%s, %s, %s)"
    val = (area_id, start_time, end_time)
    maincursor.execute(sql, val)
    mydb.commit()
    st.experimental_rerun()

# Main function for adding slots
def add_slots():
    st.title("Add Available Slot")

    # Display the form to add a new slot
    with st.form(key='add_slot_form'):
        area_id = st.number_input('Area ID', step=1, min_value=0)
        start_date = st.date_input('Start Date', min_value=datetime.now())
        start_time = st.time_input('Start Time')
        end_date = st.date_input('End Date', min_value=datetime.now())
        end_time = st.time_input('End Time')
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            # Insert the slot data into the database
            insert_available_slot(area_id, start_datetime, end_datetime)
            st.success("Slot information submitted successfully.")

# Function to delete an available slot
def delete_available_slot(slot_id):
    query = "DELETE FROM available_slots WHERE slot_id = %s"
    maincursor.execute(query, (slot_id,))
    mydb.commit()
    st.experimental_rerun()

# Main function for admin slot management
def admin_slots():

    # st.title("Booked Slots")
    
    # # Fetch and display booked slots
    # booked_slots = fetch_booked_slots()
    # if booked_slots:
    #     booked_slots_df = pd.DataFrame(booked_slots, columns=["Area ID", "Booked By", "Start Time", "End Time"])
    #     st.dataframe(booked_slots_df)
    # else:
    #     st.write("No booked slots found.")
    
    st.title("Available Slots")
    
    # Fetch and display available slots
    available_slots = fetch_available_slots()
    if available_slots:
        available_slots_df = pd.DataFrame(available_slots, columns=["Slot ID", "Area ID", "Start Time", "End Time"])
        st.dataframe(available_slots_df)

        # Provide option to delete a slot
        slot_to_delete = st.number_input("Enter Slot ID to delete:", step=1, min_value=0)
        delete_button = st.button("Delete Slot")
        if delete_button:
            delete_available_slot(slot_to_delete)
            st.success("Slot deleted successfully.")
    else:
        st.write("No available slots found.")
        
    add_slots()

# Main function to create tabs and call respective sections
def main():
    menu()
    access_loggedout()
    # mycursor = create_db_cursor(mydb)
    st.title("Admin Dashboard")

    tab1, p1, tab2, p2, tab3, p3, tab4 = st.tabs(["Banning", " ", "Coaches", " ", "View/Delete Bookings", " ", "Add Slot"])
    with tab1:
        ban_unban_student_section()
    with p1:
        pass
    with tab2:
        add_coach_all_coaches_section()
    with p2:
        pass
    with tab3:
        booking_section(maincursor)
    with p3:
        pass
    with tab4:
        admin_slots()


# Run the main function
if __name__ == "__main__":
    main()

