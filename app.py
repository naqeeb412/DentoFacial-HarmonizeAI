import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import base64
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import hashlib

# =============================================================
# CONFIG & PAGE SETUP
# =============================================================
st.set_page_config(
    page_title="HarmonizeAI™ | Dentofacial Synergy",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----- Firebase Admin (Optional - uncomment if you have serviceAccountKey.json) -----
# import firebase_admin
# from firebase_admin import credentials, firestore, auth as firebase_auth, storage
# if not firebase_admin._apps:
#     cred = credentials.Certificate("serviceAccountKey.json")
#     firebase_admin.initialize_app(cred, {'storageBucket': 'naqeeb412-harmonizeai.appspot.com'})
#     db = firestore.client()

# =============================================================
# CSS - RTL & Dark Theme (Matching your HTML design)
# =============================================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #075e68 0%, #0a8491 100%);
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebarNav"] ul {
    padding-right: 0;
}
[data-testid="stSidebarNav"] li {
    border-right: 3px solid transparent;
    transition: 0.2s;
}
[data-testid="stSidebarNav"] li:hover, [data-testid="stSidebarNav"] li[aria-selected="true"] {
    background: rgba(255,255,255,0.08);
    border-right-color: #e67e22;
}
.stButton>button {
    border-radius: 60px !important;
    font-weight: 600 !important;
    font-family: 'Cairo', sans-serif !important;
}
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
    border-radius: 30px !important;
    direction: rtl;
    text-align: right;
}
.metric-card {
    background: #1e293b;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #334155;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    text-align: center;
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #e67e22;
}
.badge-gold {
    display: inline-block;
    background: rgba(230,126,34,0.12);
    color: #e67e22;
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid rgba(230,126,34,0.2);
}
.card {
    background: #1e293b;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #334155;
    margin-bottom: 16px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================
# AUTHENTICATION SYSTEM
# =============================================================
OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        OWNER_EMAIL: {
            "name": "علي النقيب",
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD_HASH,
            "role": "owner",
            "specialty": "طب أسنان تجميلي",
            "country": "اليمن",
            "phone": "+967 77 123 4567",
            "bio": "مؤسس منصة Dentofacial HarmonizeAI™",
            "avatar": "",
            "created_at": datetime.now().isoformat()
        }
    }
if "patients" not in st.session_state:
    st.session_state.patients = []
if "dentbook_posts" not in st.session_state:
    st.session_state.dentbook_posts = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lab_messages" not in st.session_state:
    st.session_state.lab_messages = []
if "forum_questions" not in st.session_state:
    st.session_state.forum_questions = []
if "ads" not in st.session_state:
    st.session_state.ads = []
if "materials" not in st.session_state:
    st.session_state.materials = []
if "specialists" not in st.session_state:
    st.session_state.specialists = [
        {"name": "د. أحمد العمري", "specialty": "تقويم أسنان", "online": True},
        {"name": "د. سارة الحكيم", "specialty": "جراحة الفم والوجه", "online": True},
        {"name": "د. خالد النقيب", "specialty": "طب الأسنان التجميلي", "online": False},
        {"name": "د. ليلى العتيبي", "specialty": "علاج الجذور", "online": True},
    ]
if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = []
if "pipeline_progress" not in st.session_state:
    st.session_state.pipeline_progress = 58
if "pipeline_steps" not in st.session_state:
    st.session_state.pipeline_steps = {
        1: {"name": "التحضير والتوليد", "status": "done", "progress": 100},
        2: {"name": "النسب التناظرية", "status": "done", "progress": 100},
        3: {"name": "الهندسة السنية", "status": "pending", "progress": 60},
        4: {"name": "الشبكة الوجهية", "status": "pending", "progress": 30},
        5: {"name": "الرندرة الفائقة", "status": "inactive", "progress": 0},
    }
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

def login_user(email, password):
    db = st.session_state.users_db
    if email in db:
        if db[email]["password"] == hash_pass(password):
            st.session_state.authenticated = True
            st.session_state.current_user = db[email]
            return True
    return False

def signup_user(name, email, password, role="doctor"):
    if email in st.session_state.users_db:
        return False, "البريد الإلكتروني مستخدم مسبقاً"
    st.session_state.users_db[email] = {
        "name": name,
        "email": email,
        "password": hash_pass(password),
        "role": role,
        "specialty": "",
        "country": "",
        "phone": "",
        "bio": "",
        "avatar": "",
        "created_at": datetime.now().isoformat()
    }
    return True, "تم إنشاء الحساب بنجاح"

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_page = "home"
    st.rerun()

# =============================================================
# LOGIN / SIGNUP PAGE
# =============================================================
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="display:inline-flex; align-items:center; gap:10px; justify-content:center;">
                <div style="background:#e67e22; width:55px; height:55px; border-radius:16px; display:flex; align-items:center; justify-content:center; font-size:28px;">🦷</div>
                <div style="text-align:right; line-height:1.2;">
                    <div style="font-size:1.4rem; font-weight:300; color:#94a3b8;">Dentofacial</div>
                    <div style="font-size:2rem; font-weight:800; color:#e67e22; margin-top:-4px;">HarmonizeAI</div>
                    <div style="font-size:0.75rem; color:#94a3b8; letter-spacing:2px;">Naqeeb412 · Synergy</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب"])

        with tab1:
            with st.form("login_form"):
                role = st.selectbox("الدور", ["👑 المالك", "👨‍⚕️ طبيب", "🧑‍⚕️ مريض"])
                email = st.text_input("البريد الإلكتروني", value="ndcdental2025@outlook.com")
                password = st.text_input("كلمة المرور", type="password", value="ndc2025")
                submitted = st.form_submit_button("دخول", use_container_width=True)
                if submitted:
                    if login_user(email, password):
                        st.success("✅ مرحباً بك يا د. علي النقيب!" if email == OWNER_EMAIL else "✅ تم تسجيل الدخول!")
                        st.rerun()
                    else:
                        st.error("❌ بريد أو كلمة مرور غير صحيحة")

        with tab2:
            with st.form("signup_form"):
                s_name = st.text_input("الاسم الكامل")
                s_email = st.text_input("البريد الإلكتروني الجديد")
                s_pass = st.text_input("كلمة المرور", type="password")
                s_role = st.selectbox("نوع الحساب", ["doctor", "patient"])
                s_submitted = st.form_submit_button("إنشاء حساب", use_container_width=True)
                if s_submitted:
                    ok, msg = signup_user(s_name, s_email, s_pass, s_role)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

