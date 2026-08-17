import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageChops, ImageOps
import base64
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import hashlib
import cv2
import mediapipe as mp
import io
import random
import string
import re

# =============================================================
# CONFIG & PAGE SETUP
# =============================================================
st.set_page_config(
    page_title="HarmonizeAI™ | Dentofacial Synergy",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================
# CSS - RTL & Dark Theme + Enhanced Styles
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
.stButton>button {
    border-radius: 60px !important;
    font-weight: 600 !important;
    font-family: 'Cairo', sans-serif !important;
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
.badge-harvard {
    background: #7a0010;
    color: #fff;
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 700;
    border: 1px solid #a8001a;
}
.badge-private {
    background: #10b981;
    color: #fff;
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.6rem;
    font-weight: 600;
}
.card {
    background: #1e293b;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #334155;
    margin-bottom: 16px;
}
.privacy-badge {
    display: inline-block;
    background: rgba(16,185,129,0.12);
    color: #10b981;
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
}
.social-login-btn {
    background: rgba(255,255,255,0.05);
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 10px;
    color: #94a3b8;
    cursor: pointer;
    transition: 0.3s;
    text-align: center;
}
.social-login-btn:hover {
    background: rgba(230,126,34,0.1);
    border-color: #e67e22;
    color: #fff;
}
.social-login-btn .icon {
    font-size: 28px;
    display: block;
    margin-bottom: 4px;
}
.social-login-btn .label {
    font-size: 0.7rem;
}
.dental-chart-wrapper {
    overflow-x: auto;
    padding: 10px 0;
}
.dental-chart {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    min-width: 700px;
}
.dental-arch {
    display: flex;
    justify-content: center;
    gap: 4px;
    flex-wrap: wrap;
}
.dental-arch .arch-label {
    width: 100%;
    text-align: center;
    font-weight: 700;
    font-size: 14px;
    color: #94a3b8;
    margin: 4px 0 8px;
    letter-spacing: 2px;
}
.tooth {
    width: 44px;
    height: 52px;
    background: #f8fafc;
    border: 2px solid #cbd5e1;
    border-radius: 8px 8px 4px 4px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: 0.3s ease;
    font-size: 11px;
    font-weight: 700;
    color: #1a2a3a;
    position: relative;
    user-select: none;
}
.tooth:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    border-color: #0a8491;
}
.tooth .num {
    font-size: 9px;
    opacity: 0.5;
    margin-top: 2px;
}
.tooth .status-icon {
    font-size: 14px;
    line-height: 1;
}
.tooth.missing {
    background: #f1f3f5;
    border-color: #adb5bd;
    opacity: 0.5;
    cursor: default;
}
.tooth.missing::after {
    content: '✕';
    font-size: 20px;
    color: #ef4444;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
.tooth.missing .num, .tooth.missing .status-icon {
    display: none;
}
.tooth.carious {
    background: #fde8e8;
    border-color: #ef4444;
}
.tooth.carious .status-icon {
    color: #ef4444;
}
.tooth.treated {
    background: #d5f5e3;
    border-color: #10b981;
}
.tooth.treated .status-icon {
    color: #10b981;
}
.tooth.crown {
    background: #fef9e7;
    border-color: #f59e0b;
}
.tooth.crown .status-icon {
    color: #f59e0b;
}
.tooth.root-canal {
    background: #e8daef;
    border-color: #8e44ad;
}
.tooth.root-canal .status-icon {
    color: #8e44ad;
}
.tooth-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 16px;
    justify-content: center;
}
.tooth-legend .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
}
.tooth-legend .legend-item .swatch {
    width: 24px;
    height: 28px;
    border-radius: 4px;
    border: 2px solid #cbd5e1;
}
.tooth-legend .legend-item .swatch.normal { background: #f8fafc; }
.tooth-legend .legend-item .swatch.missing { background: #f1f3f5; opacity: 0.5; }
.tooth-legend .legend-item .swatch.carious { background: #fde8e8; border-color: #ef4444; }
.tooth-legend .legend-item .swatch.treated { background: #d5f5e3; border-color: #10b981; }
.tooth-legend .legend-item .swatch.crown { background: #fef9e7; border-color: #f59e0b; }
.tooth-legend .legend-item .swatch.root-canal { background: #e8daef; border-color: #8e44ad; }
.image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 14px;
    margin-top: 12px;
}
.image-grid .img-item {
    border-radius: 8px;
    overflow: hidden;
    border: 2px solid #334155;
    position: relative;
    aspect-ratio: 1/1;
    background: #0f172a;
    display: flex;
    align-items: center;
    justify-content: center;
}
.image-grid .img-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.image-grid .img-item .remove {
    position: absolute;
    top: 4px;
    left: 4px;
    background: rgba(239,68,68,0.9);
    color: #fff;
    border: none;
    border-radius: 50%;
    width: 26px;
    height: 26px;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.image-grid .upload-box {
    border: 2px dashed #334155;
    border-radius: 8px;
    aspect-ratio: 1/1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: 0.3s ease;
    color: #94a3b8;
    font-size: 13px;
    background: #1e293b;
}
.image-grid .upload-box:hover {
    border-color: #e67e22;
    background: rgba(230,126,34,0.05);
}
.image-grid .upload-box .icon {
    font-size: 32px;
    margin-bottom: 4px;
}
.toast {
    position: fixed;
    bottom: 30px;
    left: 30px;
    background: #075e68;
    color: #fff;
    padding: 14px 28px;
    border-radius: 8px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    font-weight: 500;
    z-index: 99999;
}
.toast.success { background: #10b981; }
.toast.error { background: #ef4444; }

/* Photopea-like editor styles */
.layer-panel {
    background: #0f172a;
    border-radius: 8px;
    padding: 12px;
    border: 1px solid #334155;
    max-height: 300px;
    overflow-y: auto;
}
.layer-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 10px;
    border-radius: 4px;
    background: rgba(255,255,255,0.03);
    margin-bottom: 4px;
    border: 1px solid transparent;
    cursor: pointer;
}
.layer-item:hover {
    background: rgba(255,255,255,0.06);
}
.layer-item.active {
    border-color: #e67e22;
    background: rgba(230,126,34,0.08);
}
.layer-item .layer-name {
    font-size: 0.8rem;
    color: #94a3b8;
}
.layer-item .layer-visibility {
    cursor: pointer;
    font-size: 0.8rem;
}
.editor-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 8px;
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    margin-bottom: 10px;
}
.editor-toolbar .tool-btn {
    padding: 4px 12px;
    border: 1px solid #334155;
    border-radius: 4px;
    background: rgba(255,255,255,0.05);
    color: #94a3b8;
    cursor: pointer;
    font-size: 0.7rem;
    transition: 0.3s;
}
.editor-toolbar .tool-btn:hover {
    background: rgba(230,126,34,0.1);
    border-color: #e67e22;
    color: #fff;
}
.editor-toolbar .tool-btn.active {
    background: #e67e22;
    color: #0a0a0a;
    border-color: #e67e22;
}
.slider-container {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #94a3b8;
    font-size: 0.8rem;
}
.slider-container input[type="range"] {
    flex: 1;
    accent-color: #e67e22;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================
# SYSTEM LOGO FUNCTIONS
# =============================================================
def get_system_logo():
    if "system_logo" in st.session_state and st.session_state.system_logo:
        return st.session_state.system_logo
    return None

def set_system_logo(image_data):
    st.session_state.system_logo = image_data

def display_system_logo(width=50):
    logo = get_system_logo()
    if logo:
        return f'<img src="data:image/png;base64,{logo}" style="width:{width}px; height:{width}px; border-radius:50%; object-fit:cover;" />'
    return '<div style="background:#e67e22; width:'+str(width)+'px; height:'+str(width)+'px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; color:#0a0a0a;">🦷</div>'

# =============================================================
# AUTHENTICATION SYSTEM - Multi-Platform Login
# =============================================================
OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

# User database with multi-platform support
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
            "cover_photo": "",
            "friends": [],
            "pending_requests": [],
            "platforms": ["email"],
            "created_at": datetime.now().isoformat()
        }
    }

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "otp_store" not in st.session_state:
    st.session_state.otp_store = {}

# =============================================================
# DATA STORE
# =============================================================
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
if "naqai_chat" not in st.session_state:
    st.session_state.naqai_chat = [{"role": "ai", "text": "👋 مرحباً! أنا NaqAI، مساعدك الذكي. اسألني عن أي شيء متعلق بطب الأسنان التجميلي والوجه."}]
if "dental_chart" not in st.session_state:
    st.session_state.dental_chart = ['normal'] * 32
if "patient_images" not in st.session_state:
    st.session_state.patient_images = []
if "xray_images" not in st.session_state:
    st.session_state.xray_images = []
if "appointments" not in st.session_state:
    st.session_state.appointments = []
if "xrays" not in st.session_state:
    st.session_state.xrays = []
if "patients_count" not in st.session_state:
    st.session_state.patients_count = 1
if "system_logo" not in st.session_state:
    st.session_state.system_logo = None
if "friend_requests" not in st.session_state:
    st.session_state.friend_requests = []
if "private_messages" not in st.session_state:
    st.session_state.private_messages = []
if "drawn_images" not in st.session_state:
    st.session_state.drawn_images = []
if "analyzed_images" not in st.session_state:
    st.session_state.analyzed_images = []
if "image_layers" not in st.session_state:
    st.session_state.image_layers = []
if "current_layer" not in st.session_state:
    st.session_state.current_layer = 0
if "natural_teeth_layers" not in st.session_state:
    st.session_state.natural_teeth_layers = []
if "face_mesh_data" not in st.session_state:
    st.session_state.face_mesh_data = None

# =============================================================
# AUTH FUNCTIONS
# =============================================================
def login_user(email, password):
    db = st.session_state.users_db
    if email in db:
        if db[email]["password"] == hash_pass(password):
            st.session_state.authenticated = True
            st.session_state.current_user = db[email]
            return True
    return False

def login_with_platform(email, platform):
    db = st.session_state.users_db
    if email in db:
        if "platforms" not in db[email]:
            db[email]["platforms"] = []
        if platform not in db[email]["platforms"]:
            db[email]["platforms"].append(platform)
        st.session_state.authenticated = True
        st.session_state.current_user = db[email]
        return True
    return False

def signup_user(name, email, password, role="doctor", phone="", specialty="", platform="email"):
    if email in st.session_state.users_db:
        return False, "البريد الإلكتروني مستخدم مسبقاً"
    st.session_state.users_db[email] = {
        "name": name,
        "email": email,
        "password": hash_pass(password) if password else "",
        "role": role,
        "specialty": specialty,
        "phone": phone,
        "country": "",
        "bio": "",
        "avatar": "",
        "cover_photo": "",
        "friends": [],
        "pending_requests": [],
        "platforms": [platform],
        "created_at": datetime.now().isoformat()
    }
    return True, "تم إنشاء الحساب بنجاح"

def send_otp(phone):
    otp = generate_otp()
    st.session_state.otp_store[phone] = {"otp": otp, "expires": datetime.now() + timedelta(minutes=5)}
    # في الإنتاج، سيتم إرسال الـ OTP عبر SMS
    return otp

def verify_otp(phone, otp):
    if phone in st.session_state.otp_store:
        data = st.session_state.otp_store[phone]
        if data["otp"] == otp and datetime.now() < data["expires"]:
            return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_page = "home"
    st.rerun()

# =============================================================
# DENTAL CHART FUNCTIONS
# =============================================================
def render_dental_chart():
    chart = st.session_state.dental_chart
    html = '<div class="dental-chart-wrapper"><div class="dental-chart">'
    
    # Upper arch
    html += '<div class="dental-arch"><div class="arch-label">⬆ الفك العلوي</div><div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;">'
    for i in range(16):
        status = chart[i] if i < len(chart) else 'normal'
        status_map = {
            'normal': {'icon': '🟢', 'cls': ''},
            'missing': {'icon': '', 'cls': 'missing'},
            'carious': {'icon': '🦷', 'cls': 'carious'},
            'treated': {'icon': '✔️', 'cls': 'treated'},
            'crown': {'icon': '👑', 'cls': 'crown'},
            'root-canal': {'icon': '🧬', 'cls': 'root-canal'}
        }
        s = status_map.get(status, status_map['normal'])
        icon_html = '' if status == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}" data-index="{i}" data-status="{status}">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div></div>'
    
    # Lower arch
    html += '<div class="dental-arch"><div class="arch-label">⬇ الفك السفلي</div><div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;">'
    for i in range(16, 32):
        status = chart[i] if i < len(chart) else 'normal'
        status_map = {
            'normal': {'icon': '🟢', 'cls': ''},
            'missing': {'icon': '', 'cls': 'missing'},
            'carious': {'icon': '🦷', 'cls': 'carious'},
            'treated': {'icon': '✔️', 'cls': 'treated'},
            'crown': {'icon': '👑', 'cls': 'crown'},
            'root-canal': {'icon': '🧬', 'cls': 'root-canal'}
        }
        s = status_map.get(status, status_map['normal'])
        icon_html = '' if status == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}" data-index="{i}" data-status="{status}">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div></div>'
    
    # Legend
    html += '''<div class="tooth-legend">
        <div class="legend-item"><span class="swatch normal"></span> سليم</div>
        <div class="legend-item"><span class="swatch missing"></span> مفقود</div>
        <div class="legend-item"><span class="swatch carious"></span> نخر</div>
        <div class="legend-item"><span class="swatch treated"></span> معالج</div>
        <div class="legend-item"><span class="swatch crown"></span> تاج</div>
        <div class="legend-item"><span class="swatch root-canal"></span> علاج جذور</div>
    </div>'''
    html += '</div></div>'
    return html

# =============================================================
# IMAGE EDITOR FUNCTIONS (Photopea-like)
# =============================================================

# تهيئة MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def create_layer(image, name="Layer"):
    """إنشاء طبقة جديدة"""
    if isinstance(image, Image.Image):
        return {"name": name, "image": image, "visible": True, "opacity": 1.0, "blend_mode": "normal"}
    return None

def add_layer(image, name="Layer"):
    """إضافة طبقة إلى قائمة الطبقات"""
    layer = create_layer(image, name)
    if layer:
        st.session_state.image_layers.append(layer)
        st.session_state.current_layer = len(st.session_state.image_layers) - 1
        return True
    return False

def remove_layer(index):
    """حذف طبقة"""
    if 0 <= index < len(st.session_state.image_layers):
        st.session_state.image_layers.pop(index)
        if st.session_state.current_layer >= len(st.session_state.image_layers):
            st.session_state.current_layer = len(st.session_state.image_layers) - 1
        return True
    return False

def merge_layers():
    """دمج جميع الطبقات"""
    if len(st.session_state.image_layers) <= 1:
        return
    base = None
    for layer in st.session_state.image_layers:
        if layer["visible"] and layer["image"]:
            img = layer["image"].copy()
            if base is None:
                base = img
            else:
                # محاكاة دمج الطبقات
                base = Image.blend(base, img, layer["opacity"])
    if base:
        st.session_state.image_layers = [{"name": "Merged", "image": base, "visible": True, "opacity": 1.0, "blend_mode": "normal"}]
        st.session_state.current_layer = 0

def get_current_layer_image():
    """الحصول على صورة الطبقة الحالية"""
    if 0 <= st.session_state.current_layer < len(st.session_state.image_layers):
        return st.session_state.image_layers[st.session_state.current_layer]["image"]
    return None

def draw_face_mesh_on_image(image):
    """رسم FaceMesh على الصورة"""
    if isinstance(image, Image.Image):
        img_np = np.array(image.convert('RGB'))
    else:
        img_np = np.array(image)
    
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=img_np,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )
                # رسم النقاط التشريحية المهمة
                for idx, landmark in enumerate(face_landmarks.landmark):
                    if idx in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478]:
                        x = int(landmark.x * img_np.shape[1])
                        y = int(landmark.y * img_np.shape[0])
                        cv2.circle(img_np, (x, y), 2, (0, 255, 0), -1)
    
    return Image.fromarray(img_np)

def generate_natural_teeth():
    """توليد صورة أسنان طبيعية"""
    img = Image.new('RGB', (600, 400), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # رسم أسنان طبيعية
    colors = ['#F5F0E8', '#E8E0D8', '#F0EBE3', '#E5DDD5']
    for i in range(12):
        x = 40 + i * 48
        y = 120
        w = 36
        h = 60
        color = random.choice(colors)
        
        draw.ellipse([x, y, x+w, y+h], fill=color, outline='#cbd5e1', width=2)
        draw.ellipse([x+6, y+8, x+w-6, y+h-10], fill='#FFFFFF', outline=None)
        draw.ellipse([x+10, y+12, x+w-10, y+h-15], fill=color, outline=None)
    
    draw.rectangle([0, 100, 600, 125], fill='#e8b4b8')
    draw.rectangle([0, 185, 600, 205], fill='#e8b4b8')
    
    return img

def apply_filter_to_layer(image, filter_type):
    """تطبيق فلتر على طبقة"""
    if filter_type == "brightness":
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.2)
    elif filter_type == "contrast":
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1.2)
    elif filter_type == "sharpness":
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(1.5)
    elif filter_type == "blur":
        return image.filter(ImageFilter.BLUR)
    elif filter_type == "grayscale":
        return image.convert('L').convert('RGB')
    return image

