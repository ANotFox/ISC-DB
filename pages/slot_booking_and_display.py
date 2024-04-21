import streamlit as st
import pandas as pd

from datetime import datetime
from funclib import connect_to_database, create_db_cursor, access_loggedout, is_user_banned
from login_page import menu

# Function to insert data into the slot table
def insert_slot_data(mycursor, a_id, start_time, end_time):
    current_roll_number = int(st.session_state["username"])

    # Execute MySQL query with parameterized value
    mycursor.execute("SET @current_roll_number = %s", (current_roll_number,))

    # Insert slot data into the database
    query = "INSERT INTO slot (a_id, start_time, end_time, booked_by) VALUES (%s, %s, %s, @current_roll_number)"
    values = (a_id, start_time, end_time)
    mycursor.execute(query, values)


# Function to fetch slot data from the database
def fetch_slots(mycursor):
    query = "SELECT * FROM slot"
    mycursor.execute(query)
    slots = mycursor.fetchall()
    return slots

# Main function
def main():
    # authenticate()
    # Connect to the database
    mydb = connect_to_database()
    # Create a database cursor
    maincursor = create_db_cursor(mydb)
    menu()
    access_loggedout()
    #maincursor.execute("DROP TABLE IF EXISTS area")
    username = int(st.session_state.get("username"))
    if is_user_banned(maincursor, username):
        st.error("You are banned from the system. You cannot book slots.")
        st.stop()
    
    ## Post initialisation 
    # Display the form to add a new slot
    st.write("## Add Slot Booking")

    # Checkbox for single day booking
    single_day_booking = st.checkbox("Single Day Booking")

    with st.form(key='add_slot_form'):
        a_id = st.number_input('Area ID', step=1, min_value=0)
        # booked_by = st.number_input('Booked By', step=1, min_value=0)
        start_date = st.date_input('Start Date', min_value=datetime.now())
        start_time = st.time_input('Start Time')
        
        # Conditional display of end date input field
        if single_day_booking:
            end_date = start_date
        else:
            end_date = st.date_input('End Date', min_value=datetime.now())

        end_time = st.time_input('End Time')
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            # Insert the slot booking data into the database
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            # insert_slot_data(maincursor, a_id, booked_by, start_datetime, end_datetime)
            insert_slot_data(maincursor, a_id, start_datetime, end_datetime)
            st.success("Slot information submitted successfully.")
            mydb.commit()

        # Fetch slot data from the database
    slots = fetch_slots(maincursor)

    # Display the slot bookings
    st.write("## Slot Bookings")
    if slots:
        # Convert the list of tuples to a DataFrame
        slots_df = pd.DataFrame(slots, columns=["Area ID", "Booked By", "Start Time", "End Time"])

        # Style the DataFrame
        slots_df_styled = slots_df.style.set_properties(**{'text-align': 'center'})

        # Set CSS properties for the DataFrame
        slots_df_styled = slots_df_styled.set_table_styles([{
            'selector': 'th',
            'props': [('text-align', 'center')]
        }])

        # Display the styled DataFrame
        st.write(slots_df_styled)
    else:
        st.write("No slot bookings found.")

    # Close the database cursor and connection
    maincursor.close()
    mydb.close()

# Run the main function
if __name__ == "__main__":
    main()