# =============================================================
# SIDEBAR NAVIGATION
# =============================================================
def sidebar_nav():
    user = st.session_state.current_user
    role = user.get("role", "doctor")
    is_owner = role == "owner"

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:10px;">
            <div style="font-weight:700; font-size:1.1rem;">🧬 Dentofacial</div>
            <div style="font-size:0.7rem; color:#aac4d6;">HarmonizeAI™ · v3.0</div>
        </div>
        <div style="text-align:center; margin-bottom:16px;">
            <div style="font-size:0.85rem; font-weight:600;">{user['name']}</div>
            <div style="font-size:0.65rem; color:#aac4d6;">{user.get('specialty','') or user['role']}</div>
        </div>
        """, unsafe_allow_html=True)

        menu_items = {
            "🏠 الرئيسية": "home",
            "📊 لوحة التحكم": "dashboard",
            "👨‍⚕️ المرضى": "patients",
            "➕ مريض جديد": "new_patient",
            "📸 التصوير": "photography",
            "📱 Dentbook": "dentbook",
            "👤 الملف الشخصي": "profile",
            "👥 الأعضاء": "members",
            "💬 المراسلات": "messages",
            "💌 رسائل خاصة": "private_messages",
            "🧪 مع المختبر": "lab_chat",
            "📁 مشاركة الملفات": "file_sharing",
            "🖥️ مشاركة الشاشة": "screen_share",
            "🩺 التشخيص الذكي": "diagnosis",
            "📋 خطة العلاج": "treatment_plan",
            "🧪 المواد العلاجية": "materials",
            "🧑‍⚕️ تحليل الوجه (478)": "facial",
            "🩻 تحليل الأشعة": "cephalometric",
            "😁 تصميم الابتسامة": "smile_design",
            "🎨 التصميم التجميلي": "aesthetic_design",
            "📦 نماذج 3D/Mesh": "stl_3d",
            "🧬 استوديو DSD الحيوي": "dsd_studio",
            "💎 علاج تجميلي": "aesthetic_treatment",
            "🌍 المنصة العالمية": "global_platform",
            "🔄 خط الإنتاج": "pipeline",
            "🦷 دليل المواد الطبية": "materials_guide",
            "🔌 مركز تواصل الأنظمة": "api_hub",
            "🗄️ محاكي مستودع المريض": "mock_db",
            "🔔 الإشعارات": "notifications",
            "🖥️ الأنظمة المستخدمة": "systems",
            "🔬 المسح العلمي": "scientific_scan",
            "🤖 NaqAI المساعد": "naqai",
            "👥 Interdisciplinary": "interdisciplinary",
            "📢 الإعلانات": "ads",
            "🔬 المعمل": "lab",
            "📅 المواعيد": "appointments",
            "💰 الحساب": "accounting",
            "💳 الدفع والمحفظة": "payments",
            "👑 الاشتراكات": "subscriptions",
            "📨 دعوة الأطباء": "invite",
            "⚙️ الإعدادات": "settings",
            "📄 التقارير": "reports",
            "🔒 الخصوصية": "privacy",
            "©️ حقوق الملكية": "ip",
            "⚙️ CAD/CAM & 3D": "cadcam",
            "🗣️ منتدى النقاشات": "forum",
        }

        for label, key in menu_items.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        st.divider()
        if st.button("🚪 تسجيل خروج", use_container_width=True, type="primary"):
            logout()

# =============================================================
# PAGE RENDERERS
# =============================================================
def page_home():
    st.markdown("""
    <div style="text-align:center; padding:30px 0;">
        <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
            <span class="badge-gold" style="background:#7a0010; color:#fff; border-color:#a8001a;">Harvard Protocol</span>
            <span class="badge-gold">AI-Powered · 3D Planning</span>
            <span class="badge-gold" style="background:rgba(16,185,129,0.12); color:#10b981;">Naqeeb412 Synergy</span>
        </div>
        <h1 style="font-size:2.4rem; font-weight:800;">تشخيص دقيق <span style="color:#e67e22;">بذكاء اصطناعي</span></h1>
        <p style="color:#94a3b8; font-size:1.1rem; max-width:600px; margin:12px auto;">
            Naqeeb412 HarmonizeAI يدمج بين التصوير ثلاثي الأبعاد، محاكاة الابتسامة، وتحليل الوجه لنتائج علاجية استثنائية.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("المريض", "5K+")
    with c2: st.metric("دقة التشخيص", "98%")
    with c3: st.metric("الدعم", "24/7")

    st.markdown("### 🦷 Smile Simulator")
    cols = st.columns(6)
    features = [
        ("👨‍⚕️", "رقمنة المريض", "ملف رقمي شامل"),
        ("🖼️", "رفع الصور", "2D, 3D, Mesh"),
        ("🧠", "تحليل AI", "تقرير دقيق"),
        ("↔️", "قبل / بعد", "مقارنة مرئية"),
        ("📄", "معاينة PDF", "تقرير احترافي"),
        ("🧊", "3D & Mesh", "عرض ثلاثي الأبعاد"),
    ]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center; padding:14px;">
                <div style="font-size:1.8rem; color:#e67e22;">{icon}</div>
                <div style="font-size:0.85rem; font-weight:600;">{title}</div>
                <div style="font-size:0.65rem; color:#94a3b8;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="border:2px solid #e67e22; background:rgba(230,126,34,0.03);">
        <h4 style="color:#e67e22;">🧬 استوديو إعادة بناء الابتسامة الطبيعية <span style="font-size:0.8rem; color:#94a3b8;">Bio-Mimetic DSD</span></h4>
        <p style="color:#94a3b8;">دمج أطقم أسنان حيوية ذات تدرج طبيعي وتصفية آلية لعيوب البشرة وتجاعيد الوجه في الصورة المستهدفة</p>
    </div>
    """, unsafe_allow_html=True)

def page_dashboard():
    st.markdown('<h2>📊 لوحة <span style="color:#e67e22;">التحكم</span></h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    st.markdown(f"<p style='color:#94a3b8;'>مرحباً بك في Dentofacial HarmonizeAI™، <strong>{user['name']}</strong></p>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="card-title">👨‍⚕️ المرضى</div><div class="metric-value">{len(st.session_state.patients)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="card-title">📅 مواعيد اليوم</div><div class="metric-value" style="color:#10b981;">{np.random.randint(2,12)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="card-title">🧠 تشخيصات AI</div><div class="metric-value" style="color:#a855f7;">{len(st.session_state.patients)*3 + 5}</div></div>', unsafe_allow_html=True)

    st.markdown("### 📋 آخر المرضى")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients[:5])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلين بعد.")

    st.markdown("""
    <div class="card" style="border-right:4px solid #e67e22;">
        <h4 style="color:#e67e22;">ℹ️ نبذة عن النظام</h4>
        <p style="color:#94a3b8; line-height:1.8;">
        <strong>Dentofacial HarmonizeAI™</strong> هي منصة متكاملة لتشخيص وعلاج الوجه والأسنان بالذكاء الاصطناعي...
        </p>
    </div>
    """, unsafe_allow_html=True)

def page_patients():
    st.markdown('<h2>👨‍⚕️ قائمة <span style="color:#e67e22;">المرضى</span></h2>', unsafe_allow_html=True)
    search = st.text_input("🔍 بحث عن مريض", placeholder="اكتب اسم المريض...")
    if st.button("➕ مريض جديد", type="primary"):
        st.session_state.current_page = "new_patient"
        st.rerun()

    patients = st.session_state.patients
    if search:
        patients = [p for p in patients if search.lower() in p.get("name","").lower()]

    if patients:
        df = pd.DataFrame(patients)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا يوجد مرضى.")

def page_new_patient():
    st.markdown('<h2>📝 إضافة <span style="color:#e67e22;">مريض جديد</span></h2>', unsafe_allow_html=True)
    with st.form("new_patient_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("الاسم الكامل *")
            age = st.number_input("العمر", min_value=0, max_value=120, value=30)
        with c2:
            phone = st.text_input("رقم الهاتف")
            gender = st.selectbox("الجنس", ["ذكر", "أنثى", "غير محدد"])
        notes = st.text_area("ملاحظات")
        submitted = st.form_submit_button("💾 حفظ المريض", use_container_width=True)
        if submitted and name:
            patient = {
                "id": f"P{len(st.session_state.patients)+1:04d}",
                "name": name,
                "age": age,
                "phone": phone,
                "gender": gender,
                "notes": notes,
                "created_at": datetime.now().isoformat()
            }
            st.session_state.patients.append(patient)
            st.success("✅ تم إضافة المريض بنجاح!")

def page_photography():
    st.markdown('<h2>📸 قسم <span style="color:#e67e22;">التصوير</span></h2>', unsafe_allow_html=True)
    st.info("📷 ارفع صور المريض المطلوبة:")
    cols = st.columns(4)
    types = ["أمامية", "جانبية", "ابتسامة", "فك علوي", "فك سفلي", "أنسجة", "شخصية"]
    for i, t in enumerate(types):
        with cols[i % 4]:
            st.file_uploader(t, type=["jpg","png","jpeg"], key=f"photo_{t}")

def page_dentbook():
    st.markdown('<h2>📱 Dentbook <span style="color:#e67e22;">الشبكة الاجتماعية الطبية</span></h2>', unsafe_allow_html=True)
    with st.container():
        text = st.text_area("ماذا تفكر؟ شارك حالة طبية...", height=80)
        img = st.file_uploader("📎 صورة / فيديو", type=["jpg","png","mp4"], key="dentbook_media")
        if st.button("🚀 نشر", type="primary"):
            if text or img:
                post = {
                    "author": st.session_state.current_user["name"],
                    "text": text,
                    "time": datetime.now().strftime("%H:%M"),
                    "likes": 0
                }
                st.session_state.dentbook_posts.insert(0, post)
                st.success("✅ تم النشر!")

    st.markdown("---")
    for post in st.session_state.dentbook_posts[:10]:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;">
                <strong>{post['author']}</strong>
                <span style="color:#94a3b8; font-size:0.75rem;">{post['time']}</span>
            </div>
            <p>{post['text']}</p>
            <div style="display:flex; gap:12px;">
                <span>❤️ {post['likes']}</span>
                <span>💬 0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def page_profile():
    st.markdown('<h2>👤 الملف <span style="color:#e67e22;">الشخصي</span></h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    c1, c2 = st.columns([1,3])
    with c1:
        st.markdown(f"""
        <div style="width:120px; height:120px; border-radius:50%; background:linear-gradient(145deg,#0a8491,#075e68); display:flex; align-items:center; justify-content:center; font-size:3rem; color:#fff; margin:0 auto;">
            {user['name'][0] if user['name'] else '👤'}
        </div>
        """, unsafe_allow_html=True)
    with c2:
        with st.form("profile_form"):
            name = st.text_input("الاسم", value=user.get("name",""))
            specialty = st.text_input("التخصص", value=user.get("specialty",""))
            country = st.text_input("الدولة", value=user.get("country",""))
            phone = st.text_input("الهاتف", value=user.get("phone",""))
            bio = st.text_area("نبذة", value=user.get("bio",""))
            if st.form_submit_button("💾 حفظ"):
                st.session_state.current_user.update({
                    "name": name, "specialty": specialty, "country": country, "phone": phone, "bio": bio
                })
                st.session_state.users_db[user["email"]].update(st.session_state.current_user)
                st.success("✅ تم الحفظ!")

def page_members():
    st.markdown('<h2>👥 أعضاء <span style="color:#e67e22;">النظام</span></h2>', unsafe_allow_html=True)
    st.write(f"إجمالي الأعضاء: {len(st.session_state.users_db)}")
    for email, u in st.session_state.users_db.items():
        status = "🟢" if u.get("online", True) else "🔴"
        st.markdown(f"""
        <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>{u['name']}</strong> <span style="font-size:0.75rem; color:#94a3b8;">{u.get('specialty','')}</span>
                <div style="font-size:0.7rem; color:#64748b;">{email}</div>
            </div>
            <div>{status}</div>
        </div>
        """, unsafe_allow_html=True)

def page_messages():
    st.markdown('<h2>💬 المراسلات العامة</h2>', unsafe_allow_html=True)
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages[-20:]:
            align = "flex-end" if msg["sender"] == st.session_state.current_user["name"] else "flex-start"
            bg = "var(--primary)" if msg["sender"] == st.session_state.current_user["name"] else "#1e293b"
            color = "#fff" if msg["sender"] == st.session_state.current_user["name"] else "#f8fafc"
            st.markdown(f"""
            <div style="display:flex; justify-content:{align}; margin-bottom:6px;">
                <div style="max-width:75%; padding:10px 14px; border-radius:12px; background:{bg}; color:{color}; border:1px solid #334155;">
                    <div style="font-size:0.7rem; opacity:0.8;">{msg['sender']}</div>
                    <div style="font-size:0.95rem;">{msg['text']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with st.form("msg_form", clear_on_submit=True):
        c1, c2 = st.columns([4,1])
        with c1:
            text = st.text_input("رسالتك...", label_visibility="collapsed")
        with c2:
            submitted = st.form_submit_button("📨 إرسال", use_container_width=True)
        if submitted and text:
            st.session_state.messages.append({
                "sender": st.session_state.current_user["name"],
                "text": text,
                "time": datetime.now().isoformat()
            })
            st.rerun()

def page_private_messages():
    st.markdown('<h2>💌 رسائل <span style="color:#e67e22;">خاصة بين الأطباء</span></h2>', unsafe_allow_html=True)
    recipients = [u["name"] for e,u in st.session_state.users_db.items() if e != st.session_state.current_user["email"]]
    if not recipients:
        st.info("لا يوجد أطباء آخرون.")
        return
    recipient = st.selectbox("اختر الطبيب", recipients)
    st.text_area("اكتب رسالتك...")
    st.button("📨 إرسال", type="primary")

def page_lab_chat():
    st.markdown('<h2>🧪 التواصل <span style="color:#e67e22;">مع المختبر</span></h2>', unsafe_allow_html=True)
    for msg in st.session_state.lab_messages[-10:]:
        st.markdown(f"<div class='card'><strong>{msg['sender']}:</strong> {msg['text']}</div>", unsafe_allow_html=True)
    with st.form("lab_form", clear_on_submit=True):
        txt = st.text_input("رسالتك للمختبر...")
        if st.form_submit_button("إرسال") and txt:
            st.session_state.lab_messages.append({"sender": st.session_state.current_user["name"], "text": txt})
            st.rerun()

def page_file_sharing():
    st.markdown('<h2>📁 مشاركة <span style="color:#e67e22;">الملفات</span></h2>', unsafe_allow_html=True)
    st.caption("الصيغ المدعومة: STL, PLY, OBJ, FBX, GLB, DICOM, PDF, JPG, PNG, CSV, XLSX")
    uploaded = st.file_uploader("اسحب الملفات هنا", accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            st.session_state.files_uploaded.append({"name": f.name, "size": f.size, "type": f.type})
            st.success(f"✅ تم رفع {f.name}")
    if st.session_state.files_uploaded:
        df = pd.DataFrame(st.session_state.files_uploaded)
        st.dataframe(df, use_container_width=True)

def page_screen_share():
    st.markdown('<h2>🖥️ مشاركة <span style="color:#e67e22;">الشاشة</span></h2>', unsafe_allow_html=True)
    st.info("🔹 في بيئة المتصفح، استخدم زر 'بدء المشاركة' أدناه (يتطلب متصفحاً حديثاً).")
    st.markdown("""
    <button style="background:#10b981; color:#fff; border:none; padding:10px 24px; border-radius:60px; cursor:pointer;" onclick="navigator.mediaDevices.getDisplayMedia({video:true}).then(s=>{alert('🖥️ تم بدء المشاركة')}).catch(e=>alert('تم الإلغاء'))">
        ▶️ بدء مشاركة الشاشة
    </button>
    """, unsafe_allow_html=True)

def page_diagnosis():
    st.markdown('<h2>🩺 التشخيص <span style="color:#e67e22;">الذكي</span></h2>', unsafe_allow_html=True)
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد مرضى"]
    st.selectbox("اختر المريض", patients)
    st.text_input("الأخصائي", value=st.session_state.current_user["name"])
    symptoms = st.text_area("الأعراض", placeholder="أدخل الأعراض بالتفصيل...")
    if st.button("🎓 تشخيص AI - Harvard", type="primary"):
        with st.spinner("🧠 جاري التحليل..."):
            import time; time.sleep(2)
        st.success("✅ تم التشخيص!")
        st.markdown("""
        <div class="card" style="border-right:4px solid #e67e22;">
            <h4 style="color:#e67e22;">🔬 التشخيص:</h4>
            <p>ألم في المنطقة مع التهاب لثة خفيف. يُنصح بفحص سريري شامل.</p>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <span class="badge-gold">شدة: متوسطة</span>
                <span class="badge-gold" style="background:rgba(16,185,129,0.12); color:#10b981;">نجاح: 95%</span>
                <span class="badge-gold">Harvard AI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def page_treatment_plan():
    st.markdown('<h2>📋 خطة <span style="color:#e67e22;">العلاج</span></h2>', unsafe_allow_html=True)
    st.text_input("الخطة الرئيسية")
    st.text_input("العلاج البديل")
    if st.button("🧠 توليد الخطة", type="primary"):
        st.balloons()
        st.markdown("""
        <div class="card">
            <h4 style="color:#e67e22;">⭐ التوصية النهائية:</h4>
            <p>يُوصى باعتماد الخطة الرئيسية للحصول على أفضل نتائج.</p>
            <div style="display:flex; gap:12px; flex-wrap:wrap;">
                <span class="badge-gold">نسبة النجاح: 95%</span>
                <span class="badge-gold" style="background:rgba(16,185,129,0.12); color:#10b981;">المدة: 18 شهر</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def page_materials():
    st.markdown('<h2>🧪 المواد <span style="color:#e67e22;">العلاجية</span></h2>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: name = st.text_input("اسم المادة")
    with c2: usage = st.text_input("الاستخدام")
    if st.button("➕ إضافة"):
        if name:
            st.session_state.materials.append({"name": name, "usage": usage})
            st.success("✅ تمت الإضافة")
    if st.session_state.materials:
        st.table(pd.DataFrame(st.session_state.materials))

def page_facial():
    st.markdown('<h2>🧑‍⚕️ تحليل <span style="color:#e67e22;">الوجه (478 علامة)</span></h2>', unsafe_allow_html=True)
    img = st.file_uploader("📸 حمّل صورة الوجه", type=["jpg","png"], key="facial_img")
    if img:
        image = Image.open(img)
        st.image(image, caption="الصورة المحملة", use_container_width=True)
        if st.button("🎨 تحليل الـ 478 نقطة", type="primary"):
            st.success("✅ تم رسم 478 علامة تشريحية!")
            # Simulation overlay
            draw = ImageDraw.Draw(image)
            w, h = image.size
            for i in range(20):
                x, y = np.random.randint(0, w), np.random.randint(0, h)
                draw.ellipse([x-3, y-3, x+3, y+3], fill="#e67e22")
            st.image(image, caption="التحليل التشريحي", use_container_width=True)

def page_cephalometric():
    st.markdown('<h2>🩻 تحليل <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)
    img = st.file_uploader("🩻 حمّل الأشعة", type=["jpg","png","dcm"], key="ceph_img")
    if img and st.button("🔍 تحليل تلقائي"):
        st.info("SNA: 82° | SNB: 80° | ANB: 2° (ضمن الطبيعي)")

def page_smile_design():
    st.markdown('<h2>😁 تصميم <span style="color:#e67e22;">الابتسامة</span></h2>', unsafe_allow_html=True)
    img = st.file_uploader("📸 صورة الابتسامة", type=["jpg","png"], key="smile_img")
    if img:
        st.image(img, use_container_width=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.button("🧊 توليد 3D")
        with c2: st.button("📐 DSD Overlay")
        with c3: st.button("✨ محاكاة AI", type="primary")

def page_aesthetic_design():
    st.markdown('<h2>🎨 التصميم <span style="color:#e67e22;">التجميلي (قبل / بعد)</span></h2>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.file_uploader("📸 قبل", key="before_img")
    with c2: st.file_uploader("📸 بعد", key="after_img")
    st.slider("مستوى المقارنة", 0, 100, 50)

def page_stl_3d():
    st.markdown('<h2>📦 نماذج <span style="color:#e67e22;">3D / Mesh</span></h2>', unsafe_allow_html=True)
    model = st.file_uploader("رفع STL / OBJ / PLY", type=["stl","obj","ply","glb"], key="stl_up")
    if model:
        st.success(f"✅ تم رفع {model.name}")
        # Three.js viewer via HTML component
        html_code = """
        <div style="width:100%; height:400px; background:#0f172a; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#e67e22; font-family:Cairo;">
            <div style="text-align:center;">
                <div style="font-size:3rem;">🧊</div>
                <div>عارض Three.js مدمج</div>
                <div style="font-size:0.8rem; color:#94a3b8;">يتطلب ملف Three.js حقيقي للعرض التفاعلي</div>
            </div>
        </div>
        """
        st.components.v1.html(html_code, height=420)

def page_dsd_studio():
    st.markdown('<h2>🧬 استوديو إعادة بناء الابتسامة الطبيعية <span style="color:#94a3b8; font-size:1rem;">Bio-Mimetic DSD</span></h2>', unsafe_allow_html=True)
    st.selectbox("📋 الملف الطبي للمريض", [p["name"] for p in st.session_state.patients] or ["لا يوجد"])
    st.file_uploader("📸 تحميل الصورة بالاستوديو", type=["jpg","png"], key="dsd_img")
    st.slider("عرض الابتسامة", 0, 100, 80)
    st.slider("الارتفاع العمودي", 0, 100, 50)
    st.slider("تطابق الشفافية", 0, 100, 70)
    if st.button("📊 تحليل الـ 478 معلم", type="primary"):
        st.success("✅ تم الدمج الجمالي!")

def page_aesthetic_treatment():
    st.markdown('<h2>💎 علاج الوجه <span style="color:#e67e22;">التجميلي المتقدم</span></h2>', unsafe_allow_html=True)
    st.text_input("اسم المريض")
    st.selectbox("نوع العلاج", ["تناسق الوجه", "علاج البشرة", "تناسق الأنف", "تناسق الذقن", "تناسق الشفاه"])
    st.text_area("وصف الحالة")
    if st.button("✨ توليد خطة العلاج", type="primary"):
        st.markdown("""
        <div class="card">
            <h4>خطة العلاج المقترحة:</h4>
            <ul>
                <li>حقن فيلر حمض الهيالورونيك للشفاه (1ml)</li>
                <li>بوتوكس لرفع زوايا الفم (20 وحدة)</li>
                <li>متابعة بعد 14 يوماً</li>
            </ul>
            <span class="badge-gold">التكلفة التقديرية: $1,200</span>
        </div>
        """, unsafe_allow_html=True)

def page_global_platform():
    st.markdown('<h2>🌍 المنصة العالمية <span style="color:#e67e22;">Dentofacial HarmonizeAI™</span></h2>', unsafe_allow_html=True)
    steps = st.session_state.pipeline_steps
    cols = st.columns(5)
    for i, (sid, data) in enumerate(steps.items(), 1):
        color = "#10b981" if data["status"]=="done" else "#f59e0b" if data["status"]=="pending" else "#555"
        with cols[i-1]:
            st.markdown(f"""
            <div style="background:#1e293b; border-radius:12px; padding:16px; text-align:center; border-top:4px solid {color};">
                <div style="font-size:0.7rem; background:{color}; color:#fff; padding:2px 10px; border-radius:20px; display:inline-block; margin-bottom:6px;">الخطوة {sid}</div>
                <h5 style="font-size:0.85rem;">{data['name']}</h5>
                <div style="font-size:0.65rem; color:#94a3b8;">{data['progress']}%</div>
            </div>
            """, unsafe_allow_html=True)
    st.progress(st.session_state.pipeline_progress / 100)
    st.caption(f"📊 التقدم الكلي: {st.session_state.pipeline_progress}%")

def page_pipeline():
    st.markdown('<h2>🔄 خط الإنتاج <span style="color:#e67e22;">المدمج</span></h2>', unsafe_allow_html=True)
    st.selectbox("اختر مريضاً", [p["name"] for p in st.session_state.patients] or ["لا يوجد"])
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = st.session_state.pipeline_progress,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "نسبة الإنجاز"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#e67e22"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

def page_materials_guide():
    st.markdown('<h2>🦷 دليل المواد الطبية التجميلية <span style="color:#94a3b8; font-size:1rem;">مع المراجع العلمية</span></h2>', unsafe_allow_html=True)
    data = [
        ["Lithium Disilicate (E.max)", "قشور وتركيبات", "تحضير مجهري، Mock-up", "STL من Exocad", "PubMed"],
        ["Hyaluronic Acid Filler", "فيلر الأنسجة الرخوة", "حقن تحت المخاطية", "Blender OBJ", "NCBI"],
        ["Botulinum Toxin (Botox)", "تعديل الابتسامة اللثوية", "حقن في Levator Labii", "AI Studios", "PubMed"],
        ["Zirconia Monolithic", "جسور وتأهيل كامل", "تحضير هيكلي", "Exocad", "ScienceDirect"],
    ]
    df = pd.DataFrame(data, columns=["المادة", "التصنيف", "بروتوكول الاستخدام", "الربط الرقمي", "المراجع"])
    st.dataframe(df, use_container_width=True)

def page_api_hub():
    st.markdown('<h2>🔌 مركز تواصل الأنظمة <span style="color:#94a3b8; font-size:1rem;">(Global API Hub)</span></h2>', unsafe_allow_html=True)
    systems = [
        ("Exocad", "STL", "🟢", "تصدير"),
        ("Meshy AI", "3D Face", "🟢", "فتح"),
        ("Blender", "Cycles", "🟡", "فتح"),
        ("AI Studios", "Motion", "🟢", "فتح"),
    ]
    for name, fmt, status, action in systems:
        c1, c2, c3 = st.columns([2,1,1])
        with c1: st.markdown(f"**{name}** <span style='color:#94a3b8; font-size:0.8rem;'>{fmt}</span>", unsafe_allow_html=True)
        with c2: st.markdown(f"<span style='color:#10b981;'>{status}</span>", unsafe_allow_html=True)
        with c3: st.button(action, key=f"api_{name}")

def page_mock_db():
    st.markdown('<h2>🗄️ محاكي مستودع <span style="color:#e67e22;">المريض</span></h2>', unsafe_allow_html=True)
    st.json({
        "patients_count": len(st.session_state.patients),
        "last_backup": datetime.now().isoformat(),
        "storage_used": "1.2 GB",
        "sync_status": "مُزامن"
    })

def page_notifications():
    st.markdown('<h2>🔔 الإشعارات <span style="color:#e67e22;">الواردة</span></h2>', unsafe_allow_html=True)
    notifs = [
        "📢 تم تحديث خط سير المريض (الخطوة 3)",
        "💬 رسالة جديدة من المختبر",
        "📅 موعد غداً الساعة 10:00 ص",
    ]
    for n in notifs:
        st.markdown(f'<div class="card" style="padding:10px; margin-bottom:6px;">{n}</div>', unsafe_allow_html=True)

def page_systems():
    st.markdown('<h2>🖥️ الأنظمة <span style="color:#e67e22;">المستخدمة</span></h2>', unsafe_allow_html=True)
    sys_list = ["Smile Generator", "Exocad Analysis", "Exocad 3D", "Meshy AI", "Blender Cycles", "AI Studios"]
    cols = st.columns(3)
    for i, s in enumerate(sys_list):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:2rem; color:#e67e22;">⚙️</div>
                <h5>{s}</h5>
                <span class="badge-gold" style="background:#10b981; color:#fff;">نشط</span>
            </div>
            """, unsafe_allow_html=True)

def page_scientific_scan():
    st.markdown('<h2>🔬 المسح العلمي <span style="color:#e67e22;">الشامل</span></h2>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.button("👤 مسح الوجه")
    with c2: st.button("🦷 مسح الأسنان")
    with c3: st.button("⚖️ تحليل التناغم", type="primary")
    with c4: st.button("📋 تقرير علمي")

def page_naqai():
    st.markdown('<h2>🤖 NaqAI <span style="color:#e67e22;">المساعد الذكي</span></h2>', unsafe_allow_html=True)
    if "naqai_chat" not in st.session_state:
        st.session_state.naqai_chat = [{"role": "ai", "text": "👋 مرحباً! أنا NaqAI، مساعدك الذكي. اسألني عن أي شيء متعلق بطب الأسنان التجميلي والوجه."}]

    for msg in st.session_state.naqai_chat:
        if msg["role"] == "ai":
            st.markdown(f'<div style="background:#0a8491; color:#fff; padding:10px 14px; border-radius:12px; margin-bottom:6px; align-self:flex-start; max-width:85%;">{msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#1e293b; color:#f8fafc; padding:10px 14px; border-radius:12px; margin-bottom:6px; border:1px solid #334155; text-align:left;">{msg["text"]}</div>', unsafe_allow_html=True)

    with st.form("naqai_form", clear_on_submit=True):
        q = st.text_input("اسأل NaqAI...")
        if st.form_submit_button("📨 إرسال") and q:
            st.session_state.naqai_chat.append({"role": "user", "text": q})
            # Simulate AI response
            responses = {
                "ابتسامة": "😁 تصميم الابتسامة يشمل تحليل النسب الذهبية واستخدام Exocad...",
                "فيلر": "💉 فيلر حمض الهيالورونيك يستخدم لملء التجاعيد ويدوم 6-18 شهراً...",
                "بوتوكس": "🧪 البوتوكس يستخدم لتقليل التجاعيد وعلاج الابتسامة اللثوية...",
            }
            ans = "🧠 شكراً لسؤالك! يمكنني مساعدتك في تصميم الابتسامة، العلاج التجميلي، تحليل الوجه، والمزيد."
            for k,v in responses.items():
                if k in q: ans = v; break
            st.session_state.naqai_chat.append({"role": "ai", "text": ans})
            st.rerun()

def page_interdisciplinary():
    st.markdown('<h2>👥 فرق <span style="color:#e67e22;">متعددة التخصصات</span></h2>', unsafe_allow_html=True)
    with st.form("add_spec"):
        n = st.text_input("اسم الأخصائي")
        s = st.text_input("التخصص")
        if st.form_submit_button("➕ إضافة"):
            st.session_state.specialists.append({"name": n, "specialty": s, "online": True})
            st.success("✅ تمت الإضافة")
    for sp in st.session_state.specialists:
        st.markdown(f'<div class="card"><strong>{sp["name"]}</strong> - {sp["specialty"]}</div>', unsafe_allow_html=True)

def page_ads():
    st.markdown('<h2>📢 الإعلانات</h2>', unsafe_allow_html=True)
    with st.form("ad_form"):
        t = st.text_input("عنوان الإعلان")
        c = st.text_area("المحتوى")
        if st.form_submit_button("📨 نشر"):
            st.session_state.ads.append({"title": t, "content": c})
            st.success("✅ تم النشر")
    for a in st.session_state.ads:
        st.markdown(f'<div class="card"><h5 style="color:#e67e22;">{a["title"]}</h5><p>{a["content"]}</p></div>', unsafe_allow_html=True)

def page_lab():
    st.markdown('<h2>🔬 حساب <span style="color:#e67e22;">المعمل</span></h2>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.text_input("اسم الفني", key="lab_tech")
    with c2: st.text_input("نوع العمل", key="lab_work")
    with c3: st.text_input("اسم المريض", key="lab_patient")
    with c4: st.number_input("المبلغ ($)", key="lab_amount")
    if st.button("💾 حفظ"):
        st.success("✅ تم حفظ طلب المعمل")

def page_appointments():
    st.markdown('<h2>📅 المواعيد</h2>', unsafe_allow_html=True)
    st.selectbox("المريض", [p["name"] for p in st.session_state.patients] or ["لا يوجد"])
    st.datetime_input("التاريخ والوقت", datetime.now())
    if st.button("📅 جدولة"):
        st.success("✅ تم جدولة الموعد")

def page_accounting():
    st.markdown('<h2>💰 حساب <span style="color:#e67e22;">المريض</span></h2>', unsafe_allow_html=True)
    total = st.number_input("المبلغ الكلي", value=1000)
    paid = st.number_input("المدفوع", value=0)
    st.markdown(f"""
    <div class="card">
        <div style="display:flex; justify-content:space-around; text-align:center;">
            <div><h4>الكلي</h4><div class="metric-value">{total}</div></div>
            <div><h4>المدفوع</h4><div class="metric-value" style="color:#10b981;">{paid}</div></div>
            <div><h4>المتبقي</h4><div class="metric-value" style="color:#ef4444;">{total-paid}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def page_payments():
    st.markdown('<h2>💳 الدفع <span style="color:#e67e22;">والمحفظة</span></h2>', unsafe_allow_html=True)
    methods = ["💳 Visa / Mastercard", "📱 محفظتي", "💵 أم فلوس", "💰 شامل موني", "📲 إم باي", "🏦 التحويل البنكي"]
    selected = st.selectbox("وسيلة الدفع", methods)
    if st.button("✅ تنفيذ الدفع", type="primary"):
        st.success(f"✅ تم الدفع بنجاح عبر {selected}")

def page_subscriptions():
    st.markdown('<h2>👑 خطط <span style="color:#e67e22;">الاشتراك</span></h2>', unsafe_allow_html=True)
    cols = st.columns(3)
    plans = [
        ("🆓 تجريبي", "$0", ["3 مرضى"]),
        ("⭐ شهري", "$99", ["غير محدود", "تحليل AI"]),
        ("🌟 سنوي", "$999", ["جميع الميزات", "دعم أولوي"]),
    ]
    for i, (name, price, feats) in enumerate(plans):
        with cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center; {'border:2px solid #e67e22;' if i==1 else ''}">
                <h4>{name}</h4>
                <div style="font-size:2rem; font-weight:800; color:#e67e22;">{price}</div>
                <ul style="text-align:right; list-style:none; padding:0;">
                    {"".join([f"<li style='padding:4px 0; border-bottom:1px solid #334155;'>✅ {f}</li>" for f in feats])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button("اشترك", key=f"sub_{i}", use_container_width=True):
                st.success(f"🎉 تم تفعيل الاشتراك {name}!")

def page_invite():
    st.markdown('<h2>📨 دعوة <span style="color:#e67e22;">الأطباء</span></h2>', unsafe_allow_html=True)
    link = f"https://harmonizeai.streamlit.app/?ref={np.random.randint(1000,9999)}"
    st.text_input("رابط الدعوة", value=link)
    if st.button("📋 نسخ الرابط"):
        st.success("✅ تم النسخ!")
    st.markdown(f'<a href="https://api.whatsapp.com/send?text=انضم لمنصة HarmonizeAI: {link}" target="_blank"><button style="background:#25D366; color:#fff; border:none; padding:8px 20px; border-radius:30px; cursor:pointer;">📱 مشاركة واتساب</button></a>', unsafe_allow_html=True)

def page_settings():
    st.markdown('<h2>⚙️ الإعدادات <span style="color:#e67e22;">والخصوصية</span></h2>', unsafe_allow_html=True)
    with st.form("settings"):
        st.text_input("الاسم الظاهر", value=st.session_state.current_user["name"])
        st.text_input("التخصص", value=st.session_state.current_user.get("specialty",""))
        st.text_input("مفتاح API (OpenAI)", type="password")
        st.selectbox("النموذج", ["OpenAI GPT-4", "Google Gemini"])
        if st.form_submit_button("💾 حفظ"):
            st.success("✅ تم الحفظ")
    if st.button("🗑️ حذف الحساب", type="primary"):
        st.error("⚠️ هذا الإجراء لا يمكن التراجع عنه!")

def page_reports():
    st.markdown('<h2>📄 التقارير</h2>', unsafe_allow_html=True)
    if st.button("📄 توليد تقرير PDF", type="primary"):
        st.success("✅ تم توليد التقرير!")
        st.download_button("⬇️ تحميل PDF", data=b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 2\n0000000000 65535 f \n0000000009 00000 n \ntrailer\n<<\n/Size 2\n/Root 1 0 R\n>>\nstartxref\n45\n%%EOF", file_name="report.pdf", mime="application/pdf")

def page_priv

def page_privacy():
    st.markdown('<h2>🔒 الخصوصية <span style="color:#e67e22;">والأمان</span></h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#94a3b8; line-height:1.8;">
        <strong>سياسة الخصوصية:</strong> نحن نلتزم بحماية بياناتك الشخصية. جميع المعلومات التي تقدمها تخزن بشكل آمن ولا يتم مشاركتها مع أطراف ثالثة دون موافقتك الصريحة.<br><br>
        <strong>جمع البيانات:</strong> يتم جمع البيانات الضرورية فقط لتشغيل الخدمات المقدمة، مثل أسماء المرضى، الصور، والتقارير الطبية، وذلك للأغراض العلاجية والتشخيصية.<br><br>
        <strong>حماية البيانات:</strong> نستخدم تقنيات تشفير متقدمة لحماية بياناتك أثناء النقل والتخزين، ونطبق إجراءات أمنية صارمة لمنع الوصول غير المصرح به.<br><br>
        <strong>حقوق المستخدم:</strong> يحق لك طلب نسخة من بياناتك، تعديلها، أو حذفها نهائياً، ولديك الحق في إلغاء الموافقة على معالجة بياناتك في أي وقت.
        </p>
    </div>
    """, unsafe_allow_html=True)

def page_ip():
    st.markdown('<h2>©️ حقوق <span style="color:#e67e22;">الملكية الفكرية</span></h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#94a3b8; line-height:1.8;">
        <strong>حقوق الملكية الفكرية:</strong> جميع المحتويات المنشورة على هذه المنصة، بما في ذلك النصوص، الصور، التصميمات، البرمجيات، والعلامات التجارية، هي ملكية خاصة لـ Dentofacial HarmonizeAI™ وجميع الحقوق محفوظة.<br><br>
        <strong>العلامات التجارية:</strong> اسم "Dentofacial HarmonizeAI™" وشعار المنصة هما علامتان تجاريتان مسجلتان، ولا يجوز استخدامهما دون إذن كتابي مسبق.<br><br>
        <strong>المحتوى:</strong> يُسمح باستخدام المحتوى للأغراض الشخصية والتعليمية غير التجارية، مع الإشارة إلى المصدر. يُمنع نسخ أو توزيع أو تعديل أي محتوى لأغراض تجارية دون موافقة خطية.<br><br>
        <strong>البرمجيات:</strong> جميع البرمجيات والمكتبات المستخدمة في المنصة محمية بتراخيصها الخاصة، ويتم استخدامها وفقاً لشروط كل ترخيص.
        </p>
    </div>
    """, unsafe_allow_html=True)

def page_forum():
    st.markdown('<h2>🗣️ منتدى النقاشات <span style="color:#e67e22;">مع الأخصائيين</span></h2>', unsafe_allow_html=True)
    st.caption("اطرح سؤالك، واحصل على إجابة من نخبة من الأخصائيين في مختلف التخصصات.")

    # عرض الأخصائيين
    st.markdown("### 👨‍⚕️ الأخصائيون المتاحون")
    cols = st.columns(len(st.session_state.specialists))
    for i, sp in enumerate(st.session_state.specialists):
        with cols[i]:
            status_color = "#10b981" if sp["online"] else "#555"
            st.markdown(f"""
            <div style="background:#1e293b; padding:10px; border-radius:12px; text-align:center; border:1px solid #334155;">
                <div style="width:12px; height:12px; background:{status_color}; border-radius:50%; margin:0 auto 6px;"></div>
                <strong style="font-size:0.85rem;">{sp['name']}</strong>
                <div style="font-size:0.7rem; color:#94a3b8;">{sp['specialty']}</div>
            </div>
            """, unsafe_allow_html=True)

    # إضافة أخصائي جديد
    if st.session_state.current_user.get("role") in ["owner", "admin"]:
        with st.expander("➕ استضافة أخصائي جديد"):
            c1, c2, c3 = st.columns([2,2,1])
            with c1: new_name = st.text_input("الاسم", key="new_spec_name")
            with c2: new_spec = st.text_input("التخصص", key="new_spec_spec")
            with c3:
                st.write("")
                st.write("")
                if st.button("➕ إضافة", key="add_spec_btn"):
                    if new_name and new_spec:
                        st.session_state.specialists.append({"name": new_name, "specialty": new_spec, "online": True})
                        st.success("✅ تمت الإضافة")
                        st.rerun()

    # طرح سؤال
    st.markdown("---")
    st.markdown("### ✏️ اطرح سؤالاً جديداً")
    with st.form("forum_question"):
        q_title = st.text_input("عنوان السؤال")
        q_body = st.text_area("تفاصيل السؤال")
        target = st.selectbox("موجه إلى", ["جميع الأخصائيين"] + [s["name"] for s in st.session_state.specialists])
        if st.form_submit_button("🚀 نشر السؤال"):
            if q_title and q_body:
                st.session_state.forum_questions.insert(0, {
                    "id": len(st.session_state.forum_questions) + 1,
                    "title": q_title,
                    "body": q_body,
                    "asked_by": st.session_state.current_user["name"],
                    "target": target,
                    "status": "open",
                    "answers": [],
                    "created_at": datetime.now().isoformat()
                })
                st.success("✅ تم نشر السؤال!")
                st.rerun()

    # عرض الأسئلة
    st.markdown("---")
    st.markdown("### 📋 الأسئلة المنشورة")
    if not st.session_state.forum_questions:
        st.info("📭 لا توجد أسئلة بعد. كن أول من يسأل!")
    for q in st.session_state.forum_questions:
        status_colors = {"open": "#f59e0b", "answered": "#10b981", "closed": "#ef4444"}
        status_labels = {"open": "🟡 مفتوح", "answered": "✅ تم الرد", "closed": "🔒 مغلق"}
        sc = status_colors.get(q["status"], "#f59e0b")
        sl = status_labels.get(q["status"], q["status"])
        with st.container():
            st.markdown(f"""
            <div style="background:#1e293b; border-radius:16px; padding:16px; border:1px solid #334155; margin-bottom:12px; border-right:4px solid {sc};">
                <div style="display:flex; justify-content:space-between; flex-wrap:wrap;">
                    <h4 style="margin:0; color:#f8fafc;">{q['title']}</h4>
                    <span style="background:{sc}; color:#fff; padding:2px 12px; border-radius:20px; font-size:0.7rem; font-weight:700;">{sl}</span>
                </div>
                <p style="color:#94a3b8; margin:8px 0;">{q['body']}</p>
                <div style="font-size:0.75rem; color:#64748b; margin-bottom:8px;">
                    👤 {q['asked_by']} | 🎯 {q['target']} | 💬 {len(q['answers'])} ردود
                </div>
            </div>
            """, unsafe_allow_html=True)

            # الردود
            if q["answers"]:
                for ans in q["answers"]:
                    st.markdown(f"""
                    <div style="background:#0f172a; padding:10px 14px; border-radius:10px; margin:6px 40px 6px 0; border:1px solid #334155; border-right:3px solid #e67e22;">
                        <strong style="color:#e67e22; font-size:0.8rem;">⭐ {ans['author']} (أخصائي)</strong>
                        <p style="margin:4px 0; font-size:0.9rem;">{ans['text']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            # إضافة رد
            with st.form(f"reply_{q['id']}", clear_on_submit=True):
                c1, c2 = st.columns([4,1])
                with c1: reply_text = st.text_input("أضف رداً...", key=f"reply_text_{q['id']}", label_visibility="collapsed")
                with c2: submitted = st.form_submit_button("📨 رد")
                if submitted and reply_text:
                    q["answers"].append({
                        "author": st.session_state.current_user["name"],
                        "text": reply_text,
                        "is_specialist": st.session_state.current_user.get("role") in ["owner","specialist"]
                    })
                    q["status"] = "answered"
                    st.success("✅ تم إضافة الرد!")
                    st.rerun()

def page_cadcam():
    st.markdown('<h2>⚙️ CAD/CAM & 3D <span style="color:#e67e22;">(نموذج افتراضي جاهز)</span></h2>', unsafe_allow_html=True)
    st.caption("تحميل، معاينة، تحليل، وتصدير النماذج ثلاثية الأبعاد للأسنان والوجه")

    c1, c2 = st.columns([3,1])
    with c1:
        # محاكاة عارض Three.js
        st.markdown("""
        <div style="width:100%; height:400px; background:#0f172a; border-radius:16px; border:1px solid #334155; display:flex; align-items:center; justify-content:center; position:relative; overflow:hidden;">
            <div style="text-align:center; color:#e67e22;">
                <div style="font-size:4rem; animation:spin 4s linear infinite;">🦷</div>
                <div style="font-size:1rem; margin-top:10px;">عارض 3D تفاعلي</div>
                <div style="font-size:0.8rem; color:#94a3b8;">Three.js WebGL Renderer</div>
            </div>
            <style>@keyframes spin { 100% { transform: rotateY(360deg); } }</style>
        </div>
        """, unsafe_allow_html=True)

        # أدوات التحكم
        cc1, cc2, cc3, cc4 = st.columns(4)
        with cc1: st.slider("تكبير", 0.5, 2.0, 1.0, key="cad_zoom")
        with cc2: st.slider("دوران X", -180, 180, 0, key="cad_rotx")
        with cc3: st.slider("دوران Y", -180, 180, 0, key="cad_roty")
        with cc4: st.slider("إضاءة", 0.2, 2.0, 1.0, key="cad_light")

    with c2:
        st.markdown("#### 📄 نموذج افتراضي")
        st.markdown("<div style='color:#94a3b8;'>Polygon: <strong style='color:#e67e22;'>32 سن</strong></div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#94a3b8;'>✅ <strong style='color:#10b981;'>جاهز</strong></div>", unsafe_allow_html=True)
        st.divider()
        st.button("👑 إضافة تاج", use_container_width=True)
        st.button("✏️ رسم التحليل", use_container_width=True)
        st.button("🧹 مسح الرسم", use_container_width=True)
        st.divider()
        st.button("🔷 Polygon", use_container_width=True)
        st.button("🧊 طبعة جبسية", use_container_width=True)
        st.button("✂️ قطع داخل الصورة", use_container_width=True)
        st.divider()
        st.button("🦴 عظام الفك", use_container_width=True)
        st.button("🦷 تحليل الأسنان", use_container_width=True)
        st.button("👤 تناغم الوجه", use_container_width=True)
        st.divider()
        st.button("📋 تشخيص إطباقي", use_container_width=True)
        st.button("⚙️ إطباق وظيفي", use_container_width=True)
        st.button("✨ إطباق جمالي", use_container_width=True)
        st.divider()
        st.button("📊 مقارنة مع الطبيعي", use_container_width=True, type="primary")

    # أزرار علوية
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1: st.button("📤 تحميل افتراضي", use_container_width=True, type="primary")
    with b2: st.file_uploader("STL", type=["stl","obj","ply"], label_visibility="collapsed", key="cad_stl")
    with b3: st.button("🔄 كاميرا", use_container_width=True)
    with b4: st.button("📐 شبكة", use_container_width=True)
    with b5: st.button("📷 حفظ", use_container_width=True)

    c1, c2 = st.columns(2)
    with c1: st.button("📤 تصدير STL", use_container_width=True, type="primary")
    with c2: st.button("📊 تحليل شامل", use_container_width=True, type="primary")

# =============================================================
# MAIN ROUTER
# =============================================================
PAGES = {
    "home": page_home,
    "dashboard": page_dashboard,
    "patients": page_patients,
    "new_patient": page_new_patient,
    "photography": page_photography,
    "dentbook": page_dentbook,
    "profile": page_profile,
    "members": page_members,
    "messages": page_messages,
    "private_messages": page_private_messages,
    "lab_chat": page_lab_chat,
    "file_sharing": page_file_sharing,
    "screen_share": page_screen_share,
    "diagnosis": page_diagnosis,
    "treatment_plan": page_treatment_plan,
    "materials": page_materials,
    "facial": page_facial,
    "cephalometric": page_cephalometric,
    "smile_design": page_smile_design,
    "aesthetic_design": page_aesthetic_design,
    "stl_3d": page_stl_3d,
    "dsd_studio": page_dsd_studio,
    "aesthetic_treatment": page_aesthetic_treatment,
    "global_platform": page_global_platform,
    "pipeline": page_pipeline,
    "materials_guide": page_materials_guide,
    "api_hub": page_api_hub,
    "mock_db": page_mock_db,
    "notifications": page_notifications,
    "systems": page_systems,
    "scientific_scan": page_scientific_scan,
    "naqai": page_naqai,
    "interdisciplinary": page_interdisciplinary,
    "ads": page_ads,
    "lab": page_lab,
    "appointments": page_appointments,
    "accounting": page_accounting,
    "payments": page_payments,
    "subscriptions": page_subscriptions,
    "invite": page_invite,
    "settings": page_settings,
    "reports": page_reports,
    "privacy": page_privacy,
    "ip": page_ip,
    "forum": page_forum,
    "cadcam": page_cadcam,
}

def main():
    if not st.session_state.authenticated:
        auth_page()
    else:
        sidebar_nav()
        page_func = PAGES.get(st.session_state.current_page, page_home)
        page_func()

        # Footer
        st.markdown("""
        <hr style="margin-top:40px; border-color:#334155;">
        <div style="text-align:center; color:#64748b; font-size:0.8rem; padding:20px;">
            <strong>Dentofacial <span style="color:#e67e22;">HarmonizeAI</span>™</strong><br>
            Naqeeb412 · Synergy<br>
            🇾🇪 الجمهورية اليمنية - أب - ميتم<br>
            © 2026 جميع الحقوق محفوظة.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
            label="📊 تصدير قاعدة بيانات المرضى بالكامل (CSV)",
            data=csv_export,
            file_name="all_patients_database.csv",
            mime="text/csv"
        )
    else:
        st.info("قم بإضافة مرضى أولاً لاستعراض التقرير الإحصائي.")
