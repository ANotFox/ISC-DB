import streamlit as st
import pandas as pd
import mysql.connector
from funclib import connect_to_database, create_db_cursor, access_loggedout
from login_page import menu

mydb = connect_to_database()
cursor = create_db_cursor(mydb)

def display_equipment_list(record):
    st.title("Available Equipment")
    df = pd.DataFrame(record, columns=["ID", "Type", "Count"])
    st.dataframe(df.style.set_properties(**{'max-width': '300px'}, align='center'))

def insert_equipment_data(mycursor, e_id, e_type, count):
    try:
        sql = "INSERT INTO Equipment (e_id, e_type, count) VALUES (%s, %s, %s)"
        val = (e_id, e_type, count)
        mycursor.execute(sql, val)
        mydb.commit()
        st.success("Equipment added successfully.")
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
            st.error("Error: Duplicate equipment ID or name.")
        else:
            st.error("An error occurred while adding equipment: {}".format(err.msg))

def remove_equipment_data(mycursor, e_id):
    mycursor.execute("DELETE FROM Equipment WHERE e_id = %s", (e_id,))
    mydb.commit()

def main():
    menu()
    access_loggedout()

    st.title("Equipment Page")

    # Display available equipment
    cursor.execute("SELECT * FROM Equipment")
    records = cursor.fetchall()
    display_equipment_list(records)

    if st.session_state["role"] == "admin":
        # Add Equipment Expander
        st.write("## Add Equipment")
        with st.expander("Add New Equipment"):
            with st.form(key='add_equipment_form'):
                e_id = st.number_input('Equipment ID', step=1, min_value=1)
                e_type = st.text_input('Type')
                count = st.number_input('Count', min_value=0)

                submit_button = st.form_submit_button(label='Submit')

                if submit_button:
                    insert_equipment_data(cursor, e_id, e_type, count)

        # Remove Equipment Expander
        st.write("## Remove Equipment")
        with st.expander("Remove Equipment"):
            with st.form(key='remove_equipment_form'):
                e_id_remove = st.number_input('Equipment ID', step=1, min_value=1)

                submit_button_remove = st.form_submit_button(label='Remove')

                if submit_button_remove:
                    remove_equipment_data(cursor, e_id_remove)
                    st.success("Equipment removed successfully.")

if __name__ == "__main__":
    main()
