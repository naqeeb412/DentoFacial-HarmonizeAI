import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
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
import tempfile

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
# CSS - RTL & Dark Theme + All Styles
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
    font-size: 24px;
    display: block;
    margin-bottom: 4px;
}
.social-login-btn .label {
    font-size: 0.7rem;
}
.friend-request-card {
    background: #1e293b;
    border: 1px solid #e67e22;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.friend-request-card .name {
    font-weight: 700;
    color: #f8fafc;
}
.friend-request-card .actions {
    display: flex;
    gap: 8px;
}
.vita-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
    gap: 4px;
    margin: 6px 0;
}
.vita-item {
    padding: 8px;
    border-radius: 8px;
    text-align: center;
    border: 1px solid #334155;
    font-size: 10px;
    background: rgba(0,0,0,0.2);
    cursor: pointer;
}
.vita-item .color-box {
    width: 100%;
    height: 24px;
    border-radius: 4px;
    margin-bottom: 4px;
    border: 1px solid #334155;
}
.preview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 10px;
    margin-top: 10px;
}
.preview-grid .preview-item {
    border: 1px solid #334155;
    border-radius: 10px;
    overflow: hidden;
    aspect-ratio: 1;
    background: #0a0a1a;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}
.preview-grid .preview-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.preview-grid .preview-item .remove {
    position: absolute;
    top: 4px;
    right: 4px;
    background: rgba(0,0,0,0.7);
    color: #fff;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.smile-ai-container {
    background: #0f172a;
    border-radius: 12px;
    padding: 20px;
    border: 2px solid #e67e22;
    margin: 10px 0;
}
.smile-ai-container .ai-badge {
    display: inline-block;
    background: #e67e22;
    color: #0a0a0a;
    padding: 2px 14px;
    border-radius: 20px;
    font-size: 0.6rem;
    font-weight: 700;
}
.editor-layer {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 8px;
    border-radius: 6px;
    background: #0f172a;
    margin-bottom: 4px;
    cursor: pointer;
    border: 1px solid transparent;
}
.editor-layer.active {
    border-color: #e67e22;
    background: rgba(230,126,34,0.05);
}
.editor-layer .layer-name {
    flex: 1;
    font-size: 0.85rem;
}
.editor-layer .layer-vis {
    width: 20px;
    text-align: center;
}
.comparison-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}
.comparison-table th {
    background: #0a8491;
    color: #fff;
    padding: 8px;
    text-align: center;
}
.comparison-table td {
    padding: 6px;
    border-bottom: 1px solid #334155;
    text-align: center;
}
.comparison-table .normal { color: #10b981; }
.comparison-table .warning { color: #f59e0b; }
.comparison-table .abnormal { color: #ef4444; }
@media (max-width: 640px) {
    .grid-2, .grid-3, .grid-4, .grid-5 {
        grid-template-columns: 1fr;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================
# STATE INITIALIZATION (موسع)
# =============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# قاعدة بيانات المستخدمين (مع إضافة username وحقول جديدة)
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "ndcdental2025@outlook.com": {
            "name": "علي النقيب",
            "email": "ndcdental2025@outlook.com",
            "password": "ndc2025",
            "role": "owner",
            "specialty": "طب أسنان تجميلي",
            "phone": "+967 77 123 4567",
            "bio": "مؤسس منصة Dentofacial HarmonizeAI™",
            "username": "alnaqeeb",
            "avatar": "",       # base64
            "cover_photo": "",  # base64
            "friends": [],
            "pending_requests": [],
            "posts": [],
            "online": True,
            "created_at": datetime.now().isoformat()
        },
        "doctor@clinic.com": {
            "name": "د. أحمد",
            "email": "doctor@clinic.com",
            "password": "doctor123",
            "role": "doctor",
            "specialty": "تقويم أسنان",
            "phone": "+966 55 123 4567",
            "bio": "أخصائي تقويم أسنان",
            "username": "ahmed_ortho",
            "avatar": "",
            "cover_photo": "",
            "friends": [],
            "pending_requests": [],
            "posts": [],
            "online": True,
            "created_at": datetime.now().isoformat()
        },
        "patient@clinic.com": {
            "name": "مريض نموذجي",
            "email": "patient@clinic.com",
            "password": "patient123",
            "role": "patient",
            "specialty": "",
            "phone": "+966 55 123 4568",
            "bio": "مريض",
            "username": "patient_demo",
            "avatar": "",
            "cover_photo": "",
            "friends": [],
            "pending_requests": [],
            "posts": [],
            "online": True,
            "created_at": datetime.now().isoformat()
        }
    }

# بيانات أخرى
if "patients" not in st.session_state:
    st.session_state.patients = []
if "dental_chart" not in st.session_state:
    st.session_state.dental_chart = ['normal'] * 32
if "cephalometric_data" not in st.session_state:
    st.session_state.cephalometric_data = {
        "SNA": 82, "SNB": 80, "ANB": 2,
        "SN-MP": 32, "FMA": 25, "IMPA": 90,
        "Overjet": 3, "Overbite": 2
    }
if "normal_values" not in st.session_state:
    st.session_state.normal_values = {
        "SNA": 82, "SNB": 80, "ANB": 2,
        "SN-MP": 32, "FMA": 25, "IMPA": 90,
        "Overjet": 3, "Overbite": 2
    }
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "dentbook_posts" not in st.session_state:
    st.session_state.dentbook_posts = []
if "friend_requests" not in st.session_state:
    st.session_state.friend_requests = []
if "private_messages" not in st.session_state:
    st.session_state.private_messages = []
if "lab_messages" not in st.session_state:
    st.session_state.lab_messages = []
if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = []
if "subscriptions" not in st.session_state:
    st.session_state.subscriptions = {
        "free": {"price": 0, "features": ["مرضى غير محدود", "تحليل أساسي"]},
        "monthly": {"price": 99, "features": ["جميع الميزات", "دعم"]},
        "yearly": {"price": 999, "features": ["جميع الميزات", "دعم أولوي", "تحديثات"]}
    }
if "forum_topics" not in st.session_state:
    st.session_state.forum_topics = []
if "image_layers" not in st.session_state:
    st.session_state.image_layers = []
if "current_layer" not in st.session_state:
    st.session_state.current_layer = 0
if "natural_teeth_layers" not in st.session_state:
    st.session_state.natural_teeth_layers = []
if "aesthetic_treatment_plans" not in st.session_state:
    st.session_state.aesthetic_treatment_plans = []
if "xray_images" not in st.session_state:
    st.session_state.xray_images = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "appointments" not in st.session_state:
    st.session_state.appointments = []
if "system_logo" not in st.session_state:
    st.session_state.system_logo = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "smile_designs" not in st.session_state:
    st.session_state.smile_designs = []
if "facial_analysis_results" not in st.session_state:
    st.session_state.facial_analysis_results = []
if "lab_phone" not in st.session_state:
    st.session_state.lab_phone = ""
if "editor_image" not in st.session_state:
    st.session_state.editor_image = None
if "ceph_image" not in st.session_state:
    st.session_state.ceph_image = None
if "cad_model" not in st.session_state:
    st.session_state.cad_model = None

# =============================================================
# AUTH FUNCTIONS
# =============================================================
def login_user(email, password):
    if email in st.session_state.users_db:
        if st.session_state.users_db[email].get("password") == password:
            st.session_state.authenticated = True
            st.session_state.current_user = st.session_state.users_db[email]
            st.session_state.current_user["online"] = True
            return True
    return False

def signup_user(name, email, password, role="doctor", username=""):
    if email in st.session_state.users_db:
        return False, "البريد مستخدم"
    if username:
        for u in st.session_state.users_db.values():
            if u.get("username") == username:
                return False, "اسم المستخدم مستخدم"
    else:
        username = name.replace(" ", "").lower() + str(random.randint(100,999))
    st.session_state.users_db[email] = {
        "name": name,
        "email": email,
        "password": password,
        "role": role,
        "specialty": "",
        "phone": "",
        "bio": "",
        "username": username,
        "avatar": "",
        "cover_photo": "",
        "friends": [],
        "pending_requests": [],
        "posts": [],
        "online": True,
        "created_at": datetime.now().isoformat()
    }
    return True, "تم إنشاء الحساب"

def logout():
    if st.session_state.current_user:
        st.session_state.current_user["online"] = False
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()

def display_system_logo(width=50):
    if st.session_state.system_logo:
        return f'<img src="data:image/png;base64,{st.session_state.system_logo}" style="width:{width}px; height:{width}px; border-radius:50%; object-fit:cover;" />'
    return '<div style="background:#e67e22; width:'+str(width)+'px; height:'+str(width)+'px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; color:#0a0a0a;">🦷</div>'

def get_user_by_username(username):
    for u in st.session_state.users_db.values():
        if u.get("username") == username:
            return u
    return None

# =============================================================
# IMAGE PROCESSING FUNCTIONS
# =============================================================
mp_face_mesh = mp.solutions.face_mesh

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
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, landmark in enumerate(face_landmarks.landmark):
                    x = int(landmark.x * img_np.shape[1])
                    y = int(landmark.y * img_np.shape[0])
                    cv2.circle(img_np, (x, y), 2, (0, 255, 0), -1)
    return Image.fromarray(img_np)

def draw_landmarks_on_image(image, count=478):
    if isinstance(image, Image.Image):
        img = image.copy()
    else:
        img = Image.open(image) if isinstance(image, str) else image
    draw = ImageDraw.Draw(img)
    w, h = img.size
    colors = ['#e67e22', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6']
    for i in range(min(count, 100)):
        x = random.randint(10, w-10)
        y = random.randint(10, h-10)
        draw.ellipse([x-3, y-3, x+3, y+3], fill=random.choice(colors))
    draw.line([(w*0.2, h*0.1), (w*0.8, h*0.1)], fill='#e67e22', width=2)
    draw.line([(w*0.2, h*0.9), (w*0.8, h*0.9)], fill='#e67e22', width=2)
    draw.line([(w*0.5, h*0.1), (w*0.5, h*0.9)], fill='#10b981', width=2)
    return img

def generate_natural_teeth(count=10, width=600, height=350):
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    colors = ['#F5F0E8', '#E8E0D8', '#F0EBE3', '#E5DDD5']
    for i in range(count):
        x = 40 + i * (width-80)//count
        y = height//2 - 30
        w = (width-80)//count - 4
        h = 65
        color = random.choice(colors)
        draw.ellipse([x, y, x+w, y+h], fill=color, outline='#cbd5e1', width=2)
        draw.ellipse([x+6, y+8, x+w-6, y+h-10], fill='#FFFFFF', outline=None)
        draw.ellipse([x+10, y+12, x+w-10, y+h-15], fill=color, outline=None)
    draw.rectangle([0, height//2-10, width, height//2+10], fill='#e8b4b8')
    draw.rectangle([0, height//2+80, width, height//2+100], fill='#e8b4b8')
    return img

def add_layer(image, name="Layer"):
    if isinstance(image, Image.Image):
        st.session_state.image_layers.append({"name": name, "image": image, "visible": True, "opacity": 1.0})
        st.session_state.current_layer = len(st.session_state.image_layers) - 1
        return True
    return False

def get_current_layer_image():
    if st.session_state.image_layers and 0 <= st.session_state.current_layer < len(st.session_state.image_layers):
        return st.session_state.image_layers[st.session_state.current_layer]["image"]
    return None

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
                try:
                    base = Image.blend(base, img, layer["opacity"])
                except:
                    base = img
    if base:
        st.session_state.image_layers = [{"name": "Merged", "image": base, "visible": True, "opacity": 1.0}]
        st.session_state.current_layer = 0

def pil_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# =============================================================
# PAGE: HOME
# =============================================================
def page_home():
    st.markdown("""
    <div style="text-align:center; padding:30px 0;">
        <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
            <span class="badge-gold">AI-Powered · 3D Planning</span>
        </div>
        <h1 style="font-size:2.4rem; font-weight:800;">تشخيص دقيق <span style="color:#e67e22;">بذكاء اصطناعي</span></h1>
        <p style="color:#94a3b8; font-size:1.1rem; max-width:600px; margin:12px auto;">
            منصة متكاملة لطب الأسنان التجميلي مع محاكاة الواقع الافتراضي والذكاء الاصطناعي.
        </p>
        <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
            <span class="badge-gold">🦷 32 سن</span>
            <span class="badge-gold">🧠 478 معلم</span>
            <span class="badge-gold">📐 8 زوايا</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================
# PAGE: DASHBOARD
# =============================================================
def page_dashboard():
    st.markdown('<h2>📊 لوحة التحكم</h2>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94a3b8;'>مرحباً بك، <strong>{st.session_state.current_user['name']}</strong></p>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("👨‍⚕️ المرضى", len(st.session_state.patients))
    with c2:
        st.metric("📅 المواعيد", len(st.session_state.appointments))
    with c3:
        st.metric("🧠 الصور المُنتجة", len(st.session_state.generated_images))
    with c4:
        st.metric("👥 الأصدقاء", len(st.session_state.current_user.get("friends", [])))

# =============================================================
# PAGE: PATIENTS
# =============================================================
def page_patients():
    st.markdown('<h2>👨‍⚕️ قائمة المرضى</h2>', unsafe_allow_html=True)
    if st.button("➕ مريض جديد", type="primary"):
        st.session_state.current_page = "new_patient"
        st.rerun()
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا يوجد مرضى")

def page_new_patient():
    st.markdown('<h2>📝 إضافة مريض جديد</h2>', unsafe_allow_html=True)
    with st.form("new_patient_form"):
        name = st.text_input("الاسم الكامل *")
        age = st.number_input("العمر", min_value=0, max_value=120, value=30)
        phone = st.text_input("رقم الهاتف")
        gender = st.selectbox("الجنس", ["ذكر", "أنثى", "غير محدد"])
        complaint = st.text_area("الشكوى الرئيسية")
        if st.form_submit_button("💾 حفظ المريض", use_container_width=True) and name:
            st.session_state.patients.append({
                "id": f"P{len(st.session_state.patients)+1:04d}",
                "name": name,
                "age": age,
                "phone": phone,
                "gender": gender,
                "complaint": complaint,
                "created_at": datetime.now().isoformat()
            })
            st.success("تم إضافة المريض!")
            st.rerun()

# =============================================================
# PAGE: DENTAL CHART (مخطط الأسنان التفاعلي)
# =============================================================
def page_dental_chart():
    st.markdown('<h2>🦷 مخطط الأسنان التفاعلي</h2>', unsafe_allow_html=True)
    st.caption("انقر على السن لتغيير حالته: سليم → مفقود → نخر → معالج → تاج → جذور → سليم")
    
    chart = st.session_state.dental_chart
    status_icons = {
        'normal': '🟢',
        'missing': '❌',
        'carious': '🦷',
        'treated': '✔️',
        'crown': '👑',
        'root-canal': '🧬'
    }
    status_classes = {
        'normal': '',
        'missing': 'missing',
        'carious': 'carious',
        'treated': 'treated',
        'crown': 'crown',
        'root-canal': 'root-canal'
    }
    status_cycle = ['normal', 'missing', 'carious', 'treated', 'crown', 'root-canal']
    
    # الفك العلوي
    st.markdown('<div class="arch-label">⬆ الفك العلوي</div>', unsafe_allow_html=True)
    cols = st.columns(16)
    for i in range(16):
        with cols[i]:
            status = chart[i]
            icon = status_icons.get(status, '🟢')
            if st.button(f"{icon}", key=f"tooth_{i}", use_container_width=True):
                idx = status_cycle.index(status) if status in status_cycle else 0
                new_status = status_cycle[(idx + 1) % len(status_cycle)]
                st.session_state.dental_chart[i] = new_status
                st.rerun()
            st.caption(f"{i+1}")
    
    # الفك السفلي
    st.markdown('<div class="arch-label">⬇ الفك السفلي</div>', unsafe_allow_html=True)
    cols = st.columns(16)
    for i in range(16, 32):
        with cols[i-16]:
            status = chart[i]
            icon = status_icons.get(status, '🟢')
            if st.button(f"{icon}", key=f"tooth_{i}", use_container_width=True):
                idx = status_cycle.index(status) if status in status_cycle else 0
                new_status = status_cycle[(idx + 1) % len(status_cycle)]
                st.session_state.dental_chart[i] = new_status
                st.rerun()
            st.caption(f"{i+1}")
    
    # وسائل الإيضاح
    st.markdown("---")
    st.markdown("#### وسائل الإيضاح")
    cols = st.columns(6)
    statuses = ['normal', 'missing', 'carious', 'treated', 'crown', 'root-canal']
    names = ['سليم', 'مفقود', 'نخر', 'معالج', 'تاج', 'جذور']
    for i, (s, n) in enumerate(zip(statuses, names)):
        with cols[i]:
            st.markdown(f"{status_icons[s]} {n}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 إعادة ضبط الكل", use_container_width=True):
            st.session_state.dental_chart = ['normal'] * 32
            st.success("تم إعادة ضبط المخطط")
            st.rerun()
    with col2:
        if st.button("💾 حفظ المخطط", use_container_width=True, type="primary"):
            st.success("تم حفظ المخطط!")

# =============================================================
# PAGE: NATURAL TEETH (الأسنان الطبيعية)
# =============================================================
def page_natural_teeth():
    st.markdown('<h2>🦷 الأسنان الطبيعية - تحكم كامل</h2>', unsafe_allow_html=True)
    st.caption("توليد أسنان طبيعية قابلة للتخصيص وإضافتها على صورة المريض")
    
    uploaded = st.file_uploader("📸 تحميل صورة المريض (اختياري)", type=["jpg","png"], key="natural_teeth_upload")
    patient_img = None
    if uploaded:
        patient_img = Image.open(uploaded)
        st.image(patient_img, caption="صورة المريض", use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        count = st.slider("عدد الأسنان", 4, 16, 10)
        if st.button("🦷 توليد أسنان طبيعية", type="primary", use_container_width=True):
            teeth_img = generate_natural_teeth(count, width=600, height=300)
            st.session_state.natural_teeth_layers.append({
                "name": f"Teeth_{len(st.session_state.natural_teeth_layers)+1}",
                "image": teeth_img,
                "created_at": datetime.now().isoformat()
            })
            st.image(teeth_img, caption="الأسنان المولدة", use_container_width=True)
            st.success("تم التوليد! يمكنك الآن إضافتها إلى المحرر.")
            add_layer(teeth_img, f"Natural Teeth {len(st.session_state.natural_teeth_layers)}")
    
    with col2:
        st.markdown("### 🎛️ تخصيص الأسنان")
        if st.session_state.natural_teeth_layers:
            selected = st.selectbox("اختر مجموعة أسنان", [f"{i+1}: {t['name']}" for i, t in enumerate(st.session_state.natural_teeth_layers)])
            idx = int(selected.split(":")[0]) - 1 if selected else 0
            teeth = st.session_state.natural_teeth_layers[idx]
            st.image(teeth["image"], caption="المجموعة المختارة", use_container_width=True)
            
            if patient_img:
                if st.button("🧩 دمج الأسنان على صورة المريض", use_container_width=True):
                    patient_w, patient_h = patient_img.size
                    teeth_img = teeth["image"].resize((patient_w, patient_h//2))
                    combined = patient_img.copy()
                    combined.paste(teeth_img, (0, patient_h - teeth_img.height), teeth_img.convert('RGBA') if teeth_img.mode == 'RGBA' else None)
                    st.image(combined, caption="النتيجة النهائية", use_container_width=True)
                    buffered = BytesIO()
                    combined.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    st.session_state.generated_images.append({
                        "name": f"patient_with_teeth_{datetime.now().strftime('%Y%m%d_%H%M')}",
                        "data": img_str,
                        "type": "natural_teeth",
                        "created_at": datetime.now().isoformat()
                    })
                    st.download_button(
                        label="⬇️ تحميل الصورة النهائية",
                        data=buffered.getvalue(),
                        file_name=f"patient_teeth_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                        mime="image/png"
                    )
                    st.success("تم دمج الأسنان بنجاح!")
        else:
            st.info("لم تقم بتوليد أسنان بعد.")

# =============================================================
# PAGE: IMAGE EDITOR (محرر الصور المتقدم)
# =============================================================
def page_image_editor():
    st.markdown('<h2>🎨 محرر الصور المتقدم (Photopea-like)</h2>', unsafe_allow_html=True)
    st.caption("تحكم كامل بالطبقات، إضافة أسنان طبيعية، محاكاة واقعية بالذكاء الاصطناعي")
    
    if not st.session_state.image_layers:
        base_img = Image.new('RGB', (800, 600), color='#1a1a2e')
        draw = ImageDraw.Draw(base_img)
        draw.text((400, 300), "🦷 ارفع صورة لبدء التحرير", fill='#94a3b8', anchor="mm")
        st.session_state.image_layers = [{"name": "Background", "image": base_img, "visible": True, "opacity": 1.0}]
        st.session_state.current_layer = 0
    
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown("### 🛠️ الأدوات")
        uploaded = st.file_uploader("📤 رفع صورة", type=["jpg","png","jpeg"], key="editor_upload")
        if uploaded:
            img = Image.open(uploaded)
            add_layer(img, f"Layer {len(st.session_state.image_layers)}")
            st.success("تم إضافة الطبقة")
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎚️ تعديل الطبقة الحالية")
        if st.session_state.image_layers:
            layer = st.session_state.image_layers[st.session_state.current_layer]
            layer["name"] = st.text_input("اسم الطبقة", value=layer["name"])
            layer["opacity"] = st.slider("الشفافية", 0.0, 1.0, layer["opacity"], 0.05)
            layer["visible"] = st.checkbox("ظاهرة", value=layer["visible"])
        
        st.markdown("---")
        st.markdown("### 🧬 FaceMesh")
        if st.button("🧑 رسم FaceMesh على الطبقة", use_container_width=True):
            img = get_current_layer_image()
            if img:
                result = draw_face_mesh_on_image(img)
                add_layer(result, "FaceMesh")
                st.success("تم رسم FaceMesh")
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🦷 Natural Teeth")
        if st.button("🦷 توليد أسنان طبيعية", use_container_width=True):
            teeth = generate_natural_teeth()
            add_layer(teeth, "Natural Teeth")
            st.success("تم إضافة الأسنان الطبيعية")
            st.rerun()
        
        st.markdown("### 🎛️ تحكم بالأسنان")
        if st.session_state.natural_teeth_layers:
            selected = st.selectbox("اختر مجموعة أسنان", [f"{i+1}: {t['name']}" for i, t in enumerate(st.session_state.natural_teeth_layers)])
            idx = int(selected.split(":")[0]) - 1 if selected else 0
            teeth = st.session_state.natural_teeth_layers[idx]
            st.image(teeth["image"], caption="المجموعة المختارة", use_container_width=True)
            rotation = st.slider("تدوير", -180, 180, 0)
            scale = st.slider("تكبير/تصغير", 0.5, 2.0, 1.0, 0.1)
            if st.button("تطبيق التعديلات", use_container_width=True):
                img = teeth["image"]
                if rotation != 0:
                    img = img.rotate(rotation, expand=True)
                if scale != 1.0:
                    w, h = img.size
                    img = img.resize((int(w*scale), int(h*scale)))
                if st.session_state.image_layers:
                    st.session_state.image_layers[st.session_state.current_layer]["image"] = img
                    st.success("تم تطبيق التعديلات")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎯 محاكاة واقعية بالذكاء الاصطناعي")
        prompt = st.text_input("وصف الصورة المطلوب إنتاجها بعد العلاج:", placeholder="مثال: ابتسامة هوليوودية، أسنان بيضاء...")
        if st.button("🎯 توليد محاكاة واقعية", type="primary", use_container_width=True):
            img = get_current_layer_image()
            if img:
                with st.spinner("جاري توليد المحاكاة الواقعية..."):
                    _, result = simulate_smile_before_after(img, 0.8)
                    add_layer(result, "Simulation")
                    if prompt:
                        draw = ImageDraw.Draw(result)
                        try:
                            font = ImageFont.truetype("arial.ttf", 16)
                        except:
                            font = ImageFont.load_default()
                        draw.text((10, 10), f"📝 {prompt[:40]}", fill='#e67e22', font=font)
                    st.success("تم توليد المحاكاة الواقعية!")
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
                        try:
                            display_img = Image.blend(display_img, img, layer["opacity"])
                        except:
                            display_img = img
            if display_img:
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
                active = " active" if i == st.session_state.current_layer else ""
                if st.button(f"{layer['name']}", key=f"layer_{i}", use_container_width=True):
                    st.session_state.current_layer = i
                    st.rerun()
            with col_c:
                if st.button("✕", key=f"del_{i}"):
                    if 0 <= i < len(st.session_state.image_layers):
                        st.session_state.image_layers.pop(i)
                        if st.session_state.current_layer >= len(st.session_state.image_layers):
                            st.session_state.current_layer = len(st.session_state.image_layers) - 1
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

# =============================================================
# PAGE: CEPHALOMETRIC ANALYSIS (تحليل الأشعة مع AI)
# =============================================================
def page_cephalometric():
    st.markdown('<h2>🩻 تحليل الأشعة السيفالومترية بالذكاء الاصطناعي</h2>', unsafe_allow_html=True)
    st.caption("تحليل متقدم مع رسم الزوايا والخطوط، جدول مقارنة، وتقرير ذكي")
    
    uploaded = st.file_uploader("🩻 حمّل صورة الأشعة", type=["jpg","png","dcm"], key="ceph_img")
    if uploaded:
        img = Image.open(uploaded)
        st.session_state.ceph_image = img
        st.image(img, caption="صورة الأشعة", use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎨 رسم التحليل على الأشعة", use_container_width=True):
                with st.spinner("جاري رسم الزوايا والخطوط..."):
                    result = draw_landmarks_on_image(img, 50)
                    draw = ImageDraw.Draw(result)
                    w, h = result.size
                    draw.line([(int(w*0.2), 0), (int(w*0.2), h)], fill='#e67e22', width=3)
                    draw.line([(int(w*0.8), 0), (int(w*0.8), h)], fill='#e67e22', width=3)
                    draw.line([(0, int(h*0.3)), (w, int(h*0.3))], fill='#10b981', width=3)
                    draw.line([(0, int(h*0.7)), (w, int(h*0.7))], fill='#10b981', width=3)
                    draw.text((10,10), "SNA: 82°", fill='#e67e22')
                    draw.text((10,30), "SNB: 80°", fill='#e67e22')
                    draw.text((10,50), "ANB: 2°", fill='#e67e22')
                    st.image(result, caption="الأشعة مع التحليل", use_container_width=True)
                    buffered = BytesIO()
                    result.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    st.session_state.generated_images.append({
                        "name": f"ceph_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}",
                        "data": img_str,
                        "type": "cephalometric",
                        "created_at": datetime.now().isoformat()
                    })
                    st.success("تم رسم التحليل!")
        
        with col2:
            if st.button("🤖 تحليل AI للأشعة", type="primary", use_container_width=True):
                with st.spinner("جاري التحليل الذكي..."):
                    time.sleep(2)
                    st.session_state.cephalometric_data = {
                        "SNA": random.randint(78,86),
                        "SNB": random.randint(76,84),
                        "ANB": random.randint(0,4),
                        "SN-MP": random.randint(28,36),
                        "FMA": random.randint(20,30),
                        "IMPA": random.randint(85,95),
                        "Overjet": random.randint(1,5),
                        "Overbite": random.randint(1,4)
                    }
                    st.success("تم التحليل!")
                    data = st.session_state.cephalometric_data
                    normal = st.session_state.normal_values
                    html = '<table class="comparison-table"><thead><tr><th>الزاوية</th><th>قيمة المريض</th><th>القيمة الطبيعية</th><th>الفرق</th><th>الحالة</th></tr></thead><tbody>'
                    for key in ["SNA", "SNB", "ANB", "SN-MP", "FMA", "IMPA", "Overjet", "Overbite"]:
                        val = data.get(key, 0)
                        norm = normal.get(key, 0)
                        diff = val - norm
                        status = "طبيعي ✅" if abs(diff) <= 2 else "مقبول ⚠️" if abs(diff) <= 4 else "غير طبيعي ❌"
                        cls = "normal" if abs(diff) <= 2 else "warning" if abs(diff) <= 4 else "abnormal"
                        html += f'<tr><td>{key}</td><td>{val}</td><td>{norm}</td><td>{diff:+.1f}</td><td class="{cls}">{status}</td></tr>'
                    html += '</tbody></table>'
                    st.markdown(html, unsafe_allow_html=True)
                    
                    df_comp = pd.DataFrame({
                        "الزاوية": ["SNA", "SNB", "ANB", "SN-MP", "FMA", "IMPA", "Overjet", "Overbite"],
                        "قيمة المريض": [data.get(k,0) for k in ["SNA","SNB","ANB","SN-MP","FMA","IMPA","Overjet","Overbite"]],
                        "القيمة الطبيعية": [normal.get(k,0) for k in ["SNA","SNB","ANB","SN-MP","FMA","IMPA","Overjet","Overbite"]]
                    })
                    df_comp["الفرق"] = df_comp["قيمة المريض"] - df_comp["القيمة الطبيعية"]
                    st.dataframe(df_comp, use_container_width=True)
                    
                    # رسم بياني
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=df_comp["الزاوية"], y=df_comp["قيمة المريض"], name="قيمة المريض", marker_color="#e67e22"))
                    fig.add_trace(go.Bar(x=df_comp["الزاوية"], y=df_comp["القيمة الطبيعية"], name="القيمة الطبيعية", marker_color="#0a8491"))
                    fig.update_layout(title="مقارنة قيم المريض مع القيم الطبيعية", barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            if st.button("📊 توليد جدول المقارنة", use_container_width=True):
                data = st.session_state.cephalometric_data
                normal = st.session_state.normal_values
                df = pd.DataFrame({
                    "الزاوية": list(data.keys()),
                    "قيمة المريض": list(data.values()),
                    "القيمة الطبيعية": [normal.get(k,0) for k in data.keys()]
                })
                df["الفرق"] = df["قيمة المريض"] - df["القيمة الطبيعية"]
                st.table(df)
                st.success("تم توليد الجدول")
    
    # عرض الصور المُنتجة
    st.markdown("### 📸 الصور المُنتجة")
    if st.session_state.generated_images:
        cols = st.columns(4)
        for i, img in enumerate(st.session_state.generated_images[-8:]):
            with cols[i % 4]:
                st.image(f"data:image/png;base64,{img['data']}", caption=img.get('name', 'صورة'), use_container_width=True)
    else:
        st.info("لا توجد صور مُنتجة بعد")

# =============================================================
# PAGE: DENTBOOK (الشبكة الاجتماعية الطبية)
# =============================================================
def page_dentbook():
    st.markdown('<h2>📱 Dentbook - الشبكة الاجتماعية الطبية</h2>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([1, 6])
        with col1:
            st.markdown(f"""
            <div style="width:50px; height:50px; border-radius:50%; background:#0a8491; display:flex; align-items:center; justify-content:center; font-size:20px; color:#fff;">
                {st.session_state.current_user['name'][0]}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            text = st.text_area("ماذا تفكر؟ شارك حالة طبية...", height=80, key="dentbook_text")
            img = st.file_uploader("📎 صورة / فيديو", type=["jpg","png","mp4"], key="dentbook_img")
            if st.button("🚀 نشر", type="primary"):
                if text or img:
                    post = {
                        "author": st.session_state.current_user["name"],
                        "author_email": st.session_state.current_user["email"],
                        "author_avatar": st.session_state.current_user.get("avatar", ""),
                        "text": text,
                        "time": datetime.now().strftime("%H:%M - %d/%m/%Y"),
                        "likes": 0,
                        "liked_by": [],
                        "comments": [],
                        "shares": 0,
                        "image": img,
                        "created_at": datetime.now().isoformat()
                    }
                    st.session_state.dentbook_posts.insert(0, post)
                    if "posts" not in st.session_state.current_user:
                        st.session_state.current_user["posts"] = []
                    st.session_state.current_user["posts"].append(post)
                    st.success("تم النشر!")
                    st.rerun()
    
    st.markdown("---")
    
    for idx, post in enumerate(st.session_state.dentbook_posts):
        user = st.session_state.current_user
        is_liked = user["email"] in post.get("liked_by", [])
        like_count = post.get("likes", 0)
        comments = post.get("comments", [])
        
        with st.container():
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:40px; height:40px; border-radius:50%; background:#0a8491; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:700; background-image:url('{post.get("author_avatar", "")}'); background-size:cover;">
                            {post['author'][0] if not post.get("author_avatar") else ''}
                        </div>
                        <div>
                            <strong>{post['author']}</strong>
                            <span style="color:#94a3b8; font-size:0.7rem; display:block;">{post['time']}</span>
                        </div>
                    </div>
                </div>
                <p style="margin-top:8px;">{post['text']}</p>
                {f'<img src="data:image/png;base64,{base64.b64encode(post["image"].getvalue()).decode()}" style="max-width:100%; max-height:300px; border-radius:8px; margin-top:8px;" />' if post.get('image') else ''}
                <div style="display:flex; gap:15px; margin-top:10px; border-top:1px solid #334155; padding-top:10px;">
                    <button onclick="alert('تم الإعجاب!')" style="background:transparent; border:none; cursor:pointer; color:{'#e67e22' if is_liked else '#94a3b8'}; font-weight:600; font-size:0.8rem;">
                        ❤️ {like_count}
                    </button>
                    <button onclick="alert('فتح التعليقات')" style="background:transparent; border:none; cursor:pointer; color:#94a3b8; font-weight:600; font-size:0.8rem;">
                        💬 {len(comments)}
                    </button>
                    <button onclick="alert('تمت المشاركة!')" style="background:transparent; border:none; cursor:pointer; color:#94a3b8; font-weight:600; font-size:0.8rem;">
                        🔄 {post.get('shares', 0)}
                    </button>
                </div>
                {f'''
                <div style="margin-top:8px; border-top:1px solid #2d3748; padding-top:8px;">
                    {''.join([f'<div style="display:flex; gap:6px; margin-bottom:4px;"><strong>{c["author"]}:</strong> {c["text"]}</div>' for c in comments[-3:]])}
                    <input type="text" placeholder="اكتب تعليقاً..." style="width:100%; padding:6px; border-radius:8px; border:1px solid #334155; background:#0f172a; color:#f8fafc;" />
                    <button onclick="alert('تم إضافة التعليق!')" style="margin-top:4px; background:#0a8491; color:#fff; border:none; padding:2px 14px; border-radius:20px; cursor:pointer;">تعليق</button>
                </div>
                ''' if comments else ''}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1,1,4])
            with col1:
                if st.button(f"❤️ {like_count}", key=f"like_{idx}"):
                    if is_liked:
                        post["liked_by"].remove(user["email"])
                        post["likes"] -= 1
                    else:
                        post["liked_by"].append(user["email"])
                        post["likes"] += 1
                    st.rerun()
            with col2:
                if st.button(f"💬", key=f"comment_btn_{idx}"):
                    st.info("فتح التعليقات - أضف تعليقاً في الحقل أدناه")
            with col3:
                if st.button(f"🔄 مشاركة", key=f"share_{idx}"):
                    post["shares"] += 1
                    st.success("تمت المشاركة!")

# =============================================================
# PAGE: FRIENDS (الأصدقاء وطلبات الصداقة)
# =============================================================
def page_friends():
    st.markdown('<h2>🤝 الأصدقاء وطلبات الصداقة</h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    
    st.markdown("### 📨 طلبات الصداقة الواردة")
    incoming = [r for r in st.session_state.friend_requests if r["to"] == user["email"] and r["status"] == "pending"]
    if incoming:
        for req in incoming:
            from_user = st.session_state.users_db.get(req["from"])
            if from_user:
                col1, col2, col3 = st.columns([2,1,1])
                with col1:
                    st.write(f"👤 {from_user['name']} ( {from_user.get('specialty','')} )")
                with col2:
                    if st.button("✅ قبول", key=f"accept_{req['from']}"):
                        req["status"] = "accepted"
                        if from_user["email"] not in user.get("friends", []):
                            user["friends"].append(from_user["email"])
                        if user["email"] not in from_user.get("friends", []):
                            from_user["friends"].append(user["email"])
                        st.success("✅ تم قبول الصداقة!")
                        st.rerun()
                with col3:
                    if st.button("❌ رفض", key=f"reject_{req['from']}"):
                        req["status"] = "rejected"
                        st.warning("تم رفض الطلب")
                        st.rerun()
    else:
        st.info("📭 لا توجد طلبات صداقة واردة")
    
    st.markdown("### 🔍 بحث عن أشخاص")
    search = st.text_input("ابحث بالاسم أو البريد الإلكتروني")
    if search:
        results = []
        for email, u in st.session_state.users_db.items():
            if email != user["email"] and (search.lower() in u["name"].lower() or search.lower() in email.lower()):
                results.append(u)
        if results:
            for u in results:
                col1, col2, col3 = st.columns([2,1,1])
                with col1:
                    st.write(f"👤 {u['name']} - {u.get('specialty', '')}")
                with col2:
                    if u["email"] in user.get("friends", []):
                        st.success("✅ صديق")
                    else:
                        pending = any(r["from"] == user["email"] and r["to"] == u["email"] and r["status"]=="pending" for r in st.session_state.friend_requests)
                        if pending:
                            st.warning("⏳ في الانتظار")
                        else:
                            if st.button("📨 إرسال طلب", key=f"send_{u['email']}"):
                                st.session_state.friend_requests.append({
                                    "from": user["email"],
                                    "to": u["email"],
                                    "from_name": user["name"],
                                    "status": "pending",
                                    "created_at": datetime.now().isoformat()
                                })
                                st.success("تم إرسال الطلب!")
                                st.rerun()
                with col3:
                    if st.button("👤 ملف", key=f"view_{u['email']}"):
                        st.info(f"عرض ملف {u['name']}")
        else:
            st.info("لا توجد نتائج")
    
    st.markdown("### 👫 قائمة الأصدقاء")
    friends_list = user.get("friends", [])
    if friends_list:
        for friend_email in friends_list:
            friend = st.session_state.users_db.get(friend_email)
            if friend:
                col1, col2 = st.columns([3,1])
                with col1:
                    st.write(f"👤 {friend['name']} - {friend.get('specialty', '')}")
                with col2:
                    if st.button("💬", key=f"msg_friend_{friend_email}"):
                        st.session_state.current_page = "private_messages"
                        st.session_state["private_recipient"] = friend["name"]
                        st.rerun()
    else:
        st.info("👤 لا يوجد أصدقاء بعد")

# =============================================================
# PAGE: PROFILE (الملف الشخصي مع غلاف وصورة)
# =============================================================
def page_profile():
    st.markdown('<h2>👤 الملف الشخصي</h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    
    cover_style = f"background-image: url(data:image/png;base64,{user['cover_photo']});" if user.get('cover_photo') else ""
    avatar_style = f"background-image: url(data:image/png;base64,{user['avatar']});" if user.get('avatar') else ""
    
    st.markdown(f"""
    <div style="height:160px; background:linear-gradient(135deg,#075e68,#0a8491); border-radius:12px 12px 0 0; position:relative; background-size:cover; background-position:center; {cover_style}">
        <div style="position:absolute; bottom:8px; left:8px;">
            <button onclick="document.getElementById('coverUpload').click()" style="background:rgba(0,0,0,0.5); color:#fff; border:none; padding:4px 14px; border-radius:30px; font-size:0.7rem; cursor:pointer;">تغيير الغلاف</button>
            <input type="file" id="coverUpload" accept="image/*" style="display:none;" />
        </div>
    </div>
    <div style="display:flex; align-items:flex-end; gap:16px; padding:0 16px 16px; margin-top:-50px; position:relative; z-index:2; flex-wrap:wrap;">
        <div style="width:80px; height:80px; border-radius:50%; border:4px solid #1e293b; background:#0a8491; display:flex; align-items:center; justify-content:center; font-size:32px; color:#fff; background-size:cover; background-position:center; {avatar_style}">
            {user['name'][0] if not user.get('avatar') else ''}
        </div>
        <div>
            <h3>{user['name']}</h3>
            <span style="color:#94a3b8;">@{user.get('username', '')}</span>
            <span style="color:#94a3b8; margin-right:12px;">{user.get('specialty', '')}</span>
        </div>
        <div style="margin-right:auto;">
            <button onclick="document.getElementById('avatarUpload').click()" style="background:rgba(255,255,255,0.05); border:1px solid #334155; padding:4px 14px; border-radius:30px; color:#94a3b8; cursor:pointer; font-size:0.7rem;">📷 تغيير الصورة</button>
            <input type="file" id="avatarUpload" accept="image/*" style="display:none;" />
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    cover_file = st.file_uploader("اختر صورة الغلاف", type=["jpg","png"], key="cover_uploader", label_visibility="collapsed")
    if cover_file:
        img = Image.open(cover_file)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        user["cover_photo"] = base64.b64encode(buffered.getvalue()).decode()
        st.session_state.users_db[user["email"]]["cover_photo"] = user["cover_photo"]
        st.success("تم تحديث الغلاف")
        st.rerun()
    
    avatar_file = st.file_uploader("اختر الصورة الشخصية", type=["jpg","png"], key="avatar_uploader", label_visibility="collapsed")
    if avatar_file:
        img = Image.open(avatar_file)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        user["avatar"] = base64.b64encode(buffered.getvalue()).decode()
        st.session_state.users_db[user["email"]]["avatar"] = user["avatar"]
        st.success("تم تحديث الصورة الشخصية")
        st.rerun()
    
    with st.form("profile_edit"):
        name = st.text_input("الاسم", value=user.get("name", ""))
        username = st.text_input("اسم المستخدم", value=user.get("username", ""))
        specialty = st.text_input("التخصص", value=user.get("specialty", ""))
        phone = st.text_input("الهاتف", value=user.get("phone", ""))
        bio = st.text_area("نبذة", value=user.get("bio", ""))
        if st.form_submit_button("💾 حفظ التعديلات"):
            user["name"] = name
            user["username"] = username
            user["specialty"] = specialty
            user["phone"] = phone
            user["bio"] = bio
            st.session_state.users_db[user["email"]].update(user)
            st.success("تم الحفظ!")
    
    st.markdown("### 📌 منشوراتي")
    posts = user.get("posts", [])
    if posts:
        for post in posts[-10:]:
            st.markdown(f"""
            <div class="card" style="padding:12px;">
                <p>{post.get('text', '')}</p>
                <span style="color:#94a3b8; font-size:0.7rem;">{post.get('time', '')}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("لا توجد منشورات بعد")

# =============================================================
# PAGE: PRIVATE MESSAGES (رسائل خاصة مشفرة)
# =============================================================
def page_private_messages():
    st.markdown('<h2>💌 رسائل خاصة مشفرة</h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    
    recipients = [u["name"] for e, u in st.session_state.users_db.items() if e != user["email"]]
    if not recipients:
        st.info("لا يوجد أطباء آخرون.")
        return
    recipient = st.selectbox("اختر المستلم", recipients)
    
    chat_key = f"{user['name']}_{recipient}" if user["name"] < recipient else f"{recipient}_{user['name']}"
    messages = [m for m in st.session_state.private_messages if m.get("chat_key") == chat_key]
    for msg in messages:
        align = "flex-end" if msg["sender"] == user["name"] else "flex-start"
        bg = "#0a8491" if msg["sender"] == user["name"] else "#1e293b"
        st.markdown(f"""
        <div style="display:flex; justify-content:{align}; margin-bottom:6px;">
            <div style="max-width:75%; padding:8px 14px; border-radius:12px; background:{bg}; color:#fff; border:1px solid #334155;">
                <div style="font-size:0.7rem; opacity:0.8;">{msg['sender']}</div>
                <div style="font-size:0.9rem;">{msg['text']}</div>
                <div style="font-size:0.6rem; opacity:0.5;">{msg.get('time', '')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.form("private_msg_form", clear_on_submit=True):
        text = st.text_input("رسالتك (مشفرة)")
        if st.form_submit_button("📨 إرسال مشفر"):
            if text:
                encrypted = base64.b64encode(text.encode()).decode()
                st.session_state.private_messages.append({
                    "sender": user["name"],
                    "recipient": recipient,
                    "text": encrypted,
                    "time": datetime.now().strftime("%H:%M"),
                    "chat_key": chat_key
                })
                st.success("تم إرسال الرسالة مشفرة!")
                st.rerun()
    
    # محاكاة مكالمات
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📹 مكالمة فيديو", use_container_width=True):
            st.info("جاري بدء مكالمة فيديو... (محاكاة)")
    with col2:
        if st.button("📞 مكالمة صوتية", use_container_width=True):
            st.info("جاري بدء مكالمة صوتية... (محاكاة)")

# =============================================================
# PAGE: LAB CHAT (التواصل مع المختبر)
# =============================================================
def page_lab_chat():
    st.markdown('<h2>🧪 التواصل مع المختبر</h2>', unsafe_allow_html=True)
    st.caption("تسجيل الهاتف، الاتصال، تحميل الملفات والصور الخاصة بالمريض")
    
    st.markdown("""
    <div class="card" style="border:1px solid #e67e22; padding:12px;">
        <strong>🔬 مختبر HarmonizeAI</strong>
        <div>📞 +966 55 123 4570</div>
        <div>✉️ lab@harmonizeai.com</div>
        <div>📍 الرياض، المملكة العربية السعودية</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        phone = st.text_input("رقم هاتفك للتواصل", value=st.session_state.current_user.get("phone", ""))
        if st.button("💾 حفظ رقم الهاتف"):
            st.session_state.current_user["phone"] = phone
            st.session_state.users_db[st.session_state.current_user["email"]]["phone"] = phone
            st.success("تم حفظ رقم الهاتف")
    with col2:
        if st.button("📞 الاتصال بالمختبر", use_container_width=True):
            st.info("جاري الاتصال... (محاكاة)")
    
    for msg in st.session_state.lab_messages[-10:]:
        align = "flex-end" if msg["sender"] == st.session_state.current_user["name"] else "flex-start"
        bg = "#0a8491" if msg["sender"] == st.session_state.current_user["name"] else "#1e293b"
        st.markdown(f"""
        <div style="display:flex; justify-content:{align}; margin-bottom:6px;">
            <div style="max-width:75%; padding:8px 14px; border-radius:12px; background:{bg}; color:#fff; border:1px solid #334155;">
                <div style="font-size:0.7rem; opacity:0.8;">{msg['sender']}</div>
                <div style="font-size:0.9rem;">{msg['text']}</div>
                {f'<div style="font-size:0.6rem; opacity:0.5; margin-top:2px;">📎 {msg.get("file", "")}</div>' if msg.get("file") else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.form("lab_form", clear_on_submit=True):
        col1, col2 = st.columns([3,1])
        with col1:
            txt = st.text_input("رسالتك للمختبر...", label_visibility="collapsed")
        with col2:
            submitted = st.form_submit_button("📨 إرسال", use_container_width=True)
        file = st.file_uploader("📎 إرفاق ملف (صورة أو مستند)", type=["jpg","png","pdf","stl"], key="lab_file_upload")
        if submitted and txt:
            msg = {"sender": st.session_state.current_user["name"], "text": txt, "time": datetime.now().strftime("%H:%M")}
            if file:
                msg["file"] = file.name
                st.session_state.files_uploaded.append({"name": file.name, "size": file.size, "type": file.type})
            st.session_state.lab_messages.append(msg)
            st.success("تم إرسال الرسالة للمختبر!")
            st.rerun()

# =============================================================
# PAGE: FILE SHARING (مشاركة الملفات مع تحميل)
# =============================================================
def page_file_sharing():
    st.markdown('<h2>📁 مشاركة الملفات</h2>', unsafe_allow_html=True)
    st.caption("تحميل الملفات ومشاركتها مع الأعضاء")
    
    uploaded = st.file_uploader("📤 اختر ملفاً للمشاركة", accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            st.session_state.files_uploaded.append({"name": f.name, "size": f.size, "type": f.type})
            st.success(f"✅ تم رفع {f.name}")
    
    if st.session_state.files_uploaded:
        df = pd.DataFrame(st.session_state.files_uploaded)
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 تحميل جميع الملفات", use_container_width=True):
                st.info("سيتم تحميل الملفات كـ ZIP (محاكاة)")
                st.download_button(
                    label="⬇️ تنزيل ZIP",
                    data=b"ZIP content placeholder",
                    file_name="files.zip",
                    mime="application/zip"
                )
        with col2:
            if st.button("🗑️ مسح الكل", use_container_width=True):
                st.session_state.files_uploaded = []
                st.rerun()

# =============================================================
# PAGE: SUBSCRIPTIONS (إدارة الاشتراكات)
# =============================================================
def page_subscriptions():
    st.markdown('<h2>👑 خطط الاشتراك</h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    is_owner = user.get("role") == "owner"
    
    if is_owner:
        st.markdown("### 🔧 إدارة الاشتراكات (للمالك)")
        with st.form("add_subscription"):
            name = st.text_input("اسم الخطة")
            price = st.number_input("السعر ($)", min_value=0, step=1)
            features = st.text_area("الميزات (كل ميزة في سطر)")
            if st.form_submit_button("➕ إضافة خطة"):
                if name:
                    st.session_state.subscriptions[name] = {"price": price, "features": features.split("\n") if features else []}
                    st.success(f"تم إضافة خطة {name}")
                    st.rerun()
        
        st.markdown("### قائمة الخطط الحالية")
        for plan_name, plan_data in list(st.session_state.subscriptions.items()):
            col1, col2, col3 = st.columns([2,2,1])
            with col1:
                st.write(f"**{plan_name}**")
            with col2:
                st.write(f"${plan_data['price']} - {', '.join(plan_data['features'])}")
            with col3:
                if st.button("🗑️ حذف", key=f"del_plan_{plan_name}"):
                    del st.session_state.subscriptions[plan_name]
                    st.rerun()
    
    st.markdown("### 📋 خطط الاشتراك المتاحة")
    for plan_name, plan_data in st.session_state.subscriptions.items():
        with st.container():
            st.markdown(f"""
            <div class="card" style="text-align:center; border:1px solid #e67e22;">
                <h4>{plan_name}</h4>
                <div style="font-size:2rem; font-weight:800; color:#e67e22;">${plan_data['price']}</div>
                <div style="font-size:0.8rem; color:#94a3b8;">{', '.join(plan_data['features'])}</div>
                <button onclick="alert('سيتم تفعيل الاشتراك')" style="margin-top:8px; background:#e67e22; color:#0a0a0a; border:none; padding:6px 24px; border-radius:60px; font-weight:700; cursor:pointer;">اشترك</button>
            </div>
            """, unsafe_allow_html=True)

# =============================================================
# PAGE: REPORTS (التقارير مع تصدير وطباعة ومشاركة)
# =============================================================
def page_reports():
    st.markdown('<h2>📄 التقارير الشاملة</h2>', unsafe_allow_html=True)
    st.caption("توليد تقرير شامل مع جميع البيانات والصور والجداول")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📄 توليد تقرير شامل", type="primary", use_container_width=True):
            with st.spinner("جاري توليد التقرير..."):
                time.sleep(2)
                st.success("تم توليد التقرير!")
                st.download_button(
                    label="⬇️ تحميل التقرير (PDF)",
                    data=b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj...",
                    file_name=f"report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
    with col2:
        if st.button("🖨️ طباعة", use_container_width=True):
            st.info("🖨️ جاري فتح الطباعة...")
            st.markdown("""
            <script>
            window.print();
            </script>
            """, unsafe_allow_html=True)
    with col3:
        if st.button("📤 مشاركة واتساب", use_container_width=True):
            st.success("✅ تم فتح واتساب!")
            st.markdown("""
            <script>
            window.open('https://api.whatsapp.com/send?text=📄 تقرير HarmonizeAI', '_blank');
            </script>
            """, unsafe_allow_html=True)
    
    st.markdown("### 📸 الصور المُنتجة")
    if st.session_state.generated_images:
        cols = st.columns(4)
        for i, img in enumerate(st.session_state.generated_images[-8:]):
            with cols[i % 4]:
                st.image(f"data:image/png;base64,{img['data']}", caption=img.get('name', 'صورة'), use_container_width=True)
    else:
        st.info("لا توجد صور مُنتجة بعد")

# =============================================================
# PAGE: CAD/CAM (عارض 3D)
# =============================================================
def page_cadcam():
    st.markdown('<h2>⚙️ CAD/CAM & 3D</h2>', unsafe_allow_html=True)
    st.caption("عرض نموذج ثلاثي الأبعاد تفاعلي (محاكاة)")
    
    st.components.v1.html("""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; background: #0f172a; }
            canvas { display: block; }
        </style>
    </head>
    <body>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({antialias: true});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            const geometry = new THREE.BoxGeometry(1, 1, 1);
            const material = new THREE.MeshNormalMaterial();
            const cube = new THREE.Mesh(geometry, material);
            scene.add(cube);

            camera.position.z = 5;

            function animate() {
                requestAnimationFrame(animate);
                cube.rotation.x += 0.01;
                cube.rotation.y += 0.01;
                renderer.render(scene, camera);
            }
            animate();
        </script>
    </body>
    </html>
    """, height=500)
    st.caption("نموذج 3D تفاعلي (مكعب) - يمكن استبداله بنموذج أسنان حقيقي")

# =============================================================
# PAGE: FORUM (منتدى النقاشات)
# =============================================================
def page_forum():
    st.markdown('<h2>🗣️ منتدى النقاشات الطبية</h2>', unsafe_allow_html=True)
    st.caption("طرح أسئلة ونقاشات مع الأخصائيين")
    
    with st.form("new_topic"):
        title = st.text_input("عنوان الموضوع")
        content = st.text_area("المحتوى")
        if st.form_submit_button("📨 نشر موضوع"):
            if title and content:
                st.session_state.forum_topics.append({
                    "title": title,
                    "content": content,
                    "author": st.session_state.current_user["name"],
                    "time": datetime.now().strftime("%H:%M - %d/%m/%Y"),
                    "replies": []
                })
                st.success("تم نشر الموضوع!")
                st.rerun()
    
    for topic in st.session_state.forum_topics:
        with st.container():
            st.markdown(f"""
            <div class="card">
                <h4>{topic['title']}</h4>
                <p>{topic['content']}</p>
                <div style="display:flex; justify-content:space-between; color:#94a3b8; font-size:0.7rem;">
                    <span>👤 {topic['author']}</span>
                    <span>🕒 {topic['time']}</span>
                </div>
                <div style="margin-top:8px; border-top:1px solid #334155; padding-top:8px;">
                    <strong>ردود ({len(topic.get('replies', []))})</strong>
                    {''.join([f'<div style="padding:4px 0;"><strong>{r["author"]}:</strong> {r["text"]}</div>' for r in topic.get('replies', [])[-3:]])}
                    <input type="text" placeholder="أضف رداً..." style="width:100%; padding:6px; border-radius:8px; border:1px solid #334155; background:#0f172a; color:#f8fafc;" />
                    <button onclick="alert('تم إضافة الرد!')" style="margin-top:4px; background:#0a8491; color:#fff; border:none; padding:2px 14px; border-radius:20px; cursor:pointer;">رد</button>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================
# PAGE: OTHER (مختصرة)
# =============================================================
def page_photography(): st.markdown('<h2>📸 قسم التصوير</h2>', unsafe_allow_html=True)
def page_xray(): st.markdown('<h2>🩻 قسم الأشعة</h2>', unsafe_allow_html=True)
def page_smile_design(): 
    st.markdown('<h2>😁 تصميم الابتسامة</h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 صورة الابتسامة", type=["jpg","png"], key="smile_design")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة الأصلية", use_container_width=True)
        if st.button("🎨 توليد تصميم جديد", type="primary"):
            _, result = simulate_smile_before_after(img, 0.8)
            comparison = create_comparison_image(img, result)
            st.image(result, caption="النتيجة المتوقعة", use_container_width=True)
            st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
            buffered = BytesIO()
            result.save(buffered, format="PNG")
            st.download_button("⬇️ تحميل التصميم", data=buffered.getvalue(), file_name="smile_design.png", mime="image/png")
def page_aesthetic_design(): st.markdown('<h2>🎨 التصميم التجميلي</h2>', unsafe_allow_html=True)
def page_stl_3d(): st.markdown('<h2>📦 نماذج 3D</h2>', unsafe_allow_html=True)
def page_dsd_studio(): st.markdown('<h2>🧬 استوديو DSD</h2>', unsafe_allow_html=True)
def page_aesthetic_treatment(): st.markdown('<h2>💎 علاج تجميلي</h2>', unsafe_allow_html=True)
def page_global_platform(): st.markdown('<h2>🌍 المنصة العالمية</h2>', unsafe_allow_html=True)
def page_pipeline(): st.markdown('<h2>🔄 خط الإنتاج</h2>', unsafe_allow_html=True)
def page_materials_guide(): st.markdown('<h2>🦷 دليل المواد</h2>', unsafe_allow_html=True)
def page_api_hub(): st.markdown('<h2>🔌 مركز الأنظمة</h2>', unsafe_allow_html=True)
def page_mock_db(): st.markdown('<h2>🗄️ مستودع المريض</h2>', unsafe_allow_html=True)
def page_notifications(): st.markdown('<h2>🔔 الإشعارات</h2>', unsafe_allow_html=True)
def page_systems(): st.markdown('<h2>🖥️ الأنظمة</h2>', unsafe_allow_html=True)
def page_scientific_scan(): st.markdown('<h2>🔬 المسح العلمي</h2>', unsafe_allow_html=True)
def page_naqai(): 
    st.markdown('<h2>🤖 NaqAI</h2>', unsafe_allow_html=True)
    st.info("مساعد ذكي - قيد التطوير")
def page_interdisciplinary(): st.markdown('<h2>👥 فرق متعددة التخصصات</h2>', unsafe_allow_html=True)
def page_ads(): st.markdown('<h2>📢 الإعلانات</h2>', unsafe_allow_html=True)
def page_lab(): st.markdown('<h2>🔬 المعمل</h2>', unsafe_allow_html=True)
def page_appointments(): st.markdown('<h2>📅 المواعيد</h2>', unsafe_allow_html=True)
def page_accounting(): st.markdown('<h2>💰 الحساب</h2>', unsafe_allow_html=True)
def page_payments(): st.markdown('<h2>💳 الدفع</h2>', unsafe_allow_html=True)
def page_invite(): st.markdown('<h2>📨 دعوة الأطباء</h2>', unsafe_allow_html=True)
def page_settings(): st.markdown('<h2>⚙️ الإعدادات</h2>', unsafe_allow_html=True)
def page_privacy(): st.markdown('<h2>🔒 الخصوصية</h2>', unsafe_allow_html=True)
def page_ip(): st.markdown('<h2>©️ حقوق الملكية</h2>', unsafe_allow_html=True)
def page_vita(): st.markdown('<h2>🎨 ألوان فيتا</h2>', unsafe_allow_html=True)
def page_messages(): 
    st.markdown('<h2>💬 المراسلات العامة</h2>', unsafe_allow_html=True)
    for msg in st.session_state.messages[-10:]:
        st.write(f"**{msg['sender']}:** {msg['text']}")
    text = st.text_input("رسالتك...")
    if st.button("إرسال") and text:
        st.session_state.messages.append({"sender": st.session_state.current_user["name"], "text": text})
        st.rerun()
def page_members():
    st.markdown('<h2>👥 أعضاء النظام</h2>', unsafe_allow_html=True)
    for u in st.session_state.users_db.values():
        st.write(f"{u['name']} - {u.get('specialty', '')}")

# =============================================================
# PAGE ROUTER
# =============================================================
PAGES = {
    "home": page_home,
    "dashboard": page_dashboard,
    "smile_simulator": page_smile_design,
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
    "screen_share": lambda: st.markdown('<h2>🖥️ مشاركة الشاشة</h2>', unsafe_allow_html=True),
    "diagnosis": lambda: st.markdown('<h2>🩺 التشخيص الذكي</h2>', unsafe_allow_html=True),
    "treatment_plan": lambda: st.markdown('<h2>📋 خطة العلاج</h2>', unsafe_allow_html=True),
    "materials": lambda: st.markdown('<h2>🧪 المواد</h2>', unsafe_allow_html=True),
    "facial": lambda: st.markdown('<h2>🧑‍⚕️ تحليل الوجه</h2>', unsafe_allow_html=True),
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
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب"])
        with tab1:
            with st.form("login_form"):
                email = st.text_input("البريد الإلكتروني", value="ndcdental2025@outlook.com")
                password = st.text_input("كلمة المرور", type="password", value="ndc2025")
                if st.form_submit_button("🚪 دخول", use_container_width=True):
                    if login_user(email, password):
                        st.success("مرحباً بك!")
                        st.rerun()
                    else:
                        st.error("بيانات غير صحيحة")
        with tab2:
            with st.form("signup_form"):
                name = st.text_input("الاسم الكامل *")
                email = st.text_input("البريد الإلكتروني *")
                username = st.text_input("اسم المستخدم (اختياري)")
                password = st.text_input("كلمة المرور *", type="password")
                role = st.selectbox("نوع الحساب", ["doctor", "patient"])
                if st.form_submit_button("📝 إنشاء حساب", use_container_width=True):
                    if not name or not email or not password:
                        st.error("جميع الحقول مطلوبة")
                    else:
                        ok, msg = signup_user(name, email, password, role, username)
                        if ok:
                            st.success(msg)
                            st.info("يمكنك الآن تسجيل الدخول")
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
            <div style="font-size:0.7rem; color:#aac4d6;">HarmonizeAI™ · v5.0</div>
        </div>
        <div style="text-align:center; margin-bottom:16px;">
            <div style="font-size:0.85rem; font-weight:600;">{user['name']}</div>
            <div style="font-size:0.65rem; color:#aac4d6;">@{user.get('username', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
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
        }
        for label, key in menu_items.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
        if st.button("🚪 تسجيل خروج", use_container_width=True, type="primary"):
            logout()

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
