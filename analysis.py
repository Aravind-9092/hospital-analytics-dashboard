import sqlite3
import pandas as pd

conn = sqlite3.connect("hospital.db")

# ================================
# 1. DATA QUALITY CHECKS
# ================================

print("=== DATA QUALITY CHECKS ===\n")

tables = ["patients", "doctors", "appointments", "treatments", "billing"]

for table in tables:
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    print(f"--- {table} ---")
    print(f"Rows: {len(df)}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print(f"Missing values per column:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print()


# ================================
# 2. KEY BUSINESS INSIGHTS
# ================================

print("\n=== KEY INSIGHTS ===\n")

# Insight 1: Appointment status breakdown
status_df = pd.read_sql("""
    SELECT status, COUNT(*) as total
    FROM appointments
    GROUP BY status
""", conn)
status_df["pct"] = round(100 * status_df["total"] / status_df["total"].sum(), 1)
print("Appointment status breakdown:")
print(status_df, "\n")

# Insight 2: Revenue by specialization
revenue_df = pd.read_sql("""
    SELECT d.specialization, SUM(b.amount) as total_revenue, COUNT(DISTINCT a.appointment_id) as appointments
    FROM appointments a
    JOIN doctors d ON a.doctor_id = d.doctor_id
    JOIN treatments t ON t.appointment_id = a.appointment_id
    JOIN billing b ON b.treatment_id = t.treatment_id
    GROUP BY d.specialization
    ORDER BY total_revenue DESC
""", conn)
print("Revenue by specialization:")
print(revenue_df, "\n")

# Insight 3: Patient demographics - gender split
gender_df = pd.read_sql("SELECT gender, COUNT(*) as total FROM patients GROUP BY gender", conn)
gender_df["pct"] = round(100 * gender_df["total"] / gender_df["total"].sum(), 1)
print("Patient gender split:")
print(gender_df, "\n")

# Insight 4: Payment status (unpaid/pending bills = revenue at risk)
payment_df = pd.read_sql("""
    SELECT payment_status, COUNT(*) as num_bills, ROUND(SUM(amount),2) as total_amount
    FROM billing
    GROUP BY payment_status
""", conn)
payment_df["pct_of_bills"] = round(100 * payment_df["num_bills"] / payment_df["num_bills"].sum(), 1)
print("Payment status breakdown:")
print(payment_df, "\n")

# Insight 5: Top 5 highest-earning doctors
top_doctors_df = pd.read_sql("""
    SELECT d.first_name || ' ' || d.last_name as doctor_name, d.specialization,
           SUM(b.amount) as total_revenue
    FROM doctors d
    JOIN appointments a ON a.doctor_id = d.doctor_id
    JOIN treatments t ON t.appointment_id = a.appointment_id
    JOIN billing b ON b.treatment_id = t.treatment_id
    GROUP BY d.doctor_id
    ORDER BY total_revenue DESC
    LIMIT 5
""", conn)
print("Top 5 doctors by revenue:")
print(top_doctors_df, "\n")

# ================================
# 3. EXPORT CLEAN DATA FOR POWER BI
# ================================

# This single flat table is what you'll import into Power BI in Step 5
master_df = pd.read_sql("""
    SELECT 
        p.patient_id, p.gender, p.insurance_provider,
        d.doctor_id, d.specialization, d.hospital_branch,
        a.appointment_id, a.appointment_date, a.status,
        t.treatment_type, t.cost,
        b.payment_status, b.payment_method, b.amount, b.bill_date
    FROM appointments a
    JOIN patients p ON a.patient_id = p.patient_id
    JOIN doctors d ON a.doctor_id = d.doctor_id
    LEFT JOIN treatments t ON t.appointment_id = a.appointment_id
    LEFT JOIN billing b ON b.treatment_id = t.treatment_id
""", conn)

master_df.to_csv("hospital_master_data.csv", index=False)
print(f"Exported master dataset: {len(master_df)} rows -> hospital_master_data.csv")

conn.close()