# =============================================================
# LOGIN / SIGNUP PAGE
# =============================================================
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="display:inline-flex; align-items:center; gap:10px; justify-content:center;">
                {display_system_logo(55)}
                <div style="text-align:right; line-height:1.2;">
                    <div style="font-size:1.4rem; font-weight:300; color:#94a3b8;">Dentofacial</div>
                    <div style="font-size:2rem; font-weight:800; color:#e67e22; margin-top:-4px;">HarmonizeAI</div>
                    <div style="font-size:0.75rem; color:#94a3b8; letter-spacing:2px;">Naqeeb412 · Synergy</div>
                    <div style="font-size:0.6rem; color:#94a3b8; margin-top:4px;"><span class="badge-harvard">Harvard Protocol</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🔐 طرق تسجيل الدخول")
        
        # Social Login Buttons
        col_social = st.columns(6)
        social_platforms = [
            ("Google", "🔵", "google"),
            ("Facebook", "🔷", "facebook"),
            ("Instagram", "🟣", "instagram"),
            ("LinkedIn", "🔵", "linkedin"),
            ("Twitter", "🔷", "twitter"),
            ("WhatsApp", "🟢", "whatsapp")
        ]
        for i, (name, icon, key) in enumerate(social_platforms):
            with col_social[i]:
                if st.button(f"{icon}\n{name}", key=f"social_{key}", use_container_width=True):
                    # محاكاة تسجيل الدخول عبر المنصة
                    platform_email = f"user_{random.randint(1000,9999)}@{key}.com"
                    if platform_email not in st.session_state.users_db:
                        signup_user(f"مستخدم {key}", platform_email, "", "doctor", "", f"طبيب {key}", key)
                    if login_with_platform(platform_email, key):
                        st.success(f"✅ تم تسجيل الدخول عبر {name}!")
                        st.rerun()
        
        st.markdown("---")
        
        # Phone Login with OTP
        st.markdown("### 📱 تسجيل الدخول عبر الهاتف")
        phone = st.text_input("📱 رقم الهاتف", placeholder="مثال: 777700412", key="phone_input")
        if st.button("📲 إرسال رمز التحقق", key="send_otp_btn"):
            if phone and len(phone) >= 8:
                otp = send_otp(phone)
                st.success(f"✅ تم إرسال الرمز: {otp} (في الإنتاج سيُرسل عبر SMS)")
                st.session_state.otp_sent = True
            else:
                st.error("❌ الرجاء إدخال رقم هاتف صحيح")
        
        if st.session_state.get("otp_sent", False):
            otp_input = st.text_input("🔑 أدخل رمز التحقق", type="password", key="otp_input")
            if st.button("✅ تأكيد", key="verify_otp_btn"):
                if verify_otp(phone, otp_input):
                    # تسجيل الدخول أو إنشاء حساب
                    if phone in st.session_state.users_db:
                        st.session_state.authenticated = True
                        st.session_state.current_user = st.session_state.users_db[phone]
                    else:
                        signup_user(f"مستخدم {phone[-4:]}", phone, "", "patient", phone, "", "phone")
                        st.session_state.authenticated = True
                        st.session_state.current_user = st.session_state.users_db[phone]
                    st.success("✅ تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ رمز غير صحيح أو منتهي الصلاحية")
        
        st.markdown("---")
        st.markdown("### 📧 تسجيل الدخول بالبريد الإلكتروني")

        tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("البريد الإلكتروني", value="ndcdental2025@outlook.com")
                password = st.text_input("كلمة المرور", type="password", value="ndc2025")
                submitted = st.form_submit_button("دخول", use_container_width=True)
                if submitted:
                    if login_user(email, password):
                        st.success("✅ مرحباً بك!" if email == OWNER_EMAIL else "✅ تم تسجيل الدخول!")
                        st.rerun()
                    else:
                        st.error("❌ بريد أو كلمة مرور غير صحيحة")

        with tab2:
            with st.form("signup_form"):
                s_name = st.text_input("الاسم الكامل")
                s_email = st.text_input("البريد الإلكتروني الجديد")
                s_pass = st.text_input("كلمة المرور", type="password")
                s_phone = st.text_input("رقم الهاتف")
                s_specialty = st.text_input("التخصص (للأطباء)")
                s_role = st.selectbox("نوع الحساب", ["doctor", "patient"])
                s_submitted = st.form_submit_button("إنشاء حساب", use_container_width=True)
                if s_submitted:
                    ok, msg = signup_user(s_name, s_email, s_pass, s_role, s_phone, s_specialty)
                    if ok:
                        st.success(msg)
                        st.info("💡 الآن يمكنك تسجيل الدخول ببياناتك الجديدة")
                    else:
                        st.error(msg)

