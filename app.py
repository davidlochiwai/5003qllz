import streamlit as st
import sqlite3
from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt

# Connect to SQLite database
conn = sqlite3.connect('healthcare.db', check_same_thread=False)
c = conn.cursor()

# Create tables
def create_tables():
    c.execute('''
        CREATE TABLE IF NOT EXISTS Patients (
            PatientID INTEGER PRIMARY KEY, 
            FirstName TEXT, 
            LastName TEXT, 
            DateOfBirth TEXT, 
            ContactNumber TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Doctors (
            DoctorID INTEGER PRIMARY KEY,
            FirstName TEXT,
            LastName TEXT,
            Department TEXT,
            ContactNumber TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Appointments (
            AppointmentID INTEGER PRIMARY KEY, 
            PatientID INTEGER, 
            DoctorID INTEGER,
            AppointmentDate TEXT, 
            AppointmentTime TEXT, 
            Status TEXT,
            Location TEXT,
            FOREIGN KEY (PatientID) REFERENCES Patients (PatientID),
            FOREIGN KEY (DoctorID) REFERENCES Doctors (DoctorID)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS MedicalRecords (
            RecordID INTEGER PRIMARY KEY, 
            AppointmentID INTEGER, 
            Diagnosis TEXT,
            Details TEXT,
            FOREIGN KEY (AppointmentID) REFERENCES Appointments (AppointmentID)
        )
    ''')
    conn.commit()

create_tables()

# Function to add a new appointment
def add_appointment(patient_id, doctor_id, date, time, location):
    date_str = date.strftime("%Y-%m-%d")
    time_str = time.strftime("%H:%M:%S")

    c.execute('''
        INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status, Location) 
        VALUES (?, ?, ?, ?, 'Scheduled', ?)
    ''', (patient_id, doctor_id, date_str, time_str, location))
    conn.commit()

# Function to update an appointment
def update_appointment(appointment_id, new_date, new_time, new_status, new_location):
    new_date_str = new_date.strftime("%Y-%m-%d")
    new_time_str = new_time.strftime("%H:%M:%S")

    c.execute('''
        UPDATE Appointments
        SET AppointmentDate = ?, AppointmentTime = ?, Status = ?, Location = ?
        WHERE AppointmentID = ?
    ''', (new_date_str, new_time_str, new_status, new_location, appointment_id))
    conn.commit()

# Function to delete an appointment
def delete_appointment(appointment_id):
    c.execute('''
        DELETE FROM Appointments WHERE AppointmentID = ?
    ''', (appointment_id,))
    conn.commit()

# Function to add a medical record
def add_medical_record(appointment_id, diagnosis, details):
    c.execute('''
        INSERT INTO MedicalRecords (AppointmentID, Diagnosis, Details) 
        VALUES (?, ?, ?)
    ''', (appointment_id, diagnosis, details))
    conn.commit()

# Function to update a medical record
def update_medical_record(record_id, new_diagnosis, new_details):
    c.execute('''
        UPDATE MedicalRecords
        SET Diagnosis = ?, Details = ?
        WHERE RecordID = ?
    ''', (new_diagnosis, new_details, record_id))
    conn.commit()

# Function to delete a medical record
def delete_medical_record(record_id):
    c.execute('''
        DELETE FROM MedicalRecords WHERE RecordID = ?
    ''', (record_id,))
    conn.commit()

# Function to add a new patient
def add_patient(first_name, last_name, dob, contact):
    dob_str = dob.strftime("%Y-%m-%d")
    
    c.execute('''
        INSERT INTO Patients (FirstName, LastName, DateOfBirth, ContactNumber) 
        VALUES (?, ?, ?, ?)
    ''', (first_name, last_name, dob_str, contact))
    conn.commit()

