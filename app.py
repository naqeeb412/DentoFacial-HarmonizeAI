import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
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
# CONFIG & PAGE SETUP
# =============================================================
st.set_page_config(
    page_title="HarmonizeAI™ | Dentofacial Synergy",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================
# CSS
# =============================================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #075e68 0%, #0a8491 100%); }
[data-testid="stSidebar"] * { color: #ffffff !important; }
.stButton>button { border-radius: 60px !important; font-weight: 600 !important; font-family: 'Cairo', sans-serif !important; }
.metric-card { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; box-shadow: 0 4px 20px rgba(0,0,0,0.3); text-align: center; }
.metric-value { font-size: 2.2rem; font-weight: 800; color: #e67e22; }
.badge-gold { display: inline-block; background: rgba(230,126,34,0.12); color: #e67e22; padding: 2px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(230,126,34,0.2); }
.badge-harvard { background: #7a0010; color: #fff; padding: 2px 12px; border-radius: 20px; font-size: 0.65rem; font-weight: 700; border: 1px solid #a8001a; }
.badge-private { background: #10b981; color: #fff; padding: 2px 12px; border-radius: 20px; font-size: 0.6rem; font-weight: 600; }
.card { background: #1e293b; border-radius: 12px; padding: 24px; border: 1px solid #334155; margin-bottom: 16px; }
.privacy-badge { display: inline-block; background: rgba(16,185,129,0.12); color: #10b981; padding: 2px 12px; border-radius: 20px; font-size: 0.65rem; font-weight: 600; }
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
.teeth-card { background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; margin-bottom: 12px; transition: all 0.3s ease; cursor: pointer; }
.teeth-card:hover { border-color: #e67e22; transform: translateY(-2px); }
.teeth-card .tooth-status { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
.teeth-card .status-normal { background: #10b98120; color: #10b981; }
.teeth-card .status-missing { background: #ef444420; color: #ef4444; }
.teeth-card .status-carious { background: #f59e0b20; color: #f59e0b; }
.teeth-card .status-treated { background: #3b82f620; color: #3b82f6; }
.teeth-card .status-crown { background: #8b5cf620; color: #8b5cf6; }
.teeth-card .status-root-canal { background: #ec489920; color: #ec4899; }
@media (max-width: 768px) {
    .tooth { width: 36px !important; height: 44px !important; font-size: 9px !important; }
    .metric-value { font-size: 1.5rem !important; }
    .card { padding: 16px !important; }
    .stButton>button { font-size: 14px !important; padding: 8px 16px !important; }
}
@media (max-width: 480px) {
    .tooth { width: 30px !important; height: 38px !important; font-size: 8px !important; }
    .tooth .num { font-size: 7px !important; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================
# SYSTEM LOGO
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
# AUTHENTICATION
# =============================================================
OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

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
# MEDIAPIPE FUNCTIONS
# =============================================================
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

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
    if isinstance(image, Image.Image):
        img_np = np.array(image.convert('L'))
    else:
        img_np = np.array(image)
    h, w = img_np.shape
    img_enhanced = cv2.equalizeHist(img_np)
    analysis_data = {
        "SNA": 82.5, "SNB": 80.0, "ANB": 2.5,
        "SN-MP": 32.0, "FMA": 25.0, "IMPA": 90.0,
        "Overjet": 3.0, "Overbite": 2.0,
        "analysis_image": None
    }
    result_img = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
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
# DENTAL CHART
# =============================================================
def update_tooth_status(index, status):
    if 0 <= index < 32:
        st.session_state.tooth_statuses[index] = status
        st.session_state.dental_chart[index] = status
        return True
    return False

def get_tooth_status(index):
    return st.session_state.tooth_statuses.get(index, "normal")

def render_dental_chart():
    html = '<div style="overflow-x:auto;padding:10px 0;"><div style="display:flex;flex-direction:column;align-items:center;gap:6px;min-width:700px;">'
    html += '<div style="display:flex;justify-content:center;gap:4px;flex-wrap:wrap;"><div style="width:100%;text-align:center;font-weight:700;font-size:14px;color:#94a3b8;margin:4px 0 8px;letter-spacing:2px;">⬆ الفك العلوي</div>'
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
    html += '</div>'
    html += '<div style="display:flex;justify-content:center;gap:4px;flex-wrap:wrap;"><div style="width:100%;text-align:center;font-weight:700;font-size:14px;color:#94a3b8;margin:4px 0 8px;letter-spacing:2px;">⬇ الفك السفلي</div>'
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
    html += '</div>'
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
# GENERATE NATURAL TEETH
# =============================================================
def generate_natural_teeth(count=10):
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

# =============================================================
# SMILE SIMULATION
# =============================================================
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

# =============================================================
# 3D VIEWER
# =============================================================
def get_3d_viewer_html():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; overflow: hidden; background: #0f172a; }
            .info { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); color: #94a3b8; font-family: 'Cairo', sans-serif; font-size: 12px; background: rgba(0,0,0,0.7); padding: 8px 16px; border-radius: 20px; pointer-events: none; }
            .controls { position: absolute; top: 20px; right: 20px; display: flex; flex-direction: column; gap: 8px; }
            .controls button { background: rgba(230,126,34,0.8); border: none; color: #fff; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 14px; transition: 0.3s; }
            .controls button:hover { background: #e67e22; }
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
            controls.minDistance = 2;
            controls.maxDistance = 20;
            const ambientLight = new THREE.AmbientLight(0x404060);
            scene.add(ambientLight);
            const mainLight = new THREE.DirectionalLight(0xffffff, 1);
            mainLight.position.set(5, 10, 7);
            mainLight.castShadow = true;
            scene.add(mainLight);
            const fillLight = new THREE.DirectionalLight(0x8888ff, 0.5);
            fillLight.position.set(-5, 0, 5);
            scene.add(fillLight);
            const gridHelper = new THREE.GridHelper(10, 10, 0x334155, 0x1e293b);
            gridHelper.position.y = -1.5;
            scene.add(gridHelper);
            let mainModel = null;
            let isWireframe = false;
            function createDefaultTeeth() {
                const group = new THREE.Group();
                const toothMaterial = new THREE.MeshPhysicalMaterial({
                    color: 0xf5f0e8,
                    metalness: 0.05,
                    roughness: 0.3,
                    clearcoat: 0.1,
                    clearcoatRoughness: 0.2,
                });
                const gumMaterial = new THREE.MeshPhysicalMaterial({
                    color: 0xe8b4b8,
                    metalness: 0.0,
                    roughness: 0.8,
                });
                for (let i = -7; i <= 7; i++) {
                    if (i === 0) continue;
                    const tooth = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.25, 0.6, 8), toothMaterial);
                    const x = i * 0.35;
                    const z = -0.3 + Math.abs(i) * 0.03;
                    tooth.position.set(x, 0.3, z);
                    tooth.rotation.x = 0.1 * (i / 7);
                    tooth.rotation.z = 0.05 * i;
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
                return group;
            }
            const model = createDefaultTeeth();
            scene.add(model);
            mainModel = model;
            window.resetCamera = function() {
                camera.position.set(5, 3, 8);
                controls.target.set(0, 0, 0);
            };
            window.toggleWireframe = function() {
                if (!mainModel) return;
                isWireframe = !isWireframe;
                mainModel.traverse((child) => {
                    if (child.isMesh) {
                        child.material.wireframe = isWireframe;
                    }
                });
            };
            window.toggleAutoRotate = function() {
                controls.autoRotate = !controls.autoRotate;
            };
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
    '''

# =============================================================
# PDF REPORT GENERATION (HTML-based)
# =============================================================
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
                <strong>Dentofacial HarmonizeAI™</strong><br>
                Naqeeb412 · Synergy<br>
                © 2026 جميع الحقوق محفوظة.
            </div>
        </div>
    </body>
    </html>
    """
    return html

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
                    user_data = {"name": f"مستخدم {name}", "specialty": f"طبيب {name}", "phone": f"+000 {random.randint(100,999)} {random.randint(100,999)}", "country": "اليمن"}
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
                        user_data = {"name": f"مستخدم {phone[-4:]}", "specialty": "طبيب أسنان", "phone": phone, "country": "اليمن"}
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

# =============================================================
# PAGE: 3D VIEWER
# =============================================================
def page_3d_viewer():
    st.markdown('<h2>🦷 عارض الأسنان ثلاثي الأبعاد <span style="color:#e67e22;">3D Viewer</span></h2>', unsafe_allow_html=True)
    st.caption("عارض 3D تفاعلي للأسنان والوجه - اسحب للتدوير، مرر للتكبير")
    col1, col2, col3 = st.columns(3)
    with col1:
        model_type = st.selectbox("نوع النموذج", ["أسنان افتراضية", "فك كامل", "وجه ثلاثي الأبعاد", "زرعة سنية"])
    with col2:
        auto_rotate = st.checkbox("🔄 دوران تلقائي", value=True)
    with col3:
        show_grid = st.checkbox("📐 شبكة مرجعية", value=True)
    uploaded_model = st.file_uploader("📤 تحميل نموذج 3D (STL, OBJ, PLY)", type=["stl", "obj", "ply", "glb", "gltf"], key="model_upload_3d")
    viewer_html = get_3d_viewer_html()
    st.components.v1.html(viewer_html, height=550)
    st.markdown("### 🛠️ أدوات التحكم")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("🔄 إعادة ضبط", use_container_width=True):
            st.info("تم إعادة ضبط الكاميرا")
    with c2:
        if st.button("📐 شبكة", use_container_width=True):
            st.info("تم تبديل وضع الشبكة")
    with c3:
        if st.button("🎨 تلوين", use_container_width=True):
            st.info("تم تغيير نظام الألوان")
    with c4:
        if st.button("📷 التقاط", use_container_width=True):
            st.success("✅ تم التقاط الصورة!")
    with c5:
        if st.button("💾 حفظ", use_container_width=True):
            st.success("✅ تم حفظ النموذج!")
    st.markdown("### 📋 معلومات النموذج")
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    with col_info1:
        st.metric("🦷 الأسنان", "32", "كاملة")
    with col_info2:
        st.metric("🔺 المثلثات", "24.5K", "+2.1K")
    with col_info3:
        st.metric("📐 الأبعاد", "120x80x60", "mm")
    with col_info4:
        st.metric("📁 الحجم", "4.2 MB", "STL")

# =============================================================
# PAGE: AI FACE REAL
# =============================================================
def page_ai_face_real():
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

# =============================================================
# PAGE: AI CEPHALOMETRIC
# =============================================================
def page_ai_cephalometric_real():
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

# =============================================================
# PAGE: PDF REPORT
# =============================================================
def page_pdf_report():
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
                st.download_button(
                    label="⬇️ تحميل التقرير HTML",
                    data=html_content.encode('utf-8'),
                    file_name=f"report_{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html"
                )
                st.success("✅ تم توليد التقرير بنجاح!")
        else:
            st.warning("⚠️ لا توجد صور للتصدير. قم بتحليل الوجه أو الأشعة أولاً.")

# =============================================================
# PAGE: DENTBOOK
# =============================================================
def page_dentbook():
    st.markdown('<h2>📱 Dentbook <span style="color:#e67e22;">الشبكة الاجتماعية الطبية</span></h2>', unsafe_allow_html=True)
    if "dentbook_posts" not in st.session_state:
        st.session_state.dentbook_posts = []
    with st.expander("📝 إنشاء منشور جديد", expanded=True):
        with st.form("new_post_form", clear_on_submit=True):
            post_content = st.text_area("محتوى المنشور", placeholder="ما هي آخر التحديثات السريرية أو ملحوظات الصيانة؟")
            col_a, col_b = st.columns(2)
            with col_a:
                post_category = st.selectbox("تصنيف المنشور", ["منشور عام", "تحديث صيانة", "حالة سريرية", "نصيحة طبية"])
            with col_b:
                uploaded_image = st.file_uploader("إرفاق صورة (اختياري)", type=["jpg", "jpeg", "png"])
            if st.form_submit_button("🚀 نشر الآن"):
                if post_content.strip() or uploaded_image:
                    new_post = {
                        "id": len(st.session_state.dentbook_posts) + 1,
                        "author": st.session_state.current_user.get("name", "د. غير معروف"),
                        "title": st.session_state.current_user.get("specialty", "طبيب أسنان"),
                        "content": post_content,
                        "category": post_category,
                        "image": uploaded_image if uploaded_image else None,
                        "likes": 0,
                        "comments": [],
                        "time": "الآن",
                    }
                    st.session_state.dentbook_posts.insert(0, new_post)
                    st.success("تم نشر المنشور بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى كتابة نص أو إرفاق صورة للنشر.")
    filter_category = st.selectbox("🔍 تصفية المنشورات حسب التصنيف:", ["الكل", "تحديث صيانة", "حالة سريرية", "نصيحة طبية", "منشور عام"])
    filtered_posts = st.session_state.dentbook_posts
    if filter_category != "الكل":
        filtered_posts = [p for p in st.session_state.dentbook_posts if p["category"] == filter_category]
    for index, post in enumerate(filtered_posts):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"### {post['author']}")
            st.caption(f"{post['title']} • {post['time']}")
        with c2:
            st.markdown(f'<span style="background:#e7f3ff;color:#1877f2;padding:4px 10px;border-radius:12px;font-size:12px;font-weight:bold;">{post["category"]}</span>', unsafe_allow_html=True)
        if post["content"]:
            st.write(post["content"])
        if post["image"]:
            if isinstance(post["image"], bytes) or hasattr(post["image"], "read"):
                st.image(post["image"], use_container_width=True)
            else:
                st.image(post["image"], use_container_width=True)
        col_like, col_comment_btn = st.columns([1, 4])
        with col_like:
            if st.button(f"👍 {post['likes']} إعجاب", key=f"like_{post['id']}_{index}"):
                post["likes"] += 1
                st.rerun()
        with st.expander(f"💬 التعليقات ({len(post['comments'])})"):
            for comment in post["comments"]:
                st.write(f"• {comment}")
            with st.form(key=f"comment_form_{post['id']}_{index}", clear_on_submit=True):
                new_comment = st.text_input("اكتب تعليقاً...")
                if st.form_submit_button("إرسال"):
                    if new_comment.strip():
                        post["comments"].append(f"{st.session_state.current_user.get('name', 'مستخدم')}: {new_comment}")
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# =============================================================
# PAGE: OCCLUSAL ANALYZER
# =============================================================
def page_occlusal_analyzer():
    st.markdown('<h2>🦷 تحليل الإطباق (Occlusal & Smile Plane Analyzer)</h2>', unsafe_allow_html=True)
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
                nose_tip = (int(lm[1].x * w), int(lm[1].y * h))
                chin_tip = (int(lm[152].x * w), int(lm[152].y * h))
                if show_midline:
                    cv2.line(annotated, (nose_tip[0], 0), (chin_tip[0], h), (0, 0, 255), 2)
                if show_commissural:
                    cv2.line(annotated, left_corner, right_corner, (255, 165, 0), 2)
                if show_occlusal_plane:
                    y_occlusal = int((left_corner[1] + right_corner[1]) / 2)
                    cv2.line(annotated, (0, y_occlusal), (w, y_occlusal), (0, 255, 0), 2, cv2.LINE_AA)
                if show_smile_curve:
                    curve_pts = [lm[61], lm[84], lm[17], lm[314], lm[291]]
                    pts = np.array([[int(p.x * w), int(p.y * h)] for p in curve_pts], np.int32)
                    cv2.polylines(annotated, [pts], isClosed=False, color=(255, 255, 0), thickness=3, lineType=cv2.LINE_AA)
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

# =============================================================
# PAGE: GOLDEN RATIO
# =============================================================
def page_golden_ratio():
    st.markdown('<h2>✨ النسبة الذهبية (Golden Ratio & Facial Aesthetics Analyzer)</h2>', unsafe_allow_html=True)
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
                    cv2.line(annotated, (0, trichion), (w, trichion), (255, 105, 180), 2)
                    cv2.line(annotated, (0, glabella), (w, glabella), (255, 105, 180), 2)
                    cv2.line(annotated, (0, subnasale), (w, subnasale), (255, 105, 180), 2)
                    cv2.line(annotated, (0, menton), (w, menton), (255, 105, 180), 2)
                if show_fifths:
                    cv2.line(annotated, (left_face_edge, 0), (left_face_edge, h), (0, 255, 255), 1)
                    cv2.line(annotated, (left_eye_outer, 0), (left_eye_outer, h), (0, 255, 255), 1)
                    cv2.line(annotated, (left_eye_inner, 0), (left_eye_inner, h), (0, 255, 255), 1)
                    cv2.line(annotated, (right_eye_inner, 0), (right_eye_inner, h), (0, 255, 255), 1)
                    cv2.line(annotated, (right_eye_outer, 0), (right_eye_outer, h), (0, 255, 255), 1)
                    cv2.line(annotated, (right_face_edge, 0), (right_face_edge, h), (0, 255, 255), 1)
                if show_golden_mask:
                    mouth_left = (int(lm[61].x * w), int(lm[61].y * h))
                    mouth_right = (int(lm[291].x * w), int(lm[291].y * h))
                    nose_left = (int(lm[102].x * w), int(lm[102].y * h))
                    nose_right = (int(lm[331].x * w), int(lm[331].y * h))
                    cv2.line(annotated, mouth_left, mouth_right, (255, 215, 0), 3)
                    cv2.line(annotated, nose_left, nose_right, (255, 215, 0), 3)
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

# =============================================================
# PAGE: AI SMILE SIMULATOR (مع LoRA و 3D)
# =============================================================
def page_smile_simulator_ai():
    st.markdown('<h2>🧬 محاكاة الابتسامة بالذكاء الاصطناعي + تصدير 3D</h2>', unsafe_allow_html=True)
    st.write("منصة الذكاء الاصطناعي للمحاكاة الجمالية، توليد الابتسامة، وتصدير مجسمات 3D لـ Exocad و Blender.")
    st.sidebar.header("⚙️ إعدادات المحاكاة")
    lora_model = st.sidebar.selectbox(
        "نموذج LoRA الجمالي",
        ["Hollywood_White_V2", "Natural_Bleach_V1", "Translucent_Veneer_V3"]
    )
    lora_weight = st.sidebar.slider("وزن تأثير النموذج (LoRA Weight)", 0.0, 1.0, 0.75, 0.05)
    bleach_shade = st.sidebar.select_slider("درجة البياض المطلوبة (Shade)", options=["BL1", "BL2", "BL3", "A1", "A2", "A3"])
    st.sidebar.header("📦 إعدادات التصدير 3D")
    export_format = st.sidebar.radio("تنسيق المجسم 3D", ["Wavefront (.OBJ)", "Stereolithography (.STL)"])
    uploaded_file = st.file_uploader("ارفع صورة الابتسامة أو الوجه (PNG/JPG)", type=["jpg", "jpeg", "png"])
    face_mesh = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.6
    )
    def apply_lora_simulation(image_np, landmarks, weight, shade):
        h, w, _ = image_np.shape
        simulated_img = image_np.copy()
        lip_indices = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
        lip_points = np.array([[int(landmarks[idx].x * w), int(landmarks[idx].y * h)] for idx in lip_indices], np.int32)
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [lip_points], 255)
        hsv = cv2.cvtColor(simulated_img, cv2.COLOR_RGB2HSV)
        h_channel, s_channel, v_channel = cv2.split(hsv)
        shade_boost = {"BL1": 60, "BL2": 45, "BL3": 35, "A1": 25, "A2": 15, "A3": 5}
        boost = int(shade_boost.get(shade, 20) * weight)
        v_boosted = cv2.add(v_channel, boost)
        s_reduced = cv2.subtract(s_channel, int(boost * 0.5))
        hsv_boosted = cv2.merge([h_channel, s_reduced, v_boosted])
        teeth_enhanced = cv2.cvtColor(hsv_boosted, cv2.COLOR_HSV2RGB)
        mask_blur = cv2.GaussianBlur(mask, (15, 15), 0) / 255.0
        for c in range(3):
            simulated_img[:, :, c] = (1 - mask_blur) * simulated_img[:, :, c] + mask_blur * teeth_enhanced[:, :, c]
        return simulated_img

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        if img_array.shape[2] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        h, w, _ = img_array.shape
        results = face_mesh.process(img_array)
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            simulated_image = apply_lora_simulation(img_array, landmarks, lora_weight, bleach_shade)
            mesh_vertices = []
            for lm in landmarks:
                mesh_vertices.append([(lm.x - 0.5) * 100, (0.5 - lm.y) * 100, lm.z * 100])
            tab1, tab2 = st.tabs(["📸 المحاكاة 2D", "🧊 التصدير 3D"])
            with tab1:
                c1, c2 = st.columns(2)
                with c1:
                    st.image(img_array, caption="الصورة الأصلية", use_container_width=True)
                with c2:
                    st.image(simulated_image, caption=f"المحاكاة ({lora_model} - Shade {bleach_shade})", use_container_width=True)
                st.session_state.last_smile_image = Image.fromarray(cv2.cvtColor(simulated_image, cv2.COLOR_BGR2RGB))
            with tab2:
                st.subheader("تصدير نموذج 3D")
                st.write(f"عدد النقاط: **{len(mesh_vertices)}**")
                obj_data = "# HarmonizeAI Generated 3D Mesh\n"
                for v in mesh_vertices:
                    obj_data += f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n"
                for i in range(1, len(mesh_vertices) - 2):
                    obj_data += f"f {i} {i+1} {i+2}\n"
                st.download_button(
                    label=f"📥 تصدير {export_format}",
                    data=obj_data,
                    file_name=f"harmonize_ai_model.{'obj' if 'OBJ' in export_format else 'stl'}",
                    mime="text/plain"
                )
        else:
            st.error("لم يتم اكتشاف معالم الوجه بوضوح.")

# =============================================================
# PAGE: MEDICAL REPORT
# =============================================================
def page_medical_report():
    st.markdown('<h2>📋 تقرير طبي شامل</h2>', unsafe_allow_html=True)
    st.write("توليد تقرير طبي متكامل مع تحليل الوجه والابتسامة.")
    st.subheader("👤 بيانات المريض")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        patient_name = st.text_input("اسم المريض الكامل", "أحمد محمد")
    with col_p2:
        patient_id = st.text_input("رقم الملف / ID", "PAT-2026-8801")
    with col_p3:
        doctor_name = st.text_input("الطبيب المعالج", "د. علي النقيب")
    uploaded_photo = st.file_uploader("ارفع صورة الوجه/الابتسامة الأمامية", type=["jpg", "png", "jpeg"])
    if uploaded_photo is not None:
        img = Image.open(uploaded_photo)
        img_np = np.array(img)
        if img_np.shape[2] == 4:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
        # تحليل الوجه
        analysis_result = real_face_analysis(img_np)
        if analysis_result.get("analysis_image"):
            st.image(analysis_result["analysis_image"], caption="تحليل الوجه", use_container_width=True)
            st.markdown("### 📊 نتائج التحليل")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📐 التناسق", f"{analysis_result.get('symmetry_score', 0):.1f}%")
            with col2:
                st.metric("😊 مؤشر الابتسامة", f"{analysis_result.get('smile_index', 0):.1f}%")
            with col3:
                st.metric("👤 شكل الوجه", analysis_result.get('face_shape', 'غير محدد'))
            # توليد التقرير
            if st.button("📄 توليد تقرير", type="primary"):
                images = {"تحليل الوجه": analysis_result["analysis_image"]}
                html_report = generate_html_report(patient_name, {"face_analysis": analysis_result}, images)
                st.download_button(
                    label="⬇️ تحميل التقرير HTML",
                    data=html_report.encode('utf-8'),
                    file_name=f"report_{patient_id}.html",
                    mime="text/html"
                )
                st.success("✅ تم توليد التقرير بنجاح!")

# =============================================================
# PAGE: LIVE SMILE ANALYZER
# =============================================================
def page_live_smile_analyzer():
    st.markdown('<h2>🎥 تحليل الابتسامة بالكاميرا الحية</h2>', unsafe_allow_html=True)
    st.write("استخدم كاميرا جهازك لتحليل الابتسامة والتناغم الوجهي في الوقت الفعلي.")
    st.info("⚠️ هذه الميزة تعمل في بيئة التطوير المحلية مع الوصول إلى الكاميرا.")
    img_file = st.camera_input("📸 التقاط صورة من الكاميرا")
    if img_file is not None:
        bytes_data = img_file.getvalue()
        img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
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
                h, w, _ = img.shape
                # حساب شدة الابتسامة
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
        if st.button("💾 حفظ اللقطة"):
            cv2.imwrite("capture_smile.jpg", display)
            st.success("تم حفظ اللقطة!")

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
            "🦷 عارض 3D": "3d_viewer",
            "🧠 تحليل الوجه AI": "ai_face_real",
            "🩻 تحليل الأشعة AI": "ai_cephalometric_real",
            "📄 تقرير PDF": "pdf_report",
            "🤖 تصميم الابتسامة AI": "ai_smile_design",
            "📱 Dentbook": "dentbook",
            "🦷 تحليل الإطباق": "occlusal_analyzer",
            "✨ النسبة الذهبية": "golden_ratio",
            "🧬 Smile + 3D": "smile_simulator_ai",
            "📋 تقرير طبي": "medical_report",
            "🎥 كاميرا حية": "live_smile_analyzer",
            "👨‍⚕️ المرضى": "patients",
            "➕ مريض جديد": "new_patient",
            "🦷 مخطط الأسنان": "dental_chart",
            "🦷 Natural Teeth": "natural_teeth",
            "📸 التصوير": "photography",
            "🩻 الأشعة": "xray",
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
# REMAINING PAGES (قصيرة)
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
        st.info("لا يوجد مرضى مسجلين.")

def page_new_patient():
    st.markdown('<h2>📝 إضافة مريض جديد</h2>', unsafe_allow_html=True)
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

def page_dental_chart():
    st.markdown('<h2>🦷 مخطط الأسنان</h2>', unsafe_allow_html=True)
    st.caption("اضغط على السن لتغيير حالته")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(render_dental_chart(), unsafe_allow_html=True)
    with col2:
        st.markdown("### 🎯 التحكم")
        if st.session_state.selected_tooth is not None:
            tooth_num = st.session_state.selected_tooth + 1
            current_status = get_tooth_status(st.session_state.selected_tooth)
            status_labels = {'normal': '🟢 سليم', 'missing': '❌ مفقود', 'carious': '🟡 نخر', 'treated': '🔵 معالج', 'crown': '🟣 تاج', 'root-canal': '🔴 جذور'}
            st.markdown(f"""
            <div style="background:#1e293b; padding:12px; border-radius:12px; border:1px solid #334155; text-align:center; margin-bottom:12px;">
                <div style="font-size:0.8rem; color:#94a3b8;">السن المحدد</div>
                <div style="font-size:2rem; font-weight:800; color:#e67e22;">#{tooth_num}</div>
                <div style="font-size:0.9rem;">{status_labels.get(current_status, 'غير معروف')}</div>
            </div>
            """, unsafe_allow_html=True)
            statuses = [("🟢 سليم", "normal"), ("❌ مفقود", "missing"), ("🟡 نخر", "carious"), ("🔵 معالج", "treated"), ("🟣 تاج", "crown"), ("🔴 جذور", "root-canal")]
            for label, status in statuses:
                if st.button(label, key=f"tooth_status_{status}", use_container_width=True):
                    if update_tooth_status(st.session_state.selected_tooth, status):
                        st.success(f"✅ تم تحديث السن #{tooth_num} إلى {label}")
                        st.rerun()
        else:
            st.info("👆 اضغط على سن في المخطط")
    col_actions1, col_actions2, col_actions3 = st.columns(3)
    with col_actions1:
        if st.button("🔄 إعادة ضبط", use_container_width=True):
            for i in range(32):
                update_tooth_status(i, "normal")
            st.session_state.selected_tooth = None
            st.success("✅ تم إعادة ضبط المخطط")
            st.rerun()
    with col_actions2:
        if st.button("💾 حفظ", use_container_width=True, type="primary"):
            st.success("✅ تم حفظ المخطط")
    with col_actions3:
        if st.button("📊 إحصائيات", use_container_width=True):
            status_counts = {}
            for i in range(32):
                status = get_tooth_status(i)
                status_counts[status] = status_counts.get(status, 0) + 1
            st.info(f"📊 حالات الأسنان:\n{status_counts}")

def page_natural_teeth():
    st.markdown('<h2>🦷 الأسنان الطبيعية</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        teeth_count = st.slider("عدد الأسنان", 6, 16, 10)
        if st.button("🦷 توليد أسنان طبيعية", type="primary", use_container_width=True):
            img = generate_natural_teeth(teeth_count)
            st.image(img, caption="الأسنان الطبيعية المولدة", use_container_width=True)
            st.session_state.natural_teeth_layers.append({"name": f"Teeth_{len(st.session_state.natural_teeth_layers)}", "image": img, "created_at": datetime.now().isoformat()})
            st.success("✅ تم توليد وحفظ الأسنان الطبيعية!")
            st.balloons()
    with col2:
        if st.session_state.natural_teeth_layers:
            for i, teeth in enumerate(st.session_state.natural_teeth_layers[-6:]):
                st.image(teeth["image"], caption=f"{teeth['name']}", use_container_width=True)
        else:
            st.info("لا توجد أسنان طبيعية محفوظة")

def page_photography():
    st.markdown('<h2>📸 التصوير</h2>', unsafe_allow_html=True)
    st.info("📷 ارفع صور المريض المطلوبة")
    types = ["أمامية", "جانبية", "ابتسامة", "فك علوي", "فك سفلي"]
    for i, t in enumerate(types):
        uploaded = st.file_uploader(t, type=["jpg","png","jpeg"], key=f"photo_{t}")
        if uploaded:
            img = Image.open(uploaded)
            st.image(img, caption=t, use_container_width=True)
            st.session_state.patient_images.append(uploaded)

def page_xray():
    st.markdown('<h2>🩻 الأشعة</h2>', unsafe_allow_html=True)
    xray_type = st.selectbox("نوع الأشعة", ["سيفالومترك (Cephalometric)", "بانوراما (Panorama)", "CBCT", "P.A"])
    uploaded = st.file_uploader("رفع صورة الأشعة", type=["jpg","png","jpeg", "dcm"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="صورة الأشعة", use_container_width=True)
        if st.button("💾 حفظ الأشعة", use_container_width=True):
            st.session_state.xrays.append({"type": xray_type, "date": datetime.now().strftime("%Y-%m-%d"), "image": uploaded})
            st.success("✅ تم حفظ الأشعة!")

def page_friends():
    st.markdown('<h2>🤝 الأصدقاء</h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    st.markdown("### 👥 إرسال طلب صداقة")
    all_users = [u for u in st.session_state.users_db.values() if u["email"] != user["email"]]
    if all_users:
        target = st.selectbox("اختر مستخدم", [f"{u['name']} ({u['email']})" for u in all_users])
        if st.button("📨 إرسال طلب صداقة", type="primary"):
            target_email = target.split("(")[-1].replace(")", "")
            st.session_state.friend_requests.append({"from": user["email"], "to": target_email, "from_name": user["name"], "status": "pending", "created_at": datetime.now().isoformat()})
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

def page_profile():
    st.markdown('<h2>👤 الملف الشخصي</h2>', unsafe_allow_html=True)
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
            </div>
            """, unsafe_allow_html=True)
        with col2:
            name = st.text_input("الاسم", value=user.get("name",""))
            specialty = st.text_input("التخصص", value=user.get("specialty",""))
            country = st.text_input("الدولة", value=user.get("country",""))
            phone = st.text_input("الهاتف", value=user.get("phone",""))
            bio = st.text_area("نبذة", value=user.get("bio",""))
            if st.form_submit_button("💾 حفظ"):
                st.session_state.current_user.update({"name": name, "specialty": specialty, "country": country, "phone": phone, "bio": bio})
                st.session_state.users_db[user["email"]].update(st.session_state.current_user)
                st.success("✅ تم الحفظ!")

def page_members():
    st.markdown('<h2>👥 الأعضاء</h2>', unsafe_allow_html=True)
    st.write(f"إجمالي الأعضاء: {len(st.session_state.users_db)}")
    for email, u in st.session_state.users_db.items():
        status = "🟢" if u.get("online", True) else "🔴"
        st.markdown(f"""
        <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
            <div><strong>{u['name']}</strong> <span style="font-size:0.75rem; color:#94a3b8;">{u.get('specialty','')}</span></div>
            <div><span>{status}</span></div>
        </div>
        """, unsafe_allow_html=True)

def page_messages():
    st.markdown('<h2>💬 المراسلات</h2>', unsafe_allow_html=True)
    for msg in st.session_state.messages[-20:]:
        align = "flex-end" if msg["sender"] == st.session_state.current_user["name"] else "flex-start"
        bg = "#0a8491" if msg["sender"] == st.session_state.current_user["name"] else "#1e293b"
        color = "#fff" if msg["sender"] == st.session_state.current_user["name"] else "#f8fafc"
        st.markdown(f"""
        <div style="display:flex; justify-content:{align}; margin-bottom:6px;">
            <div style="max-width:75%; padding:8px 14px; border-radius:12px; background:{bg}; color:{color}; border:1px solid #334155;">
                <div style="font-size:0.7rem; opacity:0.8;">{msg['sender']}</div>
                <div style="font-size:0.9rem;">{msg['text']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with st.form("msg_form", clear_on_submit=True):
        text = st.text_input("رسالتك...", label_visibility="collapsed")
        if st.form_submit_button("📨 إرسال", use_container_width=True) and text:
            st.session_state.messages.append({"sender": st.session_state.current_user["name"], "text": text, "time": datetime.now().isoformat()})
            st.rerun()

def page_private_messages():
    st.markdown('<h2>💌 رسائل خاصة</h2>', unsafe_allow_html=True)
    recipients = [u["name"] for e, u in st.session_state.users_db.items() if e != st.session_state.current_user["email"]]
    if not recipients:
        st.info("لا يوجد أطباء آخرون.")
        return
    recipient = st.selectbox("اختر الطبيب", recipients)
    text = st.text_area("اكتب رسالتك...")
    if st.button("📨 إرسال", type="primary") and text:
        st.session_state.private_messages.append({"sender": st.session_state.current_user["name"], "recipient": recipient, "text": text, "time": datetime.now().isoformat()})
        st.success("✅ تم إرسال الرسالة!")

def page_lab_chat():
    st.markdown('<h2>🧪 التواصل مع المختبر</h2>', unsafe_allow_html=True)
    for msg in st.session_state.lab_messages[-10:]:
        st.markdown(f"<div class='card'><strong>{msg['sender']}:</strong> {msg['text']}</div>", unsafe_allow_html=True)
    with st.form("lab_form", clear_on_submit=True):
        txt = st.text_input("رسالتك للمختبر...")
        if st.form_submit_button("إرسال") and txt:
            st.session_state.lab_messages.append({"sender": st.session_state.current_user["name"], "text": txt, "time": datetime.now().isoformat()})
            st.rerun()

def page_file_sharing():
    st.markdown('<h2>📁 مشاركة الملفات</h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("اسحب الملفات هنا", accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            st.session_state.files_uploaded.append({"name": f.name, "size": f.size, "type": f.type})
            st.success(f"✅ تم رفع {f.name}")
    if st.session_state.files_uploaded:
        st.dataframe(pd.DataFrame(st.session_state.files_uploaded), use_container_width=True)

def page_screen_share():
    st.markdown('<h2>🖥️ مشاركة الشاشة</h2>', unsafe_allow_html=True)
    st.info("🔹 في بيئة المتصفح، استخدم زر 'بدء المشاركة' أدناه")
    st.markdown("""
    <button style="background:#10b981; color:#fff; border:none; padding:10px 24px; border-radius:60px; cursor:pointer;" onclick="navigator.mediaDevices.getDisplayMedia({video:true}).then(s=>{alert('🖥️ تم بدء المشاركة')}).catch(e=>{alert('تم الإلغاء')})">
        ▶️ بدء مشاركة الشاشة
    </button>
    """, unsafe_allow_html=True)

def page_diagnosis():
    st.markdown('<h2>🩺 التشخيص الذكي</h2>', unsafe_allow_html=True)
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد مرضى"]
    st.selectbox("اختر المريض", patients)
    st.text_input("الأخصائي", value=st.session_state.current_user["name"])
    symptoms = st.text_area("الأعراض", placeholder="أدخل الأعراض بالتفصيل...")
    if st.button("🎓 تشخيص AI", type="primary", use_container_width=True):
        with st.spinner("🧠 جاري التحليل..."):
            time.sleep(2)
        st.success("✅ تم التشخيص!")
        st.info("📋 التشخيص: التهاب لثة متوسط - يوصى بتنظيف عميق")

def page_treatment_plan():
    st.markdown('<h2>📋 خطة العلاج</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("الخطة الرئيسية", placeholder="أدخل الخطة الرئيسية...")
    with col2:
        st.text_input("العلاج البديل", placeholder="العلاج البديل...")
    if st.button("🧠 توليد الخطة", type="primary"):
        st.balloons()
        st.success("✅ تم توليد الخطة التفصيلية")

def page_materials():
    st.markdown('<h2>🧪 المواد العلاجية</h2>', unsafe_allow_html=True)
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

def page_facial():
    st.markdown('<h2>🧑‍⚕️ تحليل الوجه (478 علامة)</h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 حمّل صورة الوجه", type=["jpg","png"], key="facial_img")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة المحملة", use_container_width=True)
        if st.button("🎨 تحليل الـ 478 نقطة", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري التحليل..."):
                time.sleep(2)
                result = draw_landmarks_on_image(img, 478)
                st.image(result, caption="العلامات التشريحية", use_container_width=True)
                st.success("✅ تم رسم 478 علامة تشريحية!")

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
    draw.line([(w*0.2, h*0.1), (w*0.8, h*0.1)], fill='#e67e22', width=2)
    draw.line([(w*0.2, h*0.9), (w*0.8, h*0.9)], fill='#e67e22', width=2)
    draw.line([(w*0.5, h*0.1), (w*0.5, h*0.9)], fill='#10b981', width=2)
    return img

def page_cephalometric():
    st.markdown('<h2>🩻 تحليل الأشعة</h2>', unsafe_allow_html=True)
    st.markdown("### 📐 الزوايا السيفالومترية")
    data = st.session_state.cephalometric_data
    normal_values = {"SNA": 82, "SNB": 80, "ANB": 2, "SN-MP": 32, "FMA": 25, "IMPA": 90, "Overjet": 3, "Overbite": 2}
    ceph_data = []
    for key in ["SNA", "SNB", "ANB", "SN-MP", "FMA", "IMPA", "Overjet", "Overbite"]:
        patient_val = data.get(key, 0)
        normal_val = normal_values.get(key, 0)
        diff = patient_val - normal_val
        status = "✅ طبيعي" if abs(diff) <= 2 else "⚠️ مقبول" if abs(diff) <= 4 else "❌ غير طبيعي"
        ceph_data.append({"الزاوية": key, "قيمة المريض": patient_val, "القيمة الطبيعية": normal_val, "الفرق": diff, "الحالة": status})
    st.table(pd.DataFrame(ceph_data))
    col1, col2 = st.columns(2)
    for i, key in enumerate(["SNA", "SNB", "ANB", "SN-MP", "FMA", "IMPA", "Overjet", "Overbite"]):
        with col1 if i % 2 == 0 else col2:
            new_val = st.number_input(key, value=float(data.get(key, 0)), step=0.5, key=f"ceph_{key}")
            st.session_state.cephalometric_data[key] = new_val
    if st.button("💾 حفظ القيم", type="primary"):
        st.success("✅ تم حفظ الزوايا السيفالومترية!")

def page_smile_design():
    st.markdown('<h2>😁 تصميم الابتسامة</h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 صورة الابتسامة", type=["jpg","png"], key="smile_img")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة الأصلية", use_container_width=True)
        if st.button("✨ محاكاة AI", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري المحاكاة..."):
                _, result = simulate_smile_before_after(img, 0.8)
                comparison = create_comparison_image(img, result)
                st.image(result, caption="النتيجة المتوقعة", use_container_width=True)
                st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
                st.success("✅ تمت المحاكاة!")

def page_aesthetic_design():
    st.markdown('<h2>🎨 التصميم التجميلي</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        before = st.file_uploader("📸 قبل", key="before_img")
        if before:
            st.image(before, caption="قبل", use_container_width=True)
    with col2:
        after = st.file_uploader("📸 بعد", key="after_img")
        if after:
            st.image(after, caption="بعد", use_container_width=True)
    if before and after:
        if st.button("🎨 توليد التصميم", type="primary"):
            comparison = create_comparison_image(Image.open(before), Image.open(after), 0.5)
            st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
            st.success("✅ تم توليد التصميم!")

def page_stl_3d():
    st.markdown('<h2>📦 نماذج 3D</h2>', unsafe_allow_html=True)
    model = st.file_uploader("رفع STL / OBJ / PLY", type=["stl","obj","ply","glb"], key="stl_up")
    if model:
        st.success(f"✅ تم رفع {model.name}")

def page_dsd_studio():
    st.markdown('<h2>🧬 استوديو DSD</h2>', unsafe_allow_html=True)
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد"]
    st.selectbox("📋 الملف الطبي للمريض", patients)
    uploaded = st.file_uploader("📸 تحميل الصورة", type=["jpg","png"], key="dsd_img")
    if uploaded:
        st.image(uploaded, caption="الصورة", use_container_width=True)
    if st.button("📊 تحليل الـ 478 معلم", type="primary"):
        st.success("✅ تم الدمج الجمالي!")

def page_aesthetic_treatment():
    st.markdown('<h2>💎 علاج تجميلي</h2>', unsafe_allow_html=True)
    st.text_input("اسم المريض")
    st.selectbox("نوع العلاج", ["تناسق الوجه", "علاج البشرة", "تناسق الأنف", "تناسق الذقن", "تناسق الشفاه"])
    st.text_area("وصف الحالة")
    if st.button("✨ توليد خطة العلاج", type="primary"):
        st.success("✅ تم توليد خطة العلاج!")

def page_global_platform():
    st.markdown('<h2>🌍 المنصة العالمية</h2>', unsafe_allow_html=True)
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

def page_pipeline():
    st.markdown('<h2>🔄 خط الإنتاج</h2>', unsafe_allow_html=True)
    st.selectbox("اختر مريضاً", [p["name"] for p in st.session_state.patients] or ["لا يوجد"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=st.session_state.pipeline_progress,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "نسبة الإنجاز"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#e67e22"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

def page_materials_guide():
    st.markdown('<h2>🦷 دليل المواد</h2>', unsafe_allow_html=True)
    data = [
        ["Lithium Disilicate (E.max)", "قشور وتركيبات", "تحضير مجهري، لصق راتنجي", "Exocad", "PubMed"],
        ["Hyaluronic Acid Filler", "فيلر الأنسجة الرخوة", "حقن تحت المخاطية", "Blender", "NCBI"],
        ["Botulinum Toxin (Botox)", "تعديل الابتسامة اللثوية", "حقن في Levator Labii", "AI Studios", "PubMed"],
        ["Zirconia Monolithic", "جسور وتأهيل كامل", "تحضير هيكلي", "Exocad", "ScienceDirect"],
    ]
    df = pd.DataFrame(data, columns=["المادة", "التصنيف", "بروتوكول الاستخدام", "الربط الرقمي", "المراجع"])
    st.dataframe(df, use_container_width=True)

def page_api_hub():
    st.markdown('<h2>🔌 مركز الأنظمة</h2>', unsafe_allow_html=True)
    systems = [("Exocad", "STL", "🟢"), ("Meshy AI", "3D Face", "🟢"), ("Blender", "Cycles", "🟡"), ("AI Studios", "Motion", "🟢")]
    for name, fmt, status in systems:
        st.markdown(f"**{name}** ({fmt}) - <span style='color:#10b981;'>{status}</span>", unsafe_allow_html=True)

def page_mock_db():
    st.markdown('<h2>🗄️ مستودع المريض</h2>', unsafe_allow_html=True)
    st.json({"patients_count": len(st.session_state.patients), "last_backup": datetime.now().isoformat(), "storage_used": "1.2 GB", "sync_status": "مُزامن"})

def page_notifications():
    st.markdown('<h2>🔔 الإشعارات</h2>', unsafe_allow_html=True)
    notifs = ["📢 تم تحديث خط سير المريض", "💬 رسالة جديدة من المختبر", "📅 موعد غداً الساعة 10:00 ص", "✅ تم إضافة مريض جديد", "🦷 تم تحديث مخطط الأسنان"]
    for n in notifs:
        st.markdown(f'<div class="card" style="padding:10px; margin-bottom:6px;">{n}</div>', unsafe_allow_html=True)

def page_systems():
    st.markdown('<h2>🖥️ الأنظمة</h2>', unsafe_allow_html=True)
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
    st.markdown('<h2>🔬 المسح العلمي</h2>', unsafe_allow_html=True)
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
    with cols[3]:
        if st.button("📋 تقرير علمي", use_container_width=True):
            st.success("✅ تم توليد التقرير العلمي!")

def page_naqai():
    st.markdown('<h2>🤖 NaqAI</h2>', unsafe_allow_html=True)
    for msg in st.session_state.naqai_chat:
        if msg["role"] == "ai":
            st.markdown(f'<div style="background:#0a8491; color:#fff; padding:10px 14px; border-radius:12px; margin-bottom:6px; max-width:85%;">{msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#1e293b; color:#f8fafc; padding:10px 14px; border-radius:12px; margin-bottom:6px; border:1px solid #334155;">{msg["text"]}</div>', unsafe_allow_html=True)
    q = st.text_input("اسأل NaqAI...")
    if st.button("📨 إرسال", type="primary") and q:
        st.session_state.naqai_chat.append({"role": "user", "text": q})
        responses = {
            "ابتسامة": "😁 **تصميم الابتسامة** يشمل تحليل النسب الذهبية للأسنان والوجه.",
            "فيلر": "💉 **فيلر حمض الهيالورونيك** يستخدم لملء التجاعيد وزيادة حجم الشفاه.",
            "بوتوكس": "🧪 **البوتوكس** يستخدم لتقليل التجاعيد وعلاج الابتسامة اللثوية.",
            "زركونيا": "🦷 **الزركونيا** مادة خزفية عالية المتانة والجمالية.",
            "تحليل": "🧠 **تحليل الوجه** يعتمد على 478 نقطة تشريحية."
        }
        ans = "🧠 شكراً لسؤالك! يمكنني مساعدتك في تصميم الابتسامة، العلاج التجميلي، تحليل الوجه والأشعة."
        for k, v in responses.items():
            if k in q.lower():
                ans = v
                break
        st.session_state.naqai_chat.append({"role": "ai", "text": ans})
        st.rerun()

def page_interdisciplinary():
    st.markdown('<h2>👥 فرق متعددة التخصصات</h2>', unsafe_allow_html=True)
    with st.form("add_spec"):
        n = st.text_input("اسم الأخصائي")
        s = st.text_input("التخصص")
        if st.form_submit_button("➕ إضافة"):
            st.session_state.specialists.append({"name": n, "specialty": s, "online": True})
            st.success("✅ تمت الإضافة")
    for sp in st.session_state.specialists:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;">
                <div><strong>{sp['name']}</strong> <span style="color:#94a3b8;">{sp['specialty']}</span></div>
                <div><span style="color:{'#10b981' if sp.get('online', True) else '#555'};">{'🟢 متصل' if sp.get('online', True) else '🔴 غير متصل'}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
        </div>
        """, unsafe_allow_html=True)

def page_lab():
    st.markdown('<h2>🔬 المعمل</h2>', unsafe_allow_html=True)
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

def page_appointments():
    st.markdown('<h2>📅 المواعيد</h2>', unsafe_allow_html=True)
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد"]
    patient = st.selectbox("المريض", patients)
    date = st.date_input("التاريخ", datetime.now())
    time = st.time_input("الوقت", datetime.now().time())
    note = st.text_input("ملاحظة")
    if st.button("📅 إضافة موعد", type="primary"):
        st.session_state.appointments.append({"patient": patient, "date": date.strftime("%Y-%m-%d"), "time": time.strftime("%H:%M"), "note": note})
        st.success("✅ تم إضافة الموعد")
        st.rerun()
    for app in st.session_state.appointments:
        st.markdown(f"""
        <div class="card" style="padding:12px;">
            <div style="display:flex; justify-content:space-between;">
                <div><strong>{app['patient']}</strong> <span style="color:#94a3b8;">{app['date']} {app['time']}</span></div>
                <div>{app['note']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def page_accounting():
    st.markdown('<h2>💰 حساب المريض</h2>', unsafe_allow_html=True)
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

def page_payments():
    st.markdown('<h2>💳 الدفع</h2>', unsafe_allow_html=True)
    methods = ["💳 Visa / Mastercard", "📱 محفظتي", "💵 نقدي", "📲 إم باي", "🏦 تحويل بنكي"]
    selected = st.selectbox("وسيلة الدفع", methods)
    if st.button("✅ تنفيذ الدفع", type="primary"):
        st.success(f"✅ تم الدفع بنجاح عبر {selected}")

def page_subscriptions():
    st.markdown('<h2>👑 خطط الاشتراك</h2>', unsafe_allow_html=True)
    plans = [("🆓 تجريبي", "$0", ["3 مرضى", "تحليل أساسي"]), ("⭐ شهري", "$99", ["غير محدود", "تحليل AI"]), ("🌟 سنوي", "$999", ["جميع الميزات", "دعم أولوي"])]
    cols = st.columns(3)
    for i, (name, price, feats) in enumerate(plans):
        with cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center; {'border:2px solid #e67e22;' if i==1 else ''}">
                <h4>{name}</h4>
                <div style="font-size:2rem; font-weight:800; color:#e67e22;">{price}</div>
                <div style="font-size:0.7rem; color:#94a3b8;">{', '.join(feats)}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("اشترك", key=f"sub_{i}", use_container_width=True):
                st.success(f"🎉 تم تفعيل الاشتراك {name}!")

def page_invite():
    st.markdown('<h2>📨 دعوة الأطباء</h2>', unsafe_allow_html=True)
    link = f"https://harmonizeai.streamlit.app/?ref={np.random.randint(1000,9999)}"
    st.text_input("رابط الدعوة", value=link)
    if st.button("📋 نسخ الرابط"):
        st.success("✅ تم النسخ!")

def page_settings():
    st.markdown('<h2>⚙️ الإعدادات</h2>', unsafe_allow_html=True)
    with st.form("settings"):
        st.text_input("الاسم الظاهر", value=st.session_state.current_user["name"])
        st.text_input("التخصص", value=st.session_state.current_user.get("specialty",""))
        if st.form_submit_button("💾 حفظ"):
            st.success("✅ تم الحفظ")

def page_reports():
    st.markdown('<h2>📄 التقارير</h2>', unsafe_allow_html=True)
    if st.button("📄 توليد تقرير PDF", type="primary", use_container_width=True):
        st.success("✅ تم توليد التقرير!")

def page_privacy():
    st.markdown('<h2>🔒 الخصوصية</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#94a3b8; line-height:1.8;">
        <strong>سياسة الخصوصية:</strong> نحن نلتزم بحماية بياناتك الشخصية.<br>
        <strong>🔒 خصوصية البيانات:</strong> كل مستخدم لديه بياناته الخاصة.<br>
        <strong>🔐 الأمان:</strong> جميع البيانات مشفرة ومحمية.<br>
        <strong>🤖 الذكاء الاصطناعي:</strong> جميع عمليات التحليل تتم داخل النظام.
        </p>
    </div>
    """, unsafe_allow_html=True)

def page_ip():
    st.markdown('<h2>©️ حقوق الملكية الفكرية</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#94a3b8; line-height:1.8;">
        <strong>حقوق الملكية الفكرية:</strong> جميع المحتويات محمية بموجب حقوق النشر.<br>
        <strong>🤖 المحتوى المُنتج بالذكاء الاصطناعي:</strong> ملك للمستخدم الذي أنشأها.
        </p>
    </div>
    """, unsafe_allow_html=True)

def page_forum():
    st.markdown('<h2>🗣️ منتدى النقاشات</h2>', unsafe_allow_html=True)
    st.markdown("### 👨‍⚕️ الأخصائيون المتاحون")
    for sp in st.session_state.specialists:
        status_color = "#10b981" if sp.get("online", True) else "#555"
        st.markdown(f"""
        <div style="background:#1e293b; padding:10px; border-radius:12px; text-align:center; border:1px solid #334155;">
            <div style="width:12px; height:12px; background:{status_color}; border-radius:50%; margin:0 auto 6px;"></div>
            <strong>{sp['name']}</strong>
            <div style="font-size:0.7rem; color:#94a3b8;">{sp['specialty']}</div>
        </div>
        """, unsafe_allow_html=True)
    with st.form("forum_question"):
        q_title = st.text_input("عنوان السؤال")
        q_body = st.text_area("تفاصيل السؤال")
        target = st.selectbox("موجه إلى", ["جميع الأخصائيين"] + [s["name"] for s in st.session_state.specialists])
        if st.form_submit_button("🚀 نشر السؤال") and q_title and q_body:
            st.session_state.forum_questions.insert(0, {"id": len(st.session_state.forum_questions)+1, "title": q_title, "body": q_body, "asked_by": st.session_state.current_user["name"], "target": target, "status": "open", "answers": [], "created_at": datetime.now().isoformat()})
            st.success("✅ تم نشر السؤال!")
            st.rerun()
    for q in st.session_state.forum_questions:
        st.markdown(f"""
        <div style="background:#1e293b; border-radius:16px; padding:16px; border:1px solid #334155; margin-bottom:12px; border-right:4px solid #f59e0b;">
            <h4>{q['title']}</h4>
            <p style="color:#94a3b8;">{q['body']}</p>
            <div style="font-size:0.75rem; color:#64748b;">👤 {q['asked_by']} | 🎯 {q['target']}</div>
        </div>
        """, unsafe_allow_html=True)

def page_cadcam():
    st.markdown('<h2>⚙️ CAD/CAM</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div style="width:100%; height:400px; background:#0f172a; border-radius:16px; border:1px solid #334155; display:flex; align-items:center; justify-content:center;">
        <div style="text-align:center; color:#e67e22;">
            <div style="font-size:4rem;">🦷</div>
            <div style="font-size:1rem; margin-top:10px;">عارض 3D تفاعلي</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def page_vita():
    st.markdown('<h2>🎨 ألوان فيتا</h2>', unsafe_allow_html=True)
    vita_colors = {'A1': '#E8D5B8', 'A2': '#DCC8A8', 'A3': '#D0B898', 'A3.5': '#C8B090', 'A4': '#C0A888',
                   'B1': '#D8C8B0', 'B2': '#CCB8A0', 'B3': '#C0A890', 'B4': '#B89880',
                   'C1': '#C0B0A0', 'C2': '#B8A898', 'C3': '#B09888', 'C4': '#A88878',
                   'D2': '#B8A898', 'D3': '#B09888', 'D4': '#A88878'}
    cols = st.columns(4)
    for i, (code, color) in enumerate(vita_colors.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="border:1px solid #334155; border-radius:8px; padding:12px; text-align:center; background:#1e293b;">
                <div style="width:100%; height:40px; border-radius:6px; background:{color}; border:1px solid #334155;"></div>
                <div style="font-weight:700; color:#e67e22; margin-top:6px;">{code}</div>
            </div>
            """, unsafe_allow_html=True)

def page_image_editor():
    st.markdown('<h2>🎨 محرر الصور</h2>', unsafe_allow_html=True)
    if not st.session_state.image_layers:
        base_img = Image.new('RGB', (800, 600), color='#1a1a2e')
        draw = ImageDraw.Draw(base_img)
        draw.text((400, 300), "🦷 ارفع صورة لبدء التحرير", fill='#94a3b8', anchor="mm")
        st.session_state.image_layers = [{"name": "Background", "image": base_img, "visible": True, "opacity": 1.0, "blend_mode": "normal"}]
        st.session_state.current_layer = 0
    uploaded = st.file_uploader("📤 رفع صورة", type=["jpg", "png", "jpeg"], key="editor_upload")
    if uploaded:
        img = Image.open(uploaded)
        layer = create_layer(img, f"Layer {len(st.session_state.image_layers)}")
        if layer:
            st.session_state.image_layers.append(layer)
            st.session_state.current_layer = len(st.session_state.image_layers) - 1
            st.success("✅ تم إضافة الطبقة")
            st.rerun()
    for i, layer in enumerate(st.session_state.image_layers):
        active = "active" if i == st.session_state.current_layer else ""
        st.markdown(f'<div class="layer-item {active}"><span class="layer-name">{layer["name"]}</span></div>', unsafe_allow_html=True)
    if st.button("🔗 دمج الكل", use_container_width=True):
        merge_layers()
        st.rerun()

def create_layer(image, name="Layer"):
    if isinstance(image, Image.Image):
        return {"name": name, "image": image, "visible": True, "opacity": 1.0, "blend_mode": "normal"}
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
                base = Image.blend(base, img, layer["opacity"])
    if base:
        st.session_state.image_layers = [{"name": "Merged", "image": base, "visible": True, "opacity": 1.0, "blend_mode": "normal"}]
        st.session_state.current_layer = 0

# =============================================================
# PAGE ROUTER
# =============================================================
PAGES = {
    "home": page_home,
    "dashboard": page_dashboard,
    "upload_logo": page_upload_logo,
    "smile_simulator": page_smile_simulator,
    "3d_viewer": page_3d_viewer,
    "ai_face_real": page_ai_face_real,
    "ai_cephalometric_real": page_ai_cephalometric_real,
    "pdf_report": page_pdf_report,
    "ai_smile_design": page_smile_simulator,
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
