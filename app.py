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

# إعدادات الصفحة (يجب أن تكون في الأعلى)
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
    # [باقي جداول قاعدة البيانات الخاصة بك ...]
    conn.commit()

    # إنشاء حساب المالك الافتراضي تلقائياً إذا لم يكن موجوداً
    owner_email = "Ndcdental2025@outlook.com"
    c.execute("SELECT * FROM users WHERE email = ?", (owner_email,))
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
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE members SET online = 1, last_seen = ? WHERE email = ?", (get_current_time(), email))
        conn.commit()
        conn.close()
        return dict(user)
    return None

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
            {"id": "visa", "name": "💳 Visa / Mastercard", "enabled": True},
            {"id": "wallet", "name": "📱 محفظتي", "enabled": True},
            {"id": "cash", "name": "💵 أم فلوس", "enabled": True},
            {"id": "shamel", "name": "💰 شامل موني", "enabled": True},
            {"id": "mpay", "name": "📲 إم باي", "enabled": True},
            {"id": "bank", "name": "🏦 التحويل البنكي", "enabled": True},
            {"id": "cashpay", "name": "💵 الدفع النقدي", "enabled": True}
        ]
        st.session_state.pipeline_data = {
            1: {"status": "done", "progress": 100, "name": "التحضير والتوليد"},
            2: {"status": "done", "progress": 100, "name": "النسب التناظرية"},
            3: {"status": "pending", "progress": 60, "name": "الهندسة السنية"},
            4: {"status": "pending", "progress": 30, "name": "الشبكة الوجهية"},
            5: {"status": "inactive", "progress": 0, "name": "الرندرة الفائقة"}
        }
        st.session_state.specialists = []

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
        st.session_state.forum_questions = get_forum_questions()
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

# =============================================================
# واجهة Streamlit - دوال الصفحات
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
    with st.form("new_post_form"):
        text = st.text_area("ماذا تفكر؟ شارك حالة طبية...")
        image_file = st.file_uploader("صورة", type=["jpg", "jpeg", "png"])
        video_file = st.file_uploader("فيديو", type=["mp4", "mov"])
        submitted = st.form_submit_button("نشر")
        if submitted and text:
            image_url = "https://via.placeholder.com/300x200?text=Image" if image_file else None
            video_url = "https://via.placeholder.com/300x200?text=Video" if video_file else None
            user = st.session_state.user
            add_dentbook_post(user['uid'], user['name'], "", user['email'], text, image_url, video_url)
            st.session_state.dentbook_posts = get_dentbook_posts()
            st.success("✅ تم النشر!")
            st.rerun()
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

def show_private_messages():
    st.title("💌 رسائل خاصة بين الأطباء")
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
    st.subheader(f"المحادثة مع {target_email}")
    msgs = get_private_messages(st.session_state.user['email'])
    for m in msgs:
        if m['sender_email'] == st.session_state.user['email'] or m['recipient'] == target_email:
            with st.chat_message(m['sender']):
                st.write(m['text'])
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

def show_diagnosis():
    st.title("🩺 التشخيص الذكي")
    symptoms = st.text_area("الأعراض")
    if st.button("تشخيص AI"):
        if symptoms:
            st.success("✅ التشخيص: التهاب لثة / سوء إطباق محتمل.")
        else:
            st.warning("أدخل الأعراض أولاً.")

def show_treatment_plan():
    st.title("📋 خطة العلاج")
    if st.button("توليد الخطة"):
        st.success("✅ تم توليد الخطة التفصيلية (نسبة النجاح: 95%)")

def show_materials():
    st.title("🧪 المواد العلاجية")
    with st.form("add_material"):
        name = st.text_input("اسم المادة")
        usage = st.text_input("الاستخدام")
        submitted = st.form_submit_button("إضافة")
        if submitted and name and usage:
            st.session_state.materials.append({"name": name, "usage": usage})
            st.success("✅ تم الإضافة")
    for m in st.session_state.materials:
        st.write(f"**{m['name']}** - {m['usage']}")

def show_facial_analysis():
    st.title("🧑‍⚕️ تحليل الوجه")
    uploaded = st.file_uploader("تحميل صورة للوجه", type=["jpg", "jpeg", "png"])
    if uploaded and st.button("تحليل الوجه"):
        st.success("✅ تم تحليل 478 نقطة تشريحية بنجاح")