# Function to update patient information
def update_patient(patient_id, first_name, last_name, dob, contact):
    dob_str = dob.strftime("%Y-%m-%d")

    c.execute('''
        UPDATE Patients
        SET FirstName = ?, LastName = ?, DateOfBirth = ?, ContactNumber = ?
        WHERE PatientID = ?
    ''', (first_name, last_name, dob_str, contact, patient_id))
    conn.commit()

# Function to delete a patient
def delete_patient(patient_id):
    c.execute('''
        DELETE FROM Patients WHERE PatientID = ?
    ''', (patient_id,))
    conn.commit()

# Function to calculate patient's age
def calculate_age(dob):
    today = datetime.now().date()
    dob = datetime.strptime(dob, "%Y-%m-%d").date()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

# Functions for managing doctors
def add_doctor(first_name, last_name, department, contact):
    c.execute('''
        INSERT INTO Doctors (FirstName, LastName, Department, ContactNumber) 
        VALUES (?, ?, ?, ?)
    ''', (first_name, last_name, department, contact))
    conn.commit()

def update_doctor(doctor_id, first_name, last_name, department, contact):
    c.execute('''
        UPDATE Doctors
        SET FirstName = ?, LastName = ?, Department = ?, ContactNumber = ?
        WHERE DoctorID = ?
    ''', (first_name, last_name, department, contact, doctor_id))
    conn.commit()

def delete_doctor(doctor_id):
    c.execute('''
        DELETE FROM Doctors WHERE DoctorID = ?
    ''', (doctor_id,))
    conn.commit()

# Streamlit interface

st.set_page_config(layout="wide")

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ("Home", "Manage Patients", "Manage Appointments", "Manage Medical Records","Manage Doctors", "Search Database"))

