import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import datetime
import json
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# إعدادات الصفحة
st.set_page_config(
    page_title="Dentofacial HarmonizeAI™",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================
# دوال المساعدة والقاعدة الأساسية
# =============================================================
DB_PATH = "harmonizeai.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_id():
    import uuid
    return str(uuid.uuid4())

def get_current_time():
    return datetime.datetime.now()

def get_user(uid):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE uid = ?", (uid,))
    user = c.fetchone()
    conn.close()
    return user

def get_patients():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients ORDER BY created_at DESC")
    patients = c.fetchall()
    conn.close()
    return [dict(p) for p in patients]

def add_patient(name, phone, age, gender, notes, created_by):
    pid = generate_id()
    patient_id = "P" + str(len(get_patients()) + 1).zfill(4)
    now = get_current_time()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO patients (id, name, phone, age, gender, notes, patient_id, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (pid, name, phone, age, gender, notes, patient_id, created_by, now))
    conn.commit()
    conn.close()
    return pid

def delete_patient(pid):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM patients WHERE id = ?", (pid,))
    conn.commit()
    conn.close()

def get_dentbook_posts():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM dentbook_posts ORDER BY timestamp DESC")
    posts = c.fetchall()
    conn.close()
    return [dict(p) for p in posts]

def add_dentbook_post(author_id, author_name, author_avatar, author_email, text, image_url=None, video_url=None):
    pid = generate_id()
    now = get_current_time()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO dentbook_posts (id, author_id, author_name, author_avatar, author_email, text, image_url, video_url, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (pid, author_id, author_name, author_avatar, author_email, text, image_url, video_url, now))
    conn.commit()
    conn.close()
    return pid

def get_group_messages():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM group_messages ORDER BY timestamp ASC")
    msgs = c.fetchall()
    conn.close()
    return [dict(m) for m in msgs]

def add_group_message(sender, sender_email, text, image_url=None, video_url=None, audio_url=None):
    mid = generate_id()
    now = get_current_time()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO group_messages (id, sender, sender_email, text, image_url, video_url, audio_url, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (mid, sender, sender_email, text, image_url, video_url, audio_url, now))
    conn.commit()
    conn.close()
    return mid

def get_private_messages(recipient):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM private_messages WHERE sender_email = ? OR recipient = ? ORDER BY timestamp ASC", (recipient, recipient))
    msgs = c.fetchall()
    conn.close()
    return [dict(m) for m in msgs]

def add_private_message(sender, sender_email, recipient, text, image_url=None, video_url=None, audio_url=None):
    mid = generate_id()
    now = get_current_time()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO private_messages (id, sender, sender_email, recipient, text, image_url, video_url, audio_url, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (mid, sender, sender_email, recipient, text, image_url, video_url, audio_url, now))
    conn.commit()
    conn.close()
    return mid

def create_user(email, password, name, role='doctor'):
    uid = generate_id()
    email_cleaned = email.strip().lower()
    hashed = hash_password(password)
    now = get_current_time()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (uid, name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (uid, name, email_cleaned, hashed, role, now))
        c.execute("INSERT INTO members (email, name, role, online, joined_at) VALUES (?, ?, ?, ?, ?)",
                  (email_cleaned, name, role, 1, now))
        conn.commit()
        return uid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def authenticate(email, password):
    email_cleaned = email.strip().lower()
    hashed = hash_password(password)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE LOWER(email) = ? AND password = ?", (email_cleaned, hashed))
    user = c.fetchone()
    conn.close()
    if user:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE members SET online = 1, last_seen = ? WHERE LOWER(email) = ?", (get_current_time(), email_cleaned))
        conn.commit()
        conn.close()
        return dict(user)
    return None

# =============================================================
# دالة تهيئة قاعدة البيانات
# =============================================================
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        uid TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, specialty TEXT, country TEXT, phone TEXT, bio TEXT, avatar TEXT, cover_photo TEXT, created_at TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        id TEXT PRIMARY KEY, name TEXT, phone TEXT, age TEXT, gender TEXT, notes TEXT, patient_id TEXT, created_by TEXT, created_at TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS members (
        email TEXT PRIMARY KEY, name TEXT, role TEXT, specialty TEXT, country TEXT, phone TEXT, bio TEXT, avatar TEXT, cover_photo TEXT, online INTEGER DEFAULT 0, last_seen TIMESTAMP, joined_at TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS dentbook_posts (
        id TEXT PRIMARY KEY, author_id TEXT, author_name TEXT, author_avatar TEXT, author_email TEXT, text TEXT, image_url TEXT, video_url TEXT, timestamp TIMESTAMP, likes TEXT DEFAULT '[]', comments TEXT DEFAULT '[]', shares INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS group_messages (
        id TEXT PRIMARY KEY, sender TEXT, sender_email TEXT, recipient TEXT DEFAULT 'group', text TEXT, image_url TEXT, video_url TEXT, audio_url TEXT, timestamp TIMESTAMP, read INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS private_messages (
        id TEXT PRIMARY KEY, sender TEXT, sender_email TEXT, recipient TEXT, text TEXT, image_url TEXT, video_url TEXT, audio_url TEXT, timestamp TIMESTAMP, read INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS lab_messages (
        id TEXT PRIMARY KEY, sender TEXT, sender_email TEXT, text TEXT, file_url TEXT, file_name TEXT, type TEXT, timestamp TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY, recipient TEXT, sender TEXT, sender_email TEXT, message TEXT, timestamp TIMESTAMP, read INTEGER DEFAULT 0, target_all INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ads (
        id TEXT PRIMARY KEY, title TEXT, content TEXT, target TEXT, created_by TEXT, created_by_name TEXT, created_at TIMESTAMP, status TEXT DEFAULT 'active', views INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS forum_questions (
        id TEXT PRIMARY KEY, title TEXT, body TEXT, asked_by TEXT, asked_by_uid TEXT, assigned_to TEXT, status TEXT DEFAULT 'open', created_at TIMESTAMP, answers TEXT DEFAULT '[]'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS materials (
        id TEXT PRIMARY KEY, name TEXT, usage TEXT, created_at TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS lab_orders (
        id TEXT PRIMARY KEY, tech TEXT, work TEXT, patient TEXT, amount REAL, date TIMESTAMP
    )''')
    
    conn.commit()

    owner_email = "ndcdental2025@outlook.com"
    c.execute("SELECT * FROM users WHERE LOWER(email) = ?", (owner_email,))
    if not c.fetchone():
        owner_uid = generate_id()
        owner_pass = hash_password("ndc2025")
        now = get_current_time()
        c.execute("INSERT INTO users (uid, name, email, password, role, specialty, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (owner_uid, "د. علي النقيب", owner_email, owner_pass, "doctor", "Aesthetic Dentistry", now))
        c.execute("INSERT INTO members (email, name, role, online, joined_at) VALUES (?, ?, ?, ?, ?)",
                  (owner_email, "د. علي النقيب", "doctor", 0, now))
        conn.commit()
    
    conn.close()

init_db()

# =============================================================
# إدارة الجلسة والصفحات
# =============================================================
def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.current_page = 'home'
        st.session_state.patients = []
        st.session_state.dentbook_posts = []
        st.session_state.group_messages = []
        st.session_state.private_messages = []
        st.session_state.forum_questions = []
        st.session_state.materials = []
        st.session_state.specialists = []
        st.session_state.pipeline_data = {
            1: {"status": "done", "progress": 100, "name": "التحضير والتوليد"},
            2: {"status": "done", "progress": 100, "name": "النسب التناظرية"},
            3: {"status": "pending", "progress": 60, "name": "الهندسة السنية"}
        }

init_session()

def change_page(page):
    st.session_state.current_page = page

def login_user(email, password):
    user = authenticate(email, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.patients = get_patients()
        st.session_state.dentbook_posts = get_dentbook_posts()
        st.session_state.group_messages = get_group_messages()
        st.session_state.private_messages = get_private_messages(email)
        return True
    return False

def logout_user():
    if st.session_state.user:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE members SET online = 0 WHERE email = ?", (st.session_state.user['email'],))
        conn.commit()
        conn.close()
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.current_page = 'home'

# الصفحات
def show_login():
    st.title("🔐 تسجيل الدخول")
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            if login_user(email, password):
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("البريد أو كلمة المرور غير صحيحة")

def show_signup():
    st.title("📝 إنشاء حساب جديد")
    with st.form("signup_form"):
        name = st.text_input("الاسم الكامل")
        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")
        confirm = st.text_input("تأكيد كلمة المرور", type="password")
        role = st.selectbox("الدور", ["doctor", "patient", "specialist"])
        if st.form_submit_button("إنشاء حساب"):
            if password != confirm:
                st.error("كلمة المرور غير متطابقة")
            else:
                uid = create_user(email, password, name, role)
                if uid:
                    st.success("تم إنشاء الحساب بنجاح!")
                else:
                    st.error("البريد مستخدم مسبقاً")

def show_home():
    st.title("🦷 Dentofacial HarmonizeAI™")
    st.write("مرحباً بك في النظام الذكي للتشخيص والتصميم التجميلي.")

def show_dashboard():
    st.title("📊 لوحة التحكم")
    user = st.session_state.user
    st.write(f"مرحباً د. **{user['name']}**")
    col1, col2 = st.columns(2)
    col1.metric("المرضى", len(st.session_state.patients))
    col2.metric("الحالة", "نشط 🟢")

def show_patients():
    st.title("👨‍⚕️ المرضى")
    df = pd.DataFrame(st.session_state.patients)
    if not df.empty:
        st.dataframe(df[['name', 'phone', 'age', 'gender']], use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلون.")

def show_new_patient():
    st.title("➕ إضافة مريض")
    with st.form("p_form"):
        name = st.text_input("الاسم")
        phone = st.text_input("الهاتف")
        age = st.text_input("العمر")
        gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
        notes = st.text_area("ملاحظات")
        if st.form_submit_button("حفظ"):
            add_patient(name, phone, age, gender, notes, st.session_state.user['uid'])
            st.session_state.patients = get_patients()
            st.success("تم الحفظ بنجاح!")
            st.rerun()

# القائد الرئيسي والتنقل
def main():
    with st.sidebar:
        st.title("🦷 HarmonizeAI")
        if st.session_state.logged_in:
            st.write(f"👤 {st.session_state.user['name']}")
            if st.button("🚪 خروج"):
                logout_user()
                st.rerun()
            st.divider()
            pages = {
                "الرئيسية": "home",
                "لوحة التحكم": "dashboard",
                "المرضى": "patients",
                "إضافة مريض": "new_patient"
            }
            for label, page in pages.items():
                if st.button(label, use_container_width=True):
                    change_page(page)
                    st.rerun()
        else:
            if st.button("تسجيل الدخول", use_container_width=True):
                change_page("login")
                st.rerun()
            if st.button("إنشاء حساب", use_container_width=True):
                change_page("signup")
                st.rerun()

    if not st.session_state.logged_in and st.session_state.current_page not in ['login', 'signup']:
        st.session_state.current_page = 'login'

    page = st.session_state.current_page
    if page == "login":
        show_login()
    elif page == "signup":
        show_signup()
    elif page == "home":
        show_home()
    elif page == "dashboard":
        show_dashboard()
    elif page == "patients":
        show_patients()
    elif page == "new_patient":
        show_new_patient()
    else:
        show_home()

if __name__ == "__main__":
    main()
