import streamlit as st
import pandas as pd

from funclib import connect_to_database, create_db_cursor, time_input_to_datetime, access_loggedout
from login_page import menu

def read_slots_from_file(file_path):
    slots = []
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            area_id = parts[0]
            start_time = parts[1] + " " + parts[2]
            end_time = parts[3] + " " + parts[4]
            slots.append((area_id, start_time, end_time))
    return slots

def display_slots(slots):
    st.title("Available Slots")
    slot_data = [["Area ID", "Start Time", "End Time"]] + slots
    st.table(slot_data)
        
def insert_slot_data(mycursor, a_id, start_time, end_time, slots):
    # Set the session variable current_roll_number
    mycursor.execute("SET @current_roll_number = %s", int(st.session_state["username"],))
    
    # Insert slot data into the table
    sql = "INSERT INTO slot (a_id, start_time, end_time) VALUES (%s, %s, %s)"
    val = (a_id, start_time, end_time)
    mycursor.execute(sql, val)
    
    # Print the slot that is being booked
    print("Booked slot:", a_id, start_time, end_time)
    
    # Create a new list with the slots that are not booked
    updated_slots = []
    for slot in slots:
        if slot[0] != a_id:
            updated_slots.append(slot)
        else:
            print("Removed slot:", slot)
            
    # Display the updated list of available slots
    display_slots(updated_slots)


# Function to fetch slot data from the database
def fetch_slots(mycursor):
    query = "SELECT * FROM slot"
    mycursor.execute(query)
    slots = mycursor.fetchall()
    return slots

# Main function
def main():

    mydb = connect_to_database()
    maincursor = create_db_cursor(mydb)
    menu()
    access_loggedout()
    slots = read_slots_from_file("Slot_Data.txt")
    display_slots(slots)
    print(slots[0][0], slots[0][1], slots[0][2])

    # Display the form to add a new slot
    st.write("## Add Slot Booking")
    with st.form(key='add_slot_form'):
        a_id = st.number_input('Area ID', step=1, min_value=0)
        start_time = st.text_input('Start Time')
        end_time = st.text_input('End Time')
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            # Insert the slot booking data into the database
            # start_datetime = time_input_to_datetime(start_time)
            # end_datetime = time_input_to_datetime(end_time)
            insert_slot_data(maincursor, a_id, start_time, end_time, slots)
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
