import streamlit as st

from funclib import connect_to_database, create_db_cursor, access_loggedout
from login_page import menu

# Function to insert data into the coach table
def insert_coach_data(maincursor, connection, coach_id, name, sport_taught, experience, salary):
    sql = "INSERT INTO coach (coach_id, name, sport_taught, experience, salary) VALUES (%s, %s, %s, %s, %s)"
    val = (coach_id, name, sport_taught, experience, salary)
    maincursor.execute(sql, val)
    connection.commit()

# Main function
def main():
    mydb = connect_to_database()
    maincursor = create_db_cursor(mydb)
    menu()
    access_loggedout()
    st.title("Add Coach")

    # Display the form to add a new coach
    with st.form(key='add_coach_form'):
        coach_id = st.number_input('Coach ID', step=1, min_value=0)
        name = st.text_input('Name')
        sport_taught = st.text_input('Sport Taught')
        experience = st.number_input('Experience', step=0.5, min_value=0)
        salary = st.number_input('Salary', step=0.01, min_value=0.00)
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            # Insert the coach data into the database
            insert_coach_data(maincursor, mydb, coach_id, name, sport_taught, experience, salary)
            st.success("Coach information submitted successfully.")

# Run the main function
if __name__ == "__main__":
    main()