if choice == "Home":
    st.title("Healthcare Patient Management System - Home")
    st.write("Welcome to the Healthcare Patient Management System")

    # System Introduction and Description
    st.markdown("""
    The Healthcare Patient Management System is designed to streamline the management of patient records, appointments, and medical histories in a healthcare setting. This system allows for efficient organization and access to patient information, enhancing the quality of care provided. Key features include:

    - **Patient Management**: Register new patients, update their details, or remove patient records as needed. Keep track of personal details like names, birth dates, and contact information.

    - **Appointment Scheduling**: Schedule, view, update, or cancel appointments. Manage appointment dates and times, and keep track of upcoming and past appointments.

    - **Medical Record Keeping**: Maintain comprehensive medical records for each patient. Add new records, update diagnoses, and manage historical health data.

    """)

    st.write("The current database contains:")

    # Quick Summary of System Data
    total_patients = c.execute("SELECT COUNT(*) FROM Patients").fetchone()[0]
    total_appointments = c.execute("SELECT COUNT(*) FROM Appointments").fetchone()[0]
    total_medical_records = c.execute("SELECT COUNT(*) FROM MedicalRecords").fetchone()[0]
    upcoming_appointments = c.execute("SELECT COUNT(*) FROM Appointments WHERE AppointmentDate >= DATE('now')").fetchone()[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patients", total_patients)
    col2.metric("Total Appointments", total_appointments)
    col3.metric("Upcoming Appointments", upcoming_appointments)
    col4.metric("Total Medical Records", total_medical_records)

    # Visualization of Patient Age Distribution
    dob_data = c.execute("SELECT DateOfBirth FROM Patients").fetchall()
    dob_df = pd.DataFrame(dob_data, columns=['DateOfBirth'])
    dob_df['Age'] = dob_df['DateOfBirth'].apply(calculate_age)

    plt.figure(figsize=(4, 1))
    plt.hist(dob_df['Age'], bins=20, edgecolor='black')
    plt.title('Age Distribution of Patients')
    plt.xlabel('Age')
    plt.ylabel('Number of Patients')
    st.pyplot(plt, use_container_width=False)

elif choice == "Manage Patients":
    st.title("Manage Patients")
  
    col1, col2 = st.columns([1,2]) # Split into columns
    
    with col1:
        # Add New Patient
        with st.form("new_patient_form", clear_on_submit=True):
            st.write("Add New Patient")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1))
            contact = st.text_input("Contact Number")
            submit_button = st.form_submit_button("Submit")

            if submit_button:
                add_patient(first_name, last_name, dob, contact)
                st.success("Patient Added Successfully")

        # Modify Patient Information
        with st.form("modify_patient_form", clear_on_submit=True):
            st.write("Modify Patient Information")
            patient_id = st.number_input("Patient ID to Modify", min_value=1, step=1)
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1))
            contact = st.text_input("Contact Number")
            submit_button_modify = st.form_submit_button("Update Patient")

            if submit_button_modify:
                update_patient(patient_id, first_name, last_name, dob, contact)
                st.success("Patient Information Updated Successfully")

        # Delete Patient
        with st.form("delete_patient_form", clear_on_submit=True):
            st.write("Delete Patient")
            patient_id_delete = st.number_input("Patient ID to Delete", min_value=1, step=1)
            submit_button_delete = st.form_submit_button("Delete Patient")

            if submit_button_delete:
                delete_patient(patient_id_delete)
                st.success("Patient Deleted Successfully")

    with col2:
        st.write("Search Patients")
        with st.form("search_patients_form"):
            search_field_patients = st.selectbox("Search by", ["Patient ID", "First Name", "Last Name", "Contact"])
            search_query_patients = st.text_input("Search Query")
            submit_button_search_patients = st.form_submit_button("Search")

        if submit_button_search_patients:
            if search_field_patients == "Patient ID":
                patients = c.execute("SELECT * FROM Patients WHERE PatientID LIKE ?", ("%"+search_query_patients+"%",)).fetchall()
            elif search_field_patients == "First Name":
                patients = c.execute("SELECT * FROM Patients WHERE FirstName LIKE ?", ("%"+search_query_patients+"%",)).fetchall()
            elif search_field_patients == "Last Name":
                patients = c.execute("SELECT * FROM Patients WHERE LastName LIKE ?", ("%"+search_query_patients+"%",)).fetchall()
            elif search_field_patients == "Contact":
                patients = c.execute("SELECT * FROM Patients WHERE ContactNumber LIKE ?", ("%"+search_query_patients+"%",)).fetchall()
        else:
            patients = c.execute("SELECT * FROM Patients").fetchall()

        # Display Patients
        st.write("Registered Patients")
        if patients:
            patients_df = pd.DataFrame(patients, columns=["Patient ID", "First Name", "Last Name", "DOB", "Contact"])
            st.dataframe(patients_df, height=600, use_container_width=True, hide_index=True)
        else:
            st.write("No patients found.")

