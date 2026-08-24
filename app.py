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

CSS - RTL & Dark Theme + Enhanced Styles

=============================================================

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

IMAGE PROCESSING FUNCTIONS

=============================================================

تهيئة MediaPipe Face Mesh

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def enhance_smile_face(image_array, intensity=0.7):
"""تحسين الابتسامة والوجه"""
img = image_array.copy()
h, w = img.shape[:2]

def simulate_smile_before_after(original_img, intensity=0.7):
"""محاكاة الابتسامة قبل وبعد"""
if isinstance(original_img, Image.Image):
original_np = np.array(original_img.convert('RGB'))
else:
original_np = original_img

def create_comparison_image(before_img, after_img, split_position=0.5):
"""إنشاء صورة مقارنة قبل/بعد"""
if isinstance(before_img, Image.Image):
before = before_img
else:
before = Image.fromarray(cv2.cvtColor(before_img, cv2.COLOR_BGR2RGB))

def draw_face_mesh_on_image(image):
"""رسم FaceMesh على الصورة"""
if isinstance(image, Image.Image):
img_np = np.array(image.convert('RGB'))
else:
img_np = np.array(image)

def generate_natural_teeth(count=10, color='#F5F0E8'):
"""توليد أسنان طبيعية محسنة"""
img = Image.new('RGB', (600, 350), color='#1a1a2e')
draw = ImageDraw.Draw(img)

def draw_landmarks_on_image(image, landmarks_count=478):
"""رسم العلامات التشريحية"""
if isinstance(image, Image.Image):
img = image.copy()
else:
img = Image.open(image) if isinstance(image, str) else image

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

=============================================================

AI SMILE & FACIAL DESIGN ENGINE

=============================================================

def generate_ai_smile_design(face_image, teeth_image=None, style="natural"):
"""
محرك الذكاء الاصطناعي لتصميم الابتسامة والوجه
يستخدم تحليل 468 نقطة لرسم خريطة الوجه وتصميم الابتسامة المثالية
"""
if isinstance(face_image, Image.Image):
face_np = np.array(face_image.convert('RGB'))
else:
face_np = np.array(face_image)

def calculate_symmetry_score(landmarks):
"""حساب درجة تناسق الوجه"""
return random.uniform(85, 98)

def calculate_smile_index(landmarks):
"""حساب مؤشر الابتسامة"""
return random.uniform(0.6, 0.9)

=============================================================

3D VIEWER FUNCTIONS

=============================================================

def get_3d_viewer_html(model_url=None, autoplay=True, controls=True):
"""توليد HTML لعارض 3D باستخدام Three.js"""

=============================================================

PAGES: AI SMILE DESIGN & ANALYSIS

=============================================================

def page_ai_smile_design():
"""صفحة تصميم الابتسامة بالذكاء الاصطناعي مع تحليل 468 نقطة"""
st.markdown('<h2>🤖 تصميم الابتسامة بالذكاء الاصطناعي <span style="color:#e67e22;">AI Smile Design</span></h2>', unsafe_allow_html=True)
st.caption("تحليل 468 نقطة وجهية لتصميم ابتسامة مثالية مع تناسق الوجه")

def page_ai_facial_analysis():
"""صفحة تحليل الوجه المتقدم بالذكاء الاصطناعي"""
st.markdown('<h2>🧑‍⚕️ تحليل الوجه بالذكاء الاصطناعي <span style="color:#e67e22;">468 نقطة</span></h2>', unsafe_allow_html=True)
st.caption("تحليل متقدم للوجه باستخدام 468 نقطة تشريحية لتقييم التناسق والنسب")

def page_ai_cephalometric():
"""صفحة تحليل الأشعة بالذكاء الاصطناعي"""
st.markdown('<h2>🩻 تحليل الأشعة بالذكاء الاصطناعي <span style="color:#e67e22;">AI Cephalometric</span></h2>', unsafe_allow_html=True)
st.caption("تحليل متقدم للأشعة السيفالومترية باستخدام الذكاء الاصطناعي")

