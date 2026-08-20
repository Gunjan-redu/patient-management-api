-- schema.sql : Patient Management API database
-- Rebuild: docker exec -i patient-db psql -U postgres -d patients_db < schema.sql

-- 1. Patients table 
CREATE TABLE patients (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(60) NOT NULL,
    gender  VARCHAR(20) NOT NULL CHECK (gender IN ('male', 'female', 'other')),
    age     INTEGER NOT NULL CHECK (age > 0 AND age < 120),
    height  NUMERIC(5,1) NOT NULL CHECK (height > 30 AND height < 272),
    weight  NUMERIC(5,1) NOT NULL CHECK (weight > 1 AND weight < 500),
    city    VARCHAR(60) NOT NULL
);

-- 2. Appointments table 
CREATE TABLE appointments (
    id          SERIAL PRIMARY KEY,
    patient_id  INTEGER NOT NULL REFERENCES patients(id),
    appt_at     TIMESTAMP NOT NULL,
    reason      VARCHAR(200) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT now()
);

-- 3. Seed data: 
INSERT INTO patients (name, gender, age, height, weight, city) VALUES
    ('Skyrah Bagaoisan', 'female', 11, 110, 45, 'Bristol'),
    ('Rubenas Vilkyte', 'male', 9, 90.0, 35.0, 'London'),
    ('Jeetu', 'male', 45, 180.0, 86.0, 'Pune'),
    ('Shlok', 'male', 14, 170.0, 70.0, 'Dubai'),
    ('Chandini', 'female', 29, 145.0, 50.0, 'Modinagar'),
    ('Fateme Abdal', 'female', 45, 160.0, 65.0, 'London'),
    ('Sarang Gupta', 'male', 21, 160.0, 65.0, 'Benaras'),
    ('Ishita Rao', 'female', 30, 160.0, 55.0, 'Hyderabad'),
    ('Vikram Joshi', 'male', 39, 169.0, 78.0, 'Kolkata'),
    ('Meera Nair', 'female', 47, 167.0, 74.0, 'Kochi'),
    ('Sanchi Garg', 'female', 28, 140, 60, 'Delhi'),
    ('Shreya', 'female', 30, 170.0, 55.0, 'Meerut'),
    ('Kartika', 'female', 30, 150.0, 50.0, 'Modinagar'),
    ('Shreya Solanki', 'female', 25, 153.0, 56.0, 'Pune'),
    ('Disha Pandey', 'female', 28, 130.0, 56.0, 'Bangalore');

-- 4. Seed data: 

INSERT INTO appointments (patient_id, appt_at, reason) VALUES
(2, '2026-08-25 10:30', 'Blood pressure checkup'),
(2, '2026-09-01 15:00', 'Follow-up'),
(5, '2026-08-27 09:00', 'Annual physical'),
(8, '2026-08-29 11:30', 'Vaccination');