# ISC-DB: ISC Management And General Enquiry System

This repository contains a Streamlit-based web application for managing the Indoor Sports Complex (ISC) of my university.  It provides functionalities for students, staff, and administrators to interact with the ISC's resources, including slot bookings, coach assignments, equipment management, and user administration.

## Features

* **User Authentication:** Secure login and registration system with different roles (student, staff, admin).
* **Student Management:** Students can view/edit their profiles, book slots, apply for coaching, and view assigned coaches.
* **Slot Booking:** Students can book available slots for various areas in the ISC. Staff and admins can create, view, and manage slots.
* **Coach Management:** Admins can add, delete, and update coach information. Students can apply for coaching in specific sports.
* **Equipment Management:** Admins can add and remove equipment, and view available equipment.
* **Area Management:** Staff and Admins can add, update, and delete areas within the ISC.
* **Admin Dashboard:** Provides an overview of banned students, coach management, booking management, and slot management functionalities.
* **Banning System:** Admins can ban and unban students.

## Technical Details

* **Frontend:** Streamlit
* **Backend:** Python with MySQL database
* **Libraries and Imports:** `streamlit`, `mysql.connector`, `pandas`, `numpy`, `datetime`, `streamlit_extras`

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/ISC-DB.git
```

2. **Install required libraries:**

```bash
pip install -r requirements.txt
```

3. **Set up MySQL database:**
    * Create a MySQL database named `projectDB2`.
    * Create a user with appropriate permissions.
    * Update the database credentials in the `funclib.py` and `login_page.py` files. The default credentials are `root` with password `mySQL_DevX@123` on localhost.

4. **Populate Area Data:** 
    * Ensure you have an `Area_Data.txt` file in the root directory with the format specified in the existing `Area_Data.txt`.  This file is used to populate the `area` table in the database.

5. **Run the application:**

```bash
streamlit run login_page.py
```

## File Structure

* `main.py`: Initial database setup and student information form.  Largely superseded by other files, can be removed.
* `funclib.py`: Contains helper functions for database connection, cursor creation, and other utilities.
* `pages/`: Contains Streamlit pages for different functionalities:
    * `Admin.py`: Admin dashboard.
    * `area.py`: Area management.
    * `coach.py`: Coach management.
    * `equipment.py`: Equipment management.
    * `newslot.py`: New slot booking and management.
    * `slot_booking_and_display.py`: Slot booking and display.
    * `student.py`: Student profile management.
    * `training.py`: Coach application and management for students.
* `login_page.py`: Handles user login and registration.
* `Area_Data.txt`: Contains data for area initialization.
* `Slot_Data.txt`:  Sample data for slots (currently unused in the application, used for some early debugging).
* `.vscode/settings.json`: VSCode settings.
* `trigger.txt`: Notes on triggers (not enabled in the application).

## Future Improvements

* Add more robust error handling and input validation.
* Enhance the user interface and user experience.
* Implement proper equipment booking functionality.
* Add reporting and analytics features.


## Contributing
This repo is inactive.