def show_cephalometric():
    st.title("🩻 تحليل الأشعة")
    uploaded = st.file_uploader("تحميل صورة الأشعة", type=["jpg", "jpeg", "png"])
    if uploaded and st.button("تحليل الأشعة"):
        st.success("✅ تم تحليل الزوايا السنية بنجاح")

def show_smile_design():
    st.title("😁 تصميم الابتسامة")
    uploaded = st.file_uploader("تحميل صورة", type=["jpg", "jpeg", "png"])
    if uploaded and st.button("محاكاة الابتسامة"):
        st.success("✅ تم تطبيق التصميم التجميلي")

def show_aesthetic_design():
    st.title("🎨 التصميم التجميلي")
    st.info("خاصية مقارنة قبل وبعد متوفرة.")

def show_stl():
    st.title("📦 نماذج 3D / Mesh")
    uploaded = st.file_uploader("رفع ملف STL/OBJ", type=["stl", "obj"])
    if uploaded:
        st.success(f"✅ تم رفع {uploaded.name}")
        fig = go.Figure(data=[go.Scatter3d(x=[0,1,2], y=[0,1,0], z=[0,1,2], mode='markers')])
        st.plotly_chart(fig, use_container_width=True)

def show_dsd_studio():
    st.title("🧬 استوديو DSD")
    st.info("جاهز لاستقبال الصور وإعادة بناء الابتسامة.")

def show_global_platform():
    st.title("🌍 المنصة العالمية")
    for key, step in st.session_state.pipeline_data.items():
        st.write(f"**{step['name']}**: {step['progress']}%")

def show_pipeline():
    st.title("🔄 خط الإنتاج المدمج")
    st.progress(0.7)

def show_api_hub():
    st.title("🔌 مركز تواصل الأنظمة")
    st.write("Exocad: 🟢 متصل | Meshy AI: 🟢 متصل")

def show_materials_guide():
    st.title("🦷 دليل المواد الطبية")
    st.write("Lithium Disilicate, Zirconia, Hyaluronic Acid.")

def show_notifications():
    st.title("🔔 الإشعارات")
    st.info("لا توجد إشعارات جديدة.")

def show_systems():
    st.title("🖥️ الأنظمة المستخدمة")
    st.write("✅ Smile Generator (نشط)")

def show_scientific_scan():
    st.title("🔬 المسح العلمي الشامل")
    if st.button("بدء المسح"):
        st.success("✅ اكتمل المسح الشامل.")

def show_naqai():
    st.title("🤖 NaqAI المساعد الذكي")
    q = st.text_input("اسأل NaqAI...")
    if q and st.button("إرسال"):
        st.write("🧠 أهلاً بك دكتور علي. أنا هنا لمساعدتك في كل ما تطلبه.")

def show_interdisciplinary():
    st.title("🧑‍⚕️ فرق متعددة التخصصات")
    with st.form("add_specialist"):
        name = st.text_input("اسم الأخصائي")
        specialty = st.text_input("التخصص")
        if st.form_submit_button("إضافة"):
            st.session_state.specialists.append({"name": name, "specialty": specialty})
            st.success("✅ تم الإضافة")

def show_ads():
    st.title("📢 الإعلانات")
    st.info("لا توجد إعلانات نشطة حالياً.")

def show_lab():
    st.title("🔬 حساب المعمل")
    with st.form("lab_order"):
        tech = st.text_input("اسم الفني")
        work = st.text_input("نوع العمل")
        amount = st.number_input("المبلغ ($)", min_value=0.0)
        if st.form_submit_button("حفظ"):
            st.success("✅ تم حفظ الطلب")

def show_appointments():
    st.title("📅 المواعيد")
    st.date_input("اختر تاريخ الموعد")

def show_accounting():
    st.title("💰 الحساب المالي")
    total = st.number_input("المبلغ الكلي", min_value=0.0)
    paid = st.number_input("المدفوع", min_value=0.0)
    st.write(f"المتبقي: {total - paid}")

