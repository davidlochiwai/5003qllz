import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Connect to the database
conn = sqlite3.connect('healthcare.db')
c = conn.cursor()

# Clear existing data
def clear_data():
    c.execute('DELETE FROM Patients')
    c.execute('DELETE FROM Doctors')
    c.execute('DELETE FROM Appointments')
    c.execute('DELETE FROM MedicalRecords')
    conn.commit()

# Diagnoses and symptoms by department
department_details = {
    'Cardiology': {
        'Hypertension': ['Headaches', 'Shortness of breath', 'Nosebleeds'],
        'Coronary Artery Disease': ['Chest pain', 'Nausea', 'Extreme fatigue'],
        'Heart Failure': ['Swelling in legs', 'Irregular heartbeat', 'Coughing']
    },
    'Neurology': {
        'Epilepsy': ['Seizures', 'Temporary confusion', 'Uncontrollable jerking'],
        'Migraines': ['Severe headache', 'Nausea', 'Sensitivity to light'],
        'Alzheimer’s Disease': ['Memory loss', 'Difficulty planning', 'Confusion']
    },
    'Orthopedics': {
        'Arthritis': ['Joint pain', 'Swelling', 'Decreased range of motion'],
        'Osteoporosis': ['Back pain', 'Stooped posture', 'Easily fractured bones'],
        'Fracture': ['Pain', 'Swelling', 'Bruising around the injured area']
    },
    'Pediatrics': {
        'Asthma': ['Wheezing', 'Coughing', 'Chest tightness'],
        'Chickenpox': ['Itchy rash', 'Fever', 'Loss of appetite'],
        'Measles': ['Fever', 'Dry cough', 'Runny nose']
    },
    'Oncology': {
        'Breast Cancer': ['Lump in breast', 'Change in breast shape', 'Pain in any area of the breast'],
        'Lung Cancer': ['Coughing blood', 'Chest pain', 'Weight loss'],
        'Leukemia': ['Fever or chills', 'Persistent fatigue', 'Frequent infections']
    }
}

# List of clinics
clinics = ['Clinic 01', 'Clinic 02', 'Clinic 03', 'Clinic 04', 'Clinic 05']

# Generate Doctors
def generate_doctors(n):
    for dept, diagnoses in department_details.items():
        for _ in range(n // len(department_details)):
            c.execute('''
                INSERT INTO Doctors (FirstName, LastName, Department, ContactNumber) 
                VALUES (?, ?, ?, ?)
            ''', (fake.first_name(), fake.last_name(), dept, fake.phone_number()))

# Generate Patients
def generate_patients(n):
    for _ in range(n):
        dob = fake.date_of_birth(minimum_age=0, maximum_age=100).strftime('%Y-%m-%d')
        c.execute('''
            INSERT INTO Patients (FirstName, LastName, DateOfBirth, ContactNumber) 
            VALUES (?, ?, ?, ?)
        ''', (fake.first_name(), fake.last_name(), dob, fake.phone_number()))

# Generate Appointments and Medical Records
def generate_appointments(past_n, future_n):
    statuses_past = ['Completed', 'Cancelled', 'No Show']
    statuses_future = ['Scheduled', 'Cancelled']
    today = datetime(2024, 1, 1)

    for _ in range(past_n):
        date = today - timedelta(days=random.randint(1, 365))
        doctor_id = random.randint(1, 10)
        doctor_dept = c.execute('SELECT Department FROM Doctors WHERE DoctorID = ?', (doctor_id,)).fetchone()[0]
        diagnosis = random.choice(list(department_details[doctor_dept].keys()))
        symptoms = random.choice(department_details[doctor_dept][diagnosis])
        location = random.choice(clinics)
        status = random.choice(statuses_past)
        c.execute('''
            INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status, Location)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (random.randint(1, 30), doctor_id, date.strftime('%Y-%m-%d'), fake.time(), status, location))
        
        # Create a medical record only for 'Completed' appointments
        if status == 'Completed':
            appointment_id = c.lastrowid
            c.execute('''
                INSERT INTO MedicalRecords (AppointmentID, Diagnosis, Details)
                VALUES (?, ?, ?)
            ''', (appointment_id, diagnosis, symptoms))

    for _ in range(future_n):
        date = today + timedelta(days=random.randint(1, 365))
        location = random.choice(clinics)
        status = random.choice(statuses_future)
        c.execute('''
            INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status, Location)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (random.randint(1, 30), random.randint(1, 10), date.strftime('%Y-%m-%d'), fake.time(), status, location))

# Clear existing data
clear_data()

# Generate new data
generate_doctors(10)
generate_patients(200)
generate_appointments(300, 50)

# Commit changes and close connection
conn.commit()
conn.close()

print("Data generation complete.")
