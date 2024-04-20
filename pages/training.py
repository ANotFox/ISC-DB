import streamlit as st

from funclib import connect_to_database, create_db_cursor, access_loggedout
from login_page import menu

mydb = connect_to_database()
maincursor = create_db_cursor(mydb)

# Function to call stored procedure to display coach information for a student
def display_student_coaches(student_id):
    print(student_id)
    # Create the stored procedure if it doesn't exist
    maincursor.execute("""
        CREATE PROCEDURE IF NOT EXISTS display_student_coaches(IN student_id INT)
        BEGIN
            -- Display coach information for the student
            SELECT c.coach_id, c.name AS coach_name, c.sport_taught
            FROM coach c
            JOIN coach_trains ct ON c.coach_id = ct.coach_id
            WHERE ct.student_id = student_id;
        END
    """)
    
    print(maincursor)
    
    # Call the stored procedure
    maincursor.callproc('display_student_coaches', (student_id,))
    mydb.commit()
    print(maincursor)
    result = maincursor.stored_results()
     # Initialize an empty list to store coaches
    coaches = []

    # Iterate over the result set and fetch all rows
    for cursor in result:
        for row in cursor.fetchall():
            coaches.append(row)

    return coaches

# Function to call stored procedure to assign coach based on sport
def assign_coach(sport_name, student_id):
    
    # Check for duplicate entries before insertion
    query_check_duplicate = """
        SELECT COUNT(*) 
        FROM coach_trains 
        WHERE student_id = %s 
        AND coach_id IN (SELECT coach_id FROM coach WHERE sport_taught = %s)
    """
    maincursor.execute(query_check_duplicate, (student_id, sport_name))
    count_duplicate = maincursor.fetchone()[0]
    
    if count_duplicate > 0:
        st.error("Student has already applied for coaching in this sport. Duplicate entry detected.")
        return
    
    # Create the stored procedure if it doesn't exist
    maincursor.execute("""
        CREATE PROCEDURE IF NOT EXISTS assign_coach_to_student(IN sport_name VARCHAR(255), IN student_id INT)
        BEGIN
            DECLARE coach_id_val INT;

            -- Find coach ID for the given sport
            SELECT coach_id INTO coach_id_val
            FROM coach
            WHERE sport_taught = sport_name
            LIMIT 1;

            -- Insert coach-student mapping into coach_trains table
            INSERT INTO coach_trains (coach_id, student_id) VALUES (coach_id_val, student_id);
        END
    """)

    # Call the stored procedure
    maincursor.callproc('assign_coach_to_student', (sport_name, student_id))
    st.success("Application submitted successfully.")
    mydb.commit()

# Function to cancel coaching for a specific coach ID
def cancel_coaching(coach_id):
    # Execute SQL query to delete the entry for the specified coach ID
    query = "DELETE FROM coach_trains WHERE coach_id = %s"
    maincursor.execute(query, (coach_id,))
    mydb.commit()
    st.success("Coaching canceled successfully.")
    
# Main function
def main():
    menu()
    access_loggedout()
    st.title("Apply for Coaching")

    # Display the form for students to apply for coaching
    with st.form(key='apply_for_coaching_form'):
        student_id = int(st.session_state["username"])
        sport_name = st.selectbox('Sport Name', ['Football', 'Basketball', 'Tennis', 'Swimming'])
        submit_button = st.form_submit_button(label='Apply')

        if submit_button:
            # Call stored procedure to assign coach based on sport
            assign_coach(sport_name, student_id)
            
    st.title("View Your Coaches")

    # Display the button to view coaches for the student
    display_coaches_button = st.button("Display Your Coaches")

    if display_coaches_button:
        # Get student ID from session state
        student_id = int(st.session_state["current_roll_number"])

        # Call stored procedure to display coaches
        coaches = display_student_coaches(student_id)

        if coaches:
            # Display coach information
            st.write("### Your Coaches:")
            for coach in coaches:
                st.write(f"- Coach ID: {coach[0]}, Name: {coach[1]}, Sport: {coach[2]}")
        else:
            st.write("You have not opted for any coaches yet.") 
            
            
    st.title("Cancel Coaching")

    # Display the form for canceling coaching
    with st.form(key='cancel_coaching_form'):
        coach_id = st.number_input('Coach ID', step=1, min_value=0)
        submit_button = st.form_submit_button(label='Cancel Coaching')

        if submit_button:
            # Call stored procedure to cancel coaching for the coach
            cancel_coaching(coach_id)       

# Run the main function
if __name__ == "__main__":
    main()