elif choice == "Manage Appointments":
    st.title("Manage Appointments")

    col1, col2 = st.columns([1, 2])  # Split into columns

    with col1:
        # Add New Appointment
        with st.form("new_appointment_form", clear_on_submit=True):
            st.write("Schedule New Appointment")
            patient_id = st.number_input("Patient ID", min_value=1, step=1, key="new_app_patient_id")
            doctor_id = st.number_input("Doctor ID", min_value=1, step=1, key="new_app_doctor_id")
            appointment_date = st.date_input("Appointment Date", min_value=datetime.today(), key="new_app_date")
            appointment_time = st.time_input("Appointment Time", key="new_app_time")
            location = st.text_input("Location", key="new_app_location")
            submit_button_appointment = st.form_submit_button("Schedule Appointment")

            if submit_button_appointment:
                add_appointment(patient_id, doctor_id, appointment_date, appointment_time, location)
                st.success("Appointment Scheduled Successfully")

        # Modify Appointment
        with st.form("modify_appointment_form", clear_on_submit=True):
            appointment_id = st.number_input("Appointment ID to Modify", min_value=1, step=1, key="mod_app_id")
            new_appointment_date = st.date_input("New Appointment Date", min_value=date(1900, 1, 1), key="mod_app_date")
            new_appointment_time = st.time_input("New Appointment Time", key="mod_app_time")
            new_location = st.text_input("New Location", key="mod_app_location")
            new_status = st.selectbox("Select New Status", ["Scheduled", "Confirmed", "Cancelled", "No Show", "Completed"], key="mod_app_status")
            submit_button_modify_appointment = st.form_submit_button("Update Appointment")

            if submit_button_modify_appointment:
                update_appointment(appointment_id, new_appointment_date, new_appointment_time, new_status, new_location)
                st.success("Appointment Updated Successfully")

        # Delete Appointment
        with st.form("delete_appointment_form", clear_on_submit=True):
            st.write("Delete Appointment")
            appointment_id_delete = st.number_input("Appointment ID to Delete", min_value=1, step=1, key="del_app_id")
            submit_button_delete_appointment = st.form_submit_button("Delete Appointment")

            if submit_button_delete_appointment:
                delete_appointment(appointment_id_delete)
                st.success("Appointment Deleted Successfully")

    with col2:
        st.write("Search Appointments")
        with st.form("search_appointments_form"):
            search_field_appointments = st.selectbox("Search by", ["Appointment ID", "Patient Name", "Doctor Name", "Date"])
            search_query_appointments = st.text_input("Search Query")
            submit_button_search_appointments = st.form_submit_button("Search")

        if submit_button_search_appointments:
            # Construct the search query based on the selected field
            # Include JOINs to fetch names from the related tables
            query = """
                SELECT Appointments.AppointmentID, Patients.FirstName || ' ' || Patients.LastName as PatientName,
                Doctors.FirstName || ' ' || Doctors.LastName as DoctorName, Appointments.AppointmentDate,
                Appointments.AppointmentTime, Appointments.Status, Appointments.Location
                FROM Appointments
                JOIN Patients ON Appointments.PatientID = Patients.PatientID
                JOIN Doctors ON Appointments.DoctorID = Doctors.DoctorID
            """
            if search_field_appointments == "Appointment ID":
                query += " WHERE Appointments.AppointmentID LIKE ?"
                appointments = c.execute(query, ("%"+search_query_appointments+"%",)).fetchall()
            elif search_field_appointments == "Patient Name":
                query += " WHERE Patients.FirstName || ' ' || Patients.LastName LIKE ?"
                appointments = c.execute(query, ("%"+search_query_appointments+"%",)).fetchall()
            elif search_field_appointments == "Doctor Name":
                query += " WHERE Doctors.FirstName || ' ' || Doctors.LastName LIKE ?"
                appointments = c.execute(query, ("%"+search_query_appointments+"%",)).fetchall()
            elif search_field_appointments == "Date":
                query += " WHERE Appointments.AppointmentDate LIKE ?"
                appointments = c.execute(query, ("%"+search_query_appointments+"%",)).fetchall()
        else:
            # Original query to fetch all appointments
            appointments = c.execute("""
                SELECT Appointments.AppointmentID, Patients.FirstName || ' ' || Patients.LastName as PatientName,
                Doctors.FirstName || ' ' || Doctors.LastName as DoctorName, Appointments.AppointmentDate,
                Appointments.AppointmentTime, Appointments.Status, Appointments.Location
                FROM Appointments
                JOIN Patients ON Appointments.PatientID = Patients.PatientID
                JOIN Doctors ON Appointments.DoctorID = Doctors.DoctorID
            """).fetchall()

        # Display Appointments
        st.write("Scheduled Appointments")
        if appointments:
            appointments_df = pd.DataFrame(appointments, columns=["Appointment ID", "Patient Name", "Doctor Name", "Date", "Time", "Status", "Location"])
            st.dataframe(appointments_df, height=600, use_container_width=True, hide_index=True)
        else:
            st.write("No appointments found.")

