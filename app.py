import streamlit as st
import sqlite3
from datetime import datetime
from datetime import date
import pandas as pd

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

# Function to add a medical record
def add_medical_record(patient_id, date, diagnosis):
    # Convert date to string
    date_str = date.strftime("%Y-%m-%d")

    c.execute('''
        INSERT INTO MedicalRecords (PatientID, Date, Diagnosis) 
        VALUES (?, ?, ?)
    ''', (patient_id, date_str, diagnosis))
    conn.commit()

# Streamlit interface
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ("Home", "Manage Patients", "Manage Appointments", "Manage Medical Records"))

if choice == "Home":
    st.title("Healthcare Patient Management System - Home")
    st.write("Welcome to the Healthcare Patient Management System")

elif choice == "Manage Patients":
    st.title("Manage Patients")

    # Add New Patient
    with st.form("new_patient_form", clear_on_submit=True):
        st.write("Add New Patient")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1))
        contact = st.text_input("Contact Number")
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            c.execute('''
                INSERT INTO Patients (FirstName, LastName, DateOfBirth, ContactNumber) 
                VALUES (?, ?, ?, ?)
            ''', (first_name, last_name, dob.strftime("%Y-%m-%d"), contact))
            conn.commit()
            st.success("Patient Added Successfully")

    # View Patients
    st.write("Registered Patients")
    patients = c.execute("SELECT * FROM Patients").fetchall()
    if patients:
        patients_df = pd.DataFrame(patients, columns=["Patient ID", "First Name", "Last Name", "DOB", "Contact"])
        st.dataframe(patients_df)
    else:
        st.write("No patients found.")

elif choice == "Manage Appointments":
    st.title("Manage Appointments")

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

    # View Appointments
    st.write("Scheduled Appointments")
    appointments = c.execute("SELECT * FROM Appointments").fetchall()
    if appointments:
        appointments_df = pd.DataFrame(appointments, columns=["Appointment ID", "Patient ID", "Date", "Time", "Status"])
        st.dataframe(appointments_df)
    else:
        st.write("No appointments found.")

elif choice == "Manage Medical Records":
    st.title("Manage Medical Records")

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

    # View and Manage Medical Records
    st.write("Existing Medical Records")
    medical_records = c.execute("SELECT * FROM MedicalRecords").fetchall()
    
    # Convert the data to a list of lists, each inner list representing a row
    medical_records_list = [list(record) for record in medical_records]

    # Create and display the dataframe
    if medical_records_list:
        df = pd.DataFrame(medical_records_list, columns=["Record ID", "Patient ID", "Date", "Diagnosis"])
        st.dataframe(df)
    else:
        st.write("No medical records found.")

# Always close the connection
conn.close()


