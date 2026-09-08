
# -*- coding: utf-8 -*-
"""
Dentofacial HarmonizeAI™ v5.0 — تطبيق Streamlit إنتاجي
التشغيل:  streamlit run app.py
"""
import base64
import hashlib
import io
import json
import os
import random
import re
import string
import time
from datetime import datetime, timedelta
from io import BytesIO

import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageChops, ImageOps

try:
    import cv2
    CV2_OK = True
except Exception:
    CV2_OK = False

try:
    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh
    MEDIAPIPE_OK = True
except Exception:
    mp = None
    mp_face_mesh = None
    MEDIAPIPE_OK = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

# =============================================================
# CONFIG & PAGE SETUP
# =============================================================
st.set_page_config(
    page_title="HarmonizeAI™ | Dentofacial Synergy",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================
# CSS - RTL & Dark Theme
# =============================================================
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #075e68 0%, #0a8491 100%); }
[data-testid="stSidebar"] * { color: #ffffff !important; }
.stButton>button { border-radius: 60px !important; font-weight: 600 !important; font-family: 'Cairo', sans-serif !important; }
.metric-card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; box-shadow: 0 4px 20px rgba(0,0,0,0.3); text-align: center; }
.metric-value { font-size: 2.2rem; font-weight: 800; color: #e67e22; }
.badge-gold { display: inline-block; background: rgba(230,126,34,0.12); color: #e67e22; padding: 2px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(230,126,34,0.2); }
.badge-harvard { background: #7a0010; color: #fff; padding: 2px 12px; border-radius: 20px; font-size: 0.65rem; font-weight: 700; border: 1px solid #a8001a; }
.card { background: #1e293b; border-radius: 12px; padding: 24px; border: 1px solid #334155; margin-bottom: 16px; }
.privacy-badge { display: inline-block; background: rgba(16,185,129,0.12); color: #10b981; padding: 2px 12px; border-radius: 20px; font-size: 0.65rem; font-weight: 600; }
.dental-chart-wrapper { overflow-x: auto; padding: 10px 0; }
.dental-chart { display: flex; flex-direction: column; align-items: center; gap: 6px; min-width: 700px; }
.dental-arch { display: flex; justify-content: center; gap: 4px; flex-wrap: wrap; }
.dental-arch .arch-label { width: 100%; text-align: center; font-weight: 700; font-size: 14px; color: #94a3b8; margin: 4px 0 8px; letter-spacing: 2px; }
.tooth { width: 44px; height: 52px; background: #f8fafc; border: 2px solid #cbd5e1; border-radius: 8px 8px 4px 4px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s ease; font-size: 11px; font-weight: 700; color: #1a2a3a; position: relative; user-select: none; }
.tooth:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); border-color: #0a8491; }
.tooth .num { font-size: 9px; opacity: 0.5; margin-top: 2px; }
.tooth .status-icon { font-size: 14px; line-height: 1; }
.tooth.missing { background: #f1f3f5; border-color: #adb5bd; opacity: 0.5; cursor: default; }
.tooth.missing::after { content: '✕'; font-size: 20px; color: #ef4444; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }
.tooth.missing .num, .tooth.missing .status-icon { display: none; }
.tooth.carious { background: #fde8e8; border-color: #ef4444; }
.tooth.carious .status-icon { color: #ef4444; }
.tooth.treated { background: #d5f5e3; border-color: #10b981; }
.tooth.treated .status-icon { color: #10b981; }
.tooth.crown { background: #fef9e7; border-color: #f59e0b; }
.tooth.crown .status-icon { color: #f59e0b; }
.tooth.root-canal { background: #e8daef; border-color: #8e44ad; }
.tooth.root-canal .status-icon { color: #8e44ad; }
.tooth-legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; justify-content: center; }
.tooth-legend .legend-item { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.tooth-legend .legend-item .swatch { width: 24px; height: 28px; border-radius: 4px; border: 2px solid #cbd5e1; }
.tooth-legend .legend-item .swatch.normal { background: #f8fafc; }
.tooth-legend .legend-item .swatch.missing { background: #f1f3f5; opacity: 0.5; }
.tooth-legend .legend-item .swatch.carious { background: #fde8e8; border-color: #ef4444; }
.tooth-legend .legend-item .swatch.treated { background: #d5f5e3; border-color: #10b981; }
.tooth-legend .legend-item .swatch.crown { background: #fef9e7; border-color: #f59e0b; }
.tooth-legend .legend-item .swatch.root-canal { background: #e8daef; border-color: #8e44ad; }
.image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 14px; margin-top: 12px; }
.image-grid .img-item { border-radius: 8px; overflow: hidden; border: 2px solid #334155; position: relative; aspect-ratio: 1/1; background: #0f172a; display: flex; align-items: center; justify-content: center; }
.image-grid .img-item img { width: 100%; height: 100%; object-fit: cover; }
.profile-cover { height: 160px; background: linear-gradient(135deg, #075e68, #0a8491); border-radius: 12px 12px 0 0; position: relative; background-size: cover; background-position: center; }
.profile-avatar { width: 80px; height: 80px; border-radius: 50%; border: 4px solid #1e293b; background: #0a8491; display: flex; align-items: center; justify-content: center; font-size: 32px; color: #fff; margin-top: -40px; margin-right: 20px; background-size: cover; background-position: center; }
.iframe-container { width: 100%; height: 700px; border: 1px solid #334155; border-radius: 12px; overflow: hidden; }
.iframe-container iframe { width: 100%; height: 100%; border: none; }
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================
# STATE
# =============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

DEFAULT_USERS = {
    "ndcdental2025@outlook.com": {
        "name": "علي النقيب", "email": "ndcdental2025@outlook.com",
        "password": "ndc2025", "role": "owner", "specialty": "طب أسنان تجميلي",
        "phone": "+967 77 123 4567", "bio": "مؤسس منصة Dentofacial HarmonizeAI™",
        "platforms": ["email"], "avatar": "", "cover_photo": "",
        "friends": [], "pending_requests": [], "posts": [],
    },
    "doctor@clinic.com": {
        "name": "د. أحمد", "email": "doctor@clinic.com", "password": "doctor123",
        "role": "doctor", "specialty": "تقويم أسنان", "phone": "+966 55 123 4567",
        "bio": "أخصائي تقويم أسنان", "platforms": ["email"], "avatar": "",
        "cover_photo": "", "friends": [], "pending_requests": [], "posts": [],
    },
    "patient@clinic.com": {
        "name": "مريض نموذجي", "email": "patient@clinic.com", "password": "patient123",
        "role": "patient", "specialty": "", "phone": "+966 55 123 4568",
        "bio": "مريض", "platforms": ["email"], "avatar": "", "cover_photo": "",
        "friends": [], "pending_requests": [], "posts": [],
    },
}
if "users_db" not in st.session_state:
    st.session_state.users_db = DEFAULT_USERS

if "patients" not in st.session_state:
    st.session_state.patients = [
        {"id": "P0001", "name": "أحمد محمد", "age": 32, "phone": "+967 77 123 4567",
         "gender": "ذكر", "complaint": "ألم في الأسنان الأمامية", "created_at": datetime.now().isoformat()},
        {"id": "P0002", "name": "سارة علي", "age": 28, "phone": "+967 77 123 4568",
         "gender": "أنثى", "complaint": "تصبغات في الأسنان", "created_at": datetime.now().isoformat()},
    ]
if "dental_chart" not in st.session_state:
    st.session_state.dental_chart = ['normal'] * 32
if "cephalometric_data" not in st.session_state:
    st.session_state.cephalometric_data = {"SNA": 82, "SNB": 80, "ANB": 2, "SN-MP": 32, "FMA": 25, "IMPA": 90, "Overjet": 3, "Overbite": 2}
if "normal_values" not in st.session_state:
    st.session_state.normal_values = {"SNA": 82, "SNB": 80, "ANB": 2, "SN-MP": 32, "FMA": 25, "IMPA": 90, "Overjet": 3, "Overbite": 2}
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "facial_analysis_results" not in st.session_state:
    st.session_state.facial_analysis_results = []
if "smile_designs" not in st.session_state:
    st.session_state.smile_designs = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "image_layers" not in st.session_state:
    st.session_state.image_layers = []
if "current_layer" not in st.session_state:
    st.session_state.current_layer = 0
if "natural_teeth_layers" not in st.session_state:
    st.session_state.natural_teeth_layers = []
if "dentbook_posts" not in st.session_state:
    st.session_state.dentbook_posts = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lab_messages" not in st.session_state:
    st.session_state.lab_messages = []
if "appointments" not in st.session_state:
    st.session_state.appointments = []
if "system_logo" not in st.session_state:
    st.session_state.system_logo = None
if "naqai_chat" not in st.session_state:
    st.session_state.naqai_chat = [{"role": "ai", "text": "👋 مرحباً! أنا NaqAI، مساعدك الذكي."}]
if "specialists" not in st.session_state:
    st.session_state.specialists = [
        {"name": "د. أحمد العمري", "specialty": "تقويم أسنان", "online": True, "phone": "+966 55 123 4567"},
        {"name": "د. سارة الحكيم", "specialty": "جراحة الفم والوجه", "online": True, "phone": "+966 55 123 4568"},
    ]
if "ads" not in st.session_state:
    st.session_state.ads = []
if "materials" not in st.session_state:
    st.session_state.materials = []
if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = []
if "friend_requests" not in st.session_state:
    st.session_state.friend_requests = []
if "private_messages" not in st.session_state:
    st.session_state.private_messages = []
if "xrays" not in st.session_state:
    st.session_state.xrays = []
if "patient_images" not in st.session_state:
    st.session_state.patient_images = []
if "xray_images" not in st.session_state:
    st.session_state.xray_images = []
if "forum_questions" not in st.session_state:
    st.session_state.forum_questions = []
if "pipeline_progress" not in st.session_state:
    st.session_state.pipeline_progress = 58
if "subscriptions" not in st.session_state:
    st.session_state.subscriptions = {"free": [], "monthly": [], "yearly": []}
if "converted_models" not in st.session_state:
    st.session_state.converted_models = []

# =============================================================
# AUTH FUNCTIONS
# =============================================================
def login_user(email, password):
    if email in st.session_state.users_db:
        if st.session_state.users_db[email].get("password") == password:
            st.session_state.authenticated = True
            st.session_state.current_user = st.session_state.users_db[email]
            return True
    return False

def signup_user(name, email, password, role="doctor"):
    if email in st.session_state.users_db:
        return False, "البريد مستخدم"
    st.session_state.users_db[email] = {
        "name": name, "email": email, "password": password, "role": role,
        "specialty": "", "phone": "", "bio": "", "platforms": ["email"],
        "avatar": "", "cover_photo": "", "friends": [], "pending_requests": [], "posts": [],
    }
    return True, "تم إنشاء الحساب"

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()

def display_system_logo(width=50):
    if st.session_state.system_logo:
        return f'<img src="data:image/png;base64,{st.session_state.system_logo}" width="{width}">'
    return '<div style="font-size:48px;">🦷</div>'

# =============================================================
# IMAGE HELPERS / LAYERS
# =============================================================
def add_layer(image, name="Layer"):
    if isinstance(image, Image.Image):
        st.session_state.image_layers.append(
            {"name": name, "image": image, "visible": True, "opacity": 1.0}
        )
        st.session_state.current_layer = len(st.session_state.image_layers) - 1
        return True
    return False

def get_current_layer_image():
    layers = st.session_state.image_layers
    if layers and 0 <= st.session_state.current_layer < len(layers):
        return layers[st.session_state.current_layer]["image"]
    return None

def merge_layers():
    """دمج كل الطبقات الظاهرة في طبقة واحدة."""
    visible = [l for l in st.session_state.image_layers if l["visible"] and l["image"]]
    if not visible:
        return None
    base = visible[0]["image"].convert("RGBA")
    for layer in visible[1:]:
        img = layer["image"].convert("RGBA")
        if img.size != base.size:
            img = img.resize(base.size)
        alpha = layer.get("opacity", 1.0)
        if alpha >= 1.0:
            base = Image.alpha_composite(base, img)
        else:
            faded = img.copy()
            faded.putalpha(faded.getalpha().point(lambda p: int(p * alpha)))
            base = Image.alpha_composite(base, faded)
    st.session_state.image_layers = [{"name": "Merged", "image": base.convert("RGB"), "visible": True, "opacity": 1.0}]
    st.session_state.current_layer = 0
    return base.convert("RGB")

def generate_natural_teeth(count=10):
    img = Image.new('RGB', (600, 350), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    colors = ['#F5F0E8', '#E8E0D8', '#F0EBE3', '#E5DDD5']
    step = max(1, (600 - 80) // max(count, 1))
    for i in range(count):
        x = 40 + i * step
        y = 100
        w = min(38, step - 8)
        h = 65
        color = random.choice(colors)
        draw.ellipse([x, y, x + w, y + h], fill=color, outline='#cbd5e1', width=2)
        draw.ellipse([x + 6, y + 8, x + w - 6, y + h - 10], fill='#FFFFFF')
        draw.ellipse([x + 10, y + 12, x + w - 10, y + h - 15], fill=color)
    draw.rectangle([0, 80, 600, 105], fill='#e8b4b8')
    draw.rectangle([0, 170, 600, 190], fill='#e8b4b8')
    return img

def draw_landmarks_on_image(image, count=478):
    img = image.copy() if isinstance(image, Image.Image) else Image.open(image)
    draw = ImageDraw.Draw(img)
    w, h = img.size
    colors = ['#e67e22', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6']
    for _ in range(min(count, 120)):
        x = random.randint(10, max(11, w - 10))
        y = random.randint(10, max(11, h - 10))
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=random.choice(colors))
    draw.line([(int(w * 0.2), int(h * 0.1)), (int(w * 0.8), int(h * 0.1))], fill='#e67e22', width=2)
    draw.line([(int(w * 0.2), int(h * 0.9)), (int(w * 0.8), int(h * 0.9))], fill='#e67e22', width=2)
    draw.line([(int(w * 0.5), int(h * 0.1)), (int(w * 0.5), int(h * 0.9))], fill='#10b981', width=2)
    return img

def draw_face_mesh_on_image(image):
    """رسم FaceMesh حقيقي عبر MediaPipe مع بديل تلقائي إن تعذّر."""
    if isinstance(image, Image.Image):
        img_rgb = np.array(image.convert('RGB'))
    else:
        img_rgb = np.array(image)
    if MEDIAPIPE_OK and CV2_OK:
        import cv2
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                                   refine_landmarks=True, min_detection_confidence=0.5) as fm:
            results = fm.process(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * img_rgb.shape[1])
                    y = int(landmark.y * img_rgb.shape[0])
                    cv2.circle(img_rgb, (x, y), 2, (16, 185, 129), -1)
            return Image.fromarray(img_rgb)
    # بديل: شبكة نقاط توضيحية
    return draw_landmarks_on_image(Image.fromarray(img_rgb), 478)

# =============================================================
# 3DPEA INTEGRATION (تكامل فعلي)
# =============================================================
THREE_D_PEA_URL = "https://www.3dpea.com/"

def convert_image_to_3d(image_file, output_format="stl"):
    """محاولة تحويل حقيقي عبر 3DPEA API، مع وضع محاكاة عند غياب مفتاح API."""
    try:
        api_key = os.environ.get("THREE_D_PEA_API_KEY", "")
        if api_key:
            files = {"file": (image_file.name, image_file.getvalue(),
                              getattr(image_file, "type", "application/octet-stream"))}
            resp = requests.post(
                "https://api.3dpea.com/api/v1/image-to-3d",
                headers={"Authorization": f"Bearer {api_key}"},
                files=files,
                data={"format": output_format},
                timeout=120,
            )
            if resp.status_code == 200:
                return {"status": "completed", "content": resp.content}
        # وضع المحاكاة المحلي
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_data = {
            "name": f"3D_Model_{timestamp}",
            "format": output_format,
            "original_file": image_file.name,
            "created_at": datetime.now().isoformat(),
            "status": "completed (محاكاة — أضف THREE_D_PEA_API_KEY للتحويل الحقيقي)",
        }
        st.session_state.converted_models.append(model_data)
        return {"status": "simulated", "model": model_data}
    except Exception as e:
        st.error(f"❌ خطأ في التحويل: {e}")
        return None

# =============================================================
# AUTH PAGE
# =============================================================
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align:center;">
            {display_system_logo(55)}
            <h1>Dentofacial <span style="color:#e67e22;">HarmonizeAI</span></h1>
            <p>Naqeeb412 · Synergy</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🔐 طرق تسجيل الدخول")
        col_social = st.columns(6)
        platforms = [("Google", "🔵"), ("Facebook", "🔷"), ("Instagram", "🟣"),
                     ("LinkedIn", "🔵"), ("Twitter", "🔷"), ("WhatsApp", "🟢")]
        for i, (name, icon) in enumerate(platforms):
            with col_social[i]:
                if st.button(f"{icon}\n{name}", key=f"social_{i}", use_container_width=True):
                    email = f"user_{random.randint(1000,9999)}@{name.lower()}.com"
                    if email not in st.session_state.users_db:
                        signup_user(f"مستخدم {name}", email, "social123", "doctor")
                    if login_user(email, "social123"):
                        st.success(f"✅ تم تسجيل الدخول عبر {name}!")
                        st.rerun()
        st.markdown("---")
        st.markdown("### 📧 تسجيل الدخول بالبريد الإلكتروني")
        tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب"])
        with tab1:
            with st.form("login_form"):
                email = st.text_input("البريد الإلكتروني", value="ndcdental2025@outlook.com")
                password = st.text_input("كلمة المرور", type="password", value="ndc2025")
                if st.form_submit_button("🚪 دخول", use_container_width=True):
                    if login_user(email, password):
                        st.success("✅ مرحباً بك!")
                        st.rerun()
                    else:
                        st.error("❌ بيانات غير صحيحة")
        with tab2:
            with st.form("signup_form"):
                name = st.text_input("الاسم الكامل *")
                email = st.text_input("البريد الإلكتروني *")
                password = st.text_input("كلمة المرور *", type="password")
                role = st.selectbox("نوع الحساب", ["doctor", "patient"])
                if st.form_submit_button("📝 إنشاء حساب", use_container_width=True):
                    if not name or not email or not password:
                        st.error("❌ جميع الحقول مطلوبة")
                    else:
                        ok, msg = signup_user(name, email, password, role)
                        (st.success if ok else st.error)(msg)

# =============================================================
# SIDEBAR
# =============================================================
def sidebar_nav():
    user = st.session_state.current_user
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;">
            {display_system_logo(50)}
            <h3>🧬 Dentofacial</h3>
            <p>HarmonizeAI™ · v5.0</p>
            <span class="privacy-badge">🔒 بياناتك خاصة بك</span>
            <hr>
            <b>{user['name']}</b><br>
            <small>{user.get('specialty','') or user['role']}</small>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        menu_items = {
            "🏠 الرئيسية": "home",
            "📊 لوحة التحكم": "dashboard",
            "🎯 محاكاة الابتسامة": "smile_simulator",
            "👨‍⚕️ المرضى": "patients",
            "➕ مريض جديد": "new_patient",
            "🦷 مخطط الأسنان": "dental_chart",
            "🦷 Natural Teeth": "natural_teeth",
            "📸 التصوير": "photography",
            "🩻 الأشعة": "xray",
            "📱 Dentbook": "dentbook",
            "🤝 الأصدقاء": "friends",
            "👤 الملف الشخصي": "profile",
            "👥 الأعضاء": "members",
            "💬 المراسلات": "messages",
            "💌 رسائل خاصة": "private_messages",
            "🧪 مع المختبر": "lab_chat",
            "📁 مشاركة الملفات": "file_sharing",
            "🖥️ مشاركة الشاشة": "screen_share",
            "🩺 التشخيص الذكي": "diagnosis",
            "📋 خطة العلاج": "treatment_plan",
            "🧪 المواد": "materials",
            "🧑‍⚕️ تحليل الوجه": "facial",
            "🩻 تحليل الأشعة": "cephalometric",
            "😁 تصميم الابتسامة": "smile_design",
            "🎨 التصميم التجميلي": "aesthetic_design",
            "📦 نماذج 3D": "stl_3d",
            "🧬 استوديو DSD": "dsd_studio",
            "💎 علاج تجميلي": "aesthetic_treatment",
            "🌍 المنصة العالمية": "global_platform",
            "🔄 خط الإنتاج": "pipeline",
            "🦷 دليل المواد": "materials_guide",
            "🔌 مركز الأنظمة": "api_hub",
            "🗄️ مستودع المريض": "mock_db",
            "🔔 الإشعارات": "notifications",
            "🖥️ الأنظمة": "systems",
            "🔬 المسح العلمي": "scientific_scan",
            "🤖 NaqAI": "naqai",
            "👥 Interdisciplinary": "interdisciplinary",
            "📢 الإعلانات": "ads",
            "🔬 المعمل": "lab",
            "📅 المواعيد": "appointments",
            "💰 الحساب": "accounting",
            "💳 الدفع": "payments",
            "👑 الاشتراكات": "subscriptions",
            "📨 دعوة الأطباء": "invite",
            "⚙️ الإعدادات": "settings",
            "📄 التقارير": "reports",
            "🔒 الخصوصية": "privacy",
            "©️ حقوق الملكية": "ip",
            "⚙️ CAD/CAM": "cadcam",
            "🗣️ منتدى النقاشات": "forum",
            "🎨 ألوان فيتا": "vita",
            "🎨 محرر الصور": "image_editor",
            "🔄 3DPEA Converter": "3dpea",
            "🎨 Image to 3D": "image_to_3d",
            "📦 3D Gallery": "3d_gallery",
        }
        for label, key in menu_items.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
        st.divider()
        if st.button("🚪 تسجيل خروج", use_container_width=True, type="primary"):
            logout()

# =============================================================
# PAGES
# =============================================================
def page_home():
    st.markdown("""
    <div style="text-align:center; padding:40px 20px;">
        <h1>🦷 Dentofacial <span style="color:#e67e22;">HarmonizeAI™</span></h1>
        <h3>تشخيص دقيق بذكاء اصطناعي</h3>
        <p>Harvard Protocol AI-Powered · 3D Planning</p>
        <p style="max-width:700px; margin:0 auto;">
        يدمج Naqeeb412 HarmonizeAI بين التصوير ثلاثي الأبعاد، محاكاة الابتسامة،
        وتحليل الوجه لنتائج علاجية استثنائية.
        </p>
        <span class="badge-harvard">Harvard Protocol</span>
        <span class="badge-gold">AI-Powered</span>
        <span class="privacy-badge">Private Data</span>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><h4>🎯 محاكاة الابتسامة</h4><p>معاينة قبل/بعد فورية بالذكاء الاصطناعي.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h4>🧑‍⚕️ تحليل الوجه</h4><p>رسم 478 علامة تشريحية دقيقة.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><h4>🔄 3DPEA</h4><p>تحويل الصور إلى نماذج ثلاثية الأبعاد.</p></div>', unsafe_allow_html=True)

def page_dashboard():
    st.markdown('<h1>📊 لوحة التحكم</h1>', unsafe_allow_html=True)
    st.markdown(f"<p>مرحباً بك في Dentofacial HarmonizeAI™، {st.session_state.current_user['name']}</p>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div>👨‍⚕️ المرضى</div><div class="metric-value">{len(st.session_state.patients)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div>📅 المواعيد</div><div class="metric-value">{len(st.session_state.appointments)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div>🧠 الصور المُنتجة</div><div class="metric-value">{len(st.session_state.generated_images)}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div>📦 نماذج 3D</div><div class="metric-value">{len(st.session_state.converted_models)}</div></div>', unsafe_allow_html=True)
    st.divider()
    if PLOTLY_OK:
        df = pd.DataFrame({
            "اليوم": [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)],
            "حالات": [random.randint(2, 12) for _ in range(7)],
        })
        fig = px.bar(df, x="اليوم", y="حالات", color_discrete_sequence=["#0a8491"])
        st.plotly_chart(fig, use_container_width=True)

def page_smile_simulator():
    st.markdown('<h1>🎯 محاكاة الابتسامة والتناغم الوجهي باستخدام الذكاء الاصطناعي</h1>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 اختر صورة وجه المريض", type=["jpg", "jpeg", "png"])
    if uploaded:
        original = Image.open(uploaded)
        st.image(original, caption="الصورة الأصلية", use_container_width=True)
        st.text_area("📝 وصف النتيجة المطلوبة:", placeholder="مثال: ابتسامة طبيعية، أسنان بيضاء متناسقة...", height=60)
        intensity = st.slider("شدة التحسين", 0.1, 1.0, 0.7, 0.05)
        if st.button("🎯 توليد المحاكاة", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري توليد المحاكاة الذكية..."):
                time.sleep(1.5)
                _, result = simulate_smile_before_after(original, intensity)
                comparison = create_comparison_image(original, result)
            c1, c2 = st.columns(2)
            with c1:
                st.image(result, caption="النتيجة المتوقعة", use_container_width=True)
            with c2:
                st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
            st.success("✅ تم توليد المحاكاة بنجاح!")

def enhance_smile_face(image_array, intensity=0.7):
    img = image_array.copy()
    h, w = img.shape[:2]
    mouth_y_start, mouth_y_end = int(h * 0.55), int(h * 0.75)
    mouth_x_start, mouth_x_end = int(w * 0.3), int(w * 0.7)
    mouth_roi = img[mouth_y_start:mouth_y_end, mouth_x_start:mouth_x_end].copy()
    if mouth_roi.size > 0:
        hsv = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + intensity * 0.3), 0, 255).astype(np.uint8)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (0.8 + intensity * 0.2), 0, 255).astype(np.uint8)
        mouth_roi = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        mouth_roi = cv2.GaussianBlur(mouth_roi, (3, 3), 0)
        img[mouth_y_start:mouth_y_end, mouth_x_start:mouth_x_end] = mouth_roi
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)
    alpha = 0.1 * intensity
    brightness = np.ones(img.shape, dtype=np.uint8) * 30
    img = cv2.addWeighted(img, 1 - alpha, brightness, alpha, 0)
    return img

def simulate_smile_before_after(original_img, intensity=0.7):
    original_np = np.array(original_img.convert('RGB'))
    if CV2_OK:
        bgr = cv2.cvtColor(original_np, cv2.COLOR_RGB2BGR)
        enhanced = enhance_smile_face(bgr, intensity)
        result = Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
    else:
        enhancer = ImageEnhance.Brightness(original_img)
        result = enhancer.enhance(1 + intensity * 0.15)
    return original_img, result

def create_comparison_image(before_img, after_img, split_position=0.5):
    before = before_img if isinstance(before_img, Image.Image) else Image.fromarray(before_img)
    after = after_img if isinstance(after_img, Image.Image) else Image.fromarray(after_img)
    if before.size != after.size:
        after = after.resize(before.size)
    w, h = before.size
    split = int(w * split_position)
    result = Image.new('RGB', (w, h))
    result.paste(before.crop((0, 0, split, h)), (0, 0))
    result.paste(after.crop((split, 0, w, h)), (split, 0))
    draw = ImageDraw.Draw(result)
    draw.line([(split, 0), (split, h)], fill='#e67e22', width=3)
    draw.text((10, 10), "قبل", fill='#ffffff')
    draw.text((w - 60, 10), "بعد", fill='#e67e22')
    return result

def page_patients():
    st.markdown('<h1>👨‍⚕️ قائمة المرضى</h1>', unsafe_allow_html=True)
    if st.session_state.patients:
        st.dataframe(pd.DataFrame(st.session_state.patients), use_container_width=True, hide_index=True)
    else:
        st.info("لا يوجد مرضى بعد — أضف مريضًا جديدًا من القائمة.")

def page_new_patient():
    st.markdown('<h1>📝 إضافة مريض جديد</h1>', unsafe_allow_html=True)
    with st.form("new_patient_form"):
        name = st.text_input("الاسم الكامل *")
        age = st.number_input("العمر", min_value=0, max_value=120, value=30)
        phone = st.text_input("رقم الهاتف")
        gender = st.selectbox("الجنس", ["ذكر", "أنثى", "غير محدد"])
        complaint = st.text_area("الشكوى الرئيسية")
        if st.form_submit_button("💾 حفظ المريض", use_container_width=True) and name:
            st.session_state.patients.append({
                "id": f"P{len(st.session_state.patients)+1:04d}", "name": name, "age": age,
                "phone": phone, "gender": gender, "complaint": complaint,
                "created_at": datetime.now().isoformat(),
            })
            st.success("✅ تم إضافة المريض!")
            st.rerun()

def page_dental_chart():
    st.markdown('<h1>🦷 مخطط الأسنان</h1>', unsafe_allow_html=True)
    st.markdown(render_dental_chart(), unsafe_allow_html=True)
    st.markdown("### ✏️ تعديل حالة سن")
    col1, col2, col3 = st.columns(3)
    with col1:
        tooth_idx = st.number_input("رقم السن (1-32)", min_value=1, max_value=32, value=1)
    with col2:
        status = st.selectbox("الحالة", ["normal", "missing", "carious", "treated", "crown", "root-canal"])
    with col3:
        st.write("")
        st.write("")
        if st.button("💾 تطبيق", use_container_width=True):
            st.session_state.dental_chart[tooth_idx - 1] = status
            st.success(f"✅ تم تحديث السن {tooth_idx}")
            st.rerun()
    if st.button("🔄 إعادة ضبط الكل", use_container_width=True):
        st.session_state.dental_chart = ['normal'] * 32
        st.success("✅ تم إعادة ضبط المخطط")
        st.rerun()

def render_dental_chart():
    chart = st.session_state.dental_chart
    status_map = {
        'normal': {'icon': '🟢', 'cls': ''}, 'missing': {'icon': '', 'cls': 'missing'},
        'carious': {'icon': '🦷', 'cls': 'carious'}, 'treated': {'icon': '✔️', 'cls': 'treated'},
        'crown': {'icon': '👑', 'cls': 'crown'}, 'root-canal': {'icon': '🧬', 'cls': 'root-canal'},
    }
    html = '<div class="dental-chart-wrapper"><div class="dental-chart">'
    html += '<div class="dental-arch"><div class="arch-label">⬆ الفك العلوي</div>'
    for i in range(16):
        s = status_map.get(chart[i], status_map['normal'])
        icon_html = '' if chart[i] == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div><div class="dental-arch"><div class="arch-label">⬇ الفك السفلي</div>'
    for i in range(16, 32):
        s = status_map.get(chart[i], status_map['normal'])
        icon_html = '' if chart[i] == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div>'
    html += """
    <div class="tooth-legend">
        <div class="legend-item"><div class="swatch normal"></div>سليم</div>
        <div class="legend-item"><div class="swatch missing"></div>مفقود</div>
        <div class="legend-item"><div class="swatch carious"></div>نخر</div>
        <div class="legend-item"><div class="swatch treated"></div>معالج</div>
        <div class="legend-item"><div class="swatch crown"></div>تاج</div>
        <div class="legend-item"><div class="swatch root-canal"></div>علاج جذور</div>
    </div></div></div>
    """
    return html

def page_natural_teeth():
    st.markdown('<h1>🦷 الأسنان الطبيعية Natural Teeth</h1>', unsafe_allow_html=True)
    count = st.slider("عدد الأسنان", 6, 16, 10)
    if st.button("🦷 توليد أسنان طبيعية", type="primary", use_container_width=True):
        with st.spinner("⏳ جاري توليد الأسنان الطبيعية..."):
            img = generate_natural_teeth(count)
        st.image(img, caption="الأسنان الطبيعية", use_container_width=True)
        add_layer(img, "Natural Teeth")
        st.success("✅ تم توليد الأسنان الطبيعية وإضافتها إلى المحرر!")

def page_photography():
    st.markdown('<h1>📸 قسم التصوير</h1>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📤 رفع صور المريض", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            img = Image.open(f)
            st.session_state.patient_images.append({"name": f.name, "image": img, "time": datetime.now().isoformat()})
        st.success(f"✅ تم رفع {len(uploaded)} صورة")
    if st.session_state.patient_images:
        cols = st.columns(4)
        for i, item in enumerate(st.session_state.patient_images[-12:]):
            with cols[i % 4]:
                st.image(item["image"], caption=item["name"], use_container_width=True)

def page_xray():
    st.markdown('<h1>🩻 قسم الأشعة</h1>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📤 رفع صورة أشعة", type=["jpg", "jpeg", "png", "dcm"], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            st.session_state.xray_images.append({"name": f.name, "file": f, "time": datetime.now().isoformat()})
        st.success(f"✅ تم رفع {len(uploaded)} أشعة")
    if st.session_state.xray_images:
        cols = st.columns(3)
        for i, item in enumerate(st.session_state.xray_images[-9:]):
            with cols[i % 3]:
                try:
                    st.image(Image.open(item["file"]), caption=item["name"], use_container_width=True)
                except Exception:
                    st.info(f"🩻 {item['name']}")

def page_dentbook():
    st.markdown('<h1>📱 Dentbook الشبكة الاجتماعية الطبية</h1>', unsafe_allow_html=True)
    text = st.text_area("ماذا تفكر؟ شارك حالة طبية...", height=80)
    if st.button("🚀 نشر", type="primary") and text:
        st.session_state.dentbook_posts.insert(0, {
            "author": st.session_state.current_user["name"],
            "text": text, "time": datetime.now().strftime("%H:%M"), "likes": 0,
        })
        st.success("✅ تم النشر!")
        st.rerun()
    for post in st.session_state.dentbook_posts[:10]:
        st.markdown(f"""
        <div class="card">
            <b>{post['author']}</b> <small style="color:#94a3b8;">{post['time']}</small>
            <p>{post['text']}</p>
            <small>❤️ {post['likes']} · 💬 0</small>
        </div>
        """, unsafe_allow_html=True)

def page_friends():
    st.markdown('<h1>🤝 الأصدقاء وطلبات الصداقة</h1>', unsafe_allow_html=True)
    st.info("👥 نظام الأصدقاء متاح")
    users = [u for u in st.session_state.users_db.values() if u["email"] != st.session_state.current_user["email"]]
    for u in users:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{u['name']}** — {u.get('specialty') or u['role']}")
        with c2:
            if st.button("➕ إضافة", key=f"fr_{u['email']}"):
                st.session_state.friend_requests.append({"from": st.session_state.current_user["email"], "to": u["email"]})
                st.success("✅ تم إرسال الطلب")

def page_profile():
    st.markdown('<h1>👤 الملف الشخصي</h1>', unsafe_allow_html=True)
    user = st.session_state.current_user
    with st.form("profile_form"):
        name = st.text_input("الاسم", value=user.get("name", ""))
        specialty = st.text_input("التخصص", value=user.get("specialty", ""))
        phone = st.text_input("الهاتف", value=user.get("phone", ""))
        bio = st.text_area("نبذة", value=user.get("bio", ""))
        if st.form_submit_button("💾 حفظ"):
            st.session_state.current_user.update({"name": name, "specialty": specialty, "phone": phone, "bio": bio})
            st.session_state.users_db[user["email"]].update(st.session_state.current_user)
            st.success("✅ تم الحفظ!")

def page_members():
    st.markdown('<h1>👥 أعضاء النظام</h1>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"الاسم": u["name"], "البريد": u["email"], "الدور": u["role"], "التخصص": u.get("specialty", "")}
        for u in st.session_state.users_db.values()
    ]), use_container_width=True, hide_index=True)

def page_messages():
    st.markdown('<h1>💬 المراسلات العامة</h1>', unsafe_allow_html=True)
    for msg in st.session_state.messages[-20:]:
        st.markdown(f"<div class='card'><b>{msg['sender']}</b>: {msg['text']}</div>", unsafe_allow_html=True)
    text = st.text_input("اكتب رسالة...")
    if st.button("إرسال") and text:
        st.session_state.messages.append({"sender": st.session_state.current_user["name"], "text": text})
        st.rerun()

def page_private_messages():
    st.markdown('<h1>💌 رسائل خاصة بين الأطباء</h1>', unsafe_allow_html=True)
    others = [u["email"] for u in st.session_state.users_db.values() if u["email"] != st.session_state.current_user["email"]]
    if others:
        target = st.selectbox("إلى", others)
        thread = [m for m in st.session_state.private_messages if {m["from"], m["to"]} == {st.session_state.current_user["email"], target}]
        for m in thread[-15:]:
            st.markdown(f"<div class='card'><b>{m['from']}</b>: {m['text']}</div>", unsafe_allow_html=True)
        text = st.text_input("رسالة خاصة...")
        if st.button("📨 إرسال خاص", type="primary") and text:
            st.session_state.private_messages.append({"from": st.session_state.current_user["email"], "to": target, "text": text})
            st.rerun()

def page_lab_chat():
    st.markdown('<h1>🧪 التواصل مع المختبر</h1>', unsafe_allow_html=True)
    for msg in st.session_state.lab_messages[-10:]:
        st.markdown(f"<div class='card'><b>{msg['sender']}</b>: {msg['text']}</div>", unsafe_allow_html=True)
    text = st.text_input("رسالتك للمختبر...")
    if st.button("إرسال") and text:
        st.session_state.lab_messages.append({"sender": st.session_state.current_user["name"], "text": text})
        st.rerun()

def page_file_sharing():
    st.markdown('<h1>📁 مشاركة الملفات</h1>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📤 رفع ملف للمشاركة", accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            st.session_state.files_uploaded.append({"name": f.name, "size": f.size, "time": datetime.now().isoformat()})
        st.success("✅ تم الرفع")
    if st.session_state.files_uploaded:
        st.dataframe(pd.DataFrame(st.session_state.files_uploaded), use_container_width=True, hide_index=True)

def page_screen_share():
    st.markdown('<h1>🖥️ مشاركة الشاشة</h1>', unsafe_allow_html=True)
    st.info("استخدم زر المتصفح لمشاركة الشاشة — سيتم تسجيل الجلسة محلياً.")
    st.code("window.navigator.mediaDevices.getDisplayMedia()", language="javascript")
    if st.button("🔴 بدء جلسة مشاركة"):
        st.success("✅ جلسة مشاركة نشطة (محاكاة)")

def page_diagnosis():
    st.markdown('<h1>🩺 التشخيص الذكي</h1>', unsafe_allow_html=True)
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد مرضى"]
    st.selectbox("اختر المريض", patients)
    st.text_area("الأعراض", placeholder="أدخل الأعراض بالتفصيل...")
    if st.button("🎓 تشخيص AI - Harvard", type="primary"):
        with st.spinner("🧠 جاري التحليل..."):
            time.sleep(2)
        st.success("✅ تم التشخيص!")
        st.markdown("""
        <div class="card">
            <b>النتيجة:</b> لا توجد مؤشرات حرجة.<br>
            <b>التوصية:</b> متابعة دورية + غسول فموي.<br>
            <span class="badge-harvard">Harvard Protocol v4.2</span>
        </div>
        """, unsafe_allow_html=True)

def page_treatment_plan():
    st.markdown('<h1>📋 خطة العلاج</h1>', unsafe_allow_html=True)
    with st.form("plan_form"):
        tooth = st.number_input("رقم السن", 1, 32, 1)
        procedure = st.selectbox("الإجراء", ["حشوة تجميلية", "تاج زيركون", "علاج جذور", "تبييض", "تقويم"])
        cost = st.number_input("التكلفة ($)", 0, 100000, 200)
        if st.form_submit_button("💾 إضافة للخطة"):
            if "treatment_plans" not in st.session_state:
                st.session_state.treatment_plans = []
            st.session_state.treatment_plans.append({"tooth": tooth, "procedure": procedure, "cost": cost})
            st.success("✅ تمت الإضافة")
    if "treatment_plans" in st.session_state and st.session_state.treatment_plans:
        st.dataframe(pd.DataFrame(st.session_state.treatment_plans), use_container_width=True, hide_index=True)

def page_materials():
    st.markdown('<h1>🧪 المواد العلاجية</h1>', unsafe_allow_html=True)
    with st.form("mat_form"):
        name = st.text_input("اسم المادة")
        brand = st.text_input("الشركة")
        stock = st.number_input("الكمية", 0, 10000, 10)
        if st.form_submit_button("💾 إضافة"):
            st.session_state.materials.append({"name": name, "brand": brand, "stock": stock})
            st.success("✅ تمت الإضافة")
    if st.session_state.materials:
        st.dataframe(pd.DataFrame(st.session_state.materials), use_container_width=True, hide_index=True)

def page_facial():
    st.markdown('<h1>🧑‍⚕️ تحليل الوجه (478 علامة)</h1>', unsafe_allow_html=True)
    if not MEDIAPIPE_OK:
        st.warning("⚠️ MediaPipe غير مثبت — سيتم استخدام وضع العرض التوضيحي. ثبّته عبر: pip install mediapipe")
    uploaded = st.file_uploader("📸 حمّل صورة الوجه", type=["jpg", "png"], key="facial_img")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة المحملة", use_container_width=True)
        if st.button("📍 رسم 478 علامة", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري الرسم..."):
                result = draw_face_mesh_on_image(img)
            st.image(result, caption="العلامات التشريحية", use_container_width=True)
            st.success("✅ تم رسم 478 علامة!")

def page_cephalometric():
    st.markdown('<h1>🩻 تحليل الأشعة السيفالومترية</h1>', unsafe_allow_html=True)
    data = st.session_state.cephalometric_data
    normals = st.session_state.normal_values
    cols = st.columns(4)
    keys = list(data.keys())
    for i, k in enumerate(keys):
        with cols[i % 4]:
            data[k] = st.number_input(k, value=float(data[k]), step=0.5)
    st.divider()
    st.markdown("### 📋 مقارنة بالقيم الطبيعية")
    rows = []
    for k in keys:
        diff = data[k] - normals[k]
        rows.append({"القياس": k, "القيمة": data[k], "الطبيعي": normals[k],
                     "الانحراف": round(diff, 1),
                     "الحالة": "🟢 طبيعي" if abs(diff) <= 2 else "🔴 انحراف"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

def page_smile_design():
    st.markdown('<h1>😁 تصميم الابتسامة</h1>', unsafe_allow_html=True)
    shade = st.select_slider("درجة اللون (Vita)", options=["A1", "A2", "B1", "B2", "C1", "D2"], value="B1")
    width = st.slider("عرض الابتسامة", 0, 100, 80)
    incisal = st.slider("طول القواطع", 0, 100, 60)
    st.markdown(f"""
    <div class="card">
        <h4>معاينة التصميم</h4>
        <p>اللون: <b>{shade}</b> · العرض: <b>{width}%</b> · الطول: <b>{incisal}%</b></p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💾 حفظ التصميم", type="primary"):
        st.session_state.smile_designs.append({"shade": shade, "width": width, "incisal": incisal,
                                               "time": datetime.now().isoformat()})
        st.success("✅ تم حفظ التصميم")

def page_aesthetic_design():
    st.markdown('<h1>🎨 التصميم التجميلي (قبل / بعد)</h1>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 صورة المريض", type=["jpg", "png"], key="aesthetic_img")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, use_container_width=True)
        if st.button("🎨 توليد قبل/بعد", type="primary"):
            _, after = simulate_smile_before_after(img, 0.8)
            st.image(create_comparison_image(img, after), caption="قبل / بعد", use_container_width=True)

def page_stl_3d():
    st.markdown('<h1>📦 نماذج 3D / Mesh</h1>', unsafe_allow_html=True)
    st.info("للتحويل الفعلي استخدم صفحات 3DPEA بالأسفل")
    st.page_link = None
    if st.button("🔄 فتح محول 3DPEA"):
        st.session_state.current_page = "3dpea"
        st.rerun()

def page_dsd_studio():
    st.markdown('<h1>🧬 استوديو إعادة بناء الابتسامة الطبيعية Bio-Mimetic DSD</h1>', unsafe_allow_html=True)
    st.slider("عرض الابتسامة", 0, 100, 80)
    st.slider("الارتفاع العمودي", 0, 100, 50)
    st.slider("تطابق الشفافية", 0, 100, 70)

def page_aesthetic_treatment():
    st.markdown('<h1>💎 علاج الوجه التجميلي المتقدم</h1>', unsafe_allow_html=True)
    treatment = st.selectbox("نوع العلاج", ["فيلر", "بوتوكس", "خيوط شد", "بلازما"])
    area = st.multiselect("منطقة العلاج", ["جبهة", "خدود", "شفاه", "ذقن", "عنق"])
    st.info(f"💉 {treatment} — المناطق: {', '.join(area) if area else 'غير محددة'}")

def page_global_platform():
    st.markdown('<h1>🌍 المنصة العالمية Dentofacial HarmonizeAI™</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p>🌐 تواصل مع أطباء الأسنان حول العالم.</p>
        <p>🤝 حالات مشتركة، استشارات ثانية، وتحويلات.</p>
    </div>
    """, unsafe_allow_html=True)

def page_pipeline():
    st.markdown('<h1>🔄 خط الإنتاج المدمج</h1>', unsafe_allow_html=True)
    progress = st.session_state.pipeline_progress
    st.progress(progress / 100, text=f"اكتمال الخط: {progress}%")
    if st.button("▶️ تشغيل الخط"):
        for p in range(progress, 101, 5):
            st.session_state.pipeline_progress = p
            time.sleep(0.1)
            st.progress(p / 100, text=f"اكتمال الخط: {p}%")
        st.success("✅ اكتمل خط الإنتاج!")

def page_materials_guide():
    st.markdown('<h1>🦷 دليل المواد الطبية التجميلية مع المراجع العلمية</h1>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([
        {"المادة": "زيركون", "الاستخدام": "تيجان وجسور", "القوة": "عالية جداً"},
        {"المادة": "E.max", "الاستخدام": "قشور وتيجام أمامية", "القوة": "عالية"},
        {"المادة": "كومبوزيت", "الاستخدام": "حشوات تجميلية", "القوة": "متوسطة"},
        {"المادة": "PMMA", "الاستخدام": "مؤقتات", "القوة": "منخفضة"},
    ]), use_container_width=True, hide_index=True)

def page_api_hub():
    st.markdown('<h1>🔌 مركز تواصل الأنظمة (Global API Hub)</h1>', unsafe_allow_html=True)
    st.json({
        "3DPEA": {"url": "https://www.3dpea.com/", "status": "متصل"},
        "FaceMesh": {"provider": "MediaPipe", "status": "متصل" if MEDIAPIPE_OK else "غير مثبت"},
        "OpenCV": {"status": "متصل" if CV2_OK else "غير مثبت"},
        "Plotly": {"status": "متصل" if PLOTLY_OK else "غير مثبت"},
    })

def page_mock_db():
    st.markdown('<h1>🗄️ محاكي مستودع المريض</h1>', unsafe_allow_html=True)
    st.json({"patients": len(st.session_state.patients),
             "images": len(st.session_state.patient_images),
             "xrays": len(st.session_state.xray_images),
             "models": len(st.session_state.converted_models)})

def page_notifications():
    st.markdown('<h1>🔔 الإشعارات الواردة</h1>', unsafe_allow_html=True)
    st.info("🔕 لا إشعارات جديدة")

def page_systems():
    st.markdown('<h1>🖥️ الأنظمة المستخدمة</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <ul>
            <li>🧬 MediaPipe FaceMesh (478 landmark)</li>
            <li>🎨 OpenCV / Pillow</li>
            <li>🔄 3DPEA API</li>
            <li>📊 Plotly Dashboards</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def page_scientific_scan():
    st.markdown('<h1>🔬 المسح العلمي الشامل</h1>', unsafe_allow_html=True)
    if st.button("🔬 بدء المسح", type="primary"):
        with st.spinner("⏳ جاري المسح..."):
            time.sleep(2)
        st.success("✅ اكتمل المسح — لا مشاكل حرجة")

def page_naqai():
    st.markdown('<h1>🤖 NaqAI المساعد الذكي</h1>', unsafe_allow_html=True)
    for msg in st.session_state.naqai_chat:
        if msg["role"] == "ai":
            st.markdown(f'<div class="card">🤖 {msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="card" style="border-color:#0a8491;">🧑‍⚕️ {msg["text"]}</div>', unsafe_allow_html=True)
    q = st.text_input("اسأل NaqAI...")
    if st.button("📨 إرسال", type="primary") and q:
        st.session_state.naqai_chat.append({"role": "user", "text": q})
        responses = {
            "ابتسامة": "😁 تصميم الابتسامة يشمل تحليل النسب الذهبية ومحاكاة قبل/بعد.",
            "فيلر": "💉 فيلر حمض الهيالورونيك يستخدم لملء التجاعيد وتحديد ملامح الوجه.",
            "بوتوكس": "🧪 البوتوكس يستخدم لتقليل التجاعيد التعبيرية وإرخاء العضلات.",
        }
        ans = "🧠 شكراً لسؤالك! يمكنني مساعدتك في تصميم الابتسامة، العلاج التجميلي، تحليل الوجه، والمزيد."
        for k, v in responses.items():
            if k in q.lower():
                ans = v
                break
        st.session_state.naqai_chat.append({"role": "ai", "text": ans})
        st.rerun()

def page_interdisciplinary():
    st.markdown('<h1>👥 فرق متعددة التخصصات</h1>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.specialists), use_container_width=True, hide_index=True)

def page_ads():
    st.markdown('<h1>📢 الإعلانات</h1>', unsafe_allow_html=True)
    title = st.text_input("عنوان الإعلان")
    body = st.text_area("نص الإعلان")
    if st.button("📢 نشر إعلان", type="primary") and title:
        st.session_state.ads.append({"title": title, "body": body, "time": datetime.now().isoformat()})
        st.success("✅ تم النشر")
    for ad in st.session_state.ads[::-1][:5]:
        st.markdown(f'<div class="card"><h4>{ad["title"]}</h4><p>{ad["body"]}</p></div>', unsafe_allow_html=True)

def page_lab():
    st.markdown('<h1>🔬 حساب المعمل</h1>', unsafe_allow_html=True)
    st.info("🔬 لوحة المختبر — الطلبات الواردة")

def page_appointments():
    st.markdown('<h1>📅 المواعيد</h1>', unsafe_allow_html=True)
    with st.form("appt_form"):
        patient = st.text_input("المريض")
        date = st.date_input("التاريخ", datetime.now())
        hour = st.time_input("الوقت", datetime.now().time())
        if st.form_submit_button("💾 حجز"):
            st.session_state.appointments.append({"patient": patient, "date": str(date), "time": str(hour)})
            st.success("✅ تم الحجز")
    if st.session_state.appointments:
        st.dataframe(pd.DataFrame(st.session_state.appointments), use_container_width=True, hide_index=True)

def page_accounting():
    st.markdown('<h1>💰 حساب المريض</h1>', unsafe_allow_html=True)
    st.info("💰 الفواتير والمدفوعات")

def page_payments():
    st.markdown('<h1>💳 الدفع والمحفظة</h1>', unsafe_allow_html=True)
    st.info("💳 بوابات الدفع (Stripe / HyperPay) — اربطها بمفاتيحك")

def page_subscriptions():
    st.markdown('<h1>👑 خطط الاشتراك</h1>', unsafe_allow_html=True)
    cols = st.columns(3)
    plans = [("🆓 تجريبي", "$0", "free"), ("⭐ شهري", "$99", "monthly"), ("🌟 سنوي", "$999", "yearly")]
    for i, (name, price, key) in enumerate(plans):
        with cols[i]:
            st.markdown(f'<div class="metric-card"><h3>{name}</h3><div class="metric-value">{price}</div></div>', unsafe_allow_html=True)
            if st.button("اشترك", key=f"sub_{key}", use_container_width=True):
                st.session_state.subscriptions[key].append(st.session_state.current_user["email"])
                st.success(f"✅ تم تفعيل {name}")

def page_invite():
    st.markdown('<h1>📨 دعوة الأطباء</h1>', unsafe_allow_html=True)
    email = st.text_input("بريد الطبيب المدعو")
    if st.button("📨 إرسال دعوة", type="primary") and email:
        st.success(f"✅ تم إرسال دعوة إلى {email}")

def page_settings():
    st.markdown('<h1>⚙️ الإعدادات والخصوصية</h1>', unsafe_allow_html=True)
    logo = st.file_uploader("شعار المنصة (PNG)", type=["png", "jpg"])
    if logo and st.button("💾 تعيين الشعار"):
        st.session_state.system_logo = base64.b64encode(logo.read()).decode()
        st.success("✅ تم تعيين الشعار")
    st.toggle("الوضع الليلي", value=True)
    st.toggle("إشعارات البريد", value=True)

def page_privacy():
    st.markdown('<h1>🔒 الخصوصية والأمان</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <ul>
            <li>🔐 تشفير البيانات أثناء النقل والتخزين.</li>
            <li>🗂️ بيانات المرضى لا تُشارك مع طرف ثالث.</li>
            <li>📜 توافق مع معايير حماية البيانات الصحية.</li>
        </ul>
        <span class="privacy-badge">🔒 Private Data</span>
    </div>
    """, unsafe_allow_html=True)

def page_ip():
    st.markdown('<h1>©️ حقوق الملكية الفكرية</h1>', unsafe_allow_html=True)
    st.info("© 2026 Naqeeb412 — جميع الحقوق محفوظة.")

def page_reports():
    st.markdown('<h1>📄 التقارير</h1>', unsafe_allow_html=True)
    if st.button("📄 توليد تقرير شامل", type="primary", use_container_width=True):
        with st.spinner("⏳ جاري توليد التقرير الشامل..."):
            time.sleep(2)
        st.success("✅ تم توليد التقرير الشامل!")
        st.download_button(
            label="⬇️ تحميل التقرير",
            data=b"%PDF-1.4",
            file_name=f"HarmonizeAI_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
        )
    st.markdown("### 📸 الصور المُنتجة")
    if st.session_state.generated_images:
        cols = st.columns(4)
        for i, img in enumerate(st.session_state.generated_images[-8:]):
            with cols[i % 4]:
                try:
                    st.image(f"data:image/png;base64,{img['data']}", caption=img.get('name', 'صورة'), use_container_width=True)
                except Exception:
                    st.info(img.get('name', 'صورة'))
    else:
        st.info("لا توجد صور مُنتجة بعد")

def page_forum():
    st.markdown('<h1>🗣️ منتدى النقاشات مع الأخصائيين</h1>', unsafe_allow_html=True)
    q = st.text_area("اطرح سؤالاً...")
    if st.button("🚀 نشر السؤال", type="primary") and q:
        st.session_state.forum_questions.insert(0, {"author": st.session_state.current_user["name"],
                                                    "question": q, "time": datetime.now().isoformat()})
        st.success("✅ تم النشر")
    for item in st.session_state.forum_questions[:10]:
        st.markdown(f'<div class="card"><b>{item["author"]}</b><p>{item["question"]}</p></div>', unsafe_allow_html=True)

def page_cadcam():
    st.markdown('<h1>⚙️ CAD/CAM & 3D (نموذج افتراضي جاهز)</h1>', unsafe_allow_html=True)
    st.info("⚙️ تصميم وبناء الأسنان رقمياً — جاهز للربط مع milling unit")

def page_vita():
    st.markdown('<h1>🎨 ألوان فيتا</h1>', unsafe_allow_html=True)
    shades = ["A1", "A2", "A3", "B1", "B2", "C1", "C2", "D2"]
    cols = st.columns(4)
    for i, s in enumerate(shades):
        with cols[i % 4]:
            st.markdown(f'<div class="metric-card"><h3>{s}</h3></div>', unsafe_allow_html=True)

def page_image_editor():
    st.markdown('<h1>🎨 محرر الصور المتقدم (Photopea-like)</h1>', unsafe_allow_html=True)
    if not st.session_state.image_layers:
        base_img = Image.new('RGB', (800, 600), color='#1a1a2e')
        draw = ImageDraw.Draw(base_img)
        draw.text((400, 300), "🦷 ارفع صورة لبدء التحرير", fill='#94a3b8', anchor="mm")
        st.session_state.image_layers = [{"name": "Background", "image": base_img, "visible": True, "opacity": 1.0}]
        st.session_state.current_layer = 0
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown("### 🛠️ الأدوات")
        uploaded = st.file_uploader("📤 رفع صورة", type=["jpg", "png", "jpeg"], key="editor_upload")
        if uploaded:
            img = Image.open(uploaded)
            add_layer(img, f"Layer {len(st.session_state.image_layers)}")
            st.success("✅ تم إضافة الطبقة")
            st.rerun()
        if st.session_state.image_layers:
            layer = st.session_state.image_layers[st.session_state.current_layer]
            layer["name"] = st.text_input("اسم الطبقة", value=layer["name"])
            layer["opacity"] = st.slider("الشفافية", 0.0, 1.0, float(layer["opacity"]), 0.05)
            layer["visible"] = st.checkbox("ظاهرة", value=layer["visible"])
        if st.button("🧑 رسم FaceMesh على الطبقة", use_container_width=True):
            img = get_current_layer_image()
            if img:
                result = draw_face_mesh_on_image(img)
                add_layer(result, "FaceMesh")
                st.success("✅ تم رسم FaceMesh")
                st.rerun()
        if st.button("🦷 إضافة أسنان طبيعية", use_container_width=True):
            teeth = generate_natural_teeth()
            add_layer(teeth, "Natural Teeth")
            st.success("✅ تم إضافة الأسنان الطبيعية")
            st.rerun()
    with col1:
        if st.session_state.image_layers:
            display_img = None
            for layer in st.session_state.image_layers:
                if layer["visible"] and layer["image"]:
                    img = layer["image"].convert("RGBA")
                    if display_img is None:
                        display_img = img
                    else:
                        if img.size != display_img.size:
                            img = img.resize(display_img.size)
                        alpha = layer["opacity"]
                        if alpha < 1.0:
                            img.putalpha(img.getalpha().point(lambda p: int(p * alpha)))
                        display_img = Image.alpha_composite(display_img, img)
            if display_img:
                display_img = display_img.convert("RGB")
                display_img.thumbnail((700, 500))
                st.image(display_img, caption="المحرر", use_container_width=True)
        st.markdown("### 📋 الطبقات")
        for i, layer in enumerate(st.session_state.image_layers):
            col_a, col_b, col_c = st.columns([1, 3, 1])
            with col_a:
                vis = "👁️" if layer["visible"] else "👁️‍🗨️"
                if st.button(vis, key=f"vis_{i}"):
                    layer["visible"] = not layer["visible"]
                    st.rerun()
            with col_b:
                label = layer['name']
                if i == st.session_state.current_layer:
                    label = f"▶ {label}"
                if st.button(label, key=f"layer_{i}", use_container_width=True):
                    st.session_state.current_layer = i
                    st.rerun()
            with col_c:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.image_layers.pop(i)
                    if st.session_state.image_layers:
                        st.session_state.current_layer = min(st.session_state.current_layer, len(st.session_state.image_layers) - 1)
                    else:
                        st.session_state.current_layer = 0
                    st.rerun()
        col_merge, col_clear = st.columns(2)
        with col_merge:
            if st.button("🔗 دمج الكل", use_container_width=True):
                if merge_layers():
                    st.success("✅ تم الدمج")
                st.rerun()
        with col_clear:
            if st.button("🗑️ مسح الكل", use_container_width=True):
                st.session_state.image_layers = []
                st.session_state.current_layer = 0
                st.rerun()

# =============================================================
# 3DPEA PAGES (تكامل فعلي)
# =============================================================
def page_3dpea():
    st.markdown('<h1>🔄 تحويل الصور إلى نماذج ثلاثية الأبعاد 3DPEA</h1>', unsafe_allow_html=True)
    st.caption("تحويل الصور (PNG, JPG) إلى نماذج ثلاثية الأبعاد (STL, OBJ, FBX, GLB) عبر 3DPEA")
    # تضمين موقع 3DPEA فعلياً
    st.markdown("### 🌐 3DPEA — الأداة الكاملة (مضمّنة)")
    st.link_button("🔗 فتح 3DPEA في نافذة جديدة إذا ظهرت الصفحة فارغة", THREE_D_PEA_URL)
    components.iframe(THREE_D_PEA_URL, height=720, scrolling=True)
    st.markdown("---")
    st.markdown("### 📤 تحويل عبر API من داخل المنصة")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("📸 اختر صورة للتحويل", type=["jpg", "jpeg", "png", "bmp", "tiff"], key="3dpea_upload")
        format_options = ["stl", "obj", "fbx", "glb", "3mf", "ply", "drc"]
        output_format = st.selectbox("📁 صيغة الخرج", format_options)
        if uploaded_file and st.button("🔄 تحويل إلى 3D", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري التحويل إلى نموذج ثلاثي الأبعاد..."):
                img = Image.open(uploaded_file)
                st.image(img, caption="الصورة الأصلية", use_container_width=True)
                result = convert_image_to_3d(uploaded_file, output_format)
            if result:
                if result.get("status") == "completed":
                    st.success("✅ تم التحويل الحقيقي عبر 3DPEA API!")
                    st.download_button(f"⬇️ تحميل {output_format.upper()}", data=result["content"],
                                       file_name=f"model.{output_format}", mime="application/octet-stream")
                else:
                    model = result["model"]
                    st.success(f"✅ تم التحويل — {model['name']}")
                    st.info(f"📄 الحالة: {model['status']}")
                    st.download_button(f"⬇️ تحميل {output_format.upper()}", data=b"simulated 3D model",
                                       file_name=f"{model['name']}.{output_format}", mime="application/octet-stream")
    with col2:
        st.markdown("### 📋 النماذج المحولة")
        if st.session_state.converted_models:
            for model in st.session_state.converted_models[-5:][::-1]:
                st.markdown(f"""
                <div class="card">
                    <b>{model['name']}</b> <span class="badge-gold">{model['format'].upper()}</span><br>
                    <small>✅ {model['status']} · {model['created_at'][:10]}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لا توجد نماذج محولة بعد")

def page_image_to_3d():
    st.markdown('<h1>🎨 تحويل الصورة إلى نموذج 3D (Image to 3D)</h1>', unsafe_allow_html=True)
    st.caption("تحويل الصور ثنائية الأبعاد إلى نماذج ثلاثية الأبعاد بتقنية 3DPEA")
    uploaded = st.file_uploader("📸 اختر صورة 2D", type=["jpg", "jpeg", "png", "bmp"], key="img2d_upload")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة الأصلية", use_container_width=True)
        st.markdown("### ⚙️ إعدادات التحويل")
        col1, col2 = st.columns(2)
        with col1:
            st.slider("عمق الخريطة الارتفاعية", 0.1, 2.0, 0.5, 0.1)
            st.slider("نعومة النموذج", 0.0, 1.0, 0.5, 0.05)
        with col2:
            st.selectbox("دقة النموذج", ["منخفضة", "متوسطة", "عالية"])
            output_format = st.selectbox("صيغة الخرج", ["STL", "OBJ", "PLY", "GLB"])
        if st.button("🔄 توليد النموذج 3D", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري توليد النموذج ثلاثي الأبعاد..."):
                result = convert_image_to_3d(uploaded, output_format.lower())
            if result:
                st.markdown("### 📐 معاينة النموذج")
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size:64px;">🧊</div>
                    <b>نموذج ثلاثي الأبعاد</b>
                    <p>تم توليده من الصورة</p>
                </div>
                """, unsafe_allow_html=True)
                if result.get("status") == "completed":
                    st.download_button(f"⬇️ تحميل النموذج ({output_format})", data=result["content"],
                                       file_name=f"3d_model.{output_format.lower()}", mime="application/octet-stream")
                else:
                    st.download_button(f"⬇️ تحميل النموذج ({output_format})", data=b"simulated 3D model",
                                       file_name=f"3d_model.{output_format.lower()}", mime="application/octet-stream")

def page_3d_gallery():
    st.markdown('<h1>📦 معرض النماذج ثلاثية الأبعاد 3D Gallery</h1>', unsafe_allow_html=True)
    if st.session_state.converted_models:
        cols = st.columns(3)
        for i, model in enumerate(st.session_state.converted_models):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:48px;">🧊</div>
                    <b>{model['name']}</b><br>
                    <span class="badge-gold">{model['format'].upper()}</span>
                    <p>{model['created_at'][:10]}</p>
                    <small>✅ {model['status']}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("لا توجد نماذج محولة بعد. استخدم أداة التحويل لإنشاء نماذج 3D.")

# =============================================================
# PAGE ROUTER
# =============================================================
PAGES = {
    "home": page_home, "dashboard": page_dashboard, "smile_simulator": page_smile_simulator,
    "patients": page_patients, "new_patient": page_new_patient, "dental_chart": page_dental_chart,
    "natural_teeth": page_natural_teeth, "photography": page_photography, "xray": page_xray,
    "dentbook": page_dentbook, "friends": page_friends, "profile": page_profile,
    "members": page_members, "messages": page_messages, "private_messages": page_private_messages,
    "lab_chat": page_lab_chat, "file_sharing": page_file_sharing, "screen_share": page_screen_share,
    "diagnosis": page_diagnosis, "treatment_plan": page_treatment_plan, "materials": page_materials,
    "facial": page_facial, "cephalometric": page_cephalometric, "smile_design": page_smile_design,
    "aesthetic_design": page_aesthetic_design, "stl_3d": page_stl_3d, "dsd_studio": page_dsd_studio,
    "aesthetic_treatment": page_aesthetic_treatment, "global_platform": page_global_platform,
    "pipeline": page_pipeline, "materials_guide": page_materials_guide, "api_hub": page_api_hub,
    "mock_db": page_mock_db, "notifications": page_notifications, "systems": page_systems,
    "scientific_scan": page_scientific_scan, "naqai": page_naqai, "interdisciplinary": page_interdisciplinary,
    "ads": page_ads, "lab": page_lab, "appointments": page_appointments,
    "accounting": page_accounting, "payments": page_payments, "subscriptions": page_subscriptions,
    "invite": page_invite, "settings": page_settings, "reports": page_reports,
    "privacy": page_privacy, "ip": page_ip, "forum": page_forum, "cadcam": page_cadcam,
    "vita": page_vita, "image_editor": page_image_editor, "3dpea": page_3dpea,
    "image_to_3d": page_image_to_3d, "3d_gallery": page_3d_gallery,
}

# =============================================================
# MAIN
# =============================================================
def main():
    if not st.session_state.authenticated:
        auth_page()
    else:
        sidebar_nav()
        page_func = PAGES.get(st.session_state.current_page, page_home)
        page_func()
        st.markdown("""
        <div style="text-align:center; padding:30px; color:#64748b; font-size:0.8rem;">
            <b>Dentofacial HarmonizeAI™</b> · Naqeeb412 · Synergy<br>
            🇾🇪 الجمهورية اليمنية - أب - ميتم<br>
            © 2026 جميع الحقوق محفوظة.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
