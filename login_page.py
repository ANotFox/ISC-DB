import streamlit as st
import mysql.connector
from funclib import kickstart

# Connect to MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mySQL_DevX@123",
)

cursor = connection.cursor()
kickstart(cursor, connection)

def register():
    st.title("Register Page")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    role = st.selectbox("Select Role", ("student", "staff", "admin"))

    if st.button("Register"):
        password_hash = new_password
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", (new_username, password_hash, role))
            connection.commit()
            st.success("Registration successful!")
            # st.experimental_set_query_params(page="login")  # Redirect to login page
        except mysql.connector.IntegrityError:
            st.error("Username already exists")

def login():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        password_hash = password
        cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password_hash))
        user = cursor.fetchone()
        if user:
            st.session_state["logged_in"] = True
            st.session_state["role"] = user[3]  # Store user's role in session state
            st.session_state["username"] = username  # Store username in session state
            st.success("Logged in as {}".format(username))
            # st.experimental_set_query_params(page="main")
        else:
            st.error("Invalid username or password")

def logout():
    st.session_state.pop("logged_in", None)
    st.session_state.pop("role", None)
    st.session_state.pop("username", None)
    # st.query_params(page="login")
    st.session_state["page"] = "login"

def authenticated_menu():
    # Show a navigation menu for authenticated users based on their role
    st.sidebar.write("## Navigation")
    if st.session_state["role"] not in ["staff", "admin"]:
        st.sidebar.page_link("pages/slot_booking_and_display.py", label="Slot Booking and Display")
        st.sidebar.page_link("pages/training.py", label="Training")
        # st.sidebar.page_link("pages/Slots.py", label="Slot New")
        st.sidebar.page_link("pages/newslot.py", label="New Slot")
    
    if st.session_state["role"] in ["staff", "admin"]:
        st.sidebar.page_link("pages/area.py", label="Areas")
        if st.session_state["role"] == "admin":
            st.sidebar.page_link("pages/coach.py", label="Coach")
            st.sidebar.page_link("pages/equipment.py", label="Equipment")
            st.sidebar.page_link("pages/admin.py", label="Admin Dashboard")
    st.sidebar.write("## Account")
    st.sidebar.write("Logged in as: {}".format(st.session_state.get("username")))
    if st.session_state["role"] not in ["staff", "admin"]:
        st.sidebar.page_link("pages/student.py", label="Student Profile")
    st.sidebar.button("Logout", on_click=logout)

def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("login_page.py", label="Log in here")

def menu():
    # Determine if a user is logged in or not, then show the correct navigation menu
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        unauthenticated_menu()
    else:
        authenticated_menu()

def main():
    st.title("Main Page")
    st.write("Welcome to IMAGE: ISC Management And General Enquiry system!")
    # Add your main page content here
    st.write("Hello, {}".format(st.session_state.get("username")))

def app():
    menu()  # Call the menu function to set up the navigation sidebar
    # page = st.experimental_get_query_params().get("page", ["login"])[0]

    # Check if the user is logged in
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Display the appropriate tabs based on login status
    if st.session_state["logged_in"]:
        main()
    else:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login()
        with tab2:
            register()

    # if page == "login":
        # login()
        # st.write("---")  # Add a horizontal line to separate the buttons from the content
        # if st.button("Register", key="register_btn"):
            # st.experimental_set_query_params(page="register")
    # elif page == "main":
        # main()
    # elif page == "register":
        # register()
        # st.write("")  # Add empty space for spacing between buttons
        # if st.button("Login", key="login_btn"):
            # st.experimental_set_query_params(page="login")
    # elif page == "logout":
        # logout()

if __name__ == "__main__":
    app()