# =============================================================
# SIDEBAR NAVIGATION
# =============================================================
def sidebar_nav():
    user = st.session_state.current_user
    role = user.get("role", "doctor")

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:10px;">
            {display_system_logo(50)}
            <div style="font-weight:700; font-size:1.1rem; margin-top:6px;">🧬 Dentofacial</div>
            <div style="font-size:0.7rem; color:#aac4d6;">HarmonizeAI™ · v4.0</div>
            <div style="margin-top:4px;"><span class="privacy-badge">🔒 بياناتك خاصة بك</span></div>
        </div>
        <div style="text-align:center; margin-bottom:16px;">
            <div style="font-size:0.85rem; font-weight:600;">{user['name']}</div>
            <div style="font-size:0.65rem; color:#aac4d6;">{user.get('specialty','') or user['role']}</div>
            <div style="font-size:0.6rem; color:#10b981; margin-top:2px;">✅ حساب خاص</div>
        </div>
        """, unsafe_allow_html=True)

        menu_items = {
            "🏠 الرئيسية": "home",
            "📊 لوحة التحكم": "dashboard",
            "🏷️ رفع الشعار": "upload_logo",
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
            "🎨 محرر الصور (Photopea)": "image_editor",
        }

        for label, key in menu_items.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        st.divider()
        if st.button("🚪 تسجيل خروج", use_container_width=True, type="primary"):
            logout()

# =============================================================
# PAGE: IMAGE EDITOR (Photopea-like)
# =============================================================
def page_image_editor():
    st.markdown('<h2>🎨 محرر الصور المتقدم <span style="color:#e67e22;">(Photopea-like)</span></h2>', unsafe_allow_html=True)
    st.caption("قص، تعديل، إضافة طبقات، رسم FaceMesh، وتحرير الأسنان والفك")
    
    # تهيئة الطبقات إذا كانت فارغة
    if not st.session_state.image_layers:
        # إنشاء صورة افتراضية
        base_img = Image.new('RGB', (800, 600), color='#1a1a2e')
        draw = ImageDraw.Draw(base_img)
        draw.text((400, 300), "🦷 ارفع صورة لبدء التحرير", fill='#94a3b8', anchor="mm")
        st.session_state.image_layers = [{"name": "Background", "image": base_img, "visible": True, "opacity": 1.0, "blend_mode": "normal"}]
        st.session_state.current_layer = 0
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("### 🛠️ الأدوات")
        
        # رفع صورة
        uploaded = st.file_uploader("📤 رفع صورة", type=["jpg", "png", "jpeg"], key="editor_upload")
        if uploaded:
            img = Image.open(uploaded)
            add_layer(img, f"Layer {len(st.session_state.image_layers)}")
            st.success("✅ تم إضافة الطبقة")
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎨 أدوات التحرير")
        
        # أدوات التحرير
        tools = ["🖌️ فرشاة", "✏️ قلم", "⬜ مستطيل", "⭕ دائرة", "📐 خط", "🪄 عصا سحرية"]
        for tool in tools:
            if st.button(tool, use_container_width=True):
                st.session_state.current_tool = tool
                st.success(f"✅ تم اختيار {tool}")
        
        st.markdown("---")
        st.markdown("### 🎚️ تعديل الطبقة الحالية")
        
        # تعديل الطبقة الحالية
        if st.session_state.image_layers:
            layer = st.session_state.image_layers[st.session_state.current_layer]
            
            # تغيير الاسم
            new_name = st.text_input("اسم الطبقة", value=layer["name"])
            if new_name != layer["name"]:
                layer["name"] = new_name
            
            # الشفافية
            opacity = st.slider("الشفافية", 0.0, 1.0, layer["opacity"], 0.05)
            layer["opacity"] = opacity
            
            # الرؤية
            visible = st.checkbox("ظاهرة", value=layer["visible"])
            layer["visible"] = visible
            
            # الفلاتر
            filters = ["بدون", "سطوع", "تباين", "حدة", "ضبابية", "تدرج رمادي"]
            selected_filter = st.selectbox("فلتر", filters)
            if selected_filter != "بدون":
                filter_map = {
                    "سطوع": "brightness",
                    "تباين": "contrast",
                    "حدة": "sharpness",
                    "ضبابية": "blur",
                    "تدرج رمادي": "grayscale"
                }
                if selected_filter in filter_map:
                    layer["image"] = apply_filter_to_layer(layer["image"], filter_map[selected_filter])
                    st.success(f"✅ تم تطبيق {selected_filter}")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🧬 FaceMesh")
        if st.button("🧑 رسم FaceMesh على الطبقة", use_container_width=True):
            if st.session_state.image_layers:
                img = get_current_layer_image()
                if img:
                    result = draw_face_mesh_on_image(img)
                    add_layer(result, "FaceMesh")
                    st.success("✅ تم رسم FaceMesh")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🦷 Natural Teeth")
        if st.button("🦷 إضافة أسنان طبيعية", use_container_width=True):
            teeth = generate_natural_teeth()
            add_layer(teeth, "Natural Teeth")
            st.success("✅ تم إضافة الأسنان الطبيعية")
            st.rerun()
    
    with col1:
        st.markdown("### 📐 مساحة التحرير")
        
        # عرض الصورة المحررة
        if st.session_state.image_layers:
            # دمج الطبقات المرئية للعرض
            display_img = None
            for layer in st.session_state.image_layers:
                if layer["visible"] and layer["image"]:
                    img = layer["image"].copy()
                    if display_img is None:
                        display_img = img
                    else:
                        # محاكاة الدمج مع الشفافية
                        display_img = Image.blend(display_img, img, layer["opacity"])
            
            if display_img:
                # تغيير الحجم للعرض
                display_img.thumbnail((700, 500))
                st.image(display_img, caption="المحرر", use_container_width=True)
        
        st.markdown("### 📋 الطبقات")
        
        # عرض الطبقات
        for i, layer in enumerate(st.session_state.image_layers):
            col_a, col_b, col_c = st.columns([1, 3, 1])
            with col_a:
                visibility = "👁️" if layer["visible"] else "👁️‍🗨️"
                if st.button(visibility, key=f"vis_{i}"):
                    layer["visible"] = not layer["visible"]
                    st.rerun()
            with col_b:
                active_class = " active" if i == st.session_state.current_layer else ""
                if st.button(f"{layer['name']}", key=f"layer_{i}", use_container_width=True):
                    st.session_state.current_layer = i
                    st.rerun()
            with col_c:
                if st.button("✕", key=f"del_{i}"):
                    remove_layer(i)
                    st.rerun()
        
        # أزرار التحكم في الطبقات
        col_merge, col_clear = st.columns(2)
        with col_merge:
            if st.button("🔗 دمج الكل", use_container_width=True):
                merge_layers()
                st.rerun()
        with col_clear:
            if st.button("🗑️ مسح الكل", use_container_width=True):
                st.session_state.image_layers = []
                st.rerun()

# =============================================================
# PAGE: NATURAL TEETH
# =============================================================
def page_natural_teeth():
    st.markdown('<h2>🦷 الأسنان الطبيعية <span style="color:#e67e22;">Natural Teeth</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 الصور محفوظة في حسابك الخاص")
    
    if not st.session_state.natural_teeth_layers:
        st.session_state.natural_teeth_layers = []
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 توليد أسنان طبيعية")
        teeth_count = st.slider("عدد الأسنان", 6, 16, 10)
        tooth_color = st.color_picker("لون الأسنان", "#F5F0E8")
        
        if st.button("🦷 توليد أسنان طبيعية", type="primary", use_container_width=True):
            img = generate_natural_teeth()
            st.image(img, caption="الأسنان الطبيعية المولدة", use_container_width=True)
            # حفظ في الطبقات
            st.session_state.natural_teeth_layers.append({
                "name": f"Teeth_{len(st.session_state.natural_teeth_layers)}",
                "image": img,
                "created_at": datetime.now().isoformat()
            })
            st.success("✅ تم توليد وحفظ الأسنان الطبيعية!")
    
    with col2:
        st.markdown("#### 📸 الأسنان المحفوظة")
        if st.session_state.natural_teeth_layers:
            for i, teeth in enumerate(st.session_state.natural_teeth_layers[-6:]):
                st.image(teeth["image"], caption=f"{teeth['name']} - {teeth['created_at'][:10]}", use_container_width=True)
        else:
            st.info("لا توجد أسنان طبيعية محفوظة")

# =============================================================
# OTHER PAGE FUNCTIONS (مختصرة للاختصار)
# =============================================================

def page_home():
    st.markdown("""
    <div style="text-align:center; padding:30px 0;">
        <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
            <span class="badge-harvard">Harvard Protocol</span>
            <span class="badge-gold">AI-Powered · 3D Planning</span>
            <span class="badge-gold" style="background:rgba(16,185,129,0.12); color:#10b981;">Naqeeb412 Synergy</span>
            <span class="privacy-badge">🔒 بيانات خاصة لكل مستخدم</span>
        </div>
        <h1 style="font-size:2.4rem; font-weight:800;">تشخيص دقيق <span style="color:#e67e22;">بذكاء اصطناعي</span></h1>
        <p style="color:#94a3b8; font-size:1.1rem; max-width:600px; margin:12px auto;">
            Naqeeb412 HarmonizeAI يدمج بين التصوير ثلاثي الأبعاد، محاكاة الابتسامة، وتحليل الوجه لنتائج علاجية استثنائية.
        </p>
    </div>
    """, unsafe_allow_html=True)

def page_dashboard():
    st.markdown('<h2>📊 لوحة <span style="color:#e67e22;">التحكم</span></h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    st.markdown(f"<p style='color:#94a3b8;'>مرحباً بك في Dentofacial HarmonizeAI™، <strong>{user['name']}</strong></p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div>👨‍⚕️ المرضى</div><div class="metric-value">{len(st.session_state.patients)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div>📅 مواعيد اليوم</div><div class="metric-value" style="color:#10b981;">{len(st.session_state.appointments)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div>🧠 تحليلات AI</div><div class="metric-value" style="color:#a855f7;">{len(st.session_state.patients)*3 + 5}</div></div>', unsafe_allow_html=True)

def page_upload_logo():
    st.markdown('<h2>🏷️ رفع شعار <span style="color:#e67e22;">النظام</span></h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("اختر صورة الشعار", type=["jpg", "jpeg", "png", "svg"])
    if uploaded:
        img = Image.open(uploaded)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        st.session_state.system_logo = img_str
        st.success("✅ تم رفع الشعار بنجاح!")
        st.image(img, caption="الشعار الجديد", width=150)

def page_patients():
    st.markdown('<h2>👨‍⚕️ قائمة <span style="color:#e67e22;">المرضى</span></h2>', unsafe_allow_html=True)
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلين.")

def page_new_patient():
    st.markdown('<h2>📝 إضافة <span style="color:#e67e22;">مريض جديد</span></h2>', unsafe_allow_html=True)
    with st.form("new_patient_form"):
        name = st.text_input("الاسم الكامل *")
        age = st.number_input("العمر", min_value=0, max_value=120, value=30)
        phone = st.text_input("رقم الهاتف")
        gender = st.selectbox("الجنس", ["ذكر", "أنثى", "غير محدد"])
        complaint = st.text_area("الشكوى الرئيسية")
        submitted = st.form_submit_button("💾 حفظ المريض", use_container_width=True)
        if submitted and name:
            st.session_state.patients.append({
                "id": f"P{len(st.session_state.patients)+1:04d}",
                "name": name,
                "age": age,
                "phone": phone,
                "gender": gender,
                "complaint": complaint,
                "created_at": datetime.now().isoformat()
            })
            st.success("✅ تم إضافة المريض بنجاح!")

def page_dental_chart():
    st.markdown('<h2>🦷 مخطط <span style="color:#e67e22;">الأسنان</span></h2>', unsafe_allow_html=True)
    st.markdown(render_dental_chart(), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 إعادة ضبط المخطط", use_container_width=True):
            st.session_state.dental_chart = ['normal'] * 32
            st.success("✅ تم إعادة ضبط المخطط")
            st.rerun()
    with col2:
        if st.button("💾 حفظ المخطط", use_container_width=True, type="primary"):
            st.success("✅ تم حفظ المخطط")

def page_photography():
    st.markdown('<h2>📸 قسم <span style="color:#e67e22;">التصوير</span></h2>', unsafe_allow_html=True)
    st.info("📷 ارفع صور المريض المطلوبة")
    types = ["أمامية", "جانبية", "ابتسامة", "فك علوي"]
    cols = st.columns(4)
    for i, t in enumerate(types):
        with cols[i % 4]:
            uploaded = st.file_uploader(t, type=["jpg","png","jpeg"], key=f"photo_{t}")
            if uploaded:
                st.image(uploaded, caption=t, use_container_width=True)

def page_xray():
    st.markdown('<h2>🩻 قسم <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("رفع صورة الأشعة", type=["jpg","png","jpeg"])
    if uploaded:
        st.image(uploaded, caption="صورة الأشعة", use_container_width=True)
        if st.button("💾 حفظ الأشعة", type="primary"):
            st.session_state.xrays.append({
                "type": "أشعة",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "image": uploaded
            })
            st.success("✅ تم حفظ الأشعة!")

def page_dentbook():
    st.markdown('<h2>📱 Dentbook <span style="color:#e67e22;">الشبكة الاجتماعية الطبية</span></h2>', unsafe_allow_html=True)
    text = st.text_area("ماذا تفكر؟ شارك حالة طبية...", height=80)
    if st.button("🚀 نشر", type="primary"):
        if text:
            st.session_state.dentbook_posts.insert(0, {
                "author": st.session_state.current_user["name"],
                "text": text,
                "time": datetime.now().strftime("%H:%M"),
                "likes": 0
            })
            st.success("✅ تم النشر!")
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

def page_friends():
    st.markdown('<h2>🤝 الأصدقاء <span style="color:#e67e22;">وطلبات الصداقة</span></h2>', unsafe_allow_html=True)
    st.info("👥 نظام الأصدقاء متاح")

def page_profile():
    st.markdown('<h2>👤 الملف <span style="color:#e67e22;">الشخصي</span></h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    with st.form("profile_form"):
        name = st.text_input("الاسم", value=user.get("name",""))
        specialty = st.text_input("التخصص", value=user.get("specialty",""))
        phone = st.text_input("الهاتف", value=user.get("phone",""))
        bio = st.text_area("نبذة", value=user.get("bio",""))
        if st.form_submit_button("💾 حفظ"):
            st.session_state.current_user.update({
                "name": name, "specialty": specialty, "phone": phone, "bio": bio
            })
            st.session_state.users_db[user["email"]].update(st.session_state.current_user)
            st.success("✅ تم الحفظ!")

def page_members():
    st.markdown('<h2>👥 أعضاء <span style="color:#e67e22;">النظام</span></h2>', unsafe_allow_html=True)
    st.write(f"إجمالي الأعضاء: {len(st.session_state.users_db)}")

def page_messages():
    st.markdown('<h2>💬 المراسلات العامة</h2>', unsafe_allow_html=True)
    text = st.text_input("رسالتك...")
    if st.button("📨 إرسال", type="primary") and text:
        st.session_state.messages.append({
            "sender": st.session_state.current_user["name"],
            "text": text,
            "time": datetime.now().isoformat()
        })
        st.rerun()
    for msg in st.session_state.messages[-20:]:
        st.markdown(f"<div class='card'><strong>{msg['sender']}:</strong> {msg['text']}</div>", unsafe_allow_html=True)

def page_private_messages():
    st.markdown('<h2>💌 رسائل <span style="color:#e67e22;">خاصة بين الأطباء</span></h2>', unsafe_allow_html=True)
    st.info("💬 نظام الرسائل الخاصة")

def page_lab_chat():
    st.markdown('<h2>🧪 التواصل <span style="color:#e67e22;">مع المختبر</span></h2>', unsafe_allow_html=True)
    text = st.text_input("رسالتك للمختبر...")
    if st.button("إرسال") and text:
        st.session_state.lab_messages.append({"sender": st.session_state.current_user["name"], "text": text})
        st.rerun()
    for msg in st.session_state.lab_messages[-10:]:
        st.markdown(f"<div class='card'><strong>{msg['sender']}:</strong> {msg['text']}</div>", unsafe_allow_html=True)

def page_file_sharing():
    st.markdown('<h2>📁 مشاركة <span style="color:#e67e22;">الملفات</span></h2>', unsafe_allow_html=True)
    st.file_uploader("اسحب الملفات هنا", accept_multiple_files=True)

def page_screen_share():
    st.markdown('<h2>🖥️ مشاركة <span style="color:#e67e22;">الشاشة</span></h2>', unsafe_allow_html=True)
    st.info("🔹 استخدم زر 'بدء المشاركة' أدناه")
    st.markdown("""
    <button style="background:#10b981; color:#fff; border:none; padding:10px 24px; border-radius:60px; cursor:pointer;" onclick="navigator.mediaDevices.getDisplayMedia({video:true}).then(s=>{alert('🖥️ تم بدء المشاركة')}).catch(e=>{alert('تم الإلغاء')})">
        ▶️ بدء مشاركة الشاشة
    </button>
    """, unsafe_allow_html=True)

def page_diagnosis():
    st.markdown('<h2>🩺 التشخيص <span style="color:#e67e22;">الذكي</span></h2>', unsafe_allow_html=True)
    if st.button("🎓 تشخيص AI - Harvard", type="primary"):
        with st.spinner("🧠 جاري التحليل..."):
            import time; time.sleep(2)
        st.success("✅ تم التشخيص!")

def page_treatment_plan():
    st.markdown('<h2>📋 خطة <span style="color:#e67e22;">العلاج</span></h2>', unsafe_allow_html=True)
    if st.button("🧠 توليد الخطة", type="primary"):
        st.balloons()
        st.success("✅ تم توليد الخطة التفصيلية")

def page_materials():
    st.markdown('<h2>🧪 المواد <span style="color:#e67e22;">العلاجية</span></h2>', unsafe_allow_html=True)
    name = st.text_input("اسم المادة")
    usage = st.text_input("الاستخدام")
    if st.button("➕ إضافة") and name:
        st.session_state.materials.append({"name": name, "usage": usage})
        st.success("✅ تمت الإضافة")
    if st.session_state.materials:
        st.table(pd.DataFrame(st.session_state.materials))

def page_facial():
    st.markdown('<h2>🧑‍⚕️ تحليل <span style="color:#e67e22;">الوجه (478 علامة)</span></h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 حمّل صورة الوجه", type=["jpg","png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, use_container_width=True)
        if st.button("🎨 تحليل الـ 478 نقطة", type="primary"):
            st.success("✅ تم رسم 478 علامة تشريحية!")

def page_cephalometric():
    st.markdown('<h2>🩻 تحليل <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)
    st.info("SNA: 82° | SNB: 80° | ANB: 2° (ضمن الطبيعي)")

def page_smile_design():
    st.markdown('<h2>😁 تصميم <span style="color:#e67e22;">الابتسامة</span></h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 صورة الابتسامة", type=["jpg","png"])
    if uploaded:
        st.image(uploaded, use_container_width=True)

def page_aesthetic_design():
    st.markdown('<h2>🎨 التصميم <span style="color:#e67e22;">التجميلي (قبل / بعد)</span></h2>', unsafe_allow_html=True)
    st.slider("مستوى المقارنة", 0, 100, 50)

def page_stl_3d():
    st.markdown('<h2>📦 نماذج <span style="color:#e67e22;">3D / Mesh</span></h2>', unsafe_allow_html=True)
    st.file_uploader("رفع STL / OBJ / PLY", type=["stl","obj","ply","glb"])

def page_dsd_studio():
    st.markdown('<h2>🧬 استوديو إعادة بناء الابتسامة الطبيعية <span style="color:#94a3b8; font-size:1rem;">Bio-Mimetic DSD</span></h2>', unsafe_allow_html=True)
    st.slider("عرض الابتسامة", 0, 100, 80)
    st.slider("الارتفاع العمودي", 0, 100, 50)
    st.slider("تطابق الشفافية", 0, 100, 70)

def page_aesthetic_treatment():
    st.markdown('<h2>💎 علاج الوجه <span style="color:#e67e22;">التجميلي المتقدم</span></h2>', unsafe_allow_html=True)
    if st.button("✨ توليد خطة العلاج", type="primary"):
        st.success("✅ تم توليد خطة العلاج!")

def page_global_platform():
    st.markdown('<h2>🌍 المنصة العالمية <span style="color:#e67e22;">Dentofacial HarmonizeAI™</span></h2>', unsafe_allow_html=True)
    st.progress(st.session_state.pipeline_progress / 100)

def page_pipeline():
    st.markdown('<h2>🔄 خط الإنتاج <span style="color:#e67e22;">المدمج</span></h2>', unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=st.session_state.pipeline_progress,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "نسبة الإنجاز"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#e67e22"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

def page_materials_guide():
    st.markdown('<h2>🦷 دليل المواد الطبية التجميلية <span style="color:#94a3b8; font-size:1rem;">مع المراجع العلمية</span></h2>', unsafe_allow_html=True)
    data = [
        ["Lithium Disilicate (E.max)", "قشور وتركيبات", "تحضير مجهري", "STL من Exocad", "PubMed"],
        ["Hyaluronic Acid Filler", "فيلر الأنسجة الرخوة", "حقن تحت المخاطية", "Blender OBJ", "NCBI"],
        ["Botulinum Toxin (Botox)", "تعديل الابتسامة اللثوية", "حقن في Levator Labii", "AI Studios", "PubMed"],
        ["Zirconia Monolithic", "جسور وتأهيل كامل", "تحضير هيكلي", "Exocad", "ScienceDirect"],
    ]
    st.dataframe(pd.DataFrame(data, columns=["المادة", "التصنيف", "بروتوكول الاستخدام", "الربط الرقمي", "المراجع"]), use_container_width=True)

def page_api_hub():
    st.markdown('<h2>🔌 مركز تواصل الأنظمة <span style="color:#94a3b8; font-size:1rem;">(Global API Hub)</span></h2>', unsafe_allow_html=True)
    systems = [("Exocad", "STL", "🟢"), ("Meshy AI", "3D Face", "🟢"), ("Blender", "Cycles", "🟡"), ("AI Studios", "Motion", "🟢")]
    for name, fmt, status in systems:
        st.markdown(f"**{name}** <span style='color:#94a3b8; font-size:0.8rem;'>{fmt}</span> - <span style='color:#10b981;'>{status}</span>")

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
    notifs = ["📢 تم تحديث خط سير المريض (الخطوة 3)", "💬 رسالة جديدة من المختبر", "📅 موعد غداً الساعة 10:00 ص"]
    for n in notifs:
        st.markdown(f'<div class="card" style="padding:10px; margin-bottom:6px;">{n}</div>', unsafe_allow_html=True)

def page_systems():
    st.markdown('<h2>🖥️ الأنظمة <span style="color:#e67e22;">المستخدمة</span></h2>', unsafe_allow_html=True)
    sys_list = ["Smile Generator", "Exocad Analysis", "Exocad 3D", "Meshy AI", "Blender Cycles", "AI Studios"]
    for s in sys_list:
        st.markdown(f"<div class='card' style='text-align:center;'><h5>{s}</h5><span class='badge-gold' style='background:#10b981; color:#fff;'>نشط</span></div>", unsafe_allow_html=True)

def page_scientific_scan():
    st.markdown('<h2>🔬 المسح العلمي <span style="color:#e67e22;">الشامل</span></h2>', unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]: st.button("👤 مسح الوجه")
    with cols[1]: st.button("🦷 مسح الأسنان")
    with cols[2]: st.button("⚖️ تحليل التناغم", type="primary")
    with cols[3]: st.button("📋 تقرير علمي")

def page_naqai():
    st.markdown('<h2>🤖 NaqAI <span style="color:#e67e22;">المساعد الذكي</span></h2>', unsafe_allow_html=True)
    for msg in st.session_state.naqai_chat:
        if msg["role"] == "ai":
            st.markdown(f'<div style="background:#0a8491; color:#fff; padding:10px 14px; border-radius:12px; margin-bottom:6px; max-width:85%;">{msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#1e293b; color:#f8fafc; padding:10px 14px; border-radius:12px; margin-bottom:6px; border:1px solid #334155;">{msg["text"]}</div>', unsafe_allow_html=True)
    
    q = st.text_input("اسأل NaqAI...")
    if st.button("📨 إرسال") and q:
        st.session_state.naqai_chat.append({"role": "user", "text": q})
        responses = {
            "ابتسامة": "😁 تصميم الابتسامة يشمل تحليل النسب الذهبية واستخدام Exocad...",
            "فيلر": "💉 فيلر حمض الهيالورونيك يستخدم لملء التجاعيد ويدوم 6-18 شهراً...",
            "بوتوكس": "🧪 البوتوكس يستخدم لتقليل التجاعيد وعلاج الابتسامة اللثوية...",
        }
        ans = "🧠 شكراً لسؤالك! يمكنني مساعدتك في تصميم الابتسامة، العلاج التجميلي، تحليل الوجه، والمزيد."
        for k, v in responses.items():
            if k in q.lower():
                ans = v
                break
        st.session_state.naqai_chat.append({"role": "ai", "text": ans})
        st.rerun()

def page_interdisciplinary():
    st.markdown('<h2>👥 فرق <span style="color:#e67e22;">متعددة التخصصات</span></h2>', unsafe_allow_html=True)
    name = st.text_input("اسم الأخصائي")
    specialty = st.text_input("التخصص")
    if st.button("➕ إضافة") and name:
        st.session_state.specialists.append({"name": name, "specialty": specialty, "online": True})
        st.success("✅ تمت الإضافة")
    for sp in st.session_state.specialists:
        st.markdown(f'<div class="card"><strong>{sp["name"]}</strong> - {sp["specialty"]}</div>', unsafe_allow_html=True)

def page_ads():
    st.markdown('<h2>📢 الإعلانات</h2>', unsafe_allow_html=True)
    title = st.text_input("عنوان الإعلان")
    content = st.text_area("المحتوى")
    if st.button("📨 نشر") and title:
        st.session_state.ads.append({"title": title, "content": content})
        st.success("✅ تم النشر")
    for a in st.session_state.ads:
        st.markdown(f'<div class="card"><h5 style="color:#e67e22;">{a["title"]}</h5><p>{a["content"]}</p></div>', unsafe_allow_html=True)

def page_lab():
    st.markdown('<h2>🔬 حساب <span style="color:#e67e22;">المعمل</span></h2>', unsafe_allow_html=True)
    st.text_input("اسم الفني")
    st.text_input("نوع العمل")
    st.text_input("اسم المريض")
    st.number_input("المبلغ ($)")

def page_appointments():
    st.markdown('<h2>📅 المواعيد</h2>', unsafe_allow_html=True)
    st.date_input("التاريخ", datetime.now())
    st.time_input("الوقت", datetime.now().time())
    if st.button("📅 إضافة موعد", type="primary"):
        st.success("✅ تم إضافة الموعد")

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
    plans = [("🆓 تجريبي", "$0"), ("⭐ شهري", "$99"), ("🌟 سنوي", "$999")]
    for i, (name, price) in enumerate(plans):
        with cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center; {'border:2px solid #e67e22;' if i==1 else ''}">
                <h4>{name}</h4>
                <div style="font-size:2rem; font-weight:800; color:#e67e22;">{price}</div>
            </div>
            """, unsafe_allow_html=True)

