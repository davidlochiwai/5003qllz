import sqlite3
import random
from datetime import datetime, timedelta

# Lists of common first and last names
first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth',
               'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
              'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']

diagnoses = [
    'Hypertension', 'Type 2 Diabetes', 'Common Cold', 'Influenza', 'Asthma',
    'Bronchitis', 'Pneumonia', 'Strep Throat', 'Gastroenteritis', 'Arthritis',
    'Back Pain', 'Dermatitis', 'Migraine', 'Anxiety', 'Depression',
    'Allergic Rhinitis', 'Reflux Esophagitis', 'Thyroid Disorder', 'Anemia', 'Urinary Tract Infection'
]

# Function to generate a random date of birth
def random_dob(start_year=1940, end_year=2005):
    start = datetime(year=start_year, month=1, day=1)
    years = end_year - start_year + 1
    end = datetime(year=end_year, month=12, day=31)
    return start + (end - start) * random.random()

# Function to generate a random date for appointments or medical records
def random_date(start_date):
    days = random.randint(-90, 90)
    return start_date + timedelta(days=days)

# Connect to the SQLite database
conn = sqlite3.connect('healthcare.db')
c = conn.cursor()

# Clear existing data from tables
c.execute('DELETE FROM Patients')
c.execute('DELETE FROM Appointments')
c.execute('DELETE FROM MedicalRecords')

# Generate data for the Patients table
patients_data = []
for i in range(1, 51):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    dob = random_dob().strftime('%Y-%m-%d')
    contact_number = ''.join(random.choices('0123456789', k=10))
    patients_data.append((first_name, last_name, dob, contact_number))

# Insert data into Patients table
c.executemany('INSERT INTO Patients (FirstName, LastName, DateOfBirth, ContactNumber) VALUES (?, ?, ?, ?)', patients_data)

# Generate data for the Appointments table
appointments_data = []
appointment_start_date = datetime.now()
for i in range(1, 51):
    patient_id = i
    appointment_date = random_date(appointment_start_date).strftime('%Y-%m-%d')
    appointment_time = f"{random.randint(8, 17)}:{random.choice(['00', '30'])}"
    status = random.choice(['Scheduled', 'Completed', 'Cancelled', 'No Show'])
    appointments_data.append((patient_id, appointment_date, appointment_time, status))

# Insert data into Appointments table
c.executemany('INSERT INTO Appointments (PatientID, AppointmentDate, AppointmentTime, Status) VALUES (?, ?, ?, ?)', appointments_data)

# Generate data for the MedicalRecords table
medical_records_data = []
medical_record_start_date = datetime.now() - timedelta(days=365)
for i in range(1, 51):
    patient_id = i
    date = random_date(medical_record_start_date).strftime('%Y-%m-%d')
    diagnosis = random.choice(diagnoses)  # Select a random diagnosis from the list
    medical_records_data.append((patient_id, date, diagnosis))

# Insert data into MedicalRecords table
c.executemany('INSERT INTO MedicalRecords (PatientID, Date, Diagnosis) VALUES (?, ?, ?)', medical_records_data)

# Commit the transactions and close the connection
conn.commit()
conn.close()

