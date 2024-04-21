import streamlit as st

from funclib import connect_to_database, create_db_cursor, access_loggedout
from datetime import datetime
from login_page import menu

# Connect to the database
mydb = connect_to_database()

# Create a database cursor
maincursor = create_db_cursor(mydb)

# Create the booked_slots table
maincursor.execute("""
    CREATE TABLE IF NOT EXISTS booked_slots (
        slot_id INT PRIMARY KEY,
        booked_by VARCHAR(255),
        start_time DATETIME,
        end_time DATETIME
    )
""")
maincursor.execute("""
    CREATE TABLE IF NOT EXISTS available_slots (
        slot_id INT AUTO_INCREMENT PRIMARY KEY,
        area_id INT,
        start_time DATETIME,
        end_time DATETIME
    )
""")

# Create the delete trigger
maincursor.execute("""
    CREATE TRIGGER IF NOT EXISTS delete_booked_slot
    AFTER INSERT ON booked_slots
    FOR EACH ROW
    DELETE FROM available_slots WHERE slot_id = NEW.slot_id
""")

# Commit the changes
mydb.commit()

# Function to fetch available slots
def fetch_available_slots():
    query = "SELECT * FROM available_slots"
    maincursor.execute(query)
    slots = maincursor.fetchall()
    return slots

# Function to book a slot
def book_slot(slot_id, booked_by, start_time, end_time):
    query = "INSERT INTO booked_slots (slot_id, booked_by, start_time, end_time) VALUES (%s, %s, %s, %s)"
    maincursor.execute(query, (slot_id, booked_by, start_time, end_time))
    mydb.commit()
        
# Main function to display available slots and book a slot
def book_slots():
    menu()
    access_loggedout()
    st.title("Available Slots")
    
    # Fetch and display available slots
    available_slots = fetch_available_slots()
    if available_slots:
        st.write("Select a slot to book:")
        for slot in available_slots:
            st.write(f"Slot ID: {slot[0]}, Area ID: {slot[1]}, Start Time: {slot[2]}, End Time: {slot[3]}")
        
        # Form to book a slot
        with st.form(key='book_slot_form'):
            selected_slot_id = st.number_input('Enter Slot ID to book:', step=1, min_value=0)
            start_date = st.date_input('Select Start Date:')
            start_time = st.time_input('Select Start Time:')
            end_date = st.date_input('Select End Date:')
            end_time = st.time_input('Select End Time:')
            submit_button = st.form_submit_button(label='Book Slot')

            if submit_button:
                # Combine date and time values
                start_datetime = datetime.combine(start_date, start_time)
                end_datetime = datetime.combine(end_date, end_time)
                
                # Check if the selected slot matches any available slots
                slot_exists = False
                for slot in available_slots:
                    if (slot[0] == selected_slot_id and
                        slot[2] == start_datetime and
                        slot[3] == end_datetime):
                        slot_exists = True
                        # Get the current user's username from the session state
                        booked_by = st.session_state["current_roll_number"]
                        book_slot(selected_slot_id, booked_by, start_datetime, end_datetime)
                        st.success("Slot booked successfully.")
                        st.experimental_rerun()
                        break
                
                if not slot_exists:
                    st.error("Invalid Slot ID or time slot.")

    else:
        st.write("No available slots found.")
          

# Run the main function
if __name__ == "__main__":
    book_slots()
