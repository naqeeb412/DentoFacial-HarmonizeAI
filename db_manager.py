import sqlite3
import pandas as pd
import os

DB_NAME = "harmonize_ai.db"

def init_db():
    """إنشاء قاعدة البيانات وجداول المرضى والتحليلات"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            age INTEGER,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clinical_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            symmetry_score TEXT,
            metrics_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    conn.commit()
    conn.close()

def add_patient(name, age, phone):
    """إضافة مريض جديد إلى قاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO patients (full_name, age, phone) VALUES (?, ?, ?)",
        (name, age, phone)
    )
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id

def get_patients_df():
    """استرجاع سجل المرضى كاملاً كـ DataFrame باستخدام Pandas"""
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT 
            id AS 'رقم الملف', 
            full_name AS 'اسم المريض', 
            age AS 'العمر', 
            phone AS 'رقم الهاتف', 
            created_at AS 'تاريخ التسجيل' 
        FROM patients 
        ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

init_db()
