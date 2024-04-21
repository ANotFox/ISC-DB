import streamlit as st
import pandas as pd
from funclib import connect_to_database, create_db_cursor, access_loggedout, is_user_banned
from login_page import menu

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
    query = "UPDATE users where role = 'student' SET is_banned_unavailable = 0"
    mycursor.execute(query)
    st.success("All students have been unbanned successfully.")

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
    else:
        if st.button("Ban Student"):
            ban_student(str(selected_student))

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

# Main function to create tabs and call respective sections
def main():
    menu()
    access_loggedout()
    # mycursor = create_db_cursor(mydb)
    st.title("Admin Dashboard")

    tab1, p1, tab2 = st.tabs(["Banning", " ", "Coaches"])
    with tab1:
        ban_unban_student_section()

    with p1:
        pass

    with tab2:
        add_coach_all_coaches_section()


# Run the main function
if __name__ == "__main__":
    main()

