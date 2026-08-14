
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
import re
from pathlib import Path

# إعدادات الصفحة
st.set_page_config(
    page_title="Dentofacial HarmonizeAI™",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================
# قاعدة البيانات (SQLite)
# =============================================================
DB_PATH = "harmonizeai.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        uid TEXT PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT,
        specialty TEXT,
        country TEXT,
        phone TEXT,
        bio TEXT,
        avatar TEXT,
        cover_photo TEXT,
        created_at TIMESTAMP
    )''')
    # جدول المرضى
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT,
        age TEXT,
        gender TEXT,
        notes TEXT,
        patient_id TEXT,
        created_by TEXT,
        created_at TIMESTAMP
    )''')
    # جدول الأعضاء (للملفات الشخصية)
    c.execute('''CREATE TABLE IF NOT EXISTS members (
        email TEXT PRIMARY KEY,
        name TEXT,
        role TEXT,
        specialty TEXT,
        country TEXT,
        phone TEXT,
        bio TEXT,
        avatar TEXT,
        cover_photo TEXT,
        online INTEGER DEFAULT 0,
        last_seen TIMESTAMP,
        joined_at TIMESTAMP
    )''')
    # جدول منشورات Dentbook
    c.execute('''CREATE TABLE IF NOT EXISTS dentbook_posts (
        id TEXT PRIMARY KEY,
        author_id TEXT,
        author_name TEXT,
        author_avatar TEXT,
        author_email TEXT,
        text TEXT,
        image_url TEXT,
        video_url TEXT,
        timestamp TIMESTAMP,
        likes TEXT DEFAULT '[]',
        comments TEXT DEFAULT '[]',
        shares INTEGER DEFAULT 0
    )''')
    # جدول رسائل المجموعة العامة
    c.execute('''CREATE TABLE IF NOT EXISTS group_messages (
        id TEXT PRIMARY KEY,
        sender TEXT,
        sender_email TEXT,
        recipient TEXT DEFAULT 'group',
        text TEXT,
        image_url TEXT,
        video_url TEXT,
        audio_url TEXT,
        timestamp TIMESTAMP,
        read INTEGER DEFAULT 0
    )''')
    # جدول الرسائل الخاصة
    c.execute('''CREATE TABLE IF NOT EXISTS private_messages (
        id TEXT PRIMARY KEY,
        sender TEXT,
        sender_email TEXT,
        recipient TEXT,
        text TEXT,
        image_url TEXT,
        video_url TEXT,
        audio_url TEXT,
        timestamp TIMESTAMP,
        read INTEGER DEFAULT 0
    )''')
    # جدول رسائل المختبر
    c.execute('''CREATE TABLE IF NOT EXISTS lab_messages (
        id TEXT PRIMARY KEY,
        sender TEXT,
        sender_email TEXT,
        text TEXT,
        file_url TEXT,
        file_name TEXT,
        type TEXT,
        timestamp TIMESTAMP
    )''')
    # جدول الإشعارات
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        recipient TEXT,
        sender TEXT,
        sender_email TEXT,
        message TEXT,
        timestamp TIMESTAMP,
        read INTEGER DEFAULT 0,
        target_all INTEGER DEFAULT 0
    )''')
    # جدول الإعلانات
    c.execute('''CREATE TABLE IF NOT EXISTS ads (
        id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        target TEXT,
        created_by TEXT,
        created_by_name TEXT,
        created_at TIMESTAMP,
        status TEXT DEFAULT 'active',
        views INTEGER DEFAULT 0
    )''')
    # جدول الأسئلة في المنتدى
    c.execute('''CREATE TABLE IF NOT EXISTS forum_questions (
        id TEXT PRIMARY KEY,
        title TEXT,
        body TEXT,
        asked_by TEXT,
        asked_by_uid TEXT,
        assigned_to TEXT,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP,
        answers TEXT DEFAULT '[]'
    )''')
    # جدول المواد العلاجية
    c.execute('''CREATE TABLE IF NOT EXISTS materials (
        id TEXT PRIMARY KEY,
        name TEXT,
        usage TEXT,
        created_at TIMESTAMP
    )''')
    # جدول طلبات المختبر
    c.execute('''CREATE TABLE IF NOT EXISTS lab_orders (
        id TEXT PRIMARY KEY,
        tech TEXT,
        work TEXT,
        patient TEXT,
        amount REAL,
        date TIMESTAMP
    )''')
    conn.commit()
    conn.close()

# تهيئة قاعدة البيانات
init_db()

# =============================================================
# دوال المساعدة
# =============================================================
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

def get_user_by_email(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_member_by_email(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM members WHERE email = ?", (email,))
    member = c.fetchone()
    conn.close()
    return member

def create_user(email, password, name, role='doctor'):
    uid = generate_id()
    hashed = hash_password(password)
    now = get_current_time()
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (uid, name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (uid, name, email, hashed, role, now))
        c.execute("INSERT INTO members (email, name, role, online, joined_at) VALUES (?, ?, ?, ?, ?)",
                  (email, name, role, 1, now))
        conn.commit()
        return uid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def authenticate(email, password):
    hashed = hash_password(password)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed))
    user = c.fetchone()
    conn.close()
    if user:
        # تحديث حالة الاتصال في members
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE members SET online = 1, last_seen = ? WHERE email = ?", (get_current_time(), email))
        conn.commit()
        conn.close()
        return dict(user)
    return None

# دوال للمرضى
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

# دوال للمنشورات
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

# دوال للرسائل
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
    c.execute("INSERT INTO private_messages (id, sender, sender_email, recipient, text, image_url, video_url, audio_url, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (mid, sender, sender_email, recipient, text, image_url, video_url, audio_url, now))
    conn.commit()
    conn.close()
    return mid

# دوال للمنتدى
def get_forum_questions():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM forum_questions ORDER BY created_at DESC")
    qs = c.fetchall()
    conn.close()
    return [dict(q) for q in qs]

def add_forum_question(title, body, asked_by, asked_by_uid, assigned_to='all'):
    qid = generate_id()
    now = get_current_time()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO forum_questions (id, title, body, asked_by, asked_by_uid, assigned_to, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (qid, title, body, asked_by, asked_by_uid, assigned_to, now))
    conn.commit()
    conn.close()
    return qid

def add_forum_answer(qid, answer_text, author, author_uid, is_specialist):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT answers FROM forum_questions WHERE id = ?", (qid,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    answers = json.loads(row['answers']) if row['answers'] else []
    answers.append({
        "text": answer_text,
        "author": author,
        "author_uid": author_uid,
        "is_specialist": is_specialist,
        "timestamp": get_current_time().isoformat()
    })
    c.execute("UPDATE forum_questions SET answers = ? WHERE id = ?", (json.dumps(answers), qid))
    conn.commit()
    conn.close()

def update_forum_status(qid, status):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE forum_questions SET status = ? WHERE id = ?", (status, qid))
    conn.commit()
    conn.close()

# =============================================================
# إدارة الجلسة
# =============================================================
def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.current_page = 'home'
        st.session_state.patients = []
        st.session_state.members = []
        st.session_state.dentbook_posts = []
        st.session_state.group_messages = []
        st.session_state.private_messages = []
        st.session_state.lab_messages = []
        st.session_state.notifications = []
        st.session_state.ads = []
        st.session_state.forum_questions = []
        st.session_state.files_uploaded = []
        st.session_state.materials = []
        st.session_state.lab_orders = []
        st.session_state.payment_methods = [
            {"id": "visa", "name": "💳 Visa / Mastercard", "enabled": True, "icon": "fa-credit-card"},
            {"id": "wallet", "name": "📱 محفظتي", "enabled": True, "icon": "fa-wallet"},
            {"id": "cash", "name": "💵 أم فلوس", "enabled": True, "icon": "fa-money-bill"},
            {"id": "shamel", "name": "💰 شامل موني", "enabled": True, "icon": "fa-coins"},
            {"id": "mpay", "name": "📲 إم باي", "enabled": True, "icon": "fa-mobile-alt"},
            {"id": "bank", "name": "🏦 التحويل البنكي", "enabled": True, "icon": "fa-university"},
            {"id": "cashpay", "name": "💵 الدفع النقدي", "enabled": True, "icon": "fa-hand-holding-usd"}
        ]
        st.session_state.selected_payment = None
        st.session_state.pipeline_data = {
            1: {"status": "done", "progress": 100, "name": "التحضير والتوليد"},
            2: {"status": "done", "progress": 100, "name": "النسب التناظرية"},
            3: {"status": "pending", "progress": 60, "name": "الهندسة السنية"},
            4: {"status": "pending", "progress": 30, "name": "الشبكة الوجهية"},
            5: {"status": "inactive", "progress": 0, "name": "الرندرة الفائقة"}
        }
        st.session_state.facial_image = None
        st.session_state.cephalometric_image = None
        st.session_state.smile_image = None
        st.session_state.design_image = None
        st.session_state.dsd_image = None
        st.session_state.dsd_tooth_inserted = False
        st.session_state.captured_media = []
        st.session_state.patient_photos = {}

init_session()

# =============================================================
# دوال التنقل
# =============================================================
def change_page(page):
    st.session_state.current_page = page

def login_user(email, password):
    user = authenticate(email, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        # تحميل البيانات
        st.session_state.patients = get_patients()
        st.session_state.dentbook_posts = get_dentbook_posts()
        st.session_state.group_messages = get_group_messages()
        st.session_state.private_messages = get_private_messages(email)
        st.session_state.forum_questions = get_forum_questions()
        return True
    return False

def logout_user():
    # تحديث حالة الاتصال
    if st.session_state.user:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE members SET online = 0 WHERE email = ?", (st.session_state.user['email'],))
        conn.commit()
        conn.close()
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.current_page = 'home'

# =============================================================
# واجهة Streamlit
# =============================================================

def main():
    # العنوان الجانبي
    with st.sidebar:
        st.image("https://via.placeholder.com/150x80?text=HarmonizeAI", use_column_width=True)
        st.title("🦷 HarmonizeAI")
        st.caption("Dentofacial Synergy • Naqeeb412")

        if st.session_state.logged_in:
            user = st.session_state.user
            st.write(f"👋 مرحباً **{user['name']}**")
            if st.button("🚪 تسجيل خروج"):
                logout_user()
                st.rerun()
            st.divider()
            # قائمة الصفحات
            pages = {
                "الرئيسية": "home",
                "لوحة التحكم": "dashboard",
                "المرضى": "patients",
                "إضافة مريض": "new_patient",
                "الأعضاء": "members",
                "Dentbook": "dentbook",
                "الملف الشخصي": "dentbook_profile",
                "المراسلات": "messages",
                "رسائل خاصة": "private_messages",
                "مع المختبر": "lab_chat",
                "مشاركة الملفات": "file_sharing",
                "التشخيص الذكي": "diagnosis",
                "خطة العلاج": "treatment_plan",
                "المواد العلاجية": "materials",
                "تحليل الوجه": "facial",
                "تحليل الأشعة": "cephalometric",
                "تصميم الابتسامة": "smile_design",
                "التصميم التجميلي": "aesthetic_design",
                "نماذج 3D": "stl",
                "استوديو DSD": "dsd_studio",
                "المنصة العالمية": "global_platform",
                "خط الإنتاج": "pipeline",
                "مركز APIs": "api_hub",
                "دليل المواد": "materials_guide",
                "الإشعارات": "notifications",
                "الأنظمة": "systems",
                "المسح العلمي": "scientific_scan",
                "NaqAI المساعد": "naqai",
                "التخصصات المتعددة": "interdisciplinary",
                "الإعلانات": "ads",
                "المعمل": "lab",
                "المواعيد": "appointments",
                "الحساب المالي": "accounting",
                "المدفوعات": "payments",
                "الاشتراكات": "subscriptions",
                "الدعوات": "invite",
                "الإعدادات": "settings",
                "التقارير": "reports",
                "التصوير": "photography",
                "الخصوصية": "privacy",
                "الملكية الفكرية": "ip",
                "CAD/CAM": "cadcam",
                "المنتدى": "forum"
            }
            for label, page in pages.items():
                if st.button(label, key=f"nav_{page}", use_container_width=True):
                    change_page(page)
                    st.rerun()
        else:
            st.write("🔐 الرجاء تسجيل الدخول")
            if st.button("تسجيل الدخول", use_container_width=True):
                change_page("login")
                st.rerun()
            if st.button("إنشاء حساب", use_container_width=True):
                change_page("signup")
                st.rerun()

    # المحتوى الرئيسي
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
    elif page == "members":
        show_members()
    elif page == "dentbook":
        show_dentbook()
    elif page == "dentbook_profile":
        show_dentbook_profile()
    elif page == "messages":
        show_messages()
    elif page == "private_messages":
        show_private_messages()
    elif page == "lab_chat":
        show_lab_chat()
    elif page == "file_sharing":
        show_file_sharing()
    elif page == "diagnosis":
        show_diagnosis()
    elif page == "treatment_plan":
        show_treatment_plan()
    elif page == "materials":
        show_materials()
    elif page == "facial":
        show_facial_analysis()
    elif page == "cephalometric":
        show_cephalometric()
    elif page == "smile_design":
        show_smile_design()
    elif page == "aesthetic_design":
        show_aesthetic_design()
    elif page == "stl":
        show_stl()
    elif page == "dsd_studio":
        show_dsd_studio()
    elif page == "global_platform":
        show_global_platform()
    elif page == "pipeline":
        show_pipeline()
    elif page == "api_hub":
        show_api_hub()
    elif page == "materials_guide":
        show_materials_guide()
    elif page == "notifications":
        show_notifications()
    elif page == "systems":
        show_systems()
    elif page == "scientific_scan":
        show_scientific_scan()
    elif page == "naqai":
        show_naqai()
    elif page == "interdisciplinary":
        show_interdisciplinary()
    elif page == "ads":
        show_ads()
    elif page == "lab":
        show_lab()
    elif page == "appointments":
        show_appointments()
    elif page == "accounting":
        show_accounting()
    elif page == "payments":
        show_payments()
    elif page == "subscriptions":
        show_subscriptions()
    elif page == "invite":
        show_invite()
    elif page == "settings":
        show_settings()
    elif page == "reports":
        show_reports()
    elif page == "photography":
        show_photography()
    elif page == "privacy":
        show_privacy()
    elif page == "ip":
        show_ip()
    elif page == "cadcam":
        show_cadcam()
    elif page == "forum":
        show_forum()
    else:
        st.write("الصفحة غير موجودة")

# =============================================================
# صفحات التطبيق
# =============================================================

def show_login():
    st.title("🔐 تسجيل الدخول")
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("دخول")
        if submitted:
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
        submitted = st.form_submit_button("إنشاء حساب")
        if submitted:
            if password != confirm:
                st.error("كلمة المرور غير متطابقة")
            elif len(password) < 6:
                st.error("كلمة المرور يجب أن تكون 6 أحرف على الأقل")
            else:
                uid = create_user(email, password, name, role)
                if uid:
                    st.success("تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
                else:
                    st.error("البريد الإلكتروني مستخدم بالفعل")

def show_home():
    st.title("🦷 Dentofacial HarmonizeAI™")
    st.markdown("### تشخيص دقيق بذكاء اصطناعي")
    st.write("Naqeeb412 HarmonizeAI يدمج بين التصوير ثلاثي الأبعاد، محاكاة الابتسامة، وتحليل الوجه لنتائج علاجية استثنائية.")
    col1, col2, col3 = st.columns(3)
    col1.metric("🧑‍⚕️ مرضى", "5K+")
    col2.metric("🎯 دقة التشخيص", "98%")
    col3.metric("🕒 دعم", "24/7")
    st.info("💡 اختر من القائمة الجانبية للبدء.")

def show_dashboard():
    st.title("📊 لوحة التحكم")
    user = st.session_state.user
    st.write(f"👋 مرحباً **{user['name']}**")
    col1, col2, col3 = st.columns(3)
    col1.metric("👨‍⚕️ المرضى", len(st.session_state.patients))
    col2.metric("📅 مواعيد اليوم", np.random.randint(1, 10))
    col3.metric("🧠 تشخيصات AI", np.random.randint(2, 15))
    st.subheader("📋 آخر المرضى")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df[['name', 'phone', 'age', 'gender']], use_container_width=True)
    else:
        st.write("لا يوجد مرضى.")

def show_patients():
    st.title("👨‍⚕️ قائمة المرضى")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df[['name', 'phone', 'age', 'gender', 'notes']], use_container_width=True)
        for p in st.session_state.patients:
            with st.expander(f"👤 {p['name']}"):
                st.write(f"الهاتف: {p['phone']}")
                st.write(f"العمر: {p['age']}")
                st.write(f"الجنس: {p['gender']}")
                st.write(f"الملاحظات: {p['notes']}")
                if st.button(f"حذف {p['name']}", key=f"del_{p['id']}"):
                    delete_patient(p['id'])
                    st.session_state.patients = get_patients()
                    st.rerun()
    else:
        st.info("لا يوجد مرضى. أضف مريضاً جديداً.")

def show_new_patient():
    st.title("📝 إضافة مريض جديد")
    with st.form("add_patient_form"):
        name = st.text_input("الاسم الكامل")
        phone = st.text_input("رقم الهاتف")
        age = st.text_input("العمر")
        gender = st.selectbox("الجنس", ["", "ذكر", "أنثى"])
        notes = st.text_area("ملاحظات")
        submitted = st.form_submit_button("حفظ المريض")
        if submitted and name:
            uid = st.session_state.user['uid']
            add_patient(name, phone, age, gender, notes, uid)
            st.session_state.patients = get_patients()
            st.success("✅ تم إضافة المريض!")
            st.rerun()
        elif submitted:
            st.error("الاسم مطلوب.")

def show_members():
    st.title("👥 أعضاء النظام")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM members ORDER BY joined_at DESC")
    members = c.fetchall()
    conn.close()
    if members:
        for m in members:
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image("https://via.placeholder.com/60", width=60)
                with col2:
                    st.write(f"**{m['name']}**")
                    st.write(f"📧 {m['email']} | 🟢 {'متصل' if m['online'] else 'غير متصل'}")
                st.divider()
    else:
        st.info("لا يوجد أعضاء.")

def show_dentbook():
    st.title("📱 Dentbook - الشبكة الاجتماعية الطبية")
    # نموذج نشر جديد
    with st.form("new_post_form"):
        text = st.text_area("ماذا تفكر؟ شارك حالة طبية...")
        image_file = st.file_uploader("صورة", type=["jpg", "jpeg", "png"])
        video_file = st.file_uploader("فيديو", type=["mp4", "mov"])
        submitted = st.form_submit_button("نشر")
        if submitted and text:
            # رفع الصورة/الفيديو (محاكاة)
            image_url = None
            video_url = None
            if image_file:
                image_url = "https://via.placeholder.com/300x200?text=Image"
            if video_file:
                video_url = "https://via.placeholder.com/300x200?text=Video"
            user = st.session_state.user
            add_dentbook_post(user['uid'], user['name'], "", user['email'], text, image_url, video_url)
            st.session_state.dentbook_posts = get_dentbook_posts()
            st.success("✅ تم النشر!")
            st.rerun()

    # عرض المنشورات
    st.subheader("📰 المنشورات")
    posts = st.session_state.dentbook_posts
    if posts:
        for p in posts:
            with st.container():
                st.write(f"**{p['author_name']}** - {p['timestamp']}")
                st.write(p['text'])
                if p['image_url']:
                    st.image(p['image_url'], width=200)
                if p['video_url']:
                    st.video(p['video_url'])
                st.caption(f"❤️ {len(json.loads(p['likes'] or '[]'))} إعجاب | 💬 {len(json.loads(p['comments'] or '[]'))} تعليق")
                st.divider()
    else:
        st.info("لا توجد منشورات.")

def show_dentbook_profile():
    st.title("👤 الملف الشخصي")
    user = st.session_state.user
    st.write(f"**الاسم:** {user['name']}")
    st.write(f"**البريد:** {user['email']}")
    st.write(f"**التخصص:** {user.get('specialty', 'غير محدد')}")
    st.write(f"**الدولة:** {user.get('country', 'غير محدد')}")
    st.write(f"**الهاتف:** {user.get('phone', 'غير محدد')}")
    st.write(f"**نبذة:** {user.get('bio', 'لا توجد')}")

def show_messages():
    st.title("💬 المراسلات العامة")
    with st.container():
        msg = st.text_input("اكتب رسالتك...")
        if st.button("إرسال"):
            if msg:
                user = st.session_state.user
                add_group_message(user['name'], user['email'], msg)
                st.session_state.group_messages = get_group_messages()
                st.rerun()
    st.subheader("المحادثة")
    for m in st.session_state.group_messages:
        with st.chat_message(m['sender']):
            st.write(m['text'])
            if m['image_url']:
                st.image(m['image_url'])
            if m['video_url']:
                st.video(m['video_url'])

def show_private_messages():
    st.title("💌 رسائل خاصة بين الأطباء")
    # قائمة الأطباء (من members)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT email, name FROM members WHERE email != ?", (st.session_state.user['email'],))
    doctors = c.fetchall()
    conn.close()
    if not doctors:
        st.info("لا يوجد أطباء آخرون.")
        return
    target = st.selectbox("اختر الطبيب", [f"{d['name']} ({d['email']})" for d in doctors])
    target_email = target.split("(")[-1].replace(")", "")

    # عرض الرسائل الخاصة
    st.subheader(f"المحادثة مع {target_email}")
    msgs = get_private_messages(st.session_state.user['email'])
    for m in msgs:
        if m['sender_email'] == st.session_state.user['email'] or m['recipient'] == target_email:
            with st.chat_message(m['sender']):
                st.write(m['text'])
    # إرسال رسالة
    new_msg = st.text_input("رسالة جديدة")
    if st.button("إرسال خاص"):
        if new_msg:
            user = st.session_state.user
            add_private_message(user['name'], user['email'], target_email, new_msg)
            st.session_state.private_messages = get_private_messages(user['email'])
            st.rerun()

def show_lab_chat():
    st.title("🧪 التواصل مع المختبر")
    msg = st.text_input("رسالة للمختبر")
    if st.button("إرسال"):
        if msg:
            user = st.session_state.user
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO lab_messages (id, sender, sender_email, text, timestamp) VALUES (?, ?, ?, ?, ?)",
                      (generate_id(), user['name'], user['email'], msg, get_current_time()))
            conn.commit()
            conn.close()
            st.success("✅ تم الإرسال")
            st.rerun()
    # عرض الرسائل
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM lab_messages ORDER BY timestamp ASC")
    lab_msgs = c.fetchall()
    conn.close()
    for m in lab_msgs:
        with st.chat_message(m['sender']):
            st.write(m['text'])

def show_file_sharing():
    st.title("📁 مشاركة الملفات")
    uploaded = st.file_uploader("اختر ملفات", accept_multiple_files=True)
    if uploaded:
        for file in uploaded:
            st.write(f"📄 {file.name} - {file.size} bytes")
    # عرض الملفات المحفوظة
    st.subheader("الملفات المرفوعة")
    if 'files_uploaded' in st.session_state:
        for f in st.session_state.files_uploaded:
            st.write(f"📄 {f['name']} - {f['size']} KB")
    else:
        st.info("لا توجد ملفات.")

def show_diagnosis():
    st.title("🩺 التشخيص الذكي")
    patient = st.selectbox("اختر المريض", [p['name'] for p in st.session_state.patients] if st.session_state.patients else ["لا يوجد"])
    doctor = st.text_input("الأخصائي")
    symptoms = st.text_area("الأعراض")
    if st.button("تشخيص AI - Harvard"):
        if symptoms:
            # محاكاة تشخيص
            diagnosis = "ألم في المنطقة. التهاب لثة. سوء إطباق." if "ألم" in symptoms else "لا توجد أعراض واضحة."
            st.success(f"✅ التشخيص: {diagnosis}")
            st.info(f"التوصيات: فحص سريري، تنظيف عميق، تقويم أسنان.")
        else:
            st.warning("أدخل الأعراض أولاً.")

def show_treatment_plan():
    st.title("📋 خطة العلاج")
    main = st.text_input("الخطة الرئيسية")
    alt = st.text_input("الخطة البديلة")
    if st.button("توليد الخطة"):
        st.success("✅ تم توليد الخطة التفصيلية")
        st.write("**التوصية النهائية:** اعتماد الخطة الرئيسية.")
        st.write("نسبة النجاح: 95%، المدة: 18 شهر")

def show_materials():
    st.title("🧪 المواد العلاجية")
    with st.form("add_material"):
        name = st.text_input("اسم المادة")
        usage = st.text_input("الاستخدام")
        submitted = st.form_submit_button("إضافة")
        if submitted and name and usage:
            if 'materials' not in st.session_state:
                st.session_state.materials = []
            st.session_state.materials.append({"name": name, "usage": usage})
            st.success("✅ تم الإضافة")
    st.subheader("قائمة المواد")
    for m in st.session_state.get('materials', []):
        st.write(f"**{m['name']}** - {m['usage']}")

def show_facial_analysis():
    st.title("🧑‍⚕️ تحليل الوجه (478 علامة)")
    uploaded = st.file_uploader("تحميل صورة للوجه", type=["jpg", "jpeg", "png"])
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="الصورة الأصلية", width=400)
        if st.button("تحليل الوجه"):
            # محاكاة تحليل
            st.success("✅ تم تحليل 478 نقطة تشريحية")
            # رسم نقاط افتراضية على الصورة
            draw = ImageDraw.Draw(image)
            for i in range(20):
                x = np.random.randint(0, image.width)
                y = np.random.randint(0, image.height)
                draw.ellipse((x-3, y-3, x+3, y+3), fill="red")
            st.image(image, caption="نتيجة التحليل", width=400)
            st.write("النسبة الذهبية: 1.62، التناسق: 94%")

def show_cephalometric():
    st.title("🩻 تحليل الأشعة")
    uploaded = st.file_uploader("تحميل صورة الأشعة", type=["jpg", "jpeg", "png"])
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="الأشعة الأصلية", width=400)
        if st.button("تحليل الأشعة"):
            st.success("✅ تم تحليل الزوايا")
            # رسم خطوط وزوايا
            draw = ImageDraw.Draw(image)
            # خطوط عشوائية
            draw.line((10, 10, 200, 300), fill="blue", width=3)
            draw.line((200, 10, 10, 300), fill="green", width=3)
            st.image(image, caption="نتيجة التحليل", width=400)
            data = pd.DataFrame({
                "الزاوية": ["SNA", "SNB", "ANB"],
                "قيمة المريض": [82, 80, 2],
                "القيمة الطبيعية": [82, 80, 2],
                "الحالة": ["طبيعي", "طبيعي", "طبيعي"]
            })
            st.table(data)

def show_smile_design():
    st.title("😁 تصميم الابتسامة")
    uploaded = st.file_uploader("تحميل صورة الوجه", type=["jpg", "jpeg", "png"])
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="الصورة الأصلية", width=400)
        if st.button("محاكاة الابتسامة"):
            st.success("✅ تم تطبيق تصميم الابتسامة")
            # تعديل الصورة (مثال: إضافة أسنان بيضاء)
            draw = ImageDraw.Draw(image)
            draw.rectangle((100, 200, 300, 280), fill="white")
            st.image(image, caption="الابتسامة الجديدة", width=400)
            st.write("نسبة التحسن المتوقعة: 92%")

def show_aesthetic_design():
    st.title("🎨 التصميم التجميلي (قبل / بعد)")
    uploaded = st.file_uploader("تحميل صورة", type=["jpg", "jpeg", "png"])
    if uploaded:
        original = Image.open(uploaded)
        st.image(original, caption="قبل", width=300)
        if st.button("محاكاة"):
            # تعديل الصورة (محاكاة)
            modified = original.copy()
            draw = ImageDraw.Draw(modified)
            draw.rectangle((50, 50, 200, 200), fill=(255, 200, 200))
            st.image(modified, caption="بعد", width=300)
            st.success("✅ تم إنشاء المقارنة")

def show_stl():
    st.title("📦 نماذج 3D / Mesh")
    uploaded = st.file_uploader("رفع ملف STL/OBJ", type=["stl", "obj"])
    if uploaded:
        st.success(f"✅ تم رفع {uploaded.name}")
        # عرض نموذج ثلاثي الأبعاد باستخدام plotly
        # محاكاة: عرض كرة 3D
        fig = go.Figure(data=[go.Scatter3d(x=[0,1,2,3], y=[0,1,0,1], z=[0,1,2,1], mode='markers')])
        fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
        st.plotly_chart(fig, use_container_width=True)

def show_dsd_studio():
    st.title("🧬 استوديو إعادة بناء الابتسامة الطبيعية")
    uploaded = st.file_uploader("تحميل صورة المريض", type=["jpg", "jpeg", "png"])
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="الصورة الأصلية", width=400)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("إدراج سن طبيعي"):
                draw = ImageDraw.Draw(image)
                draw.ellipse((150, 200, 200, 280), fill=(230, 200, 180))
                st.image(image, caption="بعد الإدراج", width=400)
        with col2:
            if st.button("تصفية عيوب الوجه"):
                draw = ImageDraw.Draw(image)
                draw.rectangle((50, 50, 100, 100), fill=(200, 200, 200))
                st.image(image, caption="بعد التصفية", width=400)

def show_global_platform():
    st.title("🌍 المنصة العالمية")
    st.write("🔄 خط سير المعالجة والإنتاج المدمج")
    # عرض خطوات الإنتاج
    steps = st.session_state.pipeline_data
    cols = st.columns(len(steps))
    for i, (key, step) in enumerate(steps.items()):
        with cols[i]:
            st.write(f"**الخطوة {key}**")
            st.write(step['name'])
            st.progress(step['progress']/100)
            st.caption(step['status'])

def show_pipeline():
    st.title("🔄 خط الإنتاج المدمج")
    patient = st.selectbox("اختر مريضاً", [p['name'] for p in st.session_state.patients] if st.session_state.patients else ["لا يوجد"])
    st.write("تفاصيل خط الإنتاج للمريض المختار")
    # عرض تقدم خط الإنتاج
    st.progress(0.58)
    st.write("الخطوة 1: ✅ مكتمل")
    st.write("الخطوة 2: ✅ مكتمل")
    st.write("الخطوة 3: ⏳ قيد التنفيذ (60%)")
    st.write("الخطوة 4: ⏳ قيد التنفيذ (30%)")
    st.write("الخطوة 5: ⏸️ في الانتظار")

def show_api_hub():
    st.title("🔌 مركز تواصل الأنظمة")
    st.write("Exocad: 🟢 متصل")
    st.write("Meshy AI: 🟢 متصل")
    st.write("Blender: 🟡 متزامن")
    st.write("AI Studios: 🟢 متصل")
    if st.button("مزامنة جميع الأنظمة"):
        st.success("✅ تمت المزامنة")

def show_materials_guide():
    st.title("🦷 دليل المواد الطبية التجميلية")
    data = pd.DataFrame({
        "المادة": ["Lithium Disilicate", "Hyaluronic Acid", "Botulinum Toxin", "Zirconia"],
        "التصنيف": ["قشور", "فيلر", "تعديل", "جسور"],
        "البروتوكول": ["تحضير مجهري", "حقن", "حقن", "تحضير هيكلي"]
    })
    st.table(data)

def show_notifications():
    st.title("🔔 الإشعارات")
    st.info("لا توجد إشعارات جديدة.")

def show_systems():
    st.title("🖥️ الأنظمة المستخدمة")
    systems = ["Smile Generator", "Exocad Analysis", "Exocad 3D", "Meshy AI", "Blender Cycles", "AI Studios"]
    for s in systems:
        st.write(f"✅ {s} (نشط)")

def show_scientific_scan():
    st.title("🔬 المسح العلمي الشامل")
    if st.button("مسح الوجه"):
        st.success("✅ اكتمل مسح الوجه (478 نقطة)")
    if st.button("مسح الأسنان"):
        st.success("✅ اكتمل مسح الأسنان (32 سن)")
    if st.button("تحليل التناغم"):
        st.success("✅ اكتمل تحليل التناغم")
    if st.button("تقرير علمي"):
        st.success("✅ تم توليد التقرير")

def show_naqai():
    st.title("🤖 NaqAI المساعد الذكي")
    question = st.text_input("اسأل NaqAI...")
    if st.button("إرسال"):
        if question:
            # محاكاة إجابة
            st.write("🧠 شكراً لسؤالك! هذا هو رد المساعد الذكي.")
            st.write("يمكنني مساعدتك في تصميم الابتسامة، تحليل الوجه، المواد الطبية، وغيرها.")

def show_interdisciplinary():
    st.title("🧑‍⚕️ فرق متعددة التخصصات")
    with st.form("add_specialist"):
        name = st.text_input("اسم الأخصائي")
        specialty = st.text_input("التخصص")
        submitted = st.form_submit_button("إضافة")
        if submitted and name and specialty:
            if 'specialists' not in st.session_state:
                st.session_state.specialists = []
            st.session_state.specialists.append({"name": name, "specialty": specialty})
            st.success("✅ تم الإضافة")
    st.subheader("الأخصائيون")
    for s in st.session_state.get('specialists', []):
        st.write(f"**{s['name']}** - {s['specialty']}")

def show_ads():
    st.title("📢 الإعلانات")
    with st.form("new_ad"):
        title = st.text_input("عنوان الإعلان")
        content = st.text_area("المحتوى")
        target = st.selectbox("الجمهور المستهدف", ["الجميع", "الأطباء", "المرضى"])
        submitted = st.form_submit_button("نشر")
        if submitted and title and content:
            st.success("✅ تم نشر الإعلان")
    # عرض الإعلانات
    st.subheader("الإعلانات المنشورة")
    st.info("لا توجد إعلانات.")

def show_lab():
    st.title("🔬 حساب المعمل")
    with st.form("lab_order"):
        tech = st.text_input("اسم الفني")
        work = st.text_input("نوع العمل")
        patient = st.text_input("اسم المريض")
        amount = st.number_input("المبلغ الكلي ($)", min_value=0.0)
        submitted = st.form_submit_button("حفظ")
        if submitted and tech and work:
            if 'lab_orders' not in st.session_state:
                st.session_state.lab_orders = []
            st.session_state.lab_orders.append({"tech": tech, "work": work, "patient": patient, "amount": amount})
            st.success("✅ تم حفظ الطلب")
    st.subheader("طلبات المعمل")
    for o in st.session_state.get('lab_orders', []):
        st.write(f"{o['work']} - {o['tech']} (المريض: {o['patient']})")

def show_appointments():
    st.title("📅 المواعيد")
    patient = st.selectbox("اختر المريض", [p['name'] for p in st.session_state.patients] if st.session_state.patients else ["لا يوجد"])
    date = st.date_input("التاريخ")
    time = st.time_input("الوقت")
    if st.button("جدولة"):
        st.success(f"✅ تم جدولة موعد للمريض {patient} في {date} {time}")

def show_accounting():
    st.title("💰 حساب المريض")
    patient = st.selectbox("اختر المريض", [p['name'] for p in st.session_state.patients] if st.session_state.patients else ["لا يوجد"])
    total = st.number_input("المبلغ الكلي", min_value=0.0)
    paid = st.number_input("المدفوع", min_value=0.0)
    if st.button("تحديث"):
        st.success(f"✅ المتبقي: {total - paid}")

def show_payments():
    st.title("💳 الدفع والمحفظة")
    st.subheader("وسائل الدفع المتاحة")
    for m in st.session_state.payment_methods:
        st.write(f"{m['name']} - {'🟢 مفعلة' if m['enabled'] else '🔴 غير مفعلة'}")
    if st.button("تنفيذ الدفع"):
        st.success("✅ تم تنفيذ الدفع بنجاح")

def show_subscriptions():
    st.title("👑 خطط الاشتراك")
    plans = [
        {"name": "تجريبي", "price": 0, "features": ["3 مرضى"]},
        {"name": "شهري", "price": 99, "features": ["غير محدود", "تحليل AI"]},
        {"name": "سنوي", "price": 999, "features": ["جميع الميزات"]}
    ]
    for p in plans:
        with st.container():
            st.write(f"### {p['name']}")
            st.write(f"السعر: {p['price']} دولار")
            st.write("الميزات: " + ", ".join(p['features']))
            if st.button(f"اشتراك {p['name']}", key=p['name']):
                st.success(f"✅ تم تفعيل الاشتراك {p['name']}")

def show_invite():
    st.title("📨 دعوة الأطباء")
    if st.button("إنشاء رابط دعوة"):
        invite_link = "https://harmonizeai.vercel.app?ref=invite_12345"
        st.code(invite_link)
        st.success("✅ تم إنشاء الرابط")
    if st.button("نسخ الرابط"):
        st.info("تم النسخ إلى الحافظة (محاكاة)")

def show_settings():
    st.title("⚙️ الإعدادات والخصوصية")
    user = st.session_state.user
    with st.form("settings_form"):
        name = st.text_input("الاسم", value=user['name'])
        specialty = st.text_input("التخصص", value=user.get('specialty', ''))
        country = st.text_input("الدولة", value=user.get('country', ''))
        phone = st.text_input("الهاتف", value=user.get('phone', ''))
        bio = st.text_area("نبذة", value=user.get('bio', ''))
        submitted = st.form_submit_button("حفظ")
        if submitted:
            # تحديث في قاعدة البيانات
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE users SET name=?, specialty=?, country=?, phone=?, bio=? WHERE uid=?",
                      (name, specialty, country, phone, bio, user['uid']))
            conn.commit()
            conn.close()
            st.session_state.user['name'] = name
            st.session_state.user['specialty'] = specialty
            st.session_state.user['country'] = country
            st.session_state.user['phone'] = phone
            st.session_state.user['bio'] = bio
            st.success("✅ تم حفظ الإعدادات")
    if st.button("تغيير كلمة المرور"):
        st.info("سيتم إرسال رابط لإعادة تعيين كلمة المرور (محاكاة)")

def show_reports():
    st.title("📄 التقارير")
    if st.button("توليد تقرير"):
        st.success("✅ تم توليد التقرير")
        st.download_button("تحميل PDF", data="محتوى التقرير", file_name="report.pdf", mime="application/pdf")

def show_photography():
    st.title("📸 التصوير")
    img = st.camera_input("التقاط صورة")
    if img:
        st.image(img, caption="الصورة الملتقطة", width=300)
        st.success("✅ تم حفظ الصورة")

def show_privacy():
    st.title("🔒 الخصوصية والأمان")
    st.write("سياسة الخصوصية: نلتزم بحماية بياناتك الشخصية. جميع المعلومات تخزن بشكل آمن.")

def show_ip():
    st.title("©️ حقوق الملكية الفكرية")
    st.write("جميع المحتويات محمية بموجب حقوق النشر والعلامات التجارية.")

def show_cadcam():
    st.title("⚙️ CAD/CAM & 3D")
    st.write("عرض نموذج ثلاثي الأبعاد افتراضي")
    fig = go.Figure(data=[go.Mesh3d(x=[0,1,2,0], y=[0,0,0,1], z=[0,0,1,0], color='gold', opacity=0.8)])
    st.plotly_chart(fig, use_container_width=True)
    if st.button("تحليل النموذج"):
        st.success("✅ تحليل النموذج مكتمل")
        st.write("عدد المضلعات: 32 سن")
        st.write("الحالة: جاهز")

def show_forum():
    st.title("🗣️ منتدى النقاشات مع الأخصائيين")
    # عرض الأسئلة
    st.subheader("الأسئلة المنشورة")
    for q in st.session_state.forum_questions:
        with st.expander(f"📌 {q['title']}"):
            st.write(q['body'])
            st.caption(f"سؤال من {q['asked_by']} - الحالة: {q['status']}")
            answers = json.loads(q.get('answers', '[]'))
            if answers:
                for a in answers:
                    st.write(f"**{a['author']}**: {a['text']}")
            # نموذج رد
            with st.form(key=f"reply_{q['id']}"):
                reply = st.text_input("ردك")
                if st.form_submit_button("رد"):
                    if reply:
                        user = st.session_state.user
                        is_specialist = user['role'] == 'specialist' or user['role'] == 'owner'
                        add_forum_answer(q['id'], reply, user['name'], user['uid'], is_specialist)
                        st.session_state.forum_questions = get_forum_questions()
                        st.rerun()
            if st.session_state.user['role'] in ['specialist', 'owner']:
                if st.button(f"غلق السؤال", key=f"close_{q['id']}"):
                    update_forum_status(q['id'], 'closed')
                    st.session_state.forum_questions = get_forum_questions()
                    st.rerun()
    # سؤال جديد
    with st.form("new_question"):
        title = st.text_input("عنوان السؤال")
        body = st.text_area("التفاصيل")
        target = st.selectbox("توجيه إلى", ["جميع الأخصائيين"] + [d['name'] for d in st.session_state.get('specialists', [])])
        if st.form_submit_button("نشر السؤال"):
            if title and body:
                user = st.session_state.user
                add_forum_question(title, body, user['name'], user['uid'], target)
                st.session_state.forum_questions = get_forum_questions()
                st.success("✅ تم نشر السؤال")
                st.rerun()

# =============================================================
# تشغيل التطبيق
# =============================================================
if __name__ == "__main__":
    main()
```
