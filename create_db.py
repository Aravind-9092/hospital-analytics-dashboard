import sqlite3
import pandas as pd
import os

# Connect to (or create) the database file
conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()

# Enable foreign key enforcement
cursor.execute("PRAGMA foreign_keys = ON;")

# ---- Create tables with proper schema ----

cursor.executescript("""
DROP TABLE IF EXISTS billing;
DROP TABLE IF EXISTS treatments;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    patient_id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    gender TEXT,
    date_of_birth TEXT,
    contact_number TEXT,
    address TEXT,
    registration_date TEXT,
    insurance_provider TEXT,
    insurance_number TEXT,
    email TEXT
);

CREATE TABLE doctors (
    doctor_id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    specialization TEXT,
    phone_number TEXT,
    years_experience INTEGER,
    hospital_branch TEXT,
    email TEXT
);

CREATE TABLE appointments (
    appointment_id TEXT PRIMARY KEY,
    patient_id TEXT,
    doctor_id TEXT,
    appointment_date TEXT,
    appointment_time TEXT,
    reason_for_visit TEXT,
    status TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE treatments (
    treatment_id TEXT PRIMARY KEY,
    appointment_id TEXT,
    treatment_type TEXT,
    description TEXT,
    cost REAL,
    treatment_date TEXT,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE billing (
    bill_id TEXT PRIMARY KEY,
    patient_id TEXT,
    treatment_id TEXT,
    bill_date TEXT,
    amount REAL,
    payment_method TEXT,
    payment_status TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (treatment_id) REFERENCES treatments(treatment_id)
);
""")

conn.commit()

# ---- Load CSV data into each table ----

tables = ["patients", "doctors", "appointments", "treatments", "billing"]

for table in tables:
    csv_path = os.path.join("data", f"{table}.csv")
    df = pd.read_csv(csv_path)
    df.to_sql(table, conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {table}")

conn.close()
print("Database created successfully: hospital.db")