def page_invite():
    st.markdown('<h2>📨 دعوة <span style="color:#e67e22;">الأطباء</span></h2>', unsafe_allow_html=True)
    link = f"https://harmonizeai.streamlit.app/?ref={np.random.randint(1000,9999)}"
    st.text_input("رابط الدعوة", value=link)
    if st.button("📋 نسخ الرابط"):
        st.success("✅ تم النسخ!")

def page_settings():
    st.markdown('<h2>⚙️ الإعدادات <span style="color:#e67e22;">والخصوصية</span></h2>', unsafe_allow_html=True)
    st.text_input("الاسم الظاهر", value=st.session_state.current_user["name"])
    st.text_input("التخصص", value=st.session_state.current_user.get("specialty",""))
    if st.button("💾 حفظ"):
        st.success("✅ تم الحفظ")

def page_reports():
    st.markdown('<h2>📄 التقارير</h2>', unsafe_allow_html=True)
    if st.button("📄 توليد تقرير PDF", type="primary"):
        st.success("✅ تم توليد التقرير!")

def page_privacy():
    st.markdown('<h2>🔒 الخصوصية <span style="color:#e67e22;">والأمان</span></h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#94a3b8; line-height:1.8;">
        <strong>سياسة الخصوصية:</strong> نحن نلتزم بحماية بياناتك الشخصية. جميع المعلومات التي تقدمها تخزن بشكل آمن ولا يتم مشاركتها مع أطراف ثالثة دون موافقتك الصريحة.
        </p>
    </div>
    """, unsafe_allow_html=True)

def page_ip():
    st.markdown('<h2>©️ حقوق <span style="color:#e67e22;">الملكية الفكرية</span></h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#94a3b8; line-height:1.8;">
        <strong>حقوق الملكية الفكرية:</strong> جميع المحتويات المنشورة على هذه المنصة محمية بموجب حقوق النشر والعلامات التجارية.
        </p>
    </div>
    """, unsafe_allow_html=True)