elif choice == "Manage Medical Records":
    st.title("Manage Medical Records")

    col1, col2 = st.columns([1, 2])  # Split into columns

    with col1:
        # Add New Medical Record
        with st.form("new_medical_record_form", clear_on_submit=True):
            st.write("Add New Medical Record")
            appointment_id_record = st.number_input("Appointment ID for Record", min_value=1, step=1, key="new_med_rec_app_id")
            diagnosis = st.text_area("Diagnosis", key="new_med_rec_diagnosis")
            details = st.text_area("Details", key="new_med_rec_details")
            submit_button_record = st.form_submit_button("Submit Medical Record")

            if submit_button_record:
                add_medical_record(appointment_id_record, diagnosis, details)
                st.success("Medical Record Added Successfully")

        # Modify Medical Record
        with st.form("modify_medical_record_form", clear_on_submit=True):
            st.write("Modify Medical Record")
            record_id = st.number_input("Record ID to Modify", min_value=1, step=1, key="mod_med_rec_id")
            new_diagnosis = st.text_area("New Diagnosis", key="mod_med_rec_diagnosis")
            new_details = st.text_area("New Details", key="mod_med_rec_details")
            submit_button_modify_record = st.form_submit_button("Update Medical Record")

            if submit_button_modify_record:
                update_medical_record(record_id, new_diagnosis, new_details)
                st.success("Medical Record Updated Successfully")

        # Delete Medical Record
        with st.form("delete_medical_record_form", clear_on_submit=True):
            st.write("Delete Medical Record")
            record_id_delete = st.number_input("Record ID to Delete", min_value=1, step=1, key="del_med_rec_id")
            submit_button_delete_record = st.form_submit_button("Delete Medical Record")

            if submit_button_delete_record:
                delete_medical_record(record_id_delete)
                st.success("Medical Record Deleted Successfully")

    with col2:
        st.write("Search Medical Records")
        with st.form("search_medical_records_form"):
            search_field_medical_records = st.selectbox("Search by", ["Patient Name", "Doctor Name", "Diagnosis"])
            search_query_medical_records = st.text_input("Search Query")
            submit_button_search_medical_records = st.form_submit_button("Search")

        if submit_button_search_medical_records:
            # Construct the search query based on the selected field
            # Include JOINs to fetch names from the related tables
            query = """
                SELECT MedicalRecords.RecordID, Appointments.AppointmentID, Patients.FirstName || ' ' || Patients.LastName as PatientName,
                Doctors.FirstName || ' ' || Doctors.LastName as DoctorName, MedicalRecords.Diagnosis, MedicalRecords.Details
                FROM MedicalRecords
                JOIN Appointments ON MedicalRecords.AppointmentID = Appointments.AppointmentID
                JOIN Patients ON Appointments.PatientID = Patients.PatientID
                JOIN Doctors ON Appointments.DoctorID = Doctors.DoctorID
            """
            if search_field_medical_records == "Patient Name":
                query += " WHERE Patients.FirstName || ' ' || Patients.LastName LIKE ?"
                medical_records = c.execute(query, ("%"+search_query_medical_records+"%",)).fetchall()
            elif search_field_medical_records == "Doctor Name":
                query += " WHERE Doctors.FirstName || ' ' || Doctors.LastName LIKE ?"
                medical_records = c.execute(query, ("%"+search_query_medical_records+"%",)).fetchall()
            elif search_field_medical_records == "Diagnosis":
                query += " WHERE MedicalRecords.Diagnosis LIKE ?"
                medical_records = c.execute(query, ("%"+search_query_medical_records+"%",)).fetchall()
        else:
            # Original query to fetch all medical records
            medical_records = c.execute("""
                SELECT MedicalRecords.RecordID, Appointments.AppointmentID, Patients.FirstName || ' ' || Patients.LastName as PatientName,
                Doctors.FirstName || ' ' || Doctors.LastName as DoctorName, MedicalRecords.Diagnosis, MedicalRecords.Details
                FROM MedicalRecords
                JOIN Appointments ON MedicalRecords.AppointmentID = Appointments.AppointmentID
                JOIN Patients ON Appointments.PatientID = Patients.PatientID
                JOIN Doctors ON Appointments.DoctorID = Doctors.DoctorID
            """).fetchall()

        # Display Medical Records
        st.write("Existing Medical Records")
        if medical_records:
            medical_records_df = pd.DataFrame(medical_records, columns=["Record ID", "Appointment ID", "Patient Name", "Doctor Name", "Diagnosis", "Details"])
            st.dataframe(medical_records_df, height=600, use_container_width=True, hide_index=True)
        else:
            st.write("No medical records found.")

