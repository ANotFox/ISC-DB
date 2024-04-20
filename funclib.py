import streamlit as st
import mysql.connector
from datetime import datetime

# Function to connect to the database
def connect_to_database():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mySQL_DevX@123",
        database="projectDB2"  # Specify the database name here
    )
    return mydb

# Function to create a database cursor
def create_db_cursor(mydb):
    mycursor = mydb.cursor()
    return mycursor
    
# Function to convert time inputs to datetime objects
def time_input_to_datetime(time_input):
    # Get the current date to combine with the time input
    current_date = datetime.today().date()
    # Combine the current date with the time input to create a datetime object
    datetime_obj = datetime.combine(current_date, time_input)
    return datetime_obj

def authenticate():
    if not st.session_state.get("logged_in"):
        st.error("You must be logged in to access this page.")
        st.experimental_set_query_params(page="login")
        st.sidebar.page_link(
            "login_page.py",
            label="Login Here",
        )
        st.stop()

def access_loggedout():
    if "role" not in st.session_state or st.session_state["role"] not in ["student", "staff", "admin"]:
        st.warning("You do not have permission to view this page.")
        st.stop()


def kickstart(mycursor, connection):
    mycursor.execute("CREATE DATABASE IF NOT EXISTS projectDB2")

    # Switch to the projectDB database
    mycursor.execute("USE projectDB2")
    #mycursor.execute("DROP database IF EXISTS projectdb")

    # Create the student table
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            roll_num INT PRIMARY KEY NOT NULL,
            firstname VARCHAR(50),
            lastname VARCHAR(50),
            dept VARCHAR(3),
            year DATE,
            email_id VARCHAR(50) NOT NULL
        )
    """)

    # Create the area table
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS area (
            a_id INT PRIMARY KEY NOT NULL,
            a_name VARCHAR(50) NOT NULL
        )
    """)

    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS slot (
            a_id INT NOT NULL,
            booked_by INT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            PRIMARY KEY (a_id, booked_by),
            FOREIGN KEY (booked_by) REFERENCES student(roll_num),
            FOREIGN KEY (a_id) REFERENCES area(a_id)
        )
    """)

    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(64) NOT NULL,
            role ENUM('student', 'staff', 'admin') NOT NULL DEFAULT 'student'
        )
    """)

        # Create coach table
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS coach (
            coach_id INT PRIMARY KEY,
            name VARCHAR(255),
            sport_taught VARCHAR(255),
            experience INT,
            salary DECIMAL(10, 2)
        )
    """)

    # Create coach_trains table
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS coach_trains (
            coach_id INT,
            student_id INT,
            FOREIGN KEY (coach_id) REFERENCES coach(coach_id),
            FOREIGN KEY (student_id) REFERENCES student(roll_num)
        )
    """)

    connection.commit()