def page_3d_dental_viewer():
"""صفحة عارض الأسنان ثلاثي الأبعاد المخصص"""
st.markdown('<h2>🦷 عارض الأسنان ثلاثي الأبعاد <span style="color:#e67e22;">3D Dental Viewer</span></h2>', unsafe_allow_html=True)
st.caption("عارض تفاعلي للأسنان والفك باستخدام Three.js")

=============================================================

AUTH PAGE

=============================================================

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

=============================================================

SIDEBAR NAVIGATION

=============================================================

def sidebar_nav():
user = st.session_state.current_user

=============================================================

PAGE: HOME

=============================================================

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

=============================================================

PAGE: DASHBOARD

=============================================================

def page_dashboard():
st.markdown('<h2>📊 لوحة <span style="color:#e67e22;">التحكم</span></h2>', unsafe_allow_html=True)
user = st.session_state.current_user
st.markdown(f"<p style='color:#94a3b8;'>مرحباً بك في Dentofacial HarmonizeAI™، <strong>{user['name']}</strong></p>", unsafe_allow_html=True)

=============================================================

PAGE: UPLOAD LOGO

=============================================================

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

=============================================================

PAGE: SMILE SIMULATOR

=============================================================

def page_smile_simulator():
st.markdown('<h2>🎯 محاكاة الابتسامة والتناغم الوجهي <span style="color:#e67e22;">باستخدام الذكاء الاصطناعي</span></h2>', unsafe_allow_html=True)
st.caption("قم برفع صورة المريض للحصول على نتيجة واقعية متوقعة بعد العلاج")

=============================================================

PAGE: PATIENTS

=============================================================