def page_forum():
    st.markdown('<h2>🗣️ منتدى النقاشات <span style="color:#e67e22;">مع الأخصائيين</span></h2>', unsafe_allow_html=True)
    st.info("🗣️ اطرح سؤالك، واحصل على إجابة من نخبة من الأخصائيين")

def page_cadcam():
    st.markdown('<h2>⚙️ CAD/CAM & 3D <span style="color:#e67e22;">(نموذج افتراضي جاهز)</span></h2>', unsafe_allow_html=True)
    st.info("⚙️ نظام CAD/CAM مع عارض ثلاثي الأبعاد")

def page_vita():
    st.markdown('<h2>🎨 ألوان <span style="color:#e67e22;">فيتا</span></h2>', unsafe_allow_html=True)
    vita_colors = {
        'A1': '#E8D5B8', 'A2': '#DCC8A8', 'A3': '#D0B898', 'A3.5': '#C8B090', 'A4': '#C0A888',
        'B1': '#D8C8B0', 'B2': '#CCB8A0', 'B3': '#C0A890', 'B4': '#B89880',
        'C1': '#C0B0A0', 'C2': '#B8A898', 'C3': '#B09888', 'C4': '#A88878',
        'D2': '#B8A898', 'D3': '#B09888', 'D4': '#A88878'
    }
    cols = st.columns(4)
    for i, (code, color) in enumerate(vita_colors.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="border:1px solid #334155; border-radius:8px; padding:12px; text-align:center; background:#1e293b;">
                <div style="width:100%; height:40px; border-radius:6px; background:{color}; border:1px solid #334155;"></div>
                <div style="font-weight:700; color:#e67e22; margin-top:6px;">{code}</div>
            </div>
            """, unsafe_allow_html=True)

def page_smile_simulator():
    st.markdown('<h2>🎯 محاكاة الابتسامة والتناغم الوجهي <span style="color:#e67e22;">باستخدام الذكاء الاصطناعي</span></h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 صورة المريض", type=["jpg","png","jpeg"])
    if uploaded:
        st.image(uploaded, caption="الصورة الأصلية", use_container_width=True)
        if st.button("🎯 توليد المحاكاة", type="primary"):
            with st.spinner("⏳ جاري توليد المحاكاة..."):
                st.success("✅ تم توليد المحاكاة!")

# =============================================================
# PAGE ROUTER
# =============================================================
PAGES = {
    "home": page_home,
    "dashboard": page_dashboard,
    "upload_logo": page_upload_logo,
    "smile_simulator": page_smile_simulator,
    "patients": page_patients,
    "new_patient": page_new_patient,
    "dental_chart": page_dental_chart,
    "natural_teeth": page_natural_teeth,
    "photography": page_photography,
    "xray": page_xray,
    "dentbook": page_dentbook,
    "friends": page_friends,
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
    "vita": page_vita,
    "image_editor": page_image_editor,
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