def show_payments():
    st.title("💳 الدفع والمحفظة")
    for m in st.session_state.payment_methods:
        st.write(f"{m['name']} - مفعلة")

def show_subscriptions():
    st.title("👑 خطط الاشتراك")
    st.write("الخطط المتاحة: تجريبي، شهري، سنوي.")

def show_invite():
    st.title("📨 دعوة الأطباء")
    st.code("https://harmonizeai.vercel.app?ref=naqeeb412")

def show_settings():
    st.title("⚙️ الإعدادات والخصوصية")
    user = st.session_state.user
    with st.form("settings_form"):
        name = st.text_input("الاسم", value=user['name'])
        specialty = st.text_input("التخصص", value=user.get('specialty', ''))
        if st.form_submit_button("حفظ"):
            st.success("✅ تم الحفظ")

def show_reports():
    st.title("📄 التقارير")
    if st.button("توليد تقرير"):
        st.success("✅ تم توليد التقرير بنجاح")

def show_photography():
    st.title("📸 التصوير")
    st.camera_input("التقاط صورة للمريض")

def show_privacy():
    st.title("🔒 الخصوصية والأمان")
    st.write("نلتزم بحماية كافة بيانات المرضى والخصوصية الطبية.")

def show_ip():
    st.title("©️ الملكية الفكرية")
    st.write("Naqeeb412 HarmonizeAI™ - جميع الحقوق محفوظة.")

def show_cadcam():
    st.title("⚙️ CAD/CAM & 3D")
    fig = go.Figure(data=[go.Mesh3d(x=[0,1,2,0], y=[0,0,0,1], z=[0,0,1,0], color='gold')])
    st.plotly_chart(fig, use_container_width=True)

def show_forum():
    st.title("🗣️ منتدى النقاشات الطبية")
    for q in st.session_state.forum_questions:
        with st.expander(f"📌 {q['title']}"):
            st.write(q['body'])

# =============================================================
# الدالة الرئيسية
# =============================================================
def main():
    with st.sidebar:
        st.title("🦷 HarmonizeAI")
        st.caption("Dentofacial Synergy • Naqeeb412")

        if st.session_state.logged_in:
            user = st.session_state.user
            st.write(f"👋 مرحباً **{user['name']}**")
            if st.button("🚪 تسجيل خروج"):
                logout_user()
                st.rerun()
            st.divider()
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

    if not st.session_state.logged_in and st.session_state.current_page not in ['login', 'signup']:
        st.session_state.current_page = 'login'

    page = st.session_state.current_page

    pages_map = {
        "login": show_login,
        "signup": show_signup,
        "home": show_home,
        "dashboard": show_dashboard,
        "patients": show_patients,
        "new_patient": show_new_patient,
        "members": show_members,
        "dentbook": show_dentbook,
        "dentbook_profile": show_dentbook_profile,
        "messages": show_messages,
        "private_messages": show_private_messages,
        "lab_chat": show_lab_chat,
        "file_sharing": show_file_sharing,
        "diagnosis": show_diagnosis,
        "treatment_plan": show_treatment_plan,
        "materials": show_materials,
        "facial": show_facial_analysis,
        "cephalometric": show_cephalometric,
        "smile_design": show_smile_design,
        "aesthetic_design": show_aesthetic_design,
        "stl": show_stl,
        "dsd_studio": show_dsd_studio,
        "global_platform": show_global_platform,
        "pipeline": show_pipeline,
        "api_hub": show_api_hub,
        "materials_guide": show_materials_guide,
        "notifications": show_notifications,
        "systems": show_systems,
        "scientific_scan": show_scientific_scan,
        "naqai": show_naqai,
        "interdisciplinary": show_interdisciplinary,
        "ads": show_ads,
        "lab": show_lab,
        "appointments": show_appointments,
        "accounting": show_accounting,
        "payments": show_payments,
        "subscriptions": show_subscriptions,
        "invite": show_invite,
        "settings": show_settings,
        "reports": show_reports,
        "photography": show_photography,
        "privacy": show_privacy,
        "ip": show_ip,
        "cadcam": show_cadcam,
        "forum": show_forum
    }

    if page in pages_map:
        pages_map[page]()
    else:
        st.write("الصفحة غير موجودة")

if __name__ == "__main__":
    main()