elif choice == "Manage Doctors":
    st.title("Manage Doctors")

    col1, col2 = st.columns([1, 2])  # Split into columns

    with col1:
        # Add New Doctor
        with st.form("new_doctor_form", clear_on_submit=True):
            st.write("Add New Doctor")
            first_name = st.text_input("First Name", key="doc_first_name")
            last_name = st.text_input("Last Name", key="doc_last_name")
            department = st.text_input("Department", key="doc_department")
            contact = st.text_input("Contact Number", key="doc_contact")
            submit_button = st.form_submit_button("Add Doctor")

            if submit_button:
                add_doctor(first_name, last_name, department, contact)
                st.success("Doctor Added Successfully")

        # Modify Doctor Information
        with st.form("modify_doctor_form", clear_on_submit=True):
            st.write("Modify Doctor Information")
            doctor_id = st.number_input("Doctor ID to Modify", min_value=1, step=1, key="modify_doc_id")
            first_name = st.text_input("First Name", key="modify_doc_first_name")
            last_name = st.text_input("Last Name", key="modify_doc_last_name")
            department = st.text_input("Department", key="modify_doc_department")
            contact = st.text_input("Contact Number", key="modify_doc_contact")
            submit_button_modify = st.form_submit_button("Update Doctor")

            if submit_button_modify:
                update_doctor(doctor_id, first_name, last_name, department, contact)
                st.success("Doctor Information Updated Successfully")

        # Delete Doctor
        with st.form("delete_doctor_form", clear_on_submit=True):
            st.write("Delete Doctor")
            doctor_id_delete = st.number_input("Doctor ID to Delete", min_value=1, step=1, key="delete_doc_id")
            submit_button_delete = st.form_submit_button("Delete Doctor")

            if submit_button_delete:
                delete_doctor(doctor_id_delete)
                st.success("Doctor Deleted Successfully")

    with col2:
        st.write("Search Doctors")
        with st.form("search_doctors_form"):
            search_field_doctors = st.selectbox("Search by", ["Doctor ID", "First Name", "Last Name", "Department"])
            search_query_doctors = st.text_input("Search Query")
            submit_button_search_doctors = st.form_submit_button("Search")

        if submit_button_search_doctors:
            if search_field_doctors == "Doctor ID":
                doctors = c.execute("SELECT * FROM Doctors WHERE DoctorID LIKE ?", ("%"+search_query_doctors+"%",)).fetchall()
            elif search_field_doctors == "First Name":
                doctors = c.execute("SELECT * FROM Doctors WHERE FirstName LIKE ?", ("%"+search_query_doctors+"%",)).fetchall()
            elif search_field_doctors == "Last Name":
                doctors = c.execute("SELECT * FROM Doctors WHERE LastName LIKE ?", ("%"+search_query_doctors+"%",)).fetchall()
            elif search_field_doctors == "Department":
                doctors = c.execute("SELECT * FROM Doctors WHERE Department LIKE ?", ("%"+search_query_doctors+"%",)).fetchall()
        else:
            doctors = c.execute("SELECT * FROM Doctors").fetchall()

        # Display Doctors
        st.write("Registered Doctors")
        if doctors:
            doctors_df = pd.DataFrame(doctors, columns=["Doctor ID", "First Name", "Last Name", "Department", "Contact"])
            st.dataframe(doctors_df, height=600, use_container_width=True, hide_index=True)
        else:
            st.write("No doctors found.")

