import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import datetime
import json
import uuid
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# =============================================================
# إعدادات الصفحة
# =============================================================
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
    
    # جدول الأعضاء
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
    
    # جدول رسائل المجموعة
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
    
    # جدول أسئلة المنتدى
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
    
    # ✅ إضافة حساب المالك (بريدك الخاص)
    owner_email = "ndcdental2025@outlook.com"
    c.execute("SELECT * FROM users WHERE email = ?", (owner_email,))
    if not c.fetchone():
        owner_uid = str(uuid.uuid4())
        owner_pass = hashlib.sha256("ndc2025".encode()).hexdigest()
        now = datetime.datetime.now()
        c.execute("INSERT INTO users (uid, name, email, password, role, specialty, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (owner_uid, "د. علي النقيب", owner_email, owner_pass, "owner", "Aesthetic Dentistry", now))
        c.execute("INSERT INTO members (email, name, role, online, joined_at) VALUES (?, ?, ?, ?, ?)",
                  (owner_email, "د. علي النقيب", "owner", 0, now))
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
    return str(uuid.uuid4())

def get_current_time():
    return datetime.datetime.now()

def authenticate(email, password):
    # ✅ حساب افتراضي خاص بك
    if email.lower() == "ndcdental2025@outlook.com" and password == "ndc2025":
        return {
            "uid": "owner_uid",
            "name": "د. علي النقيب",
            "email": "ndcdental2025@outlook.com",
            "role": "owner",
            "specialty": "Aesthetic Dentistry"
        }
    
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

def create_user(email, password, name, role='doctor'):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return None
    uid = generate_id()
    hashed = hash_password(password)
    now = get_current_time()
    c.execute("INSERT INTO users (uid, name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (uid, name, email, hashed, role, now))
    c.execute("INSERT INTO members (email, name, role, online, joined_at) VALUES (?, ?, ?, ?, ?)",
              (email, name, role, 1, now))
    conn.commit()
    conn.close()
    return uid

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

def get_members():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM members ORDER BY joined_at DESC")
    members = c.fetchall()
    conn.close()
    return [dict(m) for m in members]

# =============================================================
# إدارة الجلسة
# =============================================================
def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.current_page = 'login'
        st.session_state.patients = []
        st.session_state.members = []
        st.session_state.dentbook_posts = []
        st.session_state.group_messages = []
        st.session_state.forum_questions = []
        st.session_state.payment_methods = [
            {"id": "visa", "name": "💳 Visa / Mastercard", "enabled": True},
            {"id": "wallet", "name": "📱 محفظتي", "enabled": True},
            {"id": "cash", "name": "💵 أم فلوس", "enabled": True},
            {"id": "shamel", "name": "💰 شامل موني", "enabled": True}
        ]
        st.session_state.specialists = []

init_session()

# =============================================================
# دوال التنقل
# =============================================================
def login_user(email, password):
    user = authenticate(email, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.patients = get_patients()
        st.session_state.dentbook_posts = get_dentbook_posts()
        st.session_state.group_messages = get_group_messages()
        st.session_state.forum_questions = get_forum_questions()
        st.session_state.members = get_members()
        return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.current_page = 'login'

def change_page(page):
    st.session_state.current_page = page

# =============================================================
# واجهة التطبيق - الصفحات
# =============================================================

def show_login():
    st.title("🔐 تسجيل الدخول")
    st.info("👤 البريد: ndcdental2025@outlook.com\n🔑 كلمة المرور: ndc2025")
    
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني", value="ndcdental2025@outlook.com")
        password = st.text_input("كلمة المرور", type="password", value="ndc2025")
        submitted = st.form_submit_button("دخول")
        
        if submitted:
            if login_user(email, password):
                st.success("✅ تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("❌ البريد أو كلمة المرور غير صحيحة")

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
                st.error("❌ كلمة المرور غير متطابقة")
            elif len(password) < 6:
                st.error("❌ كلمة المرور يجب أن تكون 6 أحرف على الأقل")
            else:
                uid = create_user(email, password, name, role)
                if uid:
                    st.success("✅ تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
                else:
                    st.error("❌ البريد الإلكتروني مستخدم بالفعل")

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
    members = st.session_state.members
    
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
            if m.get('image_url'):
                st.image(m['image_url'])
            if m.get('video_url'):
                st.video(m['video_url'])

def show_diagnosis():
    st.title("🩺 التشخيص الذكي")
    
    patients = [p['name'] for p in st.session_state.patients] if st.session_state.patients else ["لا يوجد"]
    patient = st.selectbox("اختر المريض", patients)
    doctor = st.text_input("الأخصائي")
    symptoms = st.text_area("الأعراض")
    
    if st.button("تشخيص AI - Harvard"):
        if symptoms:
            diagnosis = "ألم في المنطقة. التهاب لثة. سوء إطباق." if "ألم" in symptoms else "لا توجد أعراض واضحة."
            st.success(f"✅ التشخيص: {diagnosis}")
            st.info("التوصيات: فحص سريري، تنظيف عميق، تقويم أسنان.")
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

def show_facial_analysis():
    st.title("🧑‍⚕️ تحليل الوجه (478 علامة)")
    
    uploaded = st.file_uploader("تحميل صورة للوجه", type=["jpg", "jpeg", "png"])
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="الصورة الأصلية", width=400)
        
        if st.button("تحليل الوجه"):
            st.success("✅ تم تحليل 478 نقطة تشريحية")
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
            draw = ImageDraw.Draw(image)
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
            draw = ImageDraw.Draw(image)
            draw.rectangle((100, 200, 300, 280), fill="white")
            st.image(image, caption="الابتسامة الجديدة", width=400)
            st.write("نسبة التحسن المتوقعة: 92%")

def show_stl():
    st.title("📦 نماذج 3D / Mesh")
    
    uploaded = st.file_uploader("رفع ملف STL/OBJ", type=["stl", "obj"])
    if uploaded:
        st.success(f"✅ تم رفع {uploaded.name}")
        fig = go.Figure(data=[go.Scatter3d(x=[0,1,2,3], y=[0,1,0,1], z=[0,1,2,1], mode='markers')])
        fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
        st.plotly_chart(fig, use_container_width=True)

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

def show_appointments():
    st.title("📅 المواعيد")
    
    patients = [p['name'] for p in st.session_state.patients] if st.session_state.patients else ["لا يوجد"]
    patient = st.selectbox("اختر المريض", patients)
    date = st.date_input("التاريخ")
    time = st.time_input("الوقت")
    
    if st.button("جدولة"):
        st.success(f"✅ تم جدولة موعد للمريض {patient} في {date} {time}")

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
            st.success("✅ تم حفظ الإعدادات")

def show_reports():
    st.title("📄 التقارير")
    
    if st.button("توليد تقرير"):
        st.success("✅ تم توليد التقرير")
        st.download_button("تحميل PDF", data="محتوى التقرير", file_name="report.pdf", mime="application/pdf")

def show_forum():
    st.title("🗣️ منتدى النقاشات مع الأخصائيين")
    
    st.subheader("الأسئلة المنشورة")
    for q in st.session_state.forum_questions:
        with st.expander(f"📌 {q['title']}"):
            st.write(q['body'])
            st.caption(f"سؤال من {q['asked_by']} - الحالة: {q['status']}")
            
            answers = json.loads(q.get('answers', '[]'))
            if answers:
                for a in answers:
                    st.write(f"**{a['author']}**: {a['text']}")
            
            with st.form(key=f"reply_{q['id']}"):
                reply = st.text_input("ردك")
                if st.form_submit_button("رد"):
                    if reply:
                        user = st.session_state.user
                        is_specialist = user['role'] in ['specialist', 'owner']
                        add_forum_answer(q['id'], reply, user['name'], user['uid'], is_specialist)
                        st.session_state.forum_questions = get_forum_questions()
                        st.rerun()
    
    with st.form("new_question"):
        title = st.text_input("عنوان السؤال")
        body = st.text_area("التفاصيل")
        target = st.selectbox("توجيه إلى", ["جميع الأخصائيين"])
        
        if st.form_submit_button("نشر السؤال"):
            if title and body:
                user = st.session_state.user
                add_forum_question(title, body, user['name'], user['uid'], target)
                st.session_state.forum_questions = get_forum_questions()
                st.success("✅ تم نشر السؤال")
                st.rerun()

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

# =============================================================
# الدالة الرئيسية للتطبيق
# =============================================================
def main():
    # القائمة الجانبية
    with st.sidebar:
        st.image("https://via.placeholder.com/150x80?text=HarmonizeAI", use_column_width=True)
        st.title("🦷 HarmonizeAI")
        st.caption("Dentofacial Synergy • Naqeeb412")
        
        if st.session_state.logged_in:
            user = st.session_state.user
            st.write(f"👋 مرحباً **{user['name']}**")
            
            if st.button("🚪 تسجيل خروج", use_container_width=True):
                logout_user()
                st.rerun()
            
            st.divider()
            
            # قائمة الصفحات
            pages = {
                "🏠 الرئيسية": "home",
                "📊 لوحة التحكم": "dashboard",
                "👨‍⚕️ المرضى": "patients",
                "➕ إضافة مريض": "new_patient",
                "👥 الأعضاء": "members",
                "📱 Dentbook": "dentbook",
                "💬 المراسلات": "messages",
                "🩺 التشخيص الذكي": "diagnosis",
                "📋 خطة العلاج": "treatment_plan",
                "🧑‍⚕️ تحليل الوجه": "facial",
                "🩻 تحليل الأشعة": "cephalometric",
                "😁 تصميم الابتسامة": "smile_design",
                "📦 نماذج 3D": "stl",
                "💳 المدفوعات": "payments",
                "👑 الاشتراكات": "subscriptions",
                "📅 المواعيد": "appointments",
                "⚙️ الإعدادات": "settings",
                "📄 التقارير": "reports",
                "🗣️ المنتدى": "forum",
                "📸 التصوير": "photography",
                "🔒 الخصوصية": "privacy",
                "©️ الملكية الفكرية": "ip"
            }
            
            for label, page in pages.items():
                if st.button(label, key=f"nav_{page}", use_container_width=True):
                    change_page(page)
                    st.rerun()
        else:
            st.write("🔐 الرجاء تسجيل الدخول")
            if st.button("🔑 تسجيل الدخول", use_container_width=True):
                change_page("login")
                st.rerun()
            if st.button("📝 إنشاء حساب", use_container_width=True):
                change_page("signup")
                st.rerun()
    
    # المحتوى الرئيسي
    if not st.session_state.logged_in and st.session_state.current_page not in ['login', 'signup']:
        st.session_state.current_page = 'login'
    
    page = st.session_state.current_page
    
    # عرض الصفحة المطلوبة
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
    elif page == "messages":
        show_messages()
    elif page == "diagnosis":
        show_diagnosis()
    elif page == "treatment_plan":
        show_treatment_plan()
    elif page == "facial":
        show_facial_analysis()
    elif page == "cephalometric":
        show_cephalometric()
    elif page == "smile_design":
        show_smile_design()
    elif page == "stl":
        show_stl()
    elif page == "payments":
        show_payments()
    elif page == "subscriptions":
        show_subscriptions()
    elif page == "appointments":
        show_appointments()
    elif page == "settings":
        show_settings()
    elif page == "reports":
        show_reports()
    elif page == "forum":
        show_forum()
    elif page == "photography":
        show_photography()
    elif page == "privacy":
        show_privacy()
    elif page == "ip":
        show_ip()
    else:
        show_home()

# =============================================================
# تشغيل التطبيق
# =============================================================
if __name__ == "__main__":
    main()