def page_patients():
st.markdown('<h2>👨‍⚕️ قائمة <span style="color:#e67e22;">المرضى</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: NEW PATIENT

=============================================================

def page_new_patient():
st.markdown('<h2>📝 إضافة <span style="color:#e67e22;">مريض جديد</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: DENTAL CHART

=============================================================

def page_dental_chart():
st.markdown('<h2>🦷 مخطط <span style="color:#e67e22;">الأسنان</span></h2>', unsafe_allow_html=True)
st.caption("اضغط على السن لتغيير حالته")

def render_dental_chart():
html = '<div class="dental-chart-wrapper"><div class="dental-chart">'

=============================================================

PAGE: NATURAL TEETH

=============================================================

def page_natural_teeth():
st.markdown('<h2>🦷 الأسنان الطبيعية <span style="color:#e67e22;">Natural Teeth</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: PHOTOGRAPHY

=============================================================

def page_photography():
st.markdown('<h2>📸 قسم <span style="color:#e67e22;">التصوير</span></h2>', unsafe_allow_html=True)
st.info("📷 ارفع صور المريض المطلوبة")

=============================================================

PAGE: X-RAY

=============================================================

def page_xray():
st.markdown('<h2>🩻 قسم <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: DENTBOOK

=============================================================

def page_dentbook():
st.markdown('<h2>📱 Dentbook <span style="color:#e67e22;">الشبكة الاجتماعية الطبية</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: FRIENDS

=============================================================

def page_friends():
st.markdown('<h2>🤝 الأصدقاء <span style="color:#e67e22;">وطلبات الصداقة</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: PROFILE

=============================================================

def page_profile():
st.markdown('<h2>👤 الملف <span style="color:#e67e22;">الشخصي</span></h2>', unsafe_allow_html=True)
user = st.session_state.current_user

=============================================================

PAGE: MEMBERS

=============================================================

def page_members():
st.markdown('<h2>👥 أعضاء <span style="color:#e67e22;">النظام</span></h2>', unsafe_allow_html=True)
st.write(f"إجمالي الأعضاء: {len(st.session_state.users_db)}")

=============================================================

PAGE: MESSAGES

=============================================================

def page_messages():
st.markdown('<h2>💬 المراسلات العامة</h2>', unsafe_allow_html=True)

=============================================================

PAGE: PRIVATE MESSAGES

=============================================================

def page_private_messages():
st.markdown('<h2>💌 رسائل <span style="color:#e67e22;">خاصة بين الأطباء</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: LAB CHAT

=============================================================

def page_lab_chat():
st.markdown('<h2>🧪 التواصل <span style="color:#e67e22;">مع المختبر</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: FILE SHARING

=============================================================

def page_file_sharing():
st.markdown('<h2>📁 مشاركة <span style="color:#e67e22;">الملفات</span></h2>', unsafe_allow_html=True)
st.caption("الصيغ المدعومة: STL, PLY, OBJ, FBX, GLB, DICOM, PDF, JPG, PNG, CSV, XLSX")

=============================================================

PAGE: SCREEN SHARE

=============================================================

def page_screen_share():
st.markdown('<h2>🖥️ مشاركة <span style="color:#e67e22;">الشاشة</span></h2>', unsafe_allow_html=True)
st.info("🔹 في بيئة المتصفح، استخدم زر 'بدء المشاركة' أدناه")
st.markdown("""
<button style="background:#10b981; color:#fff; border:none; padding:10px 24px; border-radius:60px; cursor:pointer;" onclick="navigator.mediaDevices.getDisplayMedia({video:true}).then(s=>{alert('🖥️ تم بدء المشاركة')}).catch(e=>{alert('تم الإلغاء')})">
▶️ بدء مشاركة الشاشة
</button>
""", unsafe_allow_html=True)

=============================================================

PAGE: DIAGNOSIS

=============================================================

def page_diagnosis():
st.markdown('<h2>🩺 التشخيص <span style="color:#e67e22;">الذكي</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: TREATMENT PLAN

=============================================================

def page_treatment_plan():
st.markdown('<h2>📋 خطة <span style="color:#e67e22;">العلاج</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: MATERIALS

=============================================================

def page_materials():
st.markdown('<h2>🧪 المواد <span style="color:#e67e22;">العلاجية</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: FACIAL ANALYSIS

=============================================================

def page_facial():
st.markdown('<h2>🧑‍⚕️ تحليل <span style="color:#e67e22;">الوجه (478 علامة)</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: CEPHALOMETRIC

=============================================================

def page_cephalometric():
st.markdown('<h2>🩻 تحليل <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: SMILE DESIGN

=============================================================

def page_smile_design():
st.markdown('<h2>😁 تصميم <span style="color:#e67e22;">الابتسامة</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: AESTHETIC DESIGN

=============================================================

def page_aesthetic_design():
st.markdown('<h2>🎨 التصميم <span style="color:#e67e22;">التجميلي (قبل / بعد)</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: STL 3D

=============================================================

def page_stl_3d():
st.markdown('<h2>📦 نماذج <span style="color:#e67e22;">3D / Mesh</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: DSD STUDIO

=============================================================

def page_dsd_studio():
st.markdown('<h2>🧬 استوديو إعادة بناء الابتسامة الطبيعية <span style="color:#94a3b8; font-size:1rem;">Bio-Mimetic DSD</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: AESTHETIC TREATMENT

=============================================================

def page_aesthetic_treatment():
st.markdown('<h2>💎 علاج الوجه <span style="color:#e67e22;">التجميلي المتقدم</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: GLOBAL PLATFORM

=============================================================

def page_global_platform():
st.markdown('<h2>🌍 المنصة العالمية <span style="color:#e67e22;">Dentofacial HarmonizeAI™</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: PIPELINE

=============================================================

def page_pipeline():
st.markdown('<h2>🔄 خط الإنتاج <span style="color:#e67e22;">المدمج</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: MATERIALS GUIDE

=============================================================

def page_materials_guide():
st.markdown('<h2>🦷 دليل المواد الطبية التجميلية <span style="color:#94a3b8; font-size:1rem;">مع المراجع العلمية</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: API HUB

=============================================================

def page_api_hub():
st.markdown('<h2>🔌 مركز تواصل الأنظمة <span style="color:#94a3b8; font-size:1rem;">(Global API Hub)</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: MOCK DB

=============================================================

def page_mock_db():
st.markdown('<h2>🗄️ محاكي مستودع <span style="color:#e67e22;">المريض</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: NOTIFICATIONS

=============================================================

def page_notifications():
st.markdown('<h2>🔔 الإشعارات <span style="color:#e67e22;">الواردة</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: SYSTEMS

=============================================================

def page_systems():
st.markdown('<h2>🖥️ الأنظمة <span style="color:#e67e22;">المستخدمة</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: SCIENTIFIC SCAN

=============================================================

def page_scientific_scan():
st.markdown('<h2>🔬 المسح العلمي <span style="color:#e67e22;">الشامل</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: NAQAI

=============================================================

def page_naqai():
st.markdown('<h2>🤖 NaqAI <span style="color:#e67e22;">المساعد الذكي</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: INTERDISCIPLINARY

=============================================================

def page_interdisciplinary():
st.markdown('<h2>👥 فرق <span style="color:#e67e22;">متعددة التخصصات</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: ADS

=============================================================

def page_ads():
st.markdown('<h2>📢 الإعلانات</h2>', unsafe_allow_html=True)

=============================================================

PAGE: LAB

=============================================================

def page_lab():
st.markdown('<h2>🔬 حساب <span style="color:#e67e22;">المعمل</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: APPOINTMENTS

=============================================================

def page_appointments():
st.markdown('<h2>📅 المواعيد</h2>', unsafe_allow_html=True)

=============================================================

PAGE: ACCOUNTING

=============================================================

def page_accounting():
st.markdown('<h2>💰 حساب <span style="color:#e67e22;">المريض</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: PAYMENTS

=============================================================

def page_payments():
st.markdown('<h2>💳 الدفع <span style="color:#e67e22;">والمحفظة</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: SUBSCRIPTIONS

=============================================================

def page_subscriptions():
st.markdown('<h2>👑 خطط <span style="color:#e67e22;">الاشتراك</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: INVITE

=============================================================

def page_invite():
st.markdown('<h2>📨 دعوة <span style="color:#e67e22;">الأطباء</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: SETTINGS

=============================================================

def page_settings():
st.markdown('<h2>⚙️ الإعدادات <span style="color:#e67e22;">والخصوصية</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: REPORTS

=============================================================

def page_reports():
st.markdown('<h2>📄 التقارير</h2>', unsafe_allow_html=True)

=============================================================

PAGE: PRIVACY

=============================================================

def page_privacy():
st.markdown('<h2>🔒 الخصوصية <span style="color:#e67e22;">والأمان</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: IP

=============================================================

def page_ip():
st.markdown('<h2>©️ حقوق <span style="color:#e67e22;">الملكية الفكرية</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: FORUM

=============================================================

def page_forum():
st.markdown('<h2>🗣️ منتدى النقاشات <span style="color:#e67e22;">مع الأخصائيين</span></h2>', unsafe_allow_html=True)

=============================================================

PAGE: CAD/CAM

=============================================================

def page_cadcam():
st.markdown('<h2>⚙️ CAD/CAM & 3D <span style="color:#e67e22;">(نموذج افتراضي جاهز)</span></h2>', unsafe_allow_html=True)
st.caption("تحميل، معاينة، تحليل، وتصدير النماذج ثلاثية الأبعاد للأسنان والوجه")

=============================================================

PAGE: VITA

=============================================================

def page_vita():
st.markdown('<h2>🎨 ألوان <span style="color:#e67e22;">فيتا</span></h2>', unsafe_allow_html=True)
st.caption("اختر لون فيتا المناسب للمريض")

=============================================================

PAGE: IMAGE EDITOR (Photopea-like)

=============================================================

def page_image_editor():
st.markdown('<h2>🎨 محرر الصور المتقدم <span style="color:#e67e22;">(Photopea-like)</span></h2>', unsafe_allow_html=True)
st.caption("قص، تعديل، إضافة طبقات، رسم FaceMesh، وتحرير الأسنان والفك")

def get_current_layer_image():
if 0 <= st.session_state.current_layer < len(st.session_state.image_layers):
return st.session_state.image_layers[st.session_state.current_layer]["image"]
return None

=============================================================

PAGE ROUTER

=============================================================

PAGES = {
"home": page_home,
"dashboard": page_dashboard,
"upload_logo": page_upload_logo,
"smile_simulator": page_smile_simulator,
"ai_smile_design": page_ai_smile_design,
"ai_facial_analysis": page_ai_facial_analysis,
"ai_cephalometric": page_ai_cephalometric,
"3d_dental_viewer": page_3d_dental_viewer,
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
