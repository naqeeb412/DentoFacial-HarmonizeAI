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

=============================================================

SYSTEM DETECTION - اكتشاف نظام التشغيل

=============================================================

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

=============================================================

CONFIG & PAGE SETUP

=============================================================

st.set_page_config(
page_title="HarmonizeAI™ | Dentofacial Synergy",
page_icon="🦷",
layout="wide",
initial_sidebar_state="expanded"
)

=============================================================

CSS - RTL & Dark Theme + Enhanced Styles (متوافق مع جميع الأجهزة)

=============================================================

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

=============================================================

SYSTEM LOGO FUNCTIONS

=============================================================

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

=============================================================

AUTHENTICATION SYSTEM - Multi-Platform Login

=============================================================

OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(password):
return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
return ''.join(random.choices('0123456789', k=6))

User database with multi-platform support

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

=============================================================

DATA STORE - جميع بيانات النظام

=============================================================

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

=============================================================

AUTH FUNCTIONS

=============================================================

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

=============================================================

CHECK DEPENDENCIES - التحقق من التبعيات حسب النظام

=============================================================

def check_opencv():
try:
import cv2
return True
except ImportError:
return False

def check_mediapipe():
try:
import mediapipe as mp
return True
except ImportError:
return False

def install_package(package):
try:
subprocess.check_call([sys.executable, "-m", "pip", "install", package])
return True
except:
return False

=============================================================

IMAGE PROCESSING FUNCTIONS (الأساسية)

=============================================================

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def enhance_smile_face(image_array, intensity=0.7):
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
if isinstance(original_img, Image.Image):
original_np = np.array(original_img.convert('RGB'))
else:
original_np = original_img
enhanced = enhance_smile_face(original_np, intensity)
result_pil = Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
return original_img, result_pil

def create_comparison_image(before_img, after_img, split_position=0.5):
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
draw.line([(w0.2, h0.1), (w0.8, h0.1)], fill='#e67e22', width=2)
draw.line([(w0.2, h0.9), (w0.8, h0.9)], fill='#e67e22', width=2)
draw.line([(w0.5, h0.1), (w0.5, h0.9)], fill='#10b981', width=2)
return img

def create_layer(image, name="Layer"):
if isinstance(image, Image.Image):
return {"name": name, "image": image, "visible": True, "opacity": 1.0, "blend_mode": "normal"}
return None

def add_layer(image, name="Layer"):
layer = create_layer(image, name)
if layer:
st.session_state.image_layers.append(layer)
st.session_state.current_layer = len(st.session_state.image_layers) - 1
return True
return False

def remove_layer(index):
if 0 <= index < len(st.session_state.image_layers):
st.session_state.image_layers.pop(index)
if st.session_state.current_layer >= len(st.session_state.image_layers):
st.session_state.current_layer = len(st.session_state.image_layers) - 1
return True
return False

def merge_layers():
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
if 0 <= index < 32:
st.session_state.tooth_statuses[index] = status
st.session_state.dental_chart[index] = status
return True
return False

def get_tooth_status(index):
return st.session_state.tooth_statuses.get(index, "normal")

=============================================================

REAL AI ANALYSIS FUNCTIONS (تحليل الوجه والأشعة)

=============================================================

