import streamlit as st
from datetime import datetime
from funclib import connect_to_database, create_db_cursor, access_loggedout
from login_page import menu

def insert_student_data(roll_num, firstname, lastname, dept, year, email_id):
    query = "INSERT INTO student (roll_num, firstname, lastname, dept, year, email_id) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (roll_num, firstname, lastname, dept, year, email_id)
    maincursor.execute(query, values)
    connection.commit()

def fetch_student_details(roll_num):
    query = "SELECT firstname, lastname, dept, year, email_id FROM student WHERE roll_num = %s"
    maincursor.execute(query, (roll_num,))
    return maincursor.fetchone()

def update_student_data(roll_num, firstname, lastname, dept, year, email_id):
    query = "UPDATE student SET firstname = %s, lastname = %s, dept = %s, year = %s, email_id = %s WHERE roll_num = %s"
    values = (firstname, lastname, dept, year, email_id, roll_num)
    maincursor.execute(query, values)
    connection.commit()

def student_info_form():
    st.title("Student Information Form")

    with st.form(key='edit_student_details'):
        st.write("Edit Details")
        rollnumber = st.number_input("Enter Roll Number", step=1, min_value=0)
        details = fetch_student_details(rollnumber)
        submit_button = st.form_submit_button("Submit Roll Number")

        if submit_button:
            details = fetch_student_details(rollnumber)
            if details:
                firstname, lastname, dept, year, email_id = details

                # Display student details
                st.write("**Student Details:**")
                st.write(f"**Roll Number:** {rollnumber}")
                st.write(f"**First Name:** {firstname}")
                st.write(f"**Last Name:** {lastname}")
                st.write(f"**Department:** {dept}")
                st.write(f"**Year of Enrollment:** {year.strftime('%Y-%m-%d')}")
                st.write(f"**Email Address:** {email_id}")
            else:
                st.warning("Student with given roll number not found.")

    if not details:
        with st.form(key='add_student_details'):
            st.write("Edit Details")
            rollnumber = st.number_input("Enter Roll Number", step=1, min_value=0)

            # Form to add student details
            firstname_input = st.text_input("First Name")
            lastname_input = st.text_input("Last Name")
            dept_input = st.text_input("Department", max_chars=3, help="e.g., CSE, BIO, MCH")
            year_input = st.date_input("Year of Enrollment", min_value=datetime(1900, 1, 1), max_value=datetime.now())
            email_input = st.text_input("Email Address", max_chars=50, help="e.g., example@gmail.com")

            # Submit button for adding student details
            submit_button = st.form_submit_button("Submit Details")

            if submit_button:
                if firstname_input.strip() and lastname_input.strip() and dept_input.strip() and email_input.strip():
                    # Insert student details into the database
                    insert_student_data(rollnumber, firstname_input.strip(), lastname_input.strip(), dept_input.strip(), year_input, email_input.strip())
                    st.success("Student information added successfully.")
                else:
                    st.error("Please fill in all the required fields.")

if __name__ == "__main__":
    connection = connect_to_database()
    maincursor = create_db_cursor(connection)
    menu()
    access_loggedout()
    student_info_form()