elif choice == "Search Database":
    st.title("Search Patient Records")

    # Step 1: Selection of the search field
    key = 'search_field'
    if key not in st.session_state:
        st.session_state[key] = "Patient ID"

    new_search_field = st.selectbox("Choose a field to search by", 
                                    ["Patient ID", "First Name", "Last Name", "Date of Birth", "Contact Number"],
                                    key=key)

    # Reset the confirmation state if the selection changes
    if new_search_field != st.session_state[key]:
        st.session_state[key] = new_search_field
        if 'search_field_confirmed' in st.session_state:
            del st.session_state['search_field_confirmed']

    if st.button("Press to Confirm Search Field"):
        st.session_state['search_field_confirmed'] = new_search_field

    # Step 2: Input and Search
    if 'search_field_confirmed' in st.session_state:
        with st.form("search_patient_form"):
            search_field = st.session_state['search_field_confirmed']

            if search_field == "Patient ID":
                search_value = st.number_input("Patient ID", min_value=0, step=1)
            elif search_field == "First Name":
                search_value = st.text_input("First Name")
            elif search_field == "Last Name":
                search_value = st.text_input("Last Name")
            elif search_field == "Date of Birth":
                search_value = st.date_input("Date of Birth")
            elif search_field == "Contact Number":
                search_value = st.text_input("Contact Number")

            submit_button_search = st.form_submit_button("Search")

        if submit_button_search:
            # Construct and execute the search query based on selected field
            # This query joins necessary tables to fetch comprehensive information
            query = """
                SELECT Patients.PatientID, Patients.FirstName, Patients.LastName, Patients.DateOfBirth, Patients.ContactNumber,
                Appointments.AppointmentID, Appointments.AppointmentDate, Appointments.AppointmentTime, Appointments.Status, Appointments.Location,
                Doctors.FirstName || ' ' || Doctors.LastName as DoctorName, MedicalRecords.RecordID, MedicalRecords.Diagnosis, MedicalRecords.Details
                FROM Patients
                LEFT JOIN Appointments ON Patients.PatientID = Appointments.PatientID
                LEFT JOIN Doctors ON Appointments.DoctorID = Doctors.DoctorID
                LEFT JOIN MedicalRecords ON Appointments.AppointmentID = MedicalRecords.AppointmentID
            """

            if search_field == "Patient ID":
                query += " WHERE Patients.PatientID = ?"
                result = c.execute(query, (search_value,)).fetchall()
            elif search_field == "First Name":
                query += " WHERE Patients.FirstName LIKE ?"
                result = c.execute(query, (f"%{search_value}%",)).fetchall()
            elif search_field == "Last Name":
                query += " WHERE Patients.LastName LIKE ?"
                result = c.execute(query, (f"%{search_value}%",)).fetchall()
            elif search_field == "Date of Birth":
                query += " WHERE Patients.DateOfBirth = ?"
                result = c.execute(query, (search_value.strftime("%Y-%m-%d"),)).fetchall()
            elif search_field == "Contact Number":
                query += " WHERE Patients.ContactNumber LIKE ?"
                result = c.execute(query, (f"%{search_value}%",)).fetchall()

            # Display the search results
            if result:
                # Convert the search result to a DataFrame
                result_df = pd.DataFrame(result, columns=["PatientID", "FirstName", "LastName", "DateOfBirth", "ContactNumber", 
                                                        "AppointmentID", "AppointmentDate", "AppointmentTime", "Status", 
                                                        "Location", "DoctorName", "RecordID", "Diagnosis", "Details"])

                # Display the filtered data table with sorting enabled
                st.dataframe(result_df, height=600, use_container_width=True, hide_index=True)
            else:
                st.warning("No patients found with the provided search criteria.")

# Always close the connection
conn.close()