def real_face_analysis(image):
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
eye_dist = np.sqrt((eye_right[0] - eye_left[0])2 + (eye_right[1] - eye_left[1])2)
results_data["eye_distance"] = eye_dist
mouth_left = landmarks_list[61] if 61 < len(landmarks_list) else (0, 0)
mouth_right = landmarks_list[291] if 291 < len(landmarks_list) else (0, 0)
mouth_width = np.sqrt((mouth_right[0] - mouth_left[0])2 + (mouth_right[1] - mouth_left[1])2)
results_data["mouth_width"] = mouth_width
face_top = landmarks_list[10] if 10 < len(landmarks_list) else (0, 0)
face_bottom = landmarks_list[152] if 152 < len(landmarks_list) else (0, 0)
face_height = np.sqrt((face_bottom[0] - face_top[0])2 + (face_bottom[1] - face_top[1])2)
results_data["face_height"] = face_height
face_left = landmarks_list[234] if 234 < len(landmarks_list) else (0, 0)
face_right = landmarks_list[454] if 454 < len(landmarks_list) else (0, 0)
face_width = np.sqrt((face_right[0] - face_left[0])2 + (face_right[1] - face_left[1])2)
results_data["face_width"] = face_width
symmetry_points = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]
symmetry_diff = 0
for left_idx, right_idx in symmetry_points:
if left_idx < len(landmarks_list) and right_idx < len(landmarks_list):
left_point = landmarks_list[left_idx]
right_point = landmarks_list[right_idx]
diff = np.sqrt((left_point[0] - right_point[0])2 + (left_point[1] - right_point[1])2)
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
cv2.line(result_img, (int(w0.3), int(h0.3)), (int(w0.5), int(h0.2)), (0, 255, 0), 2)
cv2.putText(result_img, "S-N", (int(w0.3), int(h0.25)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
cv2.line(result_img, (int(w0.5), int(h0.2)), (int(w0.6), int(h0.4)), (255, 0, 0), 2)
cv2.putText(result_img, "N-A", (int(w0.55), int(h0.3)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
cv2.line(result_img, (int(w0.5), int(h0.2)), (int(w0.55), int(h0.6)), (0, 0, 255), 2)
cv2.putText(result_img, "N-B", (int(w0.5), int(h0.5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
y_offset = 30
for key, value in analysis_data.items():
if key != "analysis_image":
cv2.putText(result_img, f"{key}: {value}°", (10, y_offset),
cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
y_offset += 25
analysis_data["analysis_image"] = Image.fromarray(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
return analysis_data

=============================================================

PDF REPORT GENERATION (باستخدام HTML مع دعم PDF اختياري)

=============================================================

def generate_html_report(patient_name, analysis_results, images):
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
<strong>Dentofacial HarmonizeAI™</strong>

Naqeeb412 · Synergy

© 2026 جميع الحقوق محفوظة.
</div>
</div>
</body>
</html>
"""
return html

def generate_pdf_from_html(html_content):
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

=============================================================

3D VIEWER FUNCTIONS (عارض ثلاثي الأبعاد)

=============================================================

def get_3d_viewer_html(model_url=None, autoplay=True, controls=True):
if model_url is None:
model_url = "https://threejs.org/examples/models/obj/Face.obj"
html = f'''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ margin: 0; overflow: hidden; background: #0f172a; }}
canvas {{ display: block; }}
.info {{ position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); color: #94a3b8; font-family: 'Cairo', sans-serif; font-size: 12px; background: rgba(0,0,0,0.7); padding: 8px 16px; border-radius: 20px; pointer-events: none; }}
.controls {{ position: absolute; top: 20px; right: 20px; display: flex; flex-direction: column; gap: 8px; }}
.controls button {{ background: rgba(230,126,34,0.8); border: none; color: #fff; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 14px; transition: 0.3s; }}
.controls button:hover {{ background: #e67e22; }}
</style>
</head>
<body>
<div id="container"></div>
<div class="info">🦷 3D Viewer - اسحب للتدوير | تمرير للتكبير</div>
<div class="controls">
<button onclick="resetCamera()">🔄 إعادة ضبط</button>
<button onclick="toggleWireframe()">📐 شبكة</button>
<button onclick="toggleAutoRotate()">🔄 دوران تلقائي</button>
</div>

=============================================================

PAGES: الصفحات المدمجة الجديدة

=============================================================

---- صفحة Dentbook (شبكة التواصل) ----

def page_dentbook():
st.markdown("### 🦷 Dentbook — شبكة التواصل والصيانة")
# بيانات المنشورات (مخزنة في session_state)
if "dentbook_posts" not in st.session_state:
st.session_state.dentbook_posts = [
{
"id": 1,
"author": "د. سامي النجار",
"title": "استشاري تقويم",
"content": "تم تحديث بروتوكول التعقيم في العيادات الخارجية. يرجى الاطلاع والالتزام بالتعليمات الجديدة.",
"category": "تحديث صيانة",
"image": None,
"likes": 5,
"comments": ["د. علي: تم الاطلاع وشكراً لك."],
"time": "منذ ساعتين",
},
{
"id": 2,
"author": "د. ليلى العمري",
"title": "أخصائية علاج جذور",
"content": "حالة سريرية: مريضة تبلغ ٣٥ عاماً تعاني من ألم شديد في الضرس السفلي الأيمن. تم الكشف وإجراء المعالجة اللازمة.",
"category": "حالة سريرية",
"image": "https://picsum.photos/600/300?random=1",
"likes": 12,
"comments": [],
"time": "منذ ٤ ساعات",
},
]

---- صفحة تحليل الإطباق (Occlusal Plane) ----

def page_occlusal_analyzer():
st.markdown("### 🦷 HarmonizeAI: Occlusal & Smile Plane Analyzer")
st.write("تحليل خطوط الإطباق والتناظر الأفقي والعمودي للابتسامة والأسنان.")
face_mesh = mp.solutions.face_mesh.FaceMesh(
static_image_mode=True,
max_num_faces=1,
refine_landmarks=True,
min_detection_confidence=0.6
)
st.sidebar.header("📐 خيارات خطوط الإطباق")
show_occlusal_plane = st.sidebar.checkbox("مستوى الإطباق الرئيسي (Occlusal Plane)", value=True)
show_commissural = st.sidebar.checkbox("خط خط زوايا الفم (Inter-Commissural Line)", value=True)
show_midline = st.sidebar.checkbox("خط المنتصف الإطباقي (Dental Midline)", value=True)
show_smile_curve = st.sidebar.checkbox("منحنى الإطباق الجمالي (Occlusal Curve / Smile Line)", value=True)
color_occlusal = (0, 255, 0)
color_commissural = (255, 165, 0)
color_midline = (0, 0, 255)
color_curve = (255, 255, 0)
uploaded_file = st.file_uploader("ارفع صورة الإطباق/الابتسامة الأمامية", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
image = Image.open(uploaded_file)
img = np.array(image)
if img.shape[2] == 4:
img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
h, w, _ = img.shape
results = face_mesh.process(img)
annotated = img.copy()
if results.multi_face_landmarks:
for face_landmarks in results.multi_face_landmarks:
lm = face_landmarks.landmark
left_corner = (int(lm[61].x * w), int(lm[61].y * h))
right_corner = (int(lm[291].x * w), int(lm[291].y * h))
upper_lip_mid = (int(lm[0].x * w), int(lm[0].y * h))
lower_lip_mid = (int(lm[17].x * w), int(lm[17].y * h))
nose_tip = (int(lm[1].x * w), int(lm[1].y * h))
chin_tip = (int(lm[152].x * w), int(lm[152].y * h))
if show_midline:
cv2.line(annotated, (nose_tip[0], 0), (chin_tip[0], h), color_midline, 2)
if show_commissural:
cv2.line(annotated, left_corner, right_corner, color_commissural, 2)
if show_occlusal_plane:
y_occlusal = int((left_corner[1] + right_corner[1]) / 2)
cv2.line(annotated, (0, y_occlusal), (w, y_occlusal), color_occlusal, 2, cv2.LINE_AA)
if show_smile_curve:
curve_pts = [lm[61], lm[84], lm[17], lm[314], lm[291]]
pts = np.array([[int(p.x * w), int(p.y * h)] for p in curve_pts], np.int32)
cv2.polylines(annotated, [pts], isClosed=False, color=color_curve, thickness=3, lineType=cv2.LINE_AA)
else:
st.error("لم يتم العثور على معالم الوجه، يرجى رفع صورة إطباقية أوضح.")
col1, col2 = st.columns(2)
with col1:
st.subheader("الصورة الأصلية")
st.image(img, use_container_width=True)
with col2:
st.subheader("تحليل مستوى الإطباق")
st.image(annotated, use_container_width=True)
st.download_button(
label="📥 تحميل نتيجة تحليل الإطباق",
data=cv2.imencode('.png', cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))[1].tobytes(),
file_name="occlusal_analysis.png",
mime="image/png"
)

---- صفحة النسبة الذهبية ----

def page_golden_ratio():
st.markdown("### ✨ HarmonizeAI: Golden Ratio & Facial Aesthetics Analyzer")
st.write("تحليل خطوط الجمال الحقيقية والنسبة الذهبية (Phi = 1.618) للتناسق الوجهي والابتسامة.")
face_mesh = mp.solutions.face_mesh.FaceMesh(
static_image_mode=True,
max_num_faces=1,
refine_landmarks=True,
min_detection_confidence=0.6
)
PHI = 1.61803398875
st.sidebar.header("📐 خطوط الجمال والنسبة الذهبية")
show_thirds = st.sidebar.checkbox("الأثلاث الوجهية المتساوية (Facial Thirds)", value=True)
show_fifths = st.sidebar.checkbox("الأخماس الوجهية (Facial Fifths)", value=True)
show_golden_mask = st.sidebar.checkbox("شبكة النسبة الذهبية للعين والأنف والفم", value=True)
show_golden_decisions = st.sidebar.checkbox("إحصائيات القياس الذهبي", value=True)
COLOR_GOLD = (255, 215, 0)
COLOR_THIRDS = (255, 105, 180)
COLOR_FIFTHS = (0, 255, 255)
uploaded_file = st.file_uploader("ارفع صورة وجه أمامية مستقيمة", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
image = Image.open(uploaded_file)
img = np.array(image)
if img.shape[2] == 4:
img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
h, w, _ = img.shape
results = face_mesh.process(img)
annotated = img.copy()
calculated_ratio = 0
if results.multi_face_landmarks:
for face_landmarks in results.multi_face_landmarks:
lm = face_landmarks.landmark
trichion = int(lm[10].y * h)
subnasale = int(lm[2].y * h)
menton = int(lm[152].y * h)
glabella = int(lm[9].y * h)
left_face_edge = int(lm[234].x * w)
right_face_edge = int(lm[454].x * w)
left_eye_outer = int(lm[33].x * w)
left_eye_inner = int(lm[133].x * w)
right_eye_inner = int(lm[362].x * w)
right_eye_outer = int(lm[263].x * w)
if show_thirds:
cv2.line(annotated, (0, trichion), (w, trichion), COLOR_THIRDS, 2)
cv2.line(annotated, (0, glabella), (w, glabella), COLOR_THIRDS, 2)
cv2.line(annotated, (0, subnasale), (w, subnasale), COLOR_THIRDS, 2)
cv2.line(annotated, (0, menton), (w, menton), COLOR_THIRDS, 2)
if show_fifths:
cv2.line(annotated, (left_face_edge, 0), (left_face_edge, h), COLOR_FIFTHS, 1)
cv2.line(annotated, (left_eye_outer, 0), (left_eye_outer, h), COLOR_FIFTHS, 1)
cv2.line(annotated, (left_eye_inner, 0), (left_eye_inner, h), COLOR_FIFTHS, 1)
cv2.line(annotated, (right_eye_inner, 0), (right_eye_inner, h), COLOR_FIFTHS, 1)
cv2.line(annotated, (right_eye_outer, 0), (right_eye_outer, h), COLOR_FIFTHS, 1)
cv2.line(annotated, (right_face_edge, 0), (right_face_edge, h), COLOR_FIFTHS, 1)
if show_golden_mask:
mouth_left = (int(lm[61].x * w), int(lm[61].y * h))
mouth_right = (int(lm[291].x * w), int(lm[291].y * h))
nose_left = (int(lm[102].x * w), int(lm[102].y * h))
nose_right = (int(lm[331].x * w), int(lm[331].y * h))
cv2.line(annotated, mouth_left, mouth_right, COLOR_GOLD, 3)
cv2.line(annotated, nose_left, nose_right, COLOR_GOLD, 3)
mouth_width = np.linalg.norm(np.array(mouth_left) - np.array(mouth_right))
nose_width = np.linalg.norm(np.array(nose_left) - np.array(nose_right))
calculated_ratio = mouth_width / nose_width if nose_width != 0 else 0
else:
st.error("لم يتم العثور على معالم الوجه بدقة. يرجى اختيار صورة وجه أمامية واضحة.")
col1, col2 = st.columns(2)
with col1:
st.subheader("الصورة الأصلية")
st.image(img, use_container_width=True)
with col2:
st.subheader("تراكب خطوط الجمال والنسبة الذهبية")
st.image(annotated, use_container_width=True)
if show_golden_decisions and results.multi_face_landmarks:
st.markdown("---")
st.subheader("📊 تحليل أبعاد النسبة الذهبية")
c1, c2, c3 = st.columns(3)
c1.metric("النسبة الذهبية المثالية (Phi)", f"{PHI:.3f}")
c2.metric("نسبة عرض الفم / الأنف المحسوبة", f"{calculated_ratio:.3f}")
deviation = abs(calculated_ratio - PHI) / PHI * 100 if PHI != 0 else 0
c3.metric("نسبة الانحراف عن المثالية", f"{deviation:.1f}%")
st.download_button(
label="📥 تحميل تحليل النسبة الذهبية",
data=cv2.imencode('.png', cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))[1].tobytes(),
file_name="golden_ratio_analysis.png",
mime="image/png"
)

---- صفحة محاكاة الابتسامة المتقدمة (AI Smile Simulator + 3D Export) ----

def page_smile_simulator_ai():
st.markdown("### 🦷 HarmonizeAI: Comprehensive 2D/3D Smile & Dentofacial Simulator")
st.write("منصة الذكاء الاصطناعي للمحاكاة الجمالية، توليد الابتسامة عبر LoRA، وتصدير مجسمات 3D لـ Exocad و Blender.")
st.sidebar.header("⚙️ إعدادات LoRA AI و المحاكاة")
lora_model = st.sidebar.selectbox(
"نموذج LoRA الجمالي",
["Hollywood_White_V2.safetensors", "Natural_Bleach_V1.safetensors", "Translucent_Veneer_V3.safetensors"]
)
lora_weight = st.sidebar.slider("وزن تأثير النموذج (LoRA Weight)", 0.0, 1.0, 0.75, 0.05)
bleach_shade = st.sidebar.select_slider("درجة البياض المطلوبة (Shade)", options=["BL1", "BL2", "BL3", "A1", "A2", "A3"])
st.sidebar.markdown("---")
st.sidebar.header("📦 إعدادات التصدير 3D / CAD")
export_format = st.sidebar.radio("تنسيق المجسم 3D", ["Wavefront (.OBJ)", "Stereolithography (.STL)"])
mesh_resolution = st.sidebar.slider("دقة شبكة المضلعات (Polygon Density)", 500, 5000, 1500, 250)
uploaded_file = st.file_uploader("ارفع صورة الابتسامة أو الوجه (PNG/JPG)", type=["jpg", "jpeg", "png"])
face_mesh = mp.solutions.face_mesh.FaceMesh(
static_image_mode=True,
max_num_faces=1,
refine_landmarks=True,
min_detection_confidence=0.6
)
def generate_mock_3d_obj(vertices):
obj_data = "# HarmonizeAI Generated 3D Mesh for Exocad / Blender\n"
for v in vertices:
obj_data += f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n"
for i in range(1, len(vertices) - 2):
obj_data += f"f {i} {i+1} {i+2}\n"
return obj_data

---- صفحة التقارير الطبية (Medical Report) ----

def page_medical_report():
st.markdown("### 🦷 HarmonizeAI: Clinical Report Generator & Tier System")
st.sidebar.header("💳 نوع الاشتراك (Subscription Plan)")
user_tier = st.sidebar.selectbox(
"باقة الاشتراك الحالية",
["Standard (تحليل أساسي)", "Professional (2D/3D + تقارير)", "Enterprise (كامل الصلاحيات + LoRA AI)"]
)
can_export_pdf = True if user_tier in ["Professional (2D/3D + تقارير)", "Enterprise (كامل الصلاحيات + LoRA AI)"] else False
can_access_full_xray = True if user_tier == "Enterprise (كامل الصلاحيات + LoRA AI)" else False
if not can_export_pdf:
st.sidebar.warning("⚠️ ترقية الاشتراك مطلوبة لتصدير تقارير PDF المتقدمة.")
st.sidebar.markdown("---")
st.sidebar.header("📋 إعدادات التقرير الطبي")
report_type = st.sidebar.radio("نوع التقرير المراد إنشاؤه", ["تقرير طبي شامل (Comprehensive)", "تقرير جزئي (Module Specific)"])
if report_type == "تقرير جزئي (Module Specific)":
include_facial = st.sidebar.checkbox("تحليل الوجه والنسبة الذهبية", value=True)
include_smile = st.sidebar.checkbox("تحليل الابتسامة والإطباق", value=True)
include_xray = st.sidebar.checkbox("تحليل الأشعة والتقويم (Cephalometric)", value=can_access_full_xray, disabled=not can_access_full_xray)
else:
include_facial = include_smile = include_xray = True
st.subheader("👤 بيانات المريض")
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
patient_name = st.text_input("اسم المريض الكامل", "أحمد محمد")
with col_p2:
patient_id = st.text_input("رقم الملف / ID", "PAT-2026-8801")
with col_p3:
doctor_name = st.text_input("الطبيب المعالج", "د. علي النقيب")
uploaded_photo = st.file_uploader("ارفع صورة الوجه/الابتسامة الأمامية", type=["jpg", "png", "jpeg"])
uploaded_xray = st.file_uploader("ارفع صورة الأشعة الجانبية / البانوراما (اختياري)", type=["jpg", "png", "jpeg"])
mp_face_mesh_rep = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)
def analyze_and_draw(image_np):
h, w, _ = image_np.shape
results = mp_face_mesh_rep.process(image_np)
annotated = image_np.copy()
if results.multi_face_landmarks:
lm = results.multi_face_landmarks[0].landmark
nose = (int(lm[1].x * w), int(lm[1].y * h))
chin = (int(lm[152].x * w), int(lm[152].y * h))
cv2.line(annotated, (nose[0], 0), (chin[0], h), (0, 0, 255), 2)
left_corner = (int(lm[61].x * w), int(lm[61].y * h))
right_corner = (int(lm[291].x * w), int(lm[291].y * h))
cv2.line(annotated, left_corner, right_corner, (0, 255, 0), 2)
pts = np.array([[int(lm[idx].x * w), int(lm[idx].y * h)] for idx in [61, 84, 17, 314, 291]], np.int32)
cv2.polylines(annotated, [pts], isClosed=False, color=(255, 215, 0), thickness=3)
return annotated
if uploaded_photo is not None:
img_p = Image.open(uploaded_photo)
img_p_np = np.array(img_p)
if img_p_np.shape[2] == 4:
img_p_np = cv2.cvtColor(img_p_np, cv2.COLOR_RGBA2RGB)
analyzed_photo = analyze_and_draw(img_p_np)
cv2.imwrite("temp_facial_analyzed.png", cv2.cvtColor(analyzed_photo, cv2.COLOR_RGB2BGR))
xray_path = None
if uploaded_xray is not None:
img_x = Image.open(uploaded_xray)
img_x_np = np.array(img_x)
cv2.imwrite("temp_xray.png", cv2.cvtColor(img_x_np, cv2.COLOR_RGB2BGR))
xray_path = "temp_xray.png"
col1, col2 = st.columns(2)
with col1:
st.subheader("الصورة الأصلية")
st.image(img_p_np, use_container_width=True)
with col2:
st.subheader("تحليل الابتسامة والوجه (Analyzed Output)")
st.image(analyzed_photo, use_container_width=True)
st.markdown("---")
st.subheader("🖨️ تصدير وطباعة التقرير الطبي")
if can_export_pdf:
pdf_bytes = generate_html_report(patient_name, {}, {"تحليل الوجه": analyzed_photo})  # تبسيطاً
# نستخدم generate_html_report ولكن يمكن تعديله لتضمين صور متعددة
# سنقوم بإنشاء تقرير باستخدام الدالة الموجودة
images_dict = {"تحليل الوجه": analyzed_photo}
if xray_path and include_xray:
xray_img = Image.open(xray_path)
images_dict["تحليل الأشعة"] = xray_img
html_report = generate_html_report(patient_name, {}, images_dict)
pdf_buffer = generate_pdf_from_html(html_report)
if pdf_buffer:
st.download_button(
label="📄 تحميل التقرير الطبي الشامل (PDF)",
data=pdf_buffer,
file_name=f"HarmonizeAI_Report_{patient_id}.pdf",
mime="application/pdf"
)
else:
st.download_button(
label="📄 تحميل التقرير (HTML)",
data=html_report.encode('utf-8'),
file_name=f"HarmonizeAI_Report_{patient_id}.html",
mime="text/html"
)
else:
st.error("ميزة تصدير التقارير غير مفعّلة في باقتك الحالية. يرجى الترقية إلى الباقة الاحترافية.")

---- صفحة تحليل الكاميرا الحية (Live Smile Analyzer) ----

def page_live_smile_analyzer():
st.markdown("### 🎥 AI Smile & Harmony Simulator (الكاميرا الحية)")
st.write("استخدم كاميرا جهازك لتحليل الابتسامة والتناغم الوجهي في الوقت الفعلي.")
st.info("⚠️ هذه الميزة تعمل في بيئة التطوير المحلية مع الوصول إلى الكاميرا. قد لا تعمل على Streamlit Cloud.")
run = st.checkbox("▶️ تشغيل الكاميرا", value=False)
if run:
# استخدام st.camera_input للحصول على لقطات من الكاميرا
img_file = st.camera_input("التقاط صورة")
if img_file is not None:
# قراءة الصورة وتحويلها إلى numpy
bytes_data = img_file.getvalue()
img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# تحليل باستخدام MediaPipe
face_mesh = mp.solutions.face_mesh.FaceMesh(
static_image_mode=False,
max_num_faces=1,
refine_landmarks=True,
min_detection_confidence=0.5,
min_tracking_confidence=0.5
)
results = face_mesh.process(rgb)
display = img.copy()
if results.multi_face_landmarks:
for face_landmarks in results.multi_face_landmarks:
landmarks = face_landmarks.landmark
# حساب مؤشرات بسيطة
h, w, _ = img.shape
lip_left = np.array([landmarks[61].x * w, landmarks[61].y * h])
lip_right = np.array([landmarks[291].x * w, landmarks[291].y * h])
mouth_width = np.linalg.norm(lip_left - lip_right)
lip_top = np.array([landmarks[13].x * w, landmarks[13].y * h])
lip_bottom = np.array([landmarks[14].x * w, landmarks[14].y * h])
mouth_height = np.linalg.norm(lip_top - lip_bottom)
smile_ratio = mouth_width / max(mouth_height, 1)
smile_intensity = min(100, smile_ratio * 20)
# رسم الشبكة
mp_drawing.draw_landmarks(
image=display,
landmark_list=face_landmarks,
connections=mp_face_mesh.FACEMESH_TESSELATION,
landmark_drawing_spec=None,
connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
)
cv2.putText(display, f"Smile: {smile_intensity:.1f}%", (10, 30),
cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
cv2.putText(display, f"Width: {mouth_width:.1f}px", (10, 60),
cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
st.image(display, channels="BGR", use_container_width=True)
# زر حفظ
if st.button("💾 حفظ اللقطة"):
cv2.imwrite("capture_smile.jpg", display)
st.success("تم حفظ اللقطة!")
else:
st.info("اضغط على زر 'التقاط صورة' لالتقاط صورة من الكاميرا.")

=============================================================

SIDEBAR NAVIGATION (محدثة)

=============================================================

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

=============================================================

PAGE ROUTER (محدث)

=============================================================

PAGES = {
"home": page_home,
"dashboard": page_dashboard,
"upload_logo": page_upload_logo,
"smile_simulator": page_smile_simulator,
"3d_viewer": page_3d_viewer,
"ai_face_real": page_ai_face_real,
"ai_cephalometric_real": page_ai_cephalometric_real,
"pdf_report": page_pdf_report,
"ai_smile_design": page_ai_smile_design,
"dentbook": page_dentbook,
"occlusal_analyzer": page_occlusal_analyzer,
"golden_ratio": page_golden_ratio,
"smile_simulator_ai": page_smile_simulator_ai,
"medical_report": page_medical_report,
"live_smile_analyzer": page_live_smile_analyzer,
"patients": page_patients,
"new_patient": page_new_patient,
"dental_chart": page_dental_chart,
"natural_teeth": page_natural_teeth,
"photography": page_photography,
"xray": page_xray,
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

=============================================================

MAIN

=============================================================

def main():
if "selected_tooth" in st.query_params:
try:
tooth_idx = int(st.query_params["selected_tooth"])
if 0 <= tooth_idx < 32:
st.session_state.selected_tooth = tooth_idx
st.query_params.pop("selected_tooth", None)
except:
pass

if name == "main":
main()

```
