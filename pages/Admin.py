import streamlit as st
import pandas as pd
from funclib import connect_to_database, create_db_cursor, access_loggedout
from login_page import menu

# Connect to the database
mydb = connect_to_database()

# Create a database cursor
maincursor = create_db_cursor(mydb)

# Function to insert data into the coach table
def insert_coach_data(maincursor, connection, coach_id, name, sport_taught, experience, salary):
    sql = "INSERT INTO coach (coach_id, name, sport_taught, experience, salary) VALUES (%s, %s, %s, %s, %s)"
    val = (coach_id, name, sport_taught, experience, salary)
    maincursor.execute(sql, val)
    connection.commit()

# Function to fetch all coaches
def fetch_all_coaches():
    query = "SELECT * FROM coach"
    maincursor.execute(query)
    coaches = maincursor.fetchall()
    return coaches

# Function to delete selected coach
def delete_coach(coach_id):
    query = "DELETE FROM coach WHERE coach_id = %s"
    maincursor.execute(query, (coach_id,))
    mydb.commit()

# Function to update experience or salary of coach
def update_coach_attribute(coach_id, attribute, value):
    query = f"UPDATE coach SET {attribute} = %s WHERE coach_id = %s"
    maincursor.execute(query, (value, coach_id))
    mydb.commit()

# Main function for admin functionalities
def main():
    menu()
    access_loggedout()
    st.title("Add Coach")

    # Display the form to add a new coach
    with st.form(key='add_coach_form'):
        coach_id = st.number_input('Coach ID', step=1, min_value=0)
        name = st.text_input('Name')
        sport_taught = st.text_input('Sport Taught')
        experience = st.number_input('Experience', step=1, min_value=0)
        salary = st.number_input('Salary', step=0.01, min_value=0.00)
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            # Insert the coach data into the database
            insert_coach_data(maincursor, mydb, coach_id, name, sport_taught, experience, salary)
            st.success("Coach information submitted successfully.")


    # Display all coaches and delete options in expander
    with st.expander("All Coaches and Options", expanded=True):
        # Fetch all coaches
        coaches = fetch_all_coaches()
        if coaches:
            # Convert the list of tuples to a DataFrame
            coaches_df = pd.DataFrame(coaches, columns=["Coach ID", "Name", "Sport Taught", "Experience", "Salary"])

            # Display the DataFrame
            st.dataframe(coaches_df)

            # Display radio buttons to select coach to delete
            selected_coach_id_delete = st.radio("Select Coach to Delete", [coach[0] for coach in coaches])
            if st.button("Delete Coach"):
                delete_coach(selected_coach_id_delete)
                st.success("Coach deleted successfully.")

            # Display dropdown to select attribute to update
            st.write("Update Experience or Salary:")
            selected_coach_id_update = st.selectbox("Select Coach", [coach[0] for coach in coaches])
            update_attribute = st.selectbox("Select Attribute to Update", ["Experience", "Salary"])
            new_value = st.number_input(f"Enter New {update_attribute}", step=1)

            # Button to update coach attribute
            if st.button("Update"):
                update_coach_attribute(selected_coach_id_update, update_attribute.lower(), new_value)
                st.success(f"{update_attribute} updated successfully.")
        else:
            st.write("No coaches found.")

# Run the main function
if __name__ == "__main__":
    main()
