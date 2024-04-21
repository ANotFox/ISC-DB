import streamlit as st
import pandas as pd
from datetime import datetime
from funclib import connect_to_database, create_db_cursor

# Connect to the database
mydb = connect_to_database()

# Create a database cursor
maincursor = create_db_cursor(mydb)

# Create the available_slots table with slot_id as auto-increment
maincursor.execute("""
    CREATE TABLE IF NOT EXISTS available_slots (
        slot_id INT AUTO_INCREMENT PRIMARY KEY,
        area_id INT,
        start_time DATETIME,
        end_time DATETIME
    )
""")

# Commit the changes
mydb.commit()

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
    authenticate()
    st.title("Booked Slots")
    
    # Fetch and display booked slots
    booked_slots = fetch_booked_slots()
    if booked_slots:
        booked_slots_df = pd.DataFrame(booked_slots, columns=["Area ID", "Booked By", "Start Time", "End Time"])
        st.dataframe(booked_slots_df)
    else:
        st.write("No booked slots found.")
    
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

# Run the admin slot management function
if __name__ == "__main__":
    admin_slots()
