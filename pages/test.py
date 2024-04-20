import streamlit as st
import mysql.connector

# Function to connect to the database
def connect_to_database():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mySQL_DevX@123",
        database="projectDB"  # Specify the database name here
    )
    return mydb

# Function to create a database cursor
def create_db_cursor(mydb):
    mycursor = mydb.cursor()
    return mycursor

# Function to fetch slot data from the database
def fetch_slots(mycursor):
    query = "SELECT * FROM slot"
    mycursor.execute(query)
    slots = mycursor.fetchall()
    return slots

# Main function
def main():
    # Connect to the database
    mydb = connect_to_database()

    # Create a database cursor
    maincursor = create_db_cursor(mydb)

    # Fetch slot data from the database
    slots = fetch_slots(maincursor)

    # Display the slot bookings
    st.write("## Slot Bookings")
    if slots:
        for slot in slots:
            st.write(f"Area ID: {slot[0]}, Booked By: {slot[1]}, Start Time: {slot[2]}, End Time: {slot[3]}")
    else:
        st.write("No slot bookings found.")

    # Close the database cursor and connection
    maincursor.close()
    mydb.close()

# Run the main function
if __name__ == "__main__":
    main()
