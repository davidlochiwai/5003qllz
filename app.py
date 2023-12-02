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
        CREATE TABLE IF NOT EXISTS Appointments (
            AppointmentID INTEGER PRIMARY KEY, 
            PatientID INTEGER, 
            AppointmentDate TEXT, 
            AppointmentTime TEXT, 
            Status TEXT,
            FOREIGN KEY (PatientID) REFERENCES Patients (PatientID)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS MedicalRecords (
            RecordID INTEGER PRIMARY KEY, 
            PatientID INTEGER, 
            Date TEXT, 
            Diagnosis TEXT,
            FOREIGN KEY (PatientID) REFERENCES Patients (PatientID)
        )
    ''')
    conn.commit()

create_tables()

# Function to add a new appointment
def add_appointment(patient_id, date, time):
    # Convert date and time to strings
    date_str = date.strftime("%Y-%m-%d")
    time_str = time.strftime("%H:%M:%S")

    c.execute('''
        INSERT INTO Appointments (PatientID, AppointmentDate, AppointmentTime, Status) 
        VALUES (?, ?, ?, 'Scheduled')
    ''', (patient_id, date_str, time_str))
    conn.commit()

# Function to update an appointment
def update_appointment(appointment_id, new_date, new_time, new_status):
    new_date_str = new_date.strftime("%Y-%m-%d")
    new_time_str = new_time.strftime("%H:%M:%S")

    c.execute('''
        UPDATE Appointments
        SET AppointmentDate = ?, AppointmentTime = ?, Status = ?
        WHERE AppointmentID = ?
    ''', (new_date_str, new_time_str, new_status, appointment_id))
    conn.commit()

# Function to delete an appointment
def delete_appointment(appointment_id):
    c.execute('''
        DELETE FROM Appointments WHERE AppointmentID = ?
    ''', (appointment_id,))
    conn.commit()

# Function to add a medical record
def add_medical_record(patient_id, date, diagnosis):
    # Convert date to string
    date_str = date.strftime("%Y-%m-%d")

    c.execute('''
        INSERT INTO MedicalRecords (PatientID, Date, Diagnosis) 
        VALUES (?, ?, ?)
    ''', (patient_id, date_str, diagnosis))
    conn.commit()

# Function to update a medical record
def update_medical_record(record_id, new_date, new_diagnosis):
    new_date_str = new_date.strftime("%Y-%m-%d")

    c.execute('''
        UPDATE MedicalRecords
        SET Date = ?, Diagnosis = ?
        WHERE RecordID = ?
    ''', (new_date_str, new_diagnosis, record_id))
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

# Streamlit interface

st.set_page_config(layout="wide")

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ("Home", "Manage Patients", "Manage Appointments", "Manage Medical Records"))

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

    plt.figure(figsize=(6, 2))
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
        # View Patients
        st.write("Registered Patients")
        patients = c.execute("SELECT * FROM Patients").fetchall()
        if patients:
            patients_df = pd.DataFrame(patients, columns=["Patient ID", "First Name", "Last Name", "DOB", "Contact"])
            st.dataframe(patients_df, height=600, use_container_width=True, hide_index=True)
        else:
            st.write("No patients found.")

elif choice == "Manage Appointments":
    st.title("Manage Appointments")
  
    col1, col2 = st.columns([1,2]) # Split into columns
    
    with col1:
        # Add New Appointment
        with st.form("new_appointment_form", clear_on_submit=True):
            st.write("Schedule New Appointment")
            patient_id = st.number_input("Patient ID", min_value=1, step=1)
            appointment_date = st.date_input("Appointment Date", min_value=datetime.today())
            appointment_time = st.time_input("Appointment Time")
            submit_button_appointment = st.form_submit_button("Schedule Appointment")

            if submit_button_appointment:
                add_appointment(patient_id, appointment_date, appointment_time)
                st.success("Appointment Scheduled Successfully")
        
        # Modify Appointment
        with st.form("modify_appointment_form", clear_on_submit=True):
            appointment_id = st.number_input("Appointment ID to Modify", min_value=1, step=1)
            new_appointment_date = st.date_input("New Appointment Date", min_value=date(1900, 1, 1))
            new_appointment_time = st.time_input("New Appointment Time")

            # Dropdown for selecting new status
            new_status = st.selectbox("Select New Status", ["Scheduled", "Confirmed", "Cancelled", "No Show", "Completed"])

            submit_button_modify_appointment = st.form_submit_button("Update Appointment")

            if submit_button_modify_appointment:
                update_appointment(appointment_id, new_appointment_date, new_appointment_time, new_status)
                st.success("Appointment Updated Successfully")

        # Delete Appointment
        with st.form("delete_appointment_form", clear_on_submit=True):
            st.write("Delete Appointment")
            appointment_id_delete = st.number_input("Appointment ID to Delete", min_value=1, step=1)
            submit_button_delete_appointment = st.form_submit_button("Delete Appointment")

            if submit_button_delete_appointment:
                delete_appointment(appointment_id_delete)
                st.success("Appointment Deleted Successfully")

    with col2:
    # View Appointments
        st.write("Scheduled Appointments")
        appointments = c.execute("SELECT * FROM Appointments").fetchall()
        if appointments:
            appointments_df = pd.DataFrame(appointments, columns=["Appointment ID", "Patient ID", "Date", "Time", "Status"])
            st.dataframe(appointments_df, height=600, use_container_width=True, hide_index=True)
        else:
            st.write("No appointments found.")

elif choice == "Manage Medical Records":
    st.title("Manage Medical Records")
  
    col1, col2 = st.columns([1,2]) # Split into columns
  
    with col1:
        # Add New Medical Record
        with st.form("new_medical_record_form", clear_on_submit=True):
            st.write("Add New Medical Record")
            patient_id_record = st.number_input("Patient ID for Record", min_value=1, step=1)
            record_date = st.date_input("Record Date")
            diagnosis = st.text_area("Diagnosis")
            submit_button_record = st.form_submit_button("Submit Medical Record")

            if submit_button_record:
                add_medical_record(patient_id_record, record_date, diagnosis)
                st.success("Medical Record Added Successfully")

        # Modify Medical Record
        with st.form("modify_medical_record_form", clear_on_submit=True):
            st.write("Modify Medical Record")
            record_id = st.number_input("Record ID to Modify", min_value=1, step=1)
            new_record_date = st.date_input("New Record Date")
            new_diagnosis = st.text_area("New Diagnosis")
            submit_button_modify_record = st.form_submit_button("Update Medical Record")

            if submit_button_modify_record:
                update_medical_record(record_id, new_record_date, new_diagnosis)
                st.success("Medical Record Updated Successfully")

        # Delete Medical Record
        with st.form("delete_medical_record_form", clear_on_submit=True):
            st.write("Delete Medical Record")
            record_id_delete = st.number_input("Record ID to Delete", min_value=1, step=1)
            submit_button_delete_record = st.form_submit_button("Delete Medical Record")

            if submit_button_delete_record:
                delete_medical_record(record_id_delete)
                st.success("Medical Record Deleted Successfully")

    with col2:
        # View and Manage Medical Records
        st.write("Existing Medical Records")
        medical_records = c.execute("SELECT * FROM MedicalRecords").fetchall()
        if medical_records:
            medical_records_df = pd.DataFrame(medical_records, columns=["Record ID", "Patient ID", "Date", "Diagnosis"])
            st.dataframe(medical_records_df, height=600, use_container_width=True, hide_index=True)
        else:
            st.write("No medical records found.")

# Always close the connection
conn.close()