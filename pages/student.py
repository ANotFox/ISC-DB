import streamlit as st
from datetime import datetime
from funclib import connect_to_database, create_db_cursor, access_loggedout
from login_page import menu

def insert_student_data(roll_num, firstname, lastname, dept, year, email_id):
    query = "INSERT INTO student (roll_num, firstname, lastname, dept, year, email_id) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (roll_num, firstname, lastname, dept, year, email_id)
    maincursor.execute(query, values)
    connection.commit()

def student_info_form():
    st.title("Student Information Form")

    # Input fields
    firstname = st.text_input("First Name")
    lastname = st.text_input("Last Name")
    rollnumber = st.number_input("Enter Roll Number", step=1, min_value=0)
    dept = st.text_input("Department", max_chars=3, help="e.g., CSE, BIO, MCH")
    year = st.date_input("Year of Enrollment", min_value=datetime(1900, 1, 1), max_value=datetime.now())
    email_id = st.text_input("Email Address", max_chars=50, help="e.g., example@gmail.com")


    # Submit button
    if st.button("Submit"):
        if firstname.strip() and lastname.strip() and dept.strip() and email_id.strip():
            insert_student_data(rollnumber, firstname.strip(), lastname.strip(), dept.strip(), year, email_id.strip())
            st.success("Student information submitted successfully.")
        else:
            st.error("Please fill in all the required fields.")

if __name__ == "__main__":
    connection = connect_to_database()
    maincursor = create_db_cursor(connection)
    menu()
    access_loggedout()
    student_info_form()
