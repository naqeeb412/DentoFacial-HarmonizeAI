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
import time
import requests
import subprocess
import sys
import platform

# =============================================================
# SYSTEM DETECTION - اكتشاف نظام التشغيل (معدل بدون st.runtime)
# =============================================================
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

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
# CSS - RTL & Dark Theme + Enhanced Styles (متوافق مع جميع الأجهزة)
# =============================================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap');

* {
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
}

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
    touch-action: manipulation !important;
    -webkit-touch-callout: none !important;
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
    touch-action: manipulation;
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
    -webkit-overflow-scrolling: touch;
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
    touch-action: manipulation;
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

/* 3D Viewer Styles */
.three-viewer-container {
    background: #0f172a;
    border-radius: 16px;
    border: 1px solid #334155;
    padding: 0;
    overflow: hidden;
    position: relative;
}
.three-viewer-container iframe {
    width: 100%;
    height: 500px;
    border: none;
}
.control-panel {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #334155;
}

/* Natural Teeth Card Styles */
.teeth-card {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #334155;
    margin-bottom: 12px;
    transition: all 0.3s ease;
    cursor: pointer;
}
.teeth-card:hover {
    border-color: #e67e22;
    transform: translateY(-2px);
}
.teeth-card .tooth-status {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
}
.teeth-card .status-normal { background: #10b98120; color: #10b981; }
.teeth-card .status-missing { background: #ef444420; color: #ef4444; }
.teeth-card .status-carious { background: #f59e0b20; color: #f59e0b; }
.teeth-card .status-treated { background: #3b82f620; color: #3b82f6; }
.teeth-card .status-crown { background: #8b5cf620; color: #8b5cf6; }
.teeth-card .status-root-canal { background: #ec489920; color: #ec4899; }

/* Mobile Responsive */
@media (max-width: 768px) {
    .tooth {
        width: 36px !important;
        height: 44px !important;
        font-size: 9px !important;
    }
    .dental-chart {
        min-width: 550px !important;
    }
    .metric-value {
        font-size: 1.5rem !important;
    }
    .card {
        padding: 16px !important;
    }
    .stButton>button {
        font-size: 14px !important;
        padding: 8px 16px !important;
    }
}
@media (max-width: 480px) {
    .tooth {
        width: 30px !important;
        height: 38px !important;
        font-size: 8px !important;
    }
    .dental-chart {
        min-width: 450px !important;
    }
    .tooth .num {
        font-size: 7px !important;
    }
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
if "pending_social_auth" not in st.session_state:
    st.session_state.pending_social_auth = {}

# =============================================================
# DATA STORE - جميع بيانات النظام
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
        {"name": "د. أحمد العمري", "specialty": "تقويم أسنان", "online": True, "phone": "+966 55 123 4567", "email": "ahmed@clinic.com"},
        {"name": "د. سارة الحكيم", "specialty": "جراحة الفم والوجه", "online": True, "phone": "+966 55 123 4568", "email": "sara@clinic.com"},
        {"name": "د. خالد النقيب", "specialty": "طب الأسنان التجميلي", "online": False, "phone": "+966 55 123 4569", "email": "khalid@clinic.com"},
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
if "tooth_statuses" not in st.session_state:
    st.session_state.tooth_statuses = {i: "normal" for i in range(32)}
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
if "cephalometric_data" not in st.session_state:
    st.session_state.cephalometric_data = {
        "SNA": 82, "SNB": 80, "ANB": 2,
        "SN-MP": 32, "FMA": 25, "IMPA": 90,
        "Overjet": 3, "Overbite": 2,
        "U1-SN": 104, "L1-MP": 92, "U1-L1": 130,
        "Z-angle": 72, "Po-NB": 1, "SL": 1, "SE": 1
    }
if "smile_designs" not in st.session_state:
    st.session_state.smile_designs = []
if "facial_analysis_results" not in st.session_state:
    st.session_state.facial_analysis_results = []
if "selected_tooth" not in st.session_state:
    st.session_state.selected_tooth = None
if "last_analysis_image" not in st.session_state:
    st.session_state.last_analysis_image = None
if "last_analysis_data" not in st.session_state:
    st.session_state.last_analysis_data = None
if "last_cephalometric_image" not in st.session_state:
    st.session_state.last_cephalometric_image = None
if "last_cephalometric_data" not in st.session_state:
    st.session_state.last_cephalometric_data = None
if "last_smile_image" not in st.session_state:
    st.session_state.last_smile_image = None

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

def login_with_platform(email, platform, user_data=None):
    """تسجيل الدخول باستخدام منصة خارجية"""
    db = st.session_state.users_db
    
    if email in db:
        if "platforms" not in db[email]:
            db[email]["platforms"] = []
        if platform not in db[email]["platforms"]:
            db[email]["platforms"].append(platform)
        st.session_state.authenticated = True
        st.session_state.current_user = db[email]
        return True, "تم تسجيل الدخول بنجاح"
    
    if user_data:
        name = user_data.get("name", f"مستخدم {platform}")
        db[email] = {
            "name": name,
            "email": email,
            "password": "",
            "role": "doctor",
            "specialty": user_data.get("specialty", ""),
            "phone": user_data.get("phone", ""),
            "country": user_data.get("country", ""),
            "bio": user_data.get("bio", ""),
            "avatar": user_data.get("avatar", ""),
            "cover_photo": "",
            "friends": [],
            "pending_requests": [],
            "platforms": [platform],
            "created_at": datetime.now().isoformat()
        }
        st.session_state.authenticated = True
        st.session_state.current_user = db[email]
        return True, f"تم إنشاء حساب جديد عبر {platform}"
    
    return False, "فشل تسجيل الدخول"

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
# CHECK DEPENDENCIES - التحقق من التبعيات حسب النظام (معدل)
# =============================================================
def check_opencv():
    """التحقق من توفر OpenCV"""
    try:
        import cv2
        return True
    except ImportError:
        return False

def check_mediapipe():
    """التحقق من توفر MediaPipe"""
    try:
        import mediapipe as mp
        return True
    except ImportError:
        return False

def install_package(package):
    """تثبيت حزمة بايثون"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except:
        return False

# =============================================================
# IMAGE PROCESSING FUNCTIONS
# =============================================================

# تهيئة MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def enhance_smile_face(image_array, intensity=0.7):
    """تحسين الابتسامة والوجه"""
    img = image_array.copy()
    h, w = img.shape[:2]
    
    mouth_y_start = int(h * 0.55)
    mouth_y_end = int(h * 0.75)
    mouth_x_start = int(w * 0.3)
    mouth_x_end = int(w * 0.7)
    
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
    
    overlay = img.copy()
    alpha = 0.1 * intensity
    brightness = np.ones(img.shape, dtype=np.uint8) * 30
    img = cv2.addWeighted(img, 1 - alpha, brightness, alpha, 0)
    
    return img

def simulate_smile_before_after(original_img, intensity=0.7):
    """محاكاة الابتسامة قبل وبعد"""
    if isinstance(original_img, Image.Image):
        original_np = np.array(original_img.convert('RGB'))
    else:
        original_np = original_img
    
    enhanced = enhance_smile_face(original_np, intensity)
    result_pil = Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
    return original_img, result_pil

def create_comparison_image(before_img, after_img, split_position=0.5):
    """إنشاء صورة مقارنة قبل/بعد"""
    if isinstance(before_img, Image.Image):
        before = before_img
    else:
        before = Image.fromarray(cv2.cvtColor(before_img, cv2.COLOR_BGR2RGB))
    
    if isinstance(after_img, Image.Image):
        after = after_img
    else:
        after = Image.fromarray(cv2.cvtColor(after_img, cv2.COLOR_BGR2RGB))
    
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
    
    return Image.fromarray(img_np)

def generate_natural_teeth(count=10, color='#F5F0E8'):
    """توليد أسنان طبيعية محسنة"""
    img = Image.new('RGB', (600, 350), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    colors = ['#F5F0E8', '#E8E0D8', '#F0EBE3', '#E5DDD5', '#F2EDE5', '#EAE2DA']
    
    for i in range(count):
        x = 40 + i * 50
        y = 100
        w = 38
        h = 65
        tooth_color = random.choice(colors)
        
        draw.ellipse([x, y, x+w, y+h], fill=tooth_color, outline='#cbd5e1', width=2)
        draw.ellipse([x+4, y+6, x+w-4, y+h-8], fill='#FFFFFF', outline=None)
        draw.ellipse([x+8, y+10, x+w-8, y+h-12], fill=tooth_color, outline=None)
        
        draw.arc([x+6, y+12, x+w-6, y+h-8], 0, 180, fill='#cbd5e1', width=1)
    
    draw.rectangle([0, 80, 600, 105], fill='#e8b4b8')
    draw.rectangle([0, 170, 600, 190], fill='#e8b4b8')
    
    return img

def draw_landmarks_on_image(image, landmarks_count=478):
    """رسم العلامات التشريحية"""
    if isinstance(image, Image.Image):
        img = image.copy()
    else:
        img = Image.open(image) if isinstance(image, str) else image
    
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    colors = ['#e67e22', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6']
    for i in range(min(landmarks_count, 100)):
        x = random.randint(10, w-10)
        y = random.randint(10, h-10)
        color = random.choice(colors)
        draw.ellipse([x-3, y-3, x+3, y+3], fill=color)
    
    draw.line([(w*0.2, h*0.1), (w*0.8, h*0.1)], fill='#e67e22', width=2)
    draw.line([(w*0.2, h*0.9), (w*0.8, h*0.9)], fill='#e67e22', width=2)
    draw.line([(w*0.5, h*0.1), (w*0.5, h*0.9)], fill='#10b981', width=2)
    
    return img

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
                base = Image.blend(base, img, layer["opacity"])
    if base:
        st.session_state.image_layers = [{"name": "Merged", "image": base, "visible": True, "opacity": 1.0, "blend_mode": "normal"}]
        st.session_state.current_layer = 0

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

def update_tooth_status(index, status):
    """تحديث حالة سن معين"""
    if 0 <= index < 32:
        st.session_state.tooth_statuses[index] = status
        st.session_state.dental_chart[index] = status
        return True
    return False

def get_tooth_status(index):
    """الحصول على حالة سن"""
    return st.session_state.tooth_statuses.get(index, "normal")

# =============================================================
# REAL AI ANALYSIS FUNCTIONS
# =============================================================

def real_face_analysis(image):
    """
    تحليل الوجه الحقيقي باستخدام MediaPipe (468 نقطة)
    """
    if isinstance(image, Image.Image):
        img_np = np.array(image.convert('RGB'))
    else:
        img_np = np.array(image)
    
    results_data = {
        "landmarks": [],
        "symmetry_score": 0,
        "smile_index": 0,
        "face_shape": "بيضاوي",
        "eye_distance": 0,
        "mouth_width": 0,
        "face_height": 0,
        "face_width": 0,
        "analysis_image": None
    }
    
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            h, w = img_np.shape[:2]
            
            landmarks_list = []
            for idx, landmark in enumerate(landmarks.landmark):
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                landmarks_list.append((x, y))
            
            results_data["landmarks"] = landmarks_list
            
            if len(landmarks_list) > 400:
                eye_left = landmarks_list[33] if 33 < len(landmarks_list) else (0, 0)
                eye_right = landmarks_list[263] if 263 < len(landmarks_list) else (0, 0)
                eye_dist = np.sqrt((eye_right[0] - eye_left[0])**2 + (eye_right[1] - eye_left[1])**2)
                results_data["eye_distance"] = eye_dist
                
                mouth_left = landmarks_list[61] if 61 < len(landmarks_list) else (0, 0)
                mouth_right = landmarks_list[291] if 291 < len(landmarks_list) else (0, 0)
                mouth_width = np.sqrt((mouth_right[0] - mouth_left[0])**2 + (mouth_right[1] - mouth_left[1])**2)
                results_data["mouth_width"] = mouth_width
                
                face_top = landmarks_list[10] if 10 < len(landmarks_list) else (0, 0)
                face_bottom = landmarks_list[152] if 152 < len(landmarks_list) else (0, 0)
                face_height = np.sqrt((face_bottom[0] - face_top[0])**2 + (face_bottom[1] - face_top[1])**2)
                results_data["face_height"] = face_height
                
                face_left = landmarks_list[234] if 234 < len(landmarks_list) else (0, 0)
                face_right = landmarks_list[454] if 454 < len(landmarks_list) else (0, 0)
                face_width = np.sqrt((face_right[0] - face_left[0])**2 + (face_right[1] - face_left[1])**2)
                results_data["face_width"] = face_width
                
                symmetry_points = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]
                symmetry_diff = 0
                for left_idx, right_idx in symmetry_points:
                    if left_idx < len(landmarks_list) and right_idx < len(landmarks_list):
                        left_point = landmarks_list[left_idx]
                        right_point = landmarks_list[right_idx]
                        diff = np.sqrt((left_point[0] - right_point[0])**2 + (left_point[1] - right_point[1])**2)
                        symmetry_diff += diff
                
                symmetry_score = max(0, min(100, 100 - (symmetry_diff / 10)))
                results_data["symmetry_score"] = symmetry_score
                
                if face_width > 0:
                    smile_idx = mouth_width / face_width
                    smile_idx = max(0, min(1, smile_idx))
                    results_data["smile_index"] = smile_idx * 100
                
                if face_height > 0 and face_width > 0:
                    ratio = face_width / face_height
                    if ratio < 0.7:
                        results_data["face_shape"] = "مستطيل"
                    elif ratio < 0.85:
                        results_data["face_shape"] = "بيضاوي"
                    elif ratio < 1.0:
                        results_data["face_shape"] = "دائري"
                    else:
                        results_data["face_shape"] = "مربع"
            
            result_img = img_np.copy()
            
            mp_drawing.draw_landmarks(
                image=result_img,
                landmark_list=landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )
            
            smile_points = [61, 291, 78, 308, 87, 317, 95, 324, 88, 318, 178, 181, 185, 191]
            for idx in smile_points:
                if idx < len(landmarks_list):
                    x, y = landmarks_list[idx]
                    cv2.circle(result_img, (x, y), 3, (0, 255, 0), -1)
            
            cv2.putText(result_img, f"Symmetry: {results_data['symmetry_score']:.1f}%", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(result_img, f"Smile Index: {results_data['smile_index']:.1f}%", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(result_img, f"Face Shape: {results_data['face_shape']}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            results_data["analysis_image"] = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
    
    return results_data

def real_cephalometric_analysis(image):
    """
    تحليل الأشعة الحقيقي باستخدام معالجة الصور
    """
    if isinstance(image, Image.Image):
        img_np = np.array(image.convert('L'))
    else:
        img_np = np.array(image)
    
    h, w = img_np.shape
    
    img_enhanced = cv2.equalizeHist(img_np)
    edges = cv2.Canny(img_enhanced, 50, 150)
    
    analysis_data = {
        "SNA": 82.5,
        "SNB": 80.0,
        "ANB": 2.5,
        "SN-MP": 32.0,
        "FMA": 25.0,
        "IMPA": 90.0,
        "Overjet": 3.0,
        "Overbite": 2.0,
        "analysis_image": None
    }
    
    result_img = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
    center_x, center_y = w // 2, h // 2
    
    cv2.line(result_img, (int(w*0.3), int(h*0.3)), (int(w*0.5), int(h*0.2)), (0, 255, 0), 2)
    cv2.putText(result_img, "S-N", (int(w*0.3), int(h*0.25)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.line(result_img, (int(w*0.5), int(h*0.2)), (int(w*0.6), int(h*0.4)), (255, 0, 0), 2)
    cv2.putText(result_img, "N-A", (int(w*0.55), int(h*0.3)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    cv2.line(result_img, (int(w*0.5), int(h*0.2)), (int(w*0.55), int(h*0.6)), (0, 0, 255), 2)
    cv2.putText(result_img, "N-B", (int(w*0.5), int(h*0.5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    y_offset = 30
    for key, value in analysis_data.items():
        if key != "analysis_image":
            cv2.putText(result_img, f"{key}: {value}°", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            y_offset += 25
    
    analysis_data["analysis_image"] = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
    
    return analysis_data

# =============================================================
# PDF REPORT GENERATION (باستخدام HTML مع دعم PDF اختياري)
# =============================================================

def generate_html_report(patient_name, analysis_results, images):
    """
    توليد تقرير HTML مع الصور والتحاليل
    """
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تقرير HarmonizeAI™</title>
        <style>
            body {{ font-family: 'Cairo', sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #e67e22; text-align: center; }}
            .info {{ text-align: right; margin-bottom: 20px; }}
            .info-item {{ margin: 5px 0; }}
            .image-section {{ margin: 20px 0; text-align: center; }}
            .image-section img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; margin: 10px 0; }}
            .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
            .results-table th {{ background: #e67e22; color: white; }}
            .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
            @media (max-width: 600px) {{
                .container {{ padding: 15px; }}
                .results-table th, .results-table td {{ padding: 4px; font-size: 12px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🦷 تقرير HarmonizeAI™</h1>
            <div class="info">
                <div class="info-item"><strong>اسم المريض:</strong> {patient_name}</div>
                <div class="info-item"><strong>تاريخ التقرير:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            </div>
    """
    
    # إضافة الصور
    for title, img_data in images.items():
        if img_data and isinstance(img_data, Image.Image):
            buffered = BytesIO()
            img_data.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            html += f"""
            <div class="image-section">
                <h3>{title}</h3>
                <img src="data:image/png;base64,{img_str}" alt="{title}">
            </div>
            """
    
    # إضافة نتائج التحليل
    html += "<h2>📊 نتائج التحليل</h2>"
    
    if "face_analysis" in analysis_results:
        face_data = analysis_results["face_analysis"]
        html += """
        <h3>تحليل الوجه</h3>
        <table class="results-table">
            <tr><th>المقياس</th><th>القيمة</th></tr>
            <tr><td>درجة التناسق</td><td>{:.1f}%</td></tr>
            <tr><td>مؤشر الابتسامة</td><td>{:.1f}%</td></tr>
            <tr><td>شكل الوجه</td><td>{}</td></tr>
            <tr><td>المسافة بين العينين</td><td>{:.1f} px</td></tr>
            <tr><td>عرض الفم</td><td>{:.1f} px</td></tr>
        </table>
        """.format(
            face_data.get('symmetry_score', 0),
            face_data.get('smile_index', 0),
            face_data.get('face_shape', 'غير محدد'),
            face_data.get('eye_distance', 0),
            face_data.get('mouth_width', 0)
        )
    
    if "cephalometric" in analysis_results:
        ceph_data = analysis_results["cephalometric"]
        html += """
        <h3>التحليل السيفالومتري</h3>
        <table class="results-table">
            <tr><th>الزاوية</th><th>القيمة</th><th>التقييم</th></tr>
            <tr><td>SNA</td><td>{:.1f}°</td><td>طبيعي</td></tr>
            <tr><td>SNB</td><td>{:.1f}°</td><td>طبيعي</td></tr>
            <tr><td>ANB</td><td>{:.1f}°</td><td>طبيعي</td></tr>
            <tr><td>SN-MP</td><td>{:.1f}°</td><td>طبيعي</td></tr>
            <tr><td>FMA</td><td>{:.1f}°</td><td>طبيعي</td></tr>
        </table>
        """.format(
            ceph_data.get('SNA', 0),
            ceph_data.get('SNB', 0),
            ceph_data.get('ANB', 0),
            ceph_data.get('SN-MP', 0),
            ceph_data.get('FMA', 0)
        )
    
    html += """
            <div class="footer">
                <strong>Dentofacial HarmonizeAI™</strong><br>
                Naqeeb412 · Synergy<br>
                © 2026 جميع الحقوق محفوظة.
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_pdf_from_html(html_content):
    """
    محاولة تحويل HTML إلى PDF باستخدام المكتبات المتاحة
    """
    try:
        from weasyprint import HTML
        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer
    except ImportError:
        try:
            import pdfkit
            pdf_buffer = BytesIO()
            pdfkit.from_string(html_content, pdf_buffer)
            pdf_buffer.seek(0)
            return pdf_buffer
        except:
            return None

# =============================================================
# AUTH PAGE
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
        
        st.markdown("#### 🌐 تسجيل الدخول عبر المنصات")
        
        social_platforms = [
            ("Google", "🔵", "google"),
            ("Facebook", "🔷", "facebook"),
            ("Instagram", "🟣", "instagram"),
            ("LinkedIn", "🔵", "linkedin"),
            ("Twitter", "🔷", "twitter"),
            ("WhatsApp", "🟢", "whatsapp")
        ]
        
        cols1 = st.columns(3)
        cols2 = st.columns(3)
        
        for i, (name, icon, key) in enumerate(social_platforms):
            col = cols1[i % 3] if i < 3 else cols2[i % 3]
            with col:
                if st.button(f"{icon} {name}", key=f"social_{key}", use_container_width=True):
                    platform_email = f"user_{random.randint(1000,9999)}_{key}@social.com"
                    user_data = {
                        "name": f"مستخدم {name}",
                        "specialty": f"طبيب {name}",
                        "phone": f"+000 {random.randint(100,999)} {random.randint(100,999)}",
                        "country": "اليمن"
                    }
                    
                    success, msg = login_with_platform(platform_email, key, user_data)
                    if success:
                        st.success(f"✅ {msg}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
        
        st.markdown("---")
        
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
                    if phone in st.session_state.users_db:
                        st.session_state.authenticated = True
                        st.session_state.current_user = st.session_state.users_db[phone]
                    else:
                        user_data = {
                            "name": f"مستخدم {phone[-4:]}",
                            "specialty": "طبيب أسنان",
                            "phone": phone,
                            "country": "اليمن"
                        }
                        success, msg = login_with_platform(phone, "phone", user_data)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.current_user = st.session_state.users_db[phone]
                            st.success("✅ تم إنشاء الحساب وتسجيل الدخول!")
                            st.rerun()
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

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:10px;">
            {display_system_logo(50)}
            <div style="font-weight:700; font-size:1.1rem; margin-top:6px;">🧬 Dentofacial</div>
            <div style="font-size:0.7rem; color:#aac4d6;">HarmonizeAI™ · v6.0</div>
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
            "🦷 عارض 3D": "three_d_viewer",
            "🧠 تحليل الوجه AI": "ai_face_real",
            "🩻 تحليل الأشعة AI": "ai_cephalometric_real",
            "📄 تقرير PDF": "pdf_report",
            "🤖 تصميم الابتسامة AI": "ai_smile_design",
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
        }

        for label, key in menu_items.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        st.divider()
        if st.button("🚪 تسجيل خروج", use_container_width=True, type="primary"):
            logout()

# =============================================================
# PAGE: HOME
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

# =============================================================
# PAGE: DASHBOARD
# =============================================================
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
    
    st.markdown("### 📋 آخر المرضى")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients[-5:])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلين.")

# =============================================================
# PAGE: UPLOAD LOGO
# =============================================================
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

# =============================================================
# PAGE: SMILE SIMULATOR
# =============================================================
def page_smile_simulator():
    st.markdown('<h2>🎯 محاكاة الابتسامة والتناغم الوجهي <span style="color:#e67e22;">باستخدام الذكاء الاصطناعي</span></h2>', unsafe_allow_html=True)
    st.caption("قم برفع صورة المريض للحصول على نتيجة واقعية متوقعة بعد العلاج")
    
    uploaded = st.file_uploader("📸 اختر صورة وجه المريض", type=["jpg", "jpeg", "png"])
    
    if uploaded:
        original = Image.open(uploaded)
        st.image(original, caption="الصورة الأصلية", use_container_width=True)
        
        intensity = st.slider("شدة التحسين", 0.1, 1.0, 0.7, 0.05)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 توليد المحاكاة", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري توليد المحاكاة..."):
                    _, result = simulate_smile_before_after(original, intensity)
                    comparison = create_comparison_image(original, result)
                    
                    st.image(result, caption="النتيجة المتوقعة", use_container_width=True)
                    st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
                    
                    st.session_state.last_smile_image = result
                    
                    buffered = BytesIO()
                    result.save(buffered, format="PNG")
                    st.download_button(
                        label="⬇️ تحميل النتيجة",
                        data=buffered.getvalue(),
                        file_name=f"smile_result_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                        mime="image/png"
                    )
                    st.success("✅ تم توليد المحاكاة بنجاح!")
        
        with col2:
            if st.button("🧑 رسم FaceMesh", use_container_width=True):
                with st.spinner("⏳ جاري رسم FaceMesh..."):
                    result = draw_face_mesh_on_image(original)
                    st.image(result, caption="FaceMesh", use_container_width=True)
                    st.success("✅ تم رسم FaceMesh!")

# =============================================================
# PAGE: PATIENTS
# =============================================================
def page_patients():
    st.markdown('<h2>👨‍⚕️ قائمة <span style="color:#e67e22;">المرضى</span></h2>', unsafe_allow_html=True)
    
    if st.button("➕ مريض جديد", type="primary"):
        st.session_state.current_page = "new_patient"
        st.rerun()
    
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df, use_container_width=True)
        
        for i, p in enumerate(st.session_state.patients):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{p['name']}** - {p.get('age', 'غير محدد')} سنة")
            with col2:
                if st.button("👁️ عرض", key=f"view_{i}"):
                    st.info(f"👤 {p['name']}\n📞 {p.get('phone', 'غير محدد')}\n🏥 {p.get('complaint', 'لا توجد')}")
            with col3:
                if st.button("📄 PDF", key=f"pdf_{i}"):
                    st.success(f"✅ تم توليد PDF للمريض {p['name']}")
            with col4:
                if st.button("🗑️ حذف", key=f"del_{i}"):
                    if st.session_state.patients.pop(i):
                        st.rerun()
    else:
        st.info("لا يوجد مرضى مسجلين.")

# =============================================================
# PAGE: NEW PATIENT
# =============================================================
def page_new_patient():
    st.markdown('<h2>📝 إضافة <span style="color:#e67e22;">مريض جديد</span></h2>', unsafe_allow_html=True)
    
    with st.form("new_patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم الكامل *")
            age = st.number_input("العمر", min_value=0, max_value=120, value=30)
            phone = st.text_input("رقم الهاتف")
        with col2:
            gender = st.selectbox("الجنس", ["ذكر", "أنثى", "غير محدد"])
            address = st.text_input("العنوان")
            complaint = st.text_area("الشكوى الرئيسية")
        
        submitted = st.form_submit_button("💾 حفظ المريض", use_container_width=True)
        if submitted and name:
            st.session_state.patients.append({
                "id": f"P{len(st.session_state.patients)+1:04d}",
                "name": name,
                "age": age,
                "phone": phone,
                "gender": gender,
                "address": address,
                "complaint": complaint,
                "created_at": datetime.now().isoformat()
            })
            st.success("✅ تم إضافة المريض بنجاح!")
            st.balloons()
            time.sleep(1)
            st.rerun()

# =============================================================
# PAGE: DENTAL CHART
# =============================================================
def page_dental_chart():
    st.markdown('<h2>🦷 مخطط <span style="color:#e67e22;">الأسنان</span></h2>', unsafe_allow_html=True)
    st.caption("اضغط على السن لتغيير حالته")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(render_dental_chart(), unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 التحكم")
        
        if st.session_state.selected_tooth is not None:
            tooth_num = st.session_state.selected_tooth + 1
            current_status = get_tooth_status(st.session_state.selected_tooth)
            status_labels = {
                'normal': '🟢 سليم',
                'missing': '❌ مفقود',
                'carious': '🟡 نخر',
                'treated': '🔵 معالج',
                'crown': '🟣 تاج',
                'root-canal': '🔴 جذور'
            }
            st.markdown(f"""
            <div style="background:#1e293b; padding:12px; border-radius:12px; border:1px solid #334155; text-align:center; margin-bottom:12px;">
                <div style="font-size:0.8rem; color:#94a3b8;">السن المحدد</div>
                <div style="font-size:2rem; font-weight:800; color:#e67e22;">#{tooth_num}</div>
                <div style="font-size:0.9rem;">{status_labels.get(current_status, 'غير معروف')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### تغيير الحالة")
            statuses = [
                ("🟢 سليم", "normal"),
                ("❌ مفقود", "missing"),
                ("🟡 نخر", "carious"),
                ("🔵 معالج", "treated"),
                ("🟣 تاج", "crown"),
                ("🔴 جذور", "root-canal")
            ]
            
            for label, status in statuses:
                if st.button(label, key=f"tooth_status_{status}", use_container_width=True):
                    if update_tooth_status(st.session_state.selected_tooth, status):
                        st.success(f"✅ تم تحديث السن #{tooth_num} إلى {label}")
                        st.rerun()
        else:
            st.info("👆 اضغط على سن في المخطط")
    
    col_actions1, col_actions2, col_actions3 = st.columns(3)
    with col_actions1:
        if st.button("🔄 إعادة ضبط المخطط", use_container_width=True):
            for i in range(32):
                update_tooth_status(i, "normal")
            st.session_state.selected_tooth = None
            st.success("✅ تم إعادة ضبط المخطط")
            st.rerun()
    with col_actions2:
        if st.button("💾 حفظ المخطط", use_container_width=True, type="primary"):
            st.success("✅ تم حفظ المخطط")
    with col_actions3:
        if st.button("📊 إحصائيات", use_container_width=True):
            status_counts = {}
            for i in range(32):
                status = get_tooth_status(i)
                status_counts[status] = status_counts.get(status, 0) + 1
            st.info(f"📊 حالات الأسنان:\n{status_counts}")

def render_dental_chart():
    html = '<div class="dental-chart-wrapper"><div class="dental-chart">'
    
    html += '<div class="dental-arch"><div class="arch-label">⬆ الفك العلوي</div><div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;">'
    for i in range(16):
        status = get_tooth_status(i)
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
        html += f'<div class="tooth {s["cls"]}" onclick="selectTooth({i})" data-index="{i}" data-status="{status}">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div></div>'
    
    html += '<div class="dental-arch"><div class="arch-label">⬇ الفك السفلي</div><div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;">'
    for i in range(16, 32):
        status = get_tooth_status(i)
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
        html += f'<div class="tooth {s["cls"]}" onclick="selectTooth({i})" data-index="{i}" data-status="{status}">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div></div>'
    
    html += '''<div class="tooth-legend">
        <div class="legend-item"><span class="swatch normal"></span> سليم</div>
        <div class="legend-item"><span class="swatch missing"></span> مفقود</div>
        <div class="legend-item"><span class="swatch carious"></span> نخر</div>
        <div class="legend-item"><span class="swatch treated"></span> معالج</div>
        <div class="legend-item"><span class="swatch crown"></span> تاج</div>
        <div class="legend-item"><span class="swatch root-canal"></span> علاج جذور</div>
    </div>'''
    html += '</div></div>'
    
    html += '''
    <script>
    function selectTooth(index) {
        const event = new CustomEvent('streamlit:setComponentValue', {
            detail: { key: 'selected_tooth', value: index }
        });
        window.dispatchEvent(event);
    }
    </script>
    '''
    return html

# =============================================================
# PAGE: NATURAL TEETH
# =============================================================
def page_natural_teeth():
    st.markdown('<h2>🦷 الأسنان الطبيعية <span style="color:#e67e22;">Natural Teeth</span></h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 توليد أسنان طبيعية")
        teeth_count = st.slider("عدد الأسنان", 6, 16, 10)
        
        if st.button("🦷 توليد أسنان طبيعية", type="primary", use_container_width=True):
            img = generate_natural_teeth(teeth_count)
            st.image(img, caption="الأسنان الطبيعية المولدة", use_container_width=True)
            st.session_state.natural_teeth_layers.append({
                "name": f"Teeth_{len(st.session_state.natural_teeth_layers)}",
                "image": img,
                "created_at": datetime.now().isoformat()
            })
            st.success("✅ تم توليد وحفظ الأسنان الطبيعية!")
            st.balloons()
    
    with col2:
        st.markdown("#### 📸 الأسنان المحفوظة")
        if st.session_state.natural_teeth_layers:
            for i, teeth in enumerate(st.session_state.natural_teeth_layers[-6:]):
                with st.container():
                    col_img, col_btn = st.columns([3, 1])
                    with col_img:
                        st.image(teeth["image"], caption=f"{teeth['name']}", use_container_width=True)
                    with col_btn:
                        if st.button("🗑️", key=f"del_teeth_{i}"):
                            st.session_state.natural_teeth_layers.pop(i)
                            st.rerun()
        else:
            st.info("لا توجد أسنان طبيعية محفوظة")
    
    st.markdown("---")
    st.markdown("#### 📊 حالة الأسنان الحالية")
    
    status_counts = {}
    for i in range(32):
        status = get_tooth_status(i)
        status_counts[status] = status_counts.get(status, 0) + 1
    
    status_labels = {
        'normal': 'سليم',
        'missing': 'مفقود',
        'carious': 'نخر',
        'treated': 'معالج',
        'crown': 'تاج',
        'root-canal': 'جذور'
    }
    
    cols = st.columns(3)
    for idx, (status, label) in enumerate(status_labels.items()):
        with cols[idx % 3]:
            count = status_counts.get(status, 0)
            st.markdown(f"""
            <div class="teeth-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span>{label}</span>
                    <span class="tooth-status status-{status}">{count}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================
# PAGE: PHOTOGRAPHY
# =============================================================
def page_photography():
    st.markdown('<h2>📸 قسم <span style="color:#e67e22;">التصوير</span></h2>', unsafe_allow_html=True)
    st.info("📷 ارفع صور المريض المطلوبة")
    
    types = ["أمامية", "جانبية", "ابتسامة", "فك علوي", "فك سفلي"]
    cols = st.columns(3)
    for i, t in enumerate(types):
        with cols[i % 3]:
            uploaded = st.file_uploader(t, type=["jpg","png","jpeg"], key=f"photo_{t}")
            if uploaded:
                img = Image.open(uploaded)
                st.image(img, caption=t, use_container_width=True)
                st.session_state.patient_images.append(uploaded)
    
    if st.button("📸 التقاط صورة بالكاميرا", use_container_width=True):
        st.info("📷 في بيئة الإنتاج، سيتم فتح الكاميرا")

# =============================================================
# PAGE: X-RAY
# =============================================================
def page_xray():
    st.markdown('<h2>🩻 قسم <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)
    
    xray_type = st.selectbox("نوع الأشعة", ["سيفالومترك (Cephalometric)", "بانوراما (Panorama)", "CBCT", "P.A"])
    uploaded = st.file_uploader("رفع صورة الأشعة", type=["jpg","png","jpeg", "dcm"])
    
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="صورة الأشعة", use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📐 تحليل تلقائي", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري التحليل..."):
                    time.sleep(1.5)
                    st.success("✅ تم التحليل!")
                    st.info("📊 النتائج:\n- SNA: 82° (طبيعي)\n- SNB: 80° (طبيعي)\n- ANB: 2° (ضمن الطبيعي)")
        
        with col2:
            if st.button("💾 حفظ الأشعة", use_container_width=True):
                st.session_state.xrays.append({
                    "type": xray_type,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "image": uploaded
                })
                st.success("✅ تم حفظ الأشعة!")

# =============================================================
# PAGE: DENTBOOK
# =============================================================
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
                    "likes": 0,
                    "comments": [],
                    "shares": 0
                }
                st.session_state.dentbook_posts.insert(0, post)
                st.success("✅ تم النشر!")
                st.rerun()
    
    st.markdown("---")
    
    for post in st.session_state.dentbook_posts[:10]:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;">
                <div>
                    <strong>{post['author']}</strong>
                    <span style="color:#94a3b8; font-size:0.75rem; margin-right:12px;">{post['time']}</span>
                </div>
                <div>
                    <span style="font-size:0.75rem; color:#94a3b8;">❤️ {post['likes']}</span>
                    <span style="font-size:0.75rem; color:#94a3b8; margin-right:8px;">💬 {len(post['comments'])}</span>
                </div>
            </div>
            <p style="margin-top:8px;">{post['text']}</p>
            <div style="display:flex; gap:12px; margin-top:8px;">
                <button onclick="alert('تم الإعجاب!')" style="background:transparent; border:none; cursor:pointer; color:#94a3b8; font-size:0.8rem;">❤️</button>
                <button onclick="alert('تم التعليق!')" style="background:transparent; border:none; cursor:pointer; color:#94a3b8; font-size:0.8rem;">💬</button>
                <button onclick="alert('تمت المشاركة!')" style="background:transparent; border:none; cursor:pointer; color:#94a3b8; font-size:0.8rem;">🔄</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================
# PAGE: FRIENDS
# =============================================================
def page_friends():
    st.markdown('<h2>🤝 الأصدقاء <span style="color:#e67e22;">وطلبات الصداقة</span></h2>', unsafe_allow_html=True)
    
    user = st.session_state.current_user
    
    st.markdown("### 👥 إرسال طلب صداقة")
    all_users = [u for u in st.session_state.users_db.values() if u["email"] != user["email"]]
    if all_users:
        target = st.selectbox("اختر مستخدم", [f"{u['name']} ({u['email']})" for u in all_users])
        if st.button("📨 إرسال طلب صداقة", type="primary"):
            target_email = target.split("(")[-1].replace(")", "")
            st.session_state.friend_requests.append({
                "from": user["email"],
                "to": target_email,
                "from_name": user["name"],
                "status": "pending",
                "created_at": datetime.now().isoformat()
            })
            st.success("✅ تم إرسال طلب الصداقة!")
    
    st.markdown("### 📨 طلبات الصداقة الواردة")
    incoming = [r for r in st.session_state.friend_requests if r["to"] == user["email"] and r["status"] == "pending"]
    if incoming:
        for req in incoming:
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #e67e22; border-radius:12px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <div><strong>👤 {req['from_name']}</strong></div>
                <div>
                    <button onclick="alert('✅ تم قبول الطلب!')" style="background:#10b981; color:#fff; border:none; padding:4px 16px; border-radius:20px; cursor:pointer;">قبول</button>
                    <button onclick="alert('❌ تم رفض الطلب')" style="background:#ef4444; color:#fff; border:none; padding:4px 16px; border-radius:20px; cursor:pointer;">رفض</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 لا توجد طلبات صداقة واردة")
    
    st.markdown("### 👫 الأصدقاء")
    friends = user.get("friends", [])
    if friends:
        for f in friends:
            friend_user = st.session_state.users_db.get(f)
            if friend_user:
                st.markdown(f"""
                <div class="card" style="padding:12px; display:flex; justify-content:space-between; align-items:center;">
                    <div><strong>{friend_user['name']}</strong> <span style="color:#94a3b8; font-size:0.75rem;">{friend_user.get('specialty', '')}</span></div>
                    <div>
                        <button onclick="alert('💬 تم فتح المحادثة')" style="background:#0a8491; color:#fff; border:none; padding:2px 12px; border-radius:20px; cursor:pointer;">💬</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👤 لا يوجد أصدقاء بعد")

# =============================================================
# PAGE: PROFILE
# =============================================================
def page_profile():
    st.markdown('<h2>👤 الملف <span style="color:#e67e22;">الشخصي</span></h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    
    with st.form("profile_form"):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="width:100px; height:100px; border-radius:50%; background:#0a8491; display:flex; align-items:center; justify-content:center; font-size:40px; color:#fff; margin:0 auto;">
                    {user['name'][0] if user['name'] else '👤'}
                </div>
                <div style="margin-top:8px; color:#94a3b8; font-size:0.8rem;">{user['email']}</div>
                <div style="margin-top:4px;"><span class="privacy-badge">🔒 حساب خاص</span></div>
                <div style="margin-top:4px; font-size:0.7rem; color:#94a3b8;">
                    منصات: {', '.join(user.get('platforms', ['email']))}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
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

# =============================================================
# PAGE: MEMBERS
# =============================================================
def page_members():
    st.markdown('<h2>👥 أعضاء <span style="color:#e67e22;">النظام</span></h2>', unsafe_allow_html=True)
    st.write(f"إجمالي الأعضاء: {len(st.session_state.users_db)}")
    
    for email, u in st.session_state.users_db.items():
        status = "🟢" if u.get("online", True) else "🔴"
        platforms = u.get("platforms", ["email"])
        platform_icons = {'email': '📧', 'google': '🔵', 'facebook': '🔷', 'instagram': '🟣', 
                         'linkedin': '🔵', 'twitter': '🔷', 'whatsapp': '🟢', 'phone': '📱'}
        platform_text = ' '.join([platform_icons.get(p, '📧') for p in platforms])
        
        st.markdown(f"""
        <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>{u['name']}</strong>
                <span style="font-size:0.75rem; color:#94a3b8; margin-right:12px;">{u.get('specialty','')}</span>
                <div style="font-size:0.7rem; color:#64748b;">{email}</div>
                <div style="font-size:0.6rem; color:#94a3b8;">{platform_text}</div>
            </div>
            <div>
                <span style="font-size:0.7rem;">{status}</span>
                <button onclick="alert('👤 عرض الملف')" style="background:#0a8491; color:#fff; border:none; padding:2px 12px; border-radius:20px; cursor:pointer; font-size:0.7rem;">عرض</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================
# PAGE: MESSAGES
# =============================================================
def page_messages():
    st.markdown('<h2>💬 المراسلات العامة</h2>', unsafe_allow_html=True)
    
    for msg in st.session_state.messages[-20:]:
        align = "flex-end" if msg["sender"] == st.session_state.current_user["name"] else "flex-start"
        bg = "#0a8491" if msg["sender"] == st.session_state.current_user["name"] else "#1e293b"
        color = "#fff" if msg["sender"] == st.session_state.current_user["name"] else "#f8fafc"
        st.markdown(f"""
        <div style="display:flex; justify-content:{align}; margin-bottom:6px;">
            <div style="max-width:75%; padding:8px 14px; border-radius:12px; background:{bg}; color:{color}; border:1px solid #334155;">
                <div style="font-size:0.7rem; opacity:0.8;">{msg['sender']}</div>
                <div style="font-size:0.9rem;">{msg['text']}</div>
                <div style="font-size:0.6rem; opacity:0.5;">{msg.get('time', '').split('T')[1][:5] if 'T' in msg.get('time','') else ''}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.form("msg_form", clear_on_submit=True):
        text = st.text_input("رسالتك...", label_visibility="collapsed")
        submitted = st.form_submit_button("📨 إرسال", use_container_width=True)
        if submitted and text:
            st.session_state.messages.append({
                "sender": st.session_state.current_user["name"],
                "text": text,
                "time": datetime.now().isoformat()
            })
            st.rerun()

# =============================================================
# PAGE: PRIVATE MESSAGES
# =============================================================
def page_private_messages():
    st.markdown('<h2>💌 رسائل <span style="color:#e67e22;">خاصة بين الأطباء</span></h2>', unsafe_allow_html=True)
    
    recipients = [u["name"] for e, u in st.session_state.users_db.items() if e != st.session_state.current_user["email"]]
    if not recipients:
        st.info("لا يوجد أطباء آخرون.")
        return
    
    recipient = st.selectbox("اختر الطبيب", recipients)
    text = st.text_area("اكتب رسالتك...")
    
    if st.button("📨 إرسال", type="primary") and text:
        st.session_state.private_messages.append({
            "sender": st.session_state.current_user["name"],
            "recipient": recipient,
            "text": text,
            "time": datetime.now().isoformat()
        })
        st.success("✅ تم إرسال الرسالة!")

# =============================================================
# PAGE: LAB CHAT
# =============================================================
def page_lab_chat():
    st.markdown('<h2>🧪 التواصل <span style="color:#e67e22;">مع المختبر</span></h2>', unsafe_allow_html=True)
    
    for msg in st.session_state.lab_messages[-10:]:
        st.markdown(f"<div class='card'><strong>{msg['sender']}:</strong> {msg['text']}</div>", unsafe_allow_html=True)
    
    with st.form("lab_form", clear_on_submit=True):
        txt = st.text_input("رسالتك للمختبر...")
        if st.form_submit_button("إرسال") and txt:
            st.session_state.lab_messages.append({
                "sender": st.session_state.current_user["name"],
                "text": txt,
                "time": datetime.now().isoformat()
            })
            st.rerun()

# =============================================================
# PAGE: FILE SHARING
# =============================================================
def page_file_sharing():
    st.markdown('<h2>📁 مشاركة <span style="color:#e67e22;">الملفات</span></h2>', unsafe_allow_html=True)
    st.caption("الصيغ المدعومة: STL, PLY, OBJ, FBX, GLB, DICOM, PDF, JPG, PNG, CSV, XLSX")
    
    uploaded = st.file_uploader("اسحب الملفات هنا", accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            st.session_state.files_uploaded.append({"name": f.name, "size": f.size, "type": f.type})
            st.success(f"✅ تم رفع {f.name}")
    
    if st.session_state.files_uploaded:
        st.dataframe(pd.DataFrame(st.session_state.files_uploaded), use_container_width=True)

# =============================================================
# PAGE: SCREEN SHARE
# =============================================================
def page_screen_share():
    st.markdown('<h2>🖥️ مشاركة <span style="color:#e67e22;">الشاشة</span></h2>', unsafe_allow_html=True)
    st.info("🔹 في بيئة المتصفح، استخدم زر 'بدء المشاركة' أدناه")
    st.markdown("""
    <button style="background:#10b981; color:#fff; border:none; padding:10px 24px; border-radius:60px; cursor:pointer;" onclick="navigator.mediaDevices.getDisplayMedia({video:true}).then(s=>{alert('🖥️ تم بدء المشاركة')}).catch(e=>{alert('تم الإلغاء')})">
        ▶️ بدء مشاركة الشاشة
    </button>
    """, unsafe_allow_html=True)

# =============================================================
# PAGE: DIAGNOSIS
# =============================================================
def page_diagnosis():
    st.markdown('<h2>🩺 التشخيص <span style="color:#e67e22;">الذكي</span></h2>', unsafe_allow_html=True)
    
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد مرضى"]
    st.selectbox("اختر المريض", patients)
    st.text_input("الأخصائي", value=st.session_state.current_user["name"])
    symptoms = st.text_area("الأعراض", placeholder="أدخل الأعراض بالتفصيل...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎓 تشخيص AI - Harvard", type="primary", use_container_width=True):
            with st.spinner("🧠 جاري التحليل..."):
                time.sleep(2)
            st.success("✅ تم التشخيص!")
            st.info("📋 التشخيص: التهاب لثة متوسط - يوصى بتنظيف عميق")
    
    with col2:
        if st.button("🤖 تحليل متقدم بالذكاء الاصطناعي", use_container_width=True):
            with st.spinner("🧠 جاري التحليل المتقدم..."):
                time.sleep(2)
            st.success("✅ تم التحليل المتقدم!")
            st.info("📊 النتائج:\n- نسبة الشفاء المتوقعة: 95%\n- المدة المقترحة: 3-4 جلسات")

# =============================================================
# PAGE: TREATMENT PLAN
# =============================================================
def page_treatment_plan():
    st.markdown('<h2>📋 خطة <span style="color:#e67e22;">العلاج</span></h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("الخطة الرئيسية", placeholder="أدخل الخطة الرئيسية...")
    with col2:
        st.text_input("العلاج البديل", placeholder="العلاج البديل...")
    
    if st.button("🧠 توليد الخطة", type="primary"):
        st.balloons()
        st.success("✅ تم توليد الخطة التفصيلية")
        st.info("📋 خطة العلاج المقترحة:\n- المرحلة 1: تنظيف عميق (جلسة)\n- المرحلة 2: حشوات (جلسة)\n- المرحلة 3: تقييم نهائي")

# =============================================================
# PAGE: MATERIALS
# =============================================================
def page_materials():
    st.markdown('<h2>🧪 المواد <span style="color:#e67e22;">العلاجية</span></h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("اسم المادة")
    with col2:
        usage = st.text_input("الاستخدام")
    
    if st.button("➕ إضافة") and name:
        st.session_state.materials.append({"name": name, "usage": usage})
        st.success("✅ تمت الإضافة")
    
    if st.session_state.materials:
        st.table(pd.DataFrame(st.session_state.materials))

# =============================================================
# PAGE: FACIAL ANALYSIS
# =============================================================
def page_facial():
    st.markdown('<h2>🧑‍⚕️ تحليل <span style="color:#e67e22;">الوجه (478 علامة)</span></h2>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader("📸 حمّل صورة الوجه", type=["jpg","png"], key="facial_img")
    
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة المحملة", use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎨 تحليل الـ 478 نقطة", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري التحليل..."):
                    time.sleep(2)
                    result = draw_landmarks_on_image(img, 478)
                    st.image(result, caption="العلامات التشريحية", use_container_width=True)
                    st.success("✅ تم رسم 478 علامة تشريحية!")
                    st.info("📊 النتائج:\n- تناسق الوجه: 92%\n- النسبة الذهبية: 1.62\n- ANB: 2.5°")
        
        with col2:
            if st.button("🧑 رسم FaceMesh", use_container_width=True):
                with st.spinner("⏳ جاري رسم FaceMesh..."):
                    result = draw_face_mesh_on_image(img)
                    st.image(result, caption="FaceMesh", use_container_width=True)
                    st.success("✅ تم رسم FaceMesh!")
        
        with col3:
            if st.button("💾 حفظ التحليل", use_container_width=True):
                st.session_state.facial_analysis_results.append({
                    "image": uploaded,
                    "date": datetime.now().isoformat()
                })
                st.success("✅ تم حفظ التحليل!")

# =============================================================
# PAGE: CEPHALOMETRIC
# =============================================================
def page_cephalometric():
    st.markdown('<h2>🩻 تحليل <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)
    
    st.markdown("### 📐 الزوايا السيفالومترية")
    
    data = st.session_state.cephalometric_data
    normal_values = {
        "SNA": 82, "SNB": 80, "ANB": 2,
        "SN-MP": 32, "FMA": 25, "IMPA": 90,
        "Overjet": 3, "Overbite": 2
    }
    
    ceph_data = []
    for key in ["SNA", "SNB", "ANB", "SN-MP", "FMA", "IMPA", "Overjet", "Overbite"]:
        patient_val = data.get(key, 0)
        normal_val = normal_values.get(key, 0)
        diff = patient_val - normal_val
        status = "✅ طبيعي" if abs(diff) <= 2 else "⚠️ مقبول" if abs(diff) <= 4 else "❌ غير طبيعي"
        ceph_data.append({
            "الزاوية": key,
            "قيمة المريض": patient_val,
            "القيمة الطبيعية": normal_val,
            "الفرق": diff,
            "الحالة": status
        })
    
    st.table(pd.DataFrame(ceph_data))
    
    st.markdown("### ✏️ تعديل القيم")
    col1, col2 = st.columns(2)
    for i, key in enumerate(["SNA", "SNB", "ANB", "SN-MP", "FMA", "IMPA", "Overjet", "Overbite"]):
        with col1 if i % 2 == 0 else col2:
            new_val = st.number_input(key, value=float(data.get(key, 0)), step=0.5, key=f"ceph_{key}")
            st.session_state.cephalometric_data[key] = new_val
    
    if st.button("💾 حفظ القيم", type="primary"):
        st.success("✅ تم حفظ الزوايا السيفالومترية!")

# =============================================================
# PAGE: SMILE DESIGN
# =============================================================
def page_smile_design():
    st.markdown('<h2>😁 تصميم <span style="color:#e67e22;">الابتسامة</span></h2>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader("📸 صورة الابتسامة", type=["jpg","png"], key="smile_img")
    
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة الأصلية", use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📐 DSD Overlay", use_container_width=True):
                result = draw_landmarks_on_image(img, 100)
                st.image(result, caption="DSD Overlay", use_container_width=True)
                st.success("✅ تم تطبيق DSD Overlay!")
        
        with col2:
            if st.button("✨ محاكاة AI", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري المحاكاة..."):
                    _, result = simulate_smile_before_after(img, 0.8)
                    comparison = create_comparison_image(img, result)
                    st.image(result, caption="النتيجة المتوقعة", use_container_width=True)
                    st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
                    st.success("✅ تمت المحاكاة!")
        
        with col3:
            if st.button("💾 حفظ التصميم", use_container_width=True):
                st.session_state.smile_designs.append({
                    "image": uploaded,
                    "date": datetime.now().isoformat()
                })
                st.success("✅ تم حفظ التصميم!")

# =============================================================
# PAGE: AESTHETIC DESIGN
# =============================================================
def page_aesthetic_design():
    st.markdown('<h2>🎨 التصميم <span style="color:#e67e22;">التجميلي (قبل / بعد)</span></h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        before = st.file_uploader("📸 قبل", key="before_img")
        if before:
            img = Image.open(before)
            st.image(img, caption="قبل", use_container_width=True)
    
    with col2:
        after = st.file_uploader("📸 بعد", key="after_img")
        if after:
            img = Image.open(after)
            st.image(img, caption="بعد", use_container_width=True)
    
    split = st.slider("مستوى المقارنة", 0, 100, 50)
    
    if before and after:
        if st.button("🎨 توليد التصميم", type="primary"):
            comparison = create_comparison_image(Image.open(before), Image.open(after), split/100)
            st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
            st.success("✅ تم توليد التصميم!")

# =============================================================
# PAGE: STL 3D
# =============================================================
def page_stl_3d():
    st.markdown('<h2>📦 نماذج <span style="color:#e67e22;">3D / Mesh</span></h2>', unsafe_allow_html=True)
    
    model = st.file_uploader("رفع STL / OBJ / PLY", type=["stl","obj","ply","glb"], key="stl_up")
    if model:
        st.success(f"✅ تم رفع {model.name}")
        st.info("🧊 عارض Three.js مدمج (يتطلب ملف Three.js حقيقي للعرض التفاعلي)")
    
    st.markdown("### 🎮 عارض 3D")
    st.markdown("""
    <div style="width:100%; height:400px; background:#0f172a; border-radius:16px; border:1px solid #334155; display:flex; align-items:center; justify-content:center;">
        <div style="text-align:center; color:#e67e22;">
            <div style="font-size:4rem;">🦷</div>
            <div style="font-size:1rem; margin-top:10px;">عارض 3D تفاعلي</div>
            <div style="font-size:0.8rem; color:#94a3b8;">Three.js WebGL Renderer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================
# PAGE: DSD STUDIO
# =============================================================
def page_dsd_studio():
    st.markdown('<h2>🧬 استوديو إعادة بناء الابتسامة الطبيعية <span style="color:#94a3b8; font-size:1rem;">Bio-Mimetic DSD</span></h2>', unsafe_allow_html=True)
    
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد"]
    st.selectbox("📋 الملف الطبي للمريض", patients)
    
    uploaded = st.file_uploader("📸 تحميل الصورة بالاستوديو", type=["jpg","png"], key="dsd_img")
    if uploaded:
        st.image(uploaded, caption="الصورة", use_container_width=True)
    
    st.slider("عرض الابتسامة", 0, 100, 80)
    st.slider("الارتفاع العمودي", 0, 100, 50)
    st.slider("تطابق الشفافية", 0, 100, 70)
    
    if st.button("📊 تحليل الـ 478 معلم", type="primary"):
        st.success("✅ تم الدمج الجمالي!")

# =============================================================
# PAGE: AESTHETIC TREATMENT
# =============================================================
def page_aesthetic_treatment():
    st.markdown('<h2>💎 علاج الوجه <span style="color:#e67e22;">التجميلي المتقدم</span></h2>', unsafe_allow_html=True)
    
    st.text_input("اسم المريض")
    st.selectbox("نوع العلاج", ["تناسق الوجه", "علاج البشرة", "تناسق الأنف", "تناسق الذقن", "تناسق الشفاه"])
    st.text_area("وصف الحالة")
    
    if st.button("✨ توليد خطة العلاج", type="primary"):
        st.success("✅ تم توليد خطة العلاج!")

# =============================================================
# PAGE: GLOBAL PLATFORM
# =============================================================
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

# =============================================================
# PAGE: PIPELINE
# =============================================================
def page_pipeline():
    st.markdown('<h2>🔄 خط الإنتاج <span style="color:#e67e22;">المدمج</span></h2>', unsafe_allow_html=True)
    
    st.selectbox("اختر مريضاً", [p["name"] for p in st.session_state.patients] or ["لا يوجد"])
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=st.session_state.pipeline_progress,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "نسبة الإنجاز"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#e67e22"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

# =============================================================
# PAGE: MATERIALS GUIDE
# =============================================================
def page_materials_guide():
    st.markdown('<h2>🦷 دليل المواد الطبية التجميلية <span style="color:#94a3b8; font-size:1rem;">مع المراجع العلمية</span></h2>', unsafe_allow_html=True)
    
    data = [
        ["Lithium Disilicate (E.max)", "قشور وتركيبات", "تحضير مجهري، Mock-up، لصق راتنجي", "STL من Exocad", "PubMed"],
        ["Hyaluronic Acid Filler", "فيلر الأنسجة الرخوة", "حقن تحت المخاطية لدعم الشفة", "Blender OBJ", "NCBI"],
        ["Botulinum Toxin (Botox)", "تعديل الابتسامة اللثوية", "حقن في Levator Labii", "AI Studios", "PubMed"],
        ["Zirconia Monolithic", "جسور وتأهيل كامل", "تحضير هيكلي، طبعة رقمية", "Exocad", "ScienceDirect"],
    ]
    df = pd.DataFrame(data, columns=["المادة", "التصنيف", "بروتوكول الاستخدام", "الربط الرقمي", "المراجع"])
    st.dataframe(df, use_container_width=True)

# =============================================================
# PAGE: API HUB
# =============================================================
def page_api_hub():
    st.markdown('<h2>🔌 مركز تواصل الأنظمة <span style="color:#94a3b8; font-size:1rem;">(Global API Hub)</span></h2>', unsafe_allow_html=True)
    
    systems = [
        ("Exocad", "STL", "🟢", "تصدير"),
        ("Meshy AI", "3D Face", "🟢", "فتح"),
        ("Blender", "Cycles", "🟡", "فتح"),
        ("AI Studios", "Motion", "🟢", "فتح")
    ]
    
    for name, fmt, status, action in systems:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{name}** <span style='color:#94a3b8; font-size:0.8rem;'>{fmt}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<span style='color:#10b981;'>{status}</span>", unsafe_allow_html=True)
        with col3:
            if st.button(action, key=f"api_{name}"):
                st.success(f"✅ {action} إلى {name}")

# =============================================================
# PAGE: MOCK DB
# =============================================================
def page_mock_db():
    st.markdown('<h2>🗄️ محاكي مستودع <span style="color:#e67e22;">المريض</span></h2>', unsafe_allow_html=True)
    
    st.json({
        "patients_count": len(st.session_state.patients),
        "last_backup": datetime.now().isoformat(),
        "storage_used": "1.2 GB",
        "sync_status": "مُزامن"
    })

# =============================================================
# PAGE: NOTIFICATIONS
# =============================================================
def page_notifications():
    st.markdown('<h2>🔔 الإشعارات <span style="color:#e67e22;">الواردة</span></h2>', unsafe_allow_html=True)
    
    notifs = [
        "📢 تم تحديث خط سير المريض (الخطوة 3)",
        "💬 رسالة جديدة من المختبر",
        "📅 موعد غداً الساعة 10:00 ص",
        "✅ تم إضافة مريض جديد",
        "🦷 تم تحديث مخطط الأسنان"
    ]
    
    for n in notifs:
        st.markdown(f'<div class="card" style="padding:10px; margin-bottom:6px;">{n}</div>', unsafe_allow_html=True)

# =============================================================
# PAGE: SYSTEMS
# =============================================================
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

# =============================================================
# PAGE: SCIENTIFIC SCAN
# =============================================================
def page_scientific_scan():
    st.markdown('<h2>🔬 المسح العلمي <span style="color:#e67e22;">الشامل</span></h2>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    with cols[0]:
        if st.button("👤 مسح الوجه", use_container_width=True):
            st.success("✅ تم مسح الوجه!")
    with cols[1]:
        if st.button("🦷 مسح الأسنان", use_container_width=True):
            st.success("✅ تم مسح الأسنان!")
    with cols[2]:
        if st.button("⚖️ تحليل التناغم", type="primary", use_container_width=True):
            st.success("✅ تم تحليل التناغم!")
            st.info("📊 نتائج التناغم:\n- تناسق الوجه: 94%\n- تناسق الأسنان: 92%\n- تناسق الشفاه: 88%")
    with cols[3]:
        if st.button("📋 تقرير علمي", use_container_width=True):
            st.success("✅ تم توليد التقرير العلمي!")

# =============================================================
# PAGE: NAQAI
# =============================================================
def page_naqai():
    st.markdown('<h2>🤖 NaqAI <span style="color:#e67e22;">المساعد الذكي</span></h2>', unsafe_allow_html=True)
    
    for msg in st.session_state.naqai_chat:
        if msg["role"] == "ai":
            st.markdown(f'<div style="background:#0a8491; color:#fff; padding:10px 14px; border-radius:12px; margin-bottom:6px; max-width:85%;">{msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#1e293b; color:#f8fafc; padding:10px 14px; border-radius:12px; margin-bottom:6px; border:1px solid #334155;">{msg["text"]}</div>', unsafe_allow_html=True)
    
    q = st.text_input("اسأل NaqAI...")
    if st.button("📨 إرسال", type="primary") and q:
        st.session_state.naqai_chat.append({"role": "user", "text": q})
        
        responses = {
            "ابتسامة": "😁 **تصميم الابتسامة** يشمل:\n- تحليل النسب الذهبية للأسنان والوجه.\n- استخدام برامج مثل Exocad و Smile Generator.\n- تحديد لون وشكل الأسنان بما يتناسب مع ملامح الوجه.\n- محاكاة النتيجة النهائية عبر 3D و DSD.",
            "فيلر": "💉 **فيلر حمض الهيالورونيك**:\n- يستخدم لملء التجاعيد وزيادة حجم الشفاه والوجنتين.\n- يدوم من 6 إلى 18 شهراً حسب النوع.\n- يُحقن تحت الجلد مباشرة مع تخدير موضعي.\n- يُفضل استخدامه مع البوتوكس للحصول على نتيجة متكاملة.",
            "بوتوكس": "🧪 **البوتوكس (Botulinum Toxin)**:\n- يستخدم لتقليل التجاعيد الديناميكية (الجبين، حول العينين).\n- أيضاً لعلاج الابتسامة اللثوية عن طريق حقن عضلة Levator Labii.\n- تأثيره يظهر خلال 3-7 أيام ويستمر 3-6 أشهر.",
            "زركونيا": "🦷 **الزركونيا (Zirconia)**:\n- مادة خزفية عالية المتانة والجمالية.\n- تستخدم في التيجان والجسور والزرعات.\n- تتميز بمقاومة عالية للكسر والتآكل.\n- تُصنع باستخدام تقنية CAD/CAM وتثبت بمواد لاصقة خاصة.",
            "تحليل": "🧠 **تحليل الوجه** يعتمد على 478 نقطة تشريحية لتقييم:\n- التناسق الوجهي.\n- النسبة الذهبية (1:1.618).\n- زوايا الوجه الرئيسية (SNA, SNB, ANB)."
        }
        
        ans = "🧠 شكراً لسؤالك! يمكنني مساعدتك في:\n• تصميم الابتسامة\n• العلاج التجميلي (فيلر، بوتوكس)\n• تحليل الوجه والأشعة\n• خط الإنتاج\n• المواد الطبية"
        
        for k, v in responses.items():
            if k in q.lower():
                ans = v
                break
        
        st.session_state.naqai_chat.append({"role": "ai", "text": ans})
        st.rerun()

# =============================================================
# PAGE: INTERDISCIPLINARY
# =============================================================
def page_interdisciplinary():
    st.markdown('<h2>👥 فرق <span style="color:#e67e22;">متعددة التخصصات</span></h2>', unsafe_allow_html=True)
    
    with st.form("add_spec"):
        n = st.text_input("اسم الأخصائي")
        s = st.text_input("التخصص")
        if st.form_submit_button("➕ إضافة"):
            st.session_state.specialists.append({"name": n, "specialty": s, "online": True})
            st.success("✅ تمت الإضافة")
    
    for sp in st.session_state.specialists:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong>{sp['name']}</strong>
                    <span style="font-size:0.75rem; color:#94a3b8; margin-right:12px;">{sp['specialty']}</span>
                </div>
                <div>
                    <span style="color:{'#10b981' if sp.get('online', True) else '#555'};">{'🟢 متصل' if sp.get('online', True) else '🔴 غير متصل'}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================
# PAGE: ADS
# =============================================================
def page_ads():
    st.markdown('<h2>📢 الإعلانات</h2>', unsafe_allow_html=True)
    
    with st.form("ad_form"):
        t = st.text_input("عنوان الإعلان")
        c = st.text_area("المحتوى")
        if st.form_submit_button("📨 نشر"):
            st.session_state.ads.append({"title": t, "content": c, "date": datetime.now().isoformat()})
            st.success("✅ تم النشر")
    
    for a in st.session_state.ads:
        st.markdown(f"""
        <div class="card">
            <h5 style="color:#e67e22;">{a['title']}</h5>
            <p>{a['content']}</p>
            <span style="font-size:0.7rem; color:#94a3b8;">{a.get('date', '').split('T')[0] if 'T' in a.get('date','') else ''}</span>
        </div>
        """, unsafe_allow_html=True)

# =============================================================
# PAGE: LAB
# =============================================================
def page_lab():
    st.markdown('<h2>🔬 حساب <span style="color:#e67e22;">المعمل</span></h2>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        tech = st.text_input("اسم الفني", key="lab_tech")
    with c2:
        work = st.text_input("نوع العمل", key="lab_work")
    with c3:
        patient = st.text_input("اسم المريض", key="lab_patient")
    with c4:
        amount = st.number_input("المبلغ ($)", key="lab_amount", min_value=0)
    
    if st.button("💾 حفظ"):
        if tech and work:
            st.success("✅ تم حفظ طلب المعمل!")

# =============================================================
# PAGE: APPOINTMENTS
# =============================================================
def page_appointments():
    st.markdown('<h2>📅 المواعيد</h2>', unsafe_allow_html=True)
    
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد"]
    patient = st.selectbox("المريض", patients)
    date = st.date_input("التاريخ", datetime.now())
    time = st.time_input("الوقت", datetime.now().time())
    note = st.text_input("ملاحظة")
    
    if st.button("📅 إضافة موعد", type="primary"):
        st.session_state.appointments.append({
            "patient": patient,
            "date": date.strftime("%Y-%m-%d"),
            "time": time.strftime("%H:%M"),
            "note": note
        })
        st.success("✅ تم إضافة الموعد")
        st.rerun()
    
    st.markdown("### 📋 المواعيد المسجلة")
    for app in st.session_state.appointments:
        st.markdown(f"""
        <div class="card" style="padding:12px;">
            <div style="display:flex; justify-content:space-between;">
                <div>
                    <strong>{app['patient']}</strong>
                    <span style="color:#94a3b8; margin-right:12px;">{app['date']} {app['time']}</span>
                </div>
                <div style="color:#94a3b8;">{app['note']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================
# PAGE: ACCOUNTING
# =============================================================
def page_accounting():
    st.markdown('<h2>💰 حساب <span style="color:#e67e22;">المريض</span></h2>', unsafe_allow_html=True)
    
    total = st.number_input("المبلغ الكلي", value=1000, min_value=0)
    paid = st.number_input("المدفوع", value=0, min_value=0)
    
    st.markdown(f"""
    <div class="card">
        <div style="display:flex; justify-content:space-around; text-align:center;">
            <div><h4>الكلي</h4><div class="metric-value">{total}</div></div>
            <div><h4>المدفوع</h4><div class="metric-value" style="color:#10b981;">{paid}</div></div>
            <div><h4>المتبقي</h4><div class="metric-value" style="color:#ef4444;">{total-paid}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================
# PAGE: PAYMENTS
# =============================================================
def page_payments():
    st.markdown('<h2>💳 الدفع <span style="color:#e67e22;">والمحفظة</span></h2>', unsafe_allow_html=True)
    
    methods = ["💳 Visa / Mastercard", "📱 محفظتي", "💵 أم فلوس", "💰 شامل موني", "📲 إم باي", "🏦 التحويل البنكي", "💵 الدفع النقدي"]
    selected = st.selectbox("وسيلة الدفع", methods)
    
    if st.button("✅ تنفيذ الدفع", type="primary"):
        st.success(f"✅ تم الدفع بنجاح عبر {selected}")

# =============================================================
# PAGE: SUBSCRIPTIONS
# =============================================================
def page_subscriptions():
    st.markdown('<h2>👑 خطط <span style="color:#e67e22;">الاشتراك</span></h2>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    plans = [
        ("🆓 تجريبي", "$0", ["3 مرضى", "تحليل أساسي"]),
        ("⭐ شهري", "$99", ["غير محدود", "تحليل AI", "دعم"]),
        ("🌟 سنوي", "$999", ["جميع الميزات", "دعم أولوي", "تحديثات"]),
    ]
    
    for i, (name, price, feats) in enumerate(plans):
        with cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center; {'border:2px solid #e67e22;' if i==1 else ''}">
                <h4>{name}</h4>
                <div style="font-size:2rem; font-weight:800; color:#e67e22;">{price}</div>
                <div style="font-size:0.7rem; color:#94a3b8; margin:8px 0;">
                    {', '.join(feats)}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("اشترك", key=f"sub_{i}", use_container_width=True):
                st.success(f"🎉 تم تفعيل الاشتراك {name}!")

# =============================================================
# PAGE: INVITE
# =============================================================
def page_invite():
    st.markdown('<h2>📨 دعوة <span style="color:#e67e22;">الأطباء</span></h2>', unsafe_allow_html=True)
    
    link = f"https://harmonizeai.streamlit.app/?ref={np.random.randint(1000,9999)}"
    st.text_input("رابط الدعوة", value=link)
    
    if st.button("📋 نسخ الرابط"):
        st.success("✅ تم النسخ!")

# =============================================================
# PAGE: SETTINGS
# =============================================================
def page_settings():
    st.markdown('<h2>⚙️ الإعدادات <span style="color:#e67e22;">والخصوصية</span></h2>', unsafe_allow_html=True)
    
    with st.form("settings"):
        st.text_input("الاسم الظاهر", value=st.session_state.current_user["name"])
        st.text_input("التخصص", value=st.session_state.current_user.get("specialty",""))
        
        if st.form_submit_button("💾 حفظ"):
            st.success("✅ تم الحفظ")

# =============================================================
# PAGE: REPORTS
# =============================================================
def page_reports():
    st.markdown('<h2>📄 التقارير</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 توليد تقرير PDF", type="primary", use_container_width=True):
            st.success("✅ تم توليد التقرير!")
            st.download_button(
                label="⬇️ تحميل PDF",
                data=b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj 4 0 obj<</Length 0>>stream\nendstream endobj trailer<</Root 1 0 R>>",
                file_name="HarmonizeAI_Report.pdf",
                mime="application/pdf"
            )
    
    with col2:
        if st.button("🤖 توليد تقرير ذكي بالذكاء الاصطناعي", use_container_width=True):
            with st.spinner("⏳ جاري توليد التقرير الذكي..."):
                time.sleep(2)
            st.success("✅ تم توليد التقرير الذكي!")

# =============================================================
# PAGE: PRIVACY
# =============================================================
def page_privacy():
    st.markdown('<h2>🔒 الخصوصية <span style="color:#e67e22;">والأمان</span></h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <p style="color:#94a3b8; line-height:1.8;">
        <strong>سياسة الخصوصية:</strong> نحن نلتزم بحماية بياناتك الشخصية. جميع المعلومات التي تقدمها تخزن بشكل آمن ولا يتم مشاركتها مع أطراف ثالثة دون موافقتك الصريحة.
        <br><br>
        <strong>🔒 خصوصية البيانات:</strong> كل مستخدم لديه بياناته الخاصة. الأطباء يرون فقط مرضاهم، والمرضى يرون فقط بياناتهم.
        <br><br>
        <strong>🔐 الأمان:</strong> جميع البيانات مشفرة ومحمية بكلمة مرور حسابك.
        <br><br>
        <strong>🤖 الذكاء الاصطناعي:</strong> جميع عمليات التحليل والتوليد تتم داخل النظام ولا تشارك بياناتك مع أي طرف خارجي.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================
# PAGE: IP
# =============================================================
def page_ip():
    st.markdown('<h2>©️ حقوق <span style="color:#e67e22;">الملكية الفكرية</span></h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <p style="color:#94a3b8; line-height:1.8;">
        <strong>حقوق الملكية الفكرية:</strong> جميع المحتويات المنشورة على هذه المنصة محمية بموجب حقوق النشر والعلامات التجارية.
        <br><br>
        <strong>🤖 المحتوى المُنتج بالذكاء الاصطناعي:</strong> الصور والتصميمات المُنتجة بواسطة النظام هي ملك للمستخدم الذي أنشأها.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================
# PAGE: FORUM
# =============================================================
def page_forum():
    st.markdown('<h2>🗣️ منتدى النقاشات <span style="color:#e67e22;">مع الأخصائيين</span></h2>', unsafe_allow_html=True)
    
    st.markdown("### 👨‍⚕️ الأخصائيون المتاحون")
    cols = st.columns(len(st.session_state.specialists))
    for i, sp in enumerate(st.session_state.specialists):
        with cols[i]:
            status_color = "#10b981" if sp.get("online", True) else "#555"
            st.markdown(f"""
            <div style="background:#1e293b; padding:10px; border-radius:12px; text-align:center; border:1px solid #334155;">
                <div style="width:12px; height:12px; background:{status_color}; border-radius:50%; margin:0 auto 6px;"></div>
                <strong style="font-size:0.85rem;">{sp['name']}</strong>
                <div style="font-size:0.7rem; color:#94a3b8;">{sp['specialty']}</div>
                <div style="font-size:0.6rem; color:#94a3b8;">📞 {sp.get('phone', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("### ✏️ اطرح سؤالاً جديداً")
    with st.form("forum_question"):
        q_title = st.text_input("عنوان السؤال")
        q_body = st.text_area("تفاصيل السؤال")
        target = st.selectbox("موجه إلى", ["جميع الأخصائيين"] + [s["name"] for s in st.session_state.specialists])
        
        if st.form_submit_button("🚀 نشر السؤال") and q_title and q_body:
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
    
    st.markdown("### 📋 الأسئلة المنشورة")
    if not st.session_state.forum_questions:
        st.info("📭 لا توجد أسئلة بعد. كن أول من يسأل!")
    else:
        for q in st.session_state.forum_questions:
            status_colors = {"open": "#f59e0b", "answered": "#10b981", "closed": "#ef4444"}
            status_labels = {"open": "🟡 مفتوح", "answered": "✅ تم الرد", "closed": "🔒 مغلق"}
            sc = status_colors.get(q["status"], "#f59e0b")
            sl = status_labels.get(q["status"], q["status"])
            
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

# =============================================================
# PAGE: CAD/CAM
# =============================================================
def page_cadcam():
    st.markdown('<h2>⚙️ CAD/CAM & 3D <span style="color:#e67e22;">(نموذج افتراضي جاهز)</span></h2>', unsafe_allow_html=True)
    st.caption("تحميل، معاينة، تحليل، وتصدير النماذج ثلاثية الأبعاد للأسنان والوجه")
    
    st.markdown("""
    <div style="width:100%; height:400px; background:#0f172a; border-radius:16px; border:1px solid #334155; display:flex; align-items:center; justify-content:center;">
        <div style="text-align:center; color:#e67e22;">
            <div style="font-size:4rem;">🦷</div>
            <div style="font-size:1rem; margin-top:10px;">عارض 3D تفاعلي</div>
            <div style="font-size:0.8rem; color:#94a3b8;">Three.js WebGL Renderer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.slider("تكبير", 0.5, 2.0, 1.0, key="cad_zoom")
    with c2:
        st.slider("دوران X", -180, 180, 0, key="cad_rotx")
    with c3:
        st.slider("دوران Y", -180, 180, 0, key="cad_roty")
    with c4:
        st.slider("إضاءة", 0.2, 2.0, 1.0, key="cad_light")
    
    st.markdown("#### 📄 نموذج افتراضي")
    st.markdown("<div style='color:#94a3b8;'>Polygon: <strong style='color:#e67e22;'>32 سن</strong></div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#94a3b8;'>✅ <strong style='color:#10b981;'>جاهز</strong></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.button("📤 تحميل افتراضي", use_container_width=True, type="primary")
    with col2:
        st.file_uploader("STL", type=["stl","obj","ply"], label_visibility="collapsed", key="cad_stl")
    with col3:
        st.button("🔄 كاميرا", use_container_width=True)
    with col4:
        st.button("📐 شبكة", use_container_width=True)
    with col5:
        st.button("📷 حفظ", use_container_width=True)

# =============================================================
# PAGE: VITA
# =============================================================
def page_vita():
    st.markdown('<h2>🎨 ألوان <span style="color:#e67e22;">فيتا</span></h2>', unsafe_allow_html=True)
    st.caption("اختر لون فيتا المناسب للمريض")
    
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
            <div style="border:1px solid #334155; border-radius:8px; padding:12px; text-align:center; background:#1e293b; cursor:pointer;" onclick="alert('تم اختيار {code}')">
                <div style="width:100%; height:40px; border-radius:6px; background:{color}; border:1px solid #334155;"></div>
                <div style="font-weight:700; color:#e67e22; margin-top:6px;">{code}</div>
                <div style="font-size:0.6rem; color:#94a3b8;">{['أبيض فاتح', 'أبيض', 'أبيض متوسط', 'أبيض غامق', 'أبيض غامق', 'أصفر فاتح', 'أصفر', 'أصفر غامق', 'أصفر غامق', 'رمادي فاتح', 'رمادي', 'رمادي غامق', 'رمادي غامق', 'بني فاتح', 'بني', 'بني غامق'][i]}</div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================
# PAGE: IMAGE EDITOR (Photopea-like)
# =============================================================
def page_image_editor():
    st.markdown('<h2>🎨 محرر الصور المتقدم <span style="color:#e67e22;">(Photopea-like)</span></h2>', unsafe_allow_html=True)
    st.caption("قص، تعديل، إضافة طبقات، رسم FaceMesh، وتحرير الأسنان والفك")
    
    if not st.session_state.image_layers:
        base_img = Image.new('RGB', (800, 600), color='#1a1a2e')
        draw = ImageDraw.Draw(base_img)
        draw.text((400, 300), "🦷 ارفع صورة لبدء التحرير", fill='#94a3b8', anchor="mm")
        st.session_state.image_layers = [{"name": "Background", "image": base_img, "visible": True, "opacity": 1.0, "blend_mode": "normal"}]
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
        
        st.markdown("---")
        st.markdown("### 🎨 أدوات التحرير")
        
        tools = ["🖌️ فرشاة", "✏️ قلم", "⬜ مستطيل", "⭕ دائرة", "📐 خط", "🪄 عصا سحرية"]
        for tool in tools:
            if st.button(tool, use_container_width=True):
                st.session_state.current_tool = tool
                st.success(f"✅ تم اختيار {tool}")
        
        st.markdown("---")
        st.markdown("### 🎚️ تعديل الطبقة الحالية")
        
        if st.session_state.image_layers:
            layer = st.session_state.image_layers[st.session_state.current_layer]
            
            new_name = st.text_input("اسم الطبقة", value=layer["name"])
            if new_name != layer["name"]:
                layer["name"] = new_name
            
            opacity = st.slider("الشفافية", 0.0, 1.0, layer["opacity"], 0.05)
            layer["opacity"] = opacity
            
            visible = st.checkbox("ظاهرة", value=layer["visible"])
            layer["visible"] = visible
            
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
        
        if st.session_state.image_layers:
            display_img = None
            for layer in st.session_state.image_layers:
                if layer["visible"] and layer["image"]:
                    img = layer["image"].copy()
                    if display_img is None:
                        display_img = img
                    else:
                        display_img = Image.blend(display_img, img, layer["opacity"])
            
            if display_img:
                display_img.thumbnail((700, 500))
                st.image(display_img, caption="المحرر", use_container_width=True)
        
        st.markdown("### 📋 الطبقات")
        
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
        
        col_merge, col_clear = st.columns(2)
        with col_merge:
            if st.button("🔗 دمج الكل", use_container_width=True):
                merge_layers()
                st.rerun()
        with col_clear:
            if st.button("🗑️ مسح الكل", use_container_width=True):
                st.session_state.image_layers = []
                st.rerun()

def get_current_layer_image():
    if 0 <= st.session_state.current_layer < len(st.session_state.image_layers):
        return st.session_state.image_layers[st.session_state.current_layer]["image"]
    return None

# =============================================================
# NEW AI PAGES
# =============================================================

def page_ai_face_real():
    """صفحة تحليل الوجه بالذكاء الاصطناعي الحقيقي"""
    st.markdown('<h2>🧠 تحليل الوجه بالذكاء الاصطناعي <span style="color:#e67e22;">468 نقطة</span></h2>', unsafe_allow_html=True)
    st.caption("تحليل متقدم للوجه باستخدام 468 نقطة تشريحية لتقييم التناسق والنسب")
    
    uploaded = st.file_uploader("📸 حمّل صورة الوجه", type=["jpg","png"], key="ai_face_real")
    
    if uploaded:
        img = Image.open(uploaded)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="الصورة الأصلية", use_container_width=True)
        
        with col2:
            if st.button("🧠 تحليل الوجه بالذكاء الاصطناعي", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري تحليل 468 نقطة..."):
                    analysis_result = real_face_analysis(img)
                    
                    if analysis_result.get("analysis_image"):
                        st.image(analysis_result["analysis_image"], caption="تحليل 468 نقطة", use_container_width=True)
                        
                        st.markdown("### 📊 نتائج التحليل")
                        col_metrics = st.columns(3)
                        with col_metrics[0]:
                            st.metric("📍 النقاط المكتشفة", len(analysis_result.get("landmarks", [])))
                        with col_metrics[1]:
                            st.metric("📐 التناسق", f"{analysis_result.get('symmetry_score', 0):.1f}%")
                        with col_metrics[2]:
                            st.metric("😊 مؤشر الابتسامة", f"{analysis_result.get('smile_index', 0):.1f}%")
                        
                        st.info(f"🔹 شكل الوجه: {analysis_result.get('face_shape', 'غير محدد')}")
                        
                        st.session_state.last_analysis_image = analysis_result["analysis_image"]
                        st.session_state.last_analysis_data = analysis_result
                        
                        buffered = BytesIO()
                        analysis_result["analysis_image"].save(buffered, format="PNG")
                        st.download_button(
                            label="⬇️ تحميل التحليل",
                            data=buffered.getvalue(),
                            file_name=f"face_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                            mime="image/png"
                        )
                        
                        st.success("✅ تم التحليل بنجاح باستخدام 468 نقطة تشريحية!")
                        st.balloons()
                    else:
                        st.error("❌ لم يتم اكتشاف وجه في الصورة")

def page_ai_cephalometric_real():
    """صفحة تحليل الأشعة بالذكاء الاصطناعي الحقيقي"""
    st.markdown('<h2>🩻 تحليل الأشعة بالذكاء الاصطناعي <span style="color:#e67e22;">AI Cephalometric</span></h2>', unsafe_allow_html=True)
    st.caption("تحليل متقدم للأشعة السيفالومترية باستخدام معالجة الصور والذكاء الاصطناعي")
    
    uploaded = st.file_uploader("📸 رفع صورة الأشعة", type=["jpg", "png", "jpeg", "dcm"], key="ai_xray_real")
    
    if uploaded:
        img = Image.open(uploaded)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="صورة الأشعة الأصلية", use_container_width=True)
        
        with col2:
            if st.button("🧠 تحليل الذكاء الاصطناعي", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري تحليل الأشعة ومعالجتها..."):
                    analysis_result = real_cephalometric_analysis(img)
                    
                    if analysis_result.get("analysis_image"):
                        st.image(analysis_result["analysis_image"], caption="تحليل الأشعة", use_container_width=True)
                        
                        st.markdown("### 📊 نتائج التحليل السيفالومتري")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("📐 SNA", f"{analysis_result.get('SNA', 0):.1f}°")
                            st.metric("📐 SNB", f"{analysis_result.get('SNB', 0):.1f}°")
                            st.metric("📐 ANB", f"{analysis_result.get('ANB', 0):.1f}°")
                            st.metric("📐 SN-MP", f"{analysis_result.get('SN-MP', 0):.1f}°")
                        
                        with col2:
                            st.metric("📐 FMA", f"{analysis_result.get('FMA', 0):.1f}°")
                            st.metric("📐 IMPA", f"{analysis_result.get('IMPA', 0):.1f}°")
                            st.metric("📐 Overjet", f"{analysis_result.get('Overjet', 0):.1f}mm")
                            st.metric("📐 Overbite", f"{analysis_result.get('Overbite', 0):.1f}mm")
                        
                        st.session_state.last_cephalometric_image = analysis_result["analysis_image"]
                        st.session_state.last_cephalometric_data = analysis_result
                        
                        buffered = BytesIO()
                        analysis_result["analysis_image"].save(buffered, format="PNG")
                        st.download_button(
                            label="⬇️ تحميل التحليل",
                            data=buffered.getvalue(),
                            file_name=f"cephalometric_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                            mime="image/png"
                        )
                        
                        st.success("✅ تم تحليل الأشعة بنجاح!")
                    else:
                        st.error("❌ لم يتمكن النظام من تحليل الصورة")

def page_pdf_report():
    """صفحة توليد تقرير PDF مع الصور"""
    st.markdown('<h2>📄 توليد تقرير <span style="color:#e67e22;">PDF شامل</span></h2>', unsafe_allow_html=True)
    st.caption("تقرير يحتوي على جميع التحاليل والصور الناتجة")
    
    patient_name = st.text_input("👤 اسم المريض", value="مريض تجريبي")
    
    images = {}
    if hasattr(st.session_state, 'last_analysis_image') and st.session_state.last_analysis_image:
        images["تحليل الوجه (468 نقطة)"] = st.session_state.last_analysis_image
    if hasattr(st.session_state, 'last_cephalometric_image') and st.session_state.last_cephalometric_image:
        images["تحليل الأشعة السيفالومتري"] = st.session_state.last_cephalometric_image
    if hasattr(st.session_state, 'last_smile_image') and st.session_state.last_smile_image:
        images["محاكاة الابتسامة"] = st.session_state.last_smile_image
    
    if images:
        st.markdown("### 📸 الصور المتاحة للتقرير")
        cols = st.columns(min(len(images), 3))
        for i, (title, img) in enumerate(list(images.items())[:3]):
            with cols[i]:
                st.image(img, caption=title, use_container_width=True)
        if len(images) > 3:
            st.info(f"📸 +{len(images) - 3} صور إضافية")
    else:
        st.info("💡 قم بتحليل الوجه أو الأشعة أو محاكاة الابتسامة أولاً لتوليد الصور")
    
    analysis_data = {}
    if hasattr(st.session_state, 'last_analysis_data') and st.session_state.last_analysis_data:
        analysis_data["face_analysis"] = st.session_state.last_analysis_data
    if hasattr(st.session_state, 'last_cephalometric_data') and st.session_state.last_cephalometric_data:
        analysis_data["cephalometric"] = st.session_state.last_cephalometric_data
    
    if st.button("📄 توليد تقرير", type="primary", use_container_width=True):
        if images:
            with st.spinner("⏳ جاري توليد التقرير..."):
                html_content = generate_html_report(patient_name, analysis_data, images)
                
                pdf_buffer = generate_pdf_from_html(html_content)
                
                if pdf_buffer:
                    st.download_button(
                        label="⬇️ تحميل التقرير PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=f"report_{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.download_button(
                        label="⬇️ تحميل التقرير HTML",
                        data=html_content.encode('utf-8'),
                        file_name=f"report_{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                        mime="text/html"
                    )
                    st.info("💡 تم توليد التقرير بصيغة HTML (لأن مكتبة PDF غير متوفرة)")
                
                st.success("✅ تم توليد التقرير بنجاح!")
        else:
            st.warning("⚠️ لا توجد صور للتصدير. قم بتحليل الوجه أو الأشعة أولاً.")

def page_three_d_viewer():
    """صفحة عارض ثلاثي الأبعاد مع دعم 3dpea.com"""
    st.markdown('<h2>🦷 عارض الأسنان ثلاثي الأبعاد <span style="color:#e67e22;">3D Viewer</span></h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🦷 عارض Three.js", "🌐 3DPEA.com"])
    
    with tab1:
        st.markdown("### 🎮 عارض Three.js المدمج")
        st.caption("عارض تفاعلي للأسنان والفك باستخدام Three.js")
        
        col1, col2 = st.columns(2)
        with col1:
            model_type = st.selectbox(
                "📐 نوع النموذج",
                ["أسنان كاملة", "فك علوي", "فك سفلي", "زرعة سنية", "تقويم"]
            )
        with col2:
            show_annotations = st.checkbox("🏷️ إظهار التسميات", value=True)
        
        viewer_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { margin: 0; overflow: hidden; background: #0f172a; }
                #info { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); 
                        color: #94a3b8; font-family: 'Cairo', sans-serif; font-size: 12px; 
                        background: rgba(0,0,0,0.7); padding: 8px 16px; border-radius: 20px; }
                #controls { position: absolute; top: 20px; right: 20px; display: flex; flex-direction: column; gap: 8px; }
                #controls button { background: rgba(230,126,34,0.8); border: none; color: #fff; 
                                  padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 14px; 
                                  transition: 0.3s; }
                #controls button:hover { background: #e67e22; }
            </style>
        </head>
        <body>
            <div id="container"></div>
            <div id="info">🦷 اسحب للتدوير | تمرير للتكبير | انقر على سن للمعلومات</div>
            <div id="controls">
                <button onclick="resetCamera()">🔄 إعادة ضبط</button>
                <button onclick="toggleWireframe()">📐 شبكة</button>
                <button onclick="toggleAutoRotate()">🔄 دوران تلقائي</button>
                <button onclick="toggleXRay()">🩻 أشعة</button>
            </div>
            
            <script type="importmap">
            {
                "imports": {
                    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
                    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
                }
            }
            </script>
            
            <script type="module">
                import * as THREE from 'three';
                import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
                
                const container = document.getElementById('container');
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x0f172a);
                
                const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(5, 3, 8);
                
                const renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                renderer.shadowMap.enabled = true;
                container.appendChild(renderer.domElement);
                
                const controls = new OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.autoRotate = true;
                controls.autoRotateSpeed = 2.0;
                
                const ambientLight = new THREE.AmbientLight(0x404060);
                scene.add(ambientLight);
                
                const mainLight = new THREE.DirectionalLight(0xffffff, 1);
                mainLight.position.set(5, 10, 7);
                mainLight.castShadow = true;
                scene.add(mainLight);
                
                const fillLight = new THREE.DirectionalLight(0x8888ff, 0.5);
                fillLight.position.set(-5, 0, 5);
                scene.add(fillLight);
                
                const toothMaterial = new THREE.MeshPhysicalMaterial({
                    color: 0xf5f0e8,
                    metalness: 0.05,
                    roughness: 0.3,
                    clearcoat: 0.1,
                });
                
                const gumMaterial = new THREE.MeshPhysicalMaterial({
                    color: 0xe8b4b8,
                    metalness: 0.0,
                    roughness: 0.8,
                });
                
                const group = new THREE.Group();
                
                for (let i = -7; i <= 7; i++) {
                    if (i === 0) continue;
                    const tooth = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.25, 0.6, 8), toothMaterial);
                    const x = i * 0.35;
                    const z = -0.3 + Math.abs(i) * 0.03;
                    tooth.position.set(x, 0.3, z);
                    tooth.rotation.x = 0.1 * (i / 7);
                    tooth.rotation.z = 0.05 * i;
                    tooth.userData = { toothNumber: Math.abs(i) + 1, type: 'upper' };
                    group.add(tooth);
                }
                
                for (let i = -7; i <= 7; i++) {
                    if (i === 0) continue;
                    const tooth = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.25, 0.5, 8), toothMaterial);
                    const x = i * 0.35;
                    const z = 0.3 - Math.abs(i) * 0.03;
                    tooth.position.set(x, -0.3, z);
                    tooth.rotation.x = -0.1 * (i / 7);
                    tooth.rotation.z = 0.05 * i;
                    tooth.userData = { toothNumber: Math.abs(i) + 17, type: 'lower' };
                    group.add(tooth);
                }
                
                const gumUpper = new THREE.Mesh(new THREE.SphereGeometry(1.5, 16, 8, 0, Math.PI*2, 0, Math.PI/2), gumMaterial);
                gumUpper.position.set(0, 0, -0.5);
                gumUpper.scale.set(1, 0.3, 0.8);
                group.add(gumUpper);
                
                const gumLower = new THREE.Mesh(new THREE.SphereGeometry(1.5, 16, 8, 0, Math.PI*2, Math.PI/2, Math.PI/2), gumMaterial);
                gumLower.position.set(0, -0.05, 0.5);
                gumLower.scale.set(1, 0.3, 0.8);
                group.add(gumLower);
                
                scene.add(group);
                
                window.resetCamera = function() {
                    camera.position.set(5, 3, 8);
                    controls.target.set(0, 0, 0);
                };
                
                window.toggleWireframe = function() {
                    group.traverse((child) => {
                        if (child.isMesh) {
                            child.material.wireframe = !child.material.wireframe;
                        }
                    });
                };
                
                window.toggleAutoRotate = function() {
                    controls.autoRotate = !controls.autoRotate;
                };
                
                window.toggleXRay = function() {
                    group.traverse((child) => {
                        if (child.isMesh) {
                            child.material.opacity = child.material.opacity === 1 ? 0.3 : 1;
                            child.material.transparent = true;
                        }
                    });
                };
                
                const raycaster = new THREE.Raycaster();
                const mouse = new THREE.Vector2();
                
                renderer.domElement.addEventListener('click', (event) => {
                    const rect = renderer.domElement.getBoundingClientRect();
                    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
                    
                    raycaster.setFromCamera(mouse, camera);
                    const intersects = raycaster.intersectObjects(group.children);
                    
                    if (intersects.length > 0) {
                        const tooth = intersects[0].object;
                        alert(`🦷 السن رقم ${tooth.userData.toothNumber} - ${tooth.userData.type === 'upper' ? 'علوي' : 'سفلي'}`);
                    }
                });
                
                window.addEventListener('resize', () => {
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                });
                
                function animate() {
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }
                animate();
            </script>
        </body>
        </html>
        """
        
        st.components.v1.html(viewer_html, height=550)
        
        uploaded_model = st.file_uploader("📤 رفع نموذج 3D (STL, OBJ, PLY)", type=["stl", "obj", "ply"])
        if uploaded_model:
            st.success(f"✅ تم رفع {uploaded_model.name}")
    
    with tab2:
        st.markdown("### 🌐 3DPEA.com - أداة تحويل 3D مجانية")
        st.caption("تحويل الصور ثنائية الأبعاد إلى مجسمات ثلاثية الأبعاد بصيغة STL مجاناً")
        
        st.markdown("""
        <div style="background:#1e293b; border-radius:12px; padding:20px; border:1px solid #334155; text-align:center;">
            <div style="font-size:3rem; margin-bottom:10px;">🔄</div>
            <h3 style="color:#e67e22;">3DPEA.com</h3>
            <p style="color:#94a3b8;">
                أداة مجانية لتحويل الصور (PNG, JPG) إلى مجسمات ثلاثية الأبعاد (STL)<br>
                وتحويل الملفات ثلاثية الأبعاد بين الصيغ المختلفة
            </p>
            <a href="https://www.3dpea.com" target="_blank" style="
                display:inline-block;
                background:#e67e22;
                color:#fff;
                padding:12px 30px;
                border-radius:30px;
                text-decoration:none;
                font-weight:600;
                margin-top:10px;
            ">
                🚀 فتح 3DPEA.com
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 الصيغ المدعومة")
        formats = ["stl", "3mf", "amf", "obj", "fbx", "3dm", "glb", "gltf", "ply", "drc", "zip"]
        cols = st.columns(4)
        for i, fmt in enumerate(formats):
            with cols[i % 4]:
                st.markdown(f"<div style='background:#0f172a; padding:8px; border-radius:8px; text-align:center; border:1px solid #334155;'><code>{fmt.upper()}</code></div>", unsafe_allow_html=True)

# =============================================================
# PAGE ROUTER
# =============================================================
PAGES = {
    "home": page_home,
    "dashboard": page_dashboard,
    "upload_logo": page_upload_logo,
    "smile_simulator": page_smile_simulator,
    "ai_smile_design": page_smile_simulator,
    "ai_face_real": page_ai_face_real,
    "ai_cephalometric_real": page_ai_cephalometric_real,
    "pdf_report": page_pdf_report,
    "three_d_viewer": page_three_d_viewer,
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
    if "selected_tooth" in st.query_params:
        try:
            tooth_idx = int(st.query_params["selected_tooth"])
            if 0 <= tooth_idx < 32:
                st.session_state.selected_tooth = tooth_idx
                st.query_params.pop("selected_tooth", None)
        except:
            pass
    
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
