-- ================================
-- 1. JOINS
-- ================================

-- // Full patient visit history with doctor and treatment details
SELECT 
    p.first_name || ' ' || p.last_name AS patient_name,
    d.first_name || ' ' || d.last_name AS doctor_name,
    d.specialization,
    a.appointment_date,
    t.treatment_type,
    t.cost
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id
LEFT JOIN treatments t ON t.appointment_id = a.appointment_id
ORDER BY a.appointment_date;

-- // Revenue by doctor specialization
SELECT 
    d.specialization,
    COUNT(DISTINCT a.appointment_id) AS total_appointments,
    SUM(b.amount) AS total_revenue
FROM appointments a
JOIN doctors d ON a.doctor_id = d.doctor_id
JOIN treatments t ON t.appointment_id = a.appointment_id
JOIN billing b ON b.treatment_id = t.treatment_id
GROUP BY d.specialization
ORDER BY total_revenue DESC;


-- ================================
-- //AGGREGATIONS (GROUP BY, HAVING)
-- ================================

-- Q3: Doctors handling above-average number of appointments
SELECT 
    d.doctor_id,
    d.first_name || ' ' || d.last_name AS doctor_name,
    COUNT(a.appointment_id) AS appointment_count
FROM doctors d
JOIN appointments a ON a.doctor_id = d.doctor_id
GROUP BY d.doctor_id
HAVING appointment_count > (
    SELECT AVG(cnt) FROM (
        SELECT COUNT(*) AS cnt FROM appointments GROUP BY doctor_id
    )
)
ORDER BY appointment_count DESC;

-- // Appointment status breakdown (e.g. completed vs cancelled vs no-show)
SELECT 
    status,
    COUNT(*) AS total,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM appointments), 1) AS pct_of_total
FROM appointments
GROUP BY status
ORDER BY total DESC;

-- // Average billing amount and total revenue by payment status
SELECT 
    payment_status,
    COUNT(*) AS num_bills,
    ROUND(AVG(amount), 2) AS avg_bill_amount,
    ROUND(SUM(amount), 2) AS total_amount
FROM billing
GROUP BY payment_status;


-- ================================
-- //SUBQUERIES
-- ================================

-- // Patients who have never been billed (data quality / follow-up check)
SELECT p.patient_id, p.first_name, p.last_name
FROM patients p
WHERE p.patient_id NOT IN (
    SELECT DISTINCT patient_id FROM billing
);

-- // Treatments costing more than the average treatment cost
SELECT treatment_id, treatment_type, cost
FROM treatments
WHERE cost > (SELECT AVG(cost) FROM treatments)
ORDER BY cost DESC;


-- ================================
-- 4. WINDOW FUNCTIONS
-- ================================

-- // Rank doctors by total revenue generated
SELECT 
    d.first_name || ' ' || d.last_name AS doctor_name,
    d.specialization,
    SUM(b.amount) AS total_revenue,
    RANK() OVER (ORDER BY SUM(b.amount) DESC) AS revenue_rank
FROM doctors d
JOIN appointments a ON a.doctor_id = d.doctor_id
JOIN treatments t ON t.appointment_id = a.appointment_id
JOIN billing b ON b.treatment_id = t.treatment_id
GROUP BY d.doctor_id;

-- // Running total of billing revenue over time (cumulative revenue trend)
SELECT 
    bill_date,
    amount,
    SUM(amount) OVER (ORDER BY bill_date) AS running_total_revenue
FROM billing
ORDER BY bill_date;

-- // Each patient's most recent appointment (using ROW_NUMBER)
SELECT *
FROM (
    SELECT 
        a.*,
        ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY appointment_date DESC) AS rn
    FROM appointments a
)
WHERE rn = 1;
