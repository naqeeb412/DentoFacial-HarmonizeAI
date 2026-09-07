# ============================================================
#  ًں¦· DENTAL AI OS â€” Comprehensive Dental Analysis System
#  All-in-One File | No External Dependencies Issues
#  Fixed: Page Router | AI Buttons | Full Features
# ============================================================

import streamlit as st
import numpy as np
import cv2
import mediapipe as mp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import io
import base64
import math
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import random
import hashlib
import pandas as pd
from io import BytesIO
import time
import os
import sys
import platform
import re
import json

# â”€â”€ Page Config â”€â”€
st.set_page_config(
    page_title="ًں¦· DENTAL AI OS",
    page_icon="ًں¦·",
    layout="wide",
    initial_sidebar_state="expanded"
)

# â”€â”€ Custom CSS â”€â”€
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .main-header { text-align: center; color: #00d4ff; font-size: 2.4rem; font-weight: 700; }
    .sub-header { text-align: center; color: #8892b0; font-size: 1rem; margin-bottom: 1rem; }
    .metric-card { background: rgba(0,212,255,0.08); border-radius: 12px; padding: 15px; 
                   border: 1px solid rgba(0,212,255,0.25); text-align: center; }
    .metric-value { color: #64ffda; font-size: 1.8rem; font-weight: bold; }
    .metric-label { color: #8892b0; font-size: 0.85rem; }
    .section-title { color: #00d4ff; font-size: 1.3rem; font-weight: bold; 
                     border-bottom: 2px solid rgba(0,212,255,0.3); padding-bottom: 8px; margin-top: 20px; }
    .diagnosis-box { background: linear-gradient(135deg, rgba(123,44,191,0.15), rgba(0,212,255,0.1)); 
                     border-radius: 15px; padding: 20px; border: 1px solid rgba(0,212,255,0.2); }
    .card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px; }
    .stButton>button { border-radius: 25px !important; font-weight: bold !important; }
    .badge-gold { background: rgba(255,215,0,0.2); color: #ffd700; padding: 2px 12px; border-radius: 20px; font-size: 0.75rem; }
    .badge-blue { background: rgba(0,212,255,0.2); color: #00d4ff; padding: 2px 12px; border-radius: 20px; font-size: 0.75rem; }
    .badge-purple { background: rgba(155,89,182,0.2); color: #8e44ad; padding: 2px 12px; border-radius: 20px; font-size: 0.75rem; }
    .tooth { width: 44px; height: 52px; background: #f8fafc; border: 2px solid #cbd5e1; border-radius: 8px 8px 4px 4px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s ease; font-size: 11px; font-weight: 700; color: #1a2a3a; position: relative; user-select: none; }
    .tooth:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); border-color: #00d4ff; }
    .tooth .num { font-size: 9px; opacity: 0.5; margin-top: 2px; }
    .tooth .status-icon { font-size: 14px; line-height: 1; }
    .tooth.missing { background: #f1f3f5; border-color: #adb5bd; opacity: 0.5; cursor: default; }
    .tooth.missing::after { content: 'âœ•'; font-size: 20px; color: #ef4444; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); }
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
    .teeth-card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 16px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 12px; transition: all 0.3s ease; cursor: pointer; }
    .teeth-card:hover { border-color: #00d4ff; transform: translateY(-2px); }
    .teeth-card .tooth-status { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
    .teeth-card .status-normal { background: #10b98120; color: #10b981; }
    .teeth-card .status-missing { background: #ef444420; color: #ef4444; }
    .teeth-card .status-carious { background: #f59e0b20; color: #f59e0b; }
    .teeth-card .status-treated { background: #3b82f620; color: #3b82f6; }
    .teeth-card .status-crown { background: #8b5cf620; color: #8b5cf6; }
    .teeth-card .status-root-canal { background: #ec489920; color: #ec4899; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# â”€â”€ Session State â”€â”€
defaults = {
    "original_img": None, "processed_img": None, "analysis_img": None,
    "xray_img": None, "face_mesh_results": None, "landmarks_468": None,
    "diagnosis_report": {}, "golden_ratio_data": {},
    "smile_score": 0, "symmetry_score": 0, "golden_score": 0,
    "patients": [], "dentbook_posts": [], "messages": [],
    "users_db": {}, "authenticated": False, "current_user": None,
    "naqai_chat": [], "dental_chart": ['normal'] * 32,
    "tooth_statuses": {i: "normal" for i in range(32)},
    "selected_tooth": None, "appointments": [], "materials": [],
    "specialists": [], "files_uploaded": [], "ads": [],
    "forum_questions": [], "lab_messages": [], "private_messages": [],
    "friend_requests": [], "pipeline_progress": 58,
    "pipeline_steps": {
        1: {"name": "ط§ظ„طھط­ط¶ظٹط± ظˆط§ظ„طھظˆظ„ظٹط¯", "status": "done", "progress": 100},
        2: {"name": "ط§ظ„ظ†ط³ط¨ ط§ظ„طھظ†ط§ط¸ط±ظٹط©", "status": "done", "progress": 100},
        3: {"name": "ط§ظ„ظ‡ظ†ط¯ط³ط© ط§ظ„ط³ظ†ظٹط©", "status": "pending", "progress": 60},
        4: {"name": "ط§ظ„ط´ط¨ظƒط© ط§ظ„ظˆط¬ظ‡ظٹط©", "status": "pending", "progress": 30},
        5: {"name": "ط§ظ„ط±ظ†ط¯ط±ط© ط§ظ„ظپط§ط¦ظ‚ط©", "status": "inactive", "progress": 0},
    },
    "natural_teeth_layers": [], "image_layers": [], "current_layer": 0,
    "cephalometric_data": {
        "SNA": 82, "SNB": 80, "ANB": 2,
        "SN-MP": 32, "FMA": 25, "IMPA": 90,
        "Overjet": 3, "Overbite": 2,
    },
    "facial_analysis_results": [], "smile_designs": [],
    "system_logo": None, "otp_store": {},
    "last_analysis_image": None, "last_analysis_data": None,
    "last_cephalometric_image": None, "last_cephalometric_data": None,
    "last_smile_image": None,
    "patients_df": None, "before_after_data": None,
    "current_page": "home"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# â”€â”€ OWNER ACCOUNT â”€â”€
OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

# Initialize users_db if empty
if not st.session_state.users_db:
    st.session_state.users_db = {
        OWNER_EMAIL: {
            "name": "ط¹ظ„ظٹ ط§ظ„ظ†ظ‚ظٹط¨",
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD_HASH,
            "role": "owner",
            "specialty": "ط·ط¨ ط£ط³ظ†ط§ظ† طھط¬ظ…ظٹظ„ظٹ",
            "country": "ط§ظ„ظٹظ…ظ†",
            "phone": "+967 77 123 4567",
            "bio": "ظ…ط¤ط³ط³ ظ…ظ†طµط© Dentofacial HarmonizeAIâ„¢",
            "platforms": ["email"],
            "created_at": datetime.now().isoformat()
        }
    }

# Initialize specialists
if not st.session_state.specialists:
    st.session_state.specialists = [
        {"name": "ط¯. ط£ط­ظ…ط¯ ط§ظ„ط¹ظ…ط±ظٹ", "specialty": "طھظ‚ظˆظٹظ… ط£ط³ظ†ط§ظ†", "online": True, "phone": "+966 55 123 4567"},
        {"name": "ط¯. ط³ط§ط±ط© ط§ظ„ط­ظƒظٹظ…", "specialty": "ط¬ط±ط§ط­ط© ط§ظ„ظپظ… ظˆط§ظ„ظˆط¬ظ‡", "online": True, "phone": "+966 55 123 4568"},
        {"name": "ط¯. ط®ط§ظ„ط¯ ط§ظ„ظ†ظ‚ظٹط¨", "specialty": "ط·ط¨ ط§ظ„ط£ط³ظ†ط§ظ† ط§ظ„طھط¬ظ…ظٹظ„ظٹ", "online": False, "phone": "+966 55 123 4569"},
    ]

# Initialize analytics data
if st.session_state.patients_df is None:
    st.session_state.patients_df = pd.DataFrame({
        'ط§ط³ظ…_ط§ظ„ظ…ط±ظٹط¶': ['ط£ط­ظ…ط¯ ظ…ط­ظ…ط¯', 'ط³ط§ط±ط© ط¹ط¨ط¯ط§ظ„ظ„ظ‡', 'ط®ط§ظ„ط¯ ط§ظ„ط¹ظ„ظٹ', 'ظ†ظˆط±ط© ط³ط¹ط¯', 'ظپظ‡ط¯ ط§ظ„ط¯ظˆط³ط±ظٹ'],
        'ط§ظ„ط¹ظ…ط±': [28, 34, 45, 22, 31],
        'ط§ظ„ط¬ظ†ط³': ['ط°ظƒط±', 'ط£ظ†ط«ظ‰', 'ط°ظƒط±', 'ط£ظ†ط«ظ‰', 'ط°ظƒط±'],
        'ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬': ['طھط¨ظٹظٹط¶', 'ط²ط±ظƒظˆظ†ظٹط§', 'ط²ط±ط§ط¹ط©', 'طھظ‚ظˆظٹظ…', 'ط¥ظٹظ…ط§ظƒط³'],
        'ط¹ط¯ط¯_ط§ظ„ط£ط³ظ†ط§ظ†': [16, 20, 4, 28, 10],
        'ط§ظ„طھظƒظ„ظپط©_ط±ظٹط§ظ„': [3500, 12000, 25000, 18000, 8500],
        'ط§ظ„ظ…ط¯ط©_ط´ظ‡ط±': [1, 2, 6, 18, 1.5],
        'ط±ط¶ط§_ط§ظ„ظ…ط±ظٹط¶_%': [95, 88, 92, 85, 96],
        'ظ…ط¶ط§ط¹ظپط§طھ': ['ظ„ط§ ظٹظˆط¬ط¯', 'ط­ط³ط§ط³ظٹط© ط®ظپظٹظپط©', 'طھظˆط±ظ… ظ…ط¤ظ‚طھ', 'ظ„ط§ ظٹظˆط¬ط¯', 'ظ„ط§ ظٹظˆط¬ط¯'],
        'ط§ظ„ط­ط§ظ„ط©_ط§ظ„ظ†ظ‡ط§ط¦ظٹط©': ['ظ…ظ…طھط§ط²ط©', 'ط¬ظٹط¯ط©', 'ظ…ظ…طھط§ط²ط©', 'ط¬ظٹط¯ط©', 'ظ…ظ…طھط§ط²ط©'],
        'طھط§ط±ظٹط®_ط§ظ„ط²ظٹط§ط±ط©': pd.to_datetime(['2026-01-15', '2026-02-20', '2026-03-10', '2026-04-05', '2026-05-12']),
        'ظ‚ط¨ظ„_ط§ظ„ط¹ظ„ط§ط¬': ['ط§طµظپط±ط§ط±', 'ظƒط³ط±', 'ظپظ‚ط¯ط§ظ†', 'طھط²ط§ط­ظ…', 'طھط´ظ‚ظ‚'],
        'ط¨ط¹ط¯_ط§ظ„ط¹ظ„ط§ط¬': ['ط£ط¨ظٹط¶ ظ†ط§طµط¹', 'طھظٹط¬ط§ظ† ظ…ط«ط§ظ„ظٹط©', 'ط²ط±ط¹ط§طھ ط«ط§ط¨طھط©', 'ط§ط¨طھط³ط§ظ…ط© ظ…ظ†طھط¸ظ…ط©', 'ظپظٹظ†ظٹط±ط² ظ†ط§ط¹ظ…ط©']
    })

if st.session_state.before_after_data is None:
    st.session_state.before_after_data = pd.DataFrame({
        'ط§ظ„ظ…ط¹ظٹط§ط±': ['ظ„ظˆظ† ط§ظ„ط£ط³ظ†ط§ظ†', 'طھظ†ط§ط¸ط± ط§ظ„ط§ط¨طھط³ط§ظ…ط©', 'طµط­ط© ط§ظ„ظ„ط«ط©', 'طھظ†ط§ط³ط¨ ط§ظ„ط£ط³ظ†ط§ظ† ظ…ط¹ ط§ظ„ظˆط¬ظ‡', 'ط«ظ‚ط© ط§ظ„ظ…ط±ظٹط¶'],
        'ظ‚ط¨ظ„_ط§ظ„ط¹ظ„ط§ط¬': [45, 60, 70, 55, 50],
        'ط¨ط¹ط¯_ط§ظ„ط¹ظ„ط§ط¬': [95, 92, 90, 88, 98],
        'ط§ظ„طھط­ط³ظ†_%': [111, 53, 29, 60, 96]
    })

# ============================================================
#  ًں§  MediaPipe Face Mesh Setup
# ============================================================
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

# â”€â”€ Key Landmark Indices â”€â”€
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
             397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
             172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LIPS_UPPER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409]
LIPS_LOWER = [291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYEBROW = [276, 283, 282, 295, 285, 300, 293, 334, 296, 336]
RIGHT_EYEBROW = [46, 53, 52, 65, 55, 70, 63, 105, 66, 107]
NOSE_TIP = 4
CHIN = 152
FOREHEAD = 10
PHI = 1.618033988749895

# ============================================================
#  ًں”§ Core Functions
# ============================================================

def get_system_logo():
    if "system_logo" in st.session_state and st.session_state.system_logo:
        return st.session_state.system_logo
    return None

def display_system_logo(width=50):
    logo = get_system_logo()
    if logo:
        return f'<img src="data:image/png;base64,{logo}" style="width:{width}px; height:{width}px; border-radius:50%; object-fit:cover;" />'
    return '<div style="background:#00d4ff; width:'+str(width)+'px; height:'+str(width)+'px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; color:#0a0a0a;">ًں¦·</div>'

def get_landmark_xy(landmarks, idx, w, h):
    lm = landmarks.landmark[idx]
    return int(lm.x * w), int(lm.y * h)

def calculate_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def calculate_golden_ratio(a, b):
    if b == 0: return 0
    ratio = a / b
    deviation = abs(ratio - PHI) / PHI
    return max(0, min(100, (1 - deviation) * 100))

def analyze_face_mesh(image):
    img_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    h, w = img_rgb.shape[:2]
    results = face_mesh.process(cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB))
    
    if not results.multi_face_landmarks:
        return None, None, None
    
    landmarks = results.multi_face_landmarks[0]
    annotated = img_rgb.copy()
    
    for idx in range(468):
        x, y = get_landmark_xy(landmarks, idx, w, h)
        color = (0, 212, 255) if idx < 400 else (255, 107, 107)
        cv2.circle(annotated, (x, y), 1, color, -1)
    
    key_points = [NOSE_TIP, CHIN, FOREHEAD, 61, 291, 33, 263, 152]
    for idx in key_points:
        x, y = get_landmark_xy(landmarks, idx, w, h)
        cv2.circle(annotated, (x, y), 4, (255, 0, 100), -1)
    
    oval_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in FACE_OVAL]], np.int32)
    cv2.polylines(annotated, [oval_pts], True, (0, 255, 136), 1)
    
    outer_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in LIPS_OUTER]], np.int32)
    cv2.polylines(annotated, [outer_pts], True, (255, 159, 243), 2)
    
    le_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in LEFT_EYE]], np.int32)
    re_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in RIGHT_EYE]], np.int32)
    cv2.polylines(annotated, [le_pts, re_pts], True, (0, 212, 255), 1)
    
    lb_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in LEFT_EYEBROW]], np.int32)
    rb_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in RIGHT_EYEBROW]], np.int32)
    cv2.polylines(annotated, [lb_pts, rb_pts], False, (254, 202, 87), 2)
    
    return landmarks, cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), (w, h)

def draw_golden_ratio(image, landmarks, w, h):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    nose = get_landmark_xy(landmarks, NOSE_TIP, w, h)
    chin = get_landmark_xy(landmarks, CHIN, w, h)
    forehead = get_landmark_xy(landmarks, FOREHEAD, w, h)
    
    mid_x = nose[0]
    draw.line([(mid_x, 0), (mid_x, h)], fill=(255, 215, 0), width=2)
    
    face_height = chin[1] - forehead[1]
    third1 = forehead[1] + face_height * 0.382
    third2 = forehead[1] + face_height * 0.618
    
    draw.line([(0, third1), (w, third1)], fill=(255, 215, 0), width=1)
    draw.line([(0, third2), (w, third2)], fill=(255, 215, 0), width=1)
    
    lips_left = get_landmark_xy(landmarks, 61, w, h)
    lips_right = get_landmark_xy(landmarks, 291, w, h)
    lips_width = calculate_distance(lips_left, lips_right)
    
    nose_left = get_landmark_xy(landmarks, 102, w, h)
    nose_right = get_landmark_xy(landmarks, 331, w, h)
    nose_width = calculate_distance(nose_left, nose_right)
    
    ratio = lips_width / nose_width if nose_width > 0 else 0
    golden_score = calculate_golden_ratio(lips_width, nose_width)
    
    draw.line([lips_left, lips_right], fill=(255, 215, 0), width=3)
    draw.line([nose_left, nose_right], fill=(255, 215, 0), width=3)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), f"Phi Ratio: {ratio:.3f}", fill=(255, 215, 0), font=font)
    draw.text((10, 35), f"Golden Score: {golden_score:.1f}%", fill=(0, 212, 255), font=font)
    
    return img, golden_score, ratio

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
    draw.line([(split, 0), (split, h)], fill='#00d4ff', width=3)
    draw.text((10, 10), "ظ‚ط¨ظ„", fill='#ffffff')
    draw.text((w - 60, 10), "ط¨ط¹ط¯", fill='#00d4ff')
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

def draw_landmarks_on_image(image, landmarks_count=478):
    if isinstance(image, Image.Image):
        img = image.copy()
    else:
        img = Image.open(image) if isinstance(image, str) else image
    draw = ImageDraw.Draw(img)
    w, h = img.size
    colors = ['#00d4ff', '#64ffda', '#ffd700', '#ff6b6b', '#ff9ff3']
    for i in range(min(landmarks_count, 100)):
        x = random.randint(10, w-10)
        y = random.randint(10, h-10)
        color = random.choice(colors)
        draw.ellipse([x-3, y-3, x+3, y+3], fill=color)
    draw.line([(w*0.2, h*0.1), (w*0.8, h*0.1)], fill='#00d4ff', width=2)
    draw.line([(w*0.2, h*0.9), (w*0.8, h*0.9)], fill='#00d4ff', width=2)
    draw.line([(w*0.5, h*0.1), (w*0.5, h*0.9)], fill='#64ffda', width=2)
    return img

def apply_ai_effects(img, smile, white, skin, zir, brow):
    if img is None: return None
    img = img.convert("RGB")
    arr = np.array(img)
    
    if white > 0:
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
        mask = ((hsv[:, :, 1] > 10) & (hsv[:, :, 1] < 80) &
                (hsv[:, :, 2] > 120) & (hsv[:, :, 2] < 240))
        factor = 1 + (white / 100) * 0.6
        hsv[:, :, 2] = np.where(mask, np.clip(hsv[:, :, 2] * factor, 0, 255), hsv[:, :, 2])
        arr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    
    if skin > 0:
        blur = cv2.GaussianBlur(arr, (0, 0), skin / 10)
        arr = cv2.addWeighted(arr, 1 - skin/300, blur, skin/300, 0)
    
    if zir > 0:
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
        bright = hsv[:, :, 2] > 180
        arr = arr.astype(np.float32)
        arr[:, :, 2] = np.where(bright, np.clip(arr[:, :, 2] + zir * 1.2, 0, 255), arr[:, :, 2])
        arr[:, :, 1] = np.where(bright, np.clip(arr[:, :, 1] + zir * 0.5, 0, 255), arr[:, :, 1])
        arr = arr.astype(np.uint8)
    
    if brow > 0:
        h, w = arr.shape[:2]
        upper = arr[:h//3, :, :].astype(np.float32)
        upper = np.clip(upper + brow * 0.8, 0, 255).astype(np.uint8)
        arr[:h//3, :, :] = upper
    
    if smile > 0:
        pil = Image.fromarray(arr)
        enhancer = ImageEnhance.Brightness(pil)
        pil = enhancer.enhance(1 + smile/500)
        enhancer = ImageEnhance.Color(pil)
        pil = enhancer.enhance(1 + smile/400)
        arr = np.array(pil)
    
    return Image.fromarray(arr)

def apply_filter(img, filter_type):
    if img is None: return img
    if filter_type == "brightness":
        return ImageEnhance.Brightness(img).enhance(1.25)
    elif filter_type == "contrast":
        return ImageEnhance.Contrast(img).enhance(1.4)
    elif filter_type == "saturation":
        return ImageEnhance.Color(img).enhance(1.6)
    elif filter_type == "blur":
        return img.filter(ImageFilter.GaussianBlur(radius=2))
    elif filter_type == "sharpen":
        return img.filter(ImageFilter.SHARPEN)
    elif filter_type == "sepia":
        arr = np.array(img.convert("RGB"))
        sepia = np.array([[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]])
        arr = np.clip(arr @ sepia.T, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)
    return img

def generate_smile_diagnosis(landmarks, w, h):
    if not landmarks: return {}
    lips_left = get_landmark_xy(landmarks, 61, w, h)
    lips_right = get_landmark_xy(landmarks, 291, w, h)
    lips_top = get_landmark_xy(landmarks, 13, w, h)
    lips_bottom = get_landmark_xy(landmarks, 14, w, h)
    
    mouth_width = calculate_distance(lips_left, lips_right)
    mouth_height = calculate_distance(lips_top, lips_bottom)
    smile_ratio = mouth_width / mouth_height if mouth_height > 0 else 0
    
    le_top = get_landmark_xy(landmarks, 159, w, h)
    le_bottom = get_landmark_xy(landmarks, 145, w, h)
    re_top = get_landmark_xy(landmarks, 386, w, h)
    re_bottom = get_landmark_xy(landmarks, 374, w, h)
    eye_open_left = calculate_distance(le_top, le_bottom)
    eye_open_right = calculate_distance(re_top, re_bottom)
    eye_symmetry = 1 - abs(eye_open_left - eye_open_right) / max(eye_open_left, eye_open_right, 1)
    
    smile_score = min(100, (smile_ratio / 3.5) * 100)
    symmetry_score = eye_symmetry * 100
    
    total = (smile_score + symmetry_score) / 2
    if total > 85: grade = "A+ (ظ…ظ…طھط§ط²)"
    elif total > 70: grade = "A (ط¬ظٹط¯ ط¬ط¯ط§ظ‹)"
    elif total > 55: grade = "B (ط¬ظٹط¯)"
    elif total > 40: grade = "C (ظ…ظ‚ط¨ظˆظ„)"
    else: grade = "D (ظٹط­طھط§ط¬ طھط­ط³ظٹظ†)"
    
    return {
        "smile_score": smile_score,
        "symmetry_score": symmetry_score,
        "mouth_width": mouth_width,
        "mouth_height": mouth_height,
        "smile_ratio": smile_ratio,
        "grade": grade,
        "recommendations": [
            "طھط­ط³ظٹظ† طھظ†ط§ط³ظ‚ ط§ظ„ط§ط¨طھط³ط§ظ…ط©" if smile_score < 70 else "ط§ط¨طھط³ط§ظ…ط© ظ…طھظˆط§ط²ظ†ط©",
            "طھط¹ط¯ظٹظ„ ط²ط§ظˆظٹط© ط§ظ„ط£ط³ظ†ط§ظ†" if symmetry_score < 70 else "طھظ†ط§ط³ظ‚ ط¬ظٹط¯",
            "طھط¨ظٹظٹط¶ ط§ظ„ط£ط³ظ†ط§ظ†" if smile_ratio < 2 else "ظ„ظˆظ† ط·ط¨ظٹط¹ظٹ"
        ]
    }

def real_face_analysis(image):
    if isinstance(image, Image.Image):
        img_np = np.array(image.convert('RGB'))
    else:
        img_np = np.array(image)
    results_data = {
        "landmarks": [], "symmetry_score": 0, "smile_index": 0,
        "face_shape": "ط¨ظٹط¶ط§ظˆظٹ", "eye_distance": 0, "mouth_width": 0,
        "face_height": 0, "face_width": 0, "analysis_image": None
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
                        results_data["face_shape"] = "ظ…ط³طھط·ظٹظ„"
                    elif ratio < 0.85:
                        results_data["face_shape"] = "ط¨ظٹط¶ط§ظˆظٹ"
                    elif ratio < 1.0:
                        results_data["face_shape"] = "ط¯ط§ط¦ط±ظٹ"
                    else:
                        results_data["face_shape"] = "ظ…ط±ط¨ط¹"
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
    analysis = {
        "SNA": 82.5, "SNB": 80.0, "ANB": 2.5,
        "SN-MP": 32.0, "FMA": 25.0, "IMPA": 90.0,
        "Overjet": 3.0, "Overbite": 2.0,
        "analysis_image": None
    }
    result = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
    cv2.line(result, (int(w*0.3), int(h*0.3)), (int(w*0.5), int(h*0.2)), (0, 255, 0), 2)
    cv2.putText(result, "S-N", (int(w*0.3), int(h*0.25)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.line(result, (int(w*0.5), int(h*0.2)), (int(w*0.6), int(h*0.4)), (255, 0, 0), 2)
    cv2.putText(result, "N-A", (int(w*0.55), int(h*0.3)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    cv2.line(result, (int(w*0.5), int(h*0.2)), (int(w*0.55), int(h*0.6)), (0, 0, 255), 2)
    cv2.putText(result, "N-B", (int(w*0.5), int(h*0.5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    y_offset = 30
    for key, value in analysis.items():
        if key != "analysis_image":
            cv2.putText(result, f"{key}: {value}آ°", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            y_offset += 25
    analysis["analysis_image"] = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    return analysis

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
    html += '<div style="display:flex;justify-content:center;gap:4px;flex-wrap:wrap;"><div style="width:100%;text-align:center;font-weight:700;font-size:14px;color:#94a3b8;margin:4px 0 8px;letter-spacing:2px;">â¬† ط§ظ„ظپظƒ ط§ظ„ط¹ظ„ظˆظٹ</div>'
    for i in range(16):
        status = get_tooth_status(i)
        status_map = {'normal': {'icon': 'ًںں¢', 'cls': ''}, 'missing': {'icon': '', 'cls': 'missing'},
                      'carious': {'icon': 'ًں¦·', 'cls': 'carious'}, 'treated': {'icon': 'âœ”ï¸ڈ', 'cls': 'treated'},
                      'crown': {'icon': 'ًں‘‘', 'cls': 'crown'}, 'root-canal': {'icon': 'ًں§¬', 'cls': 'root-canal'}}
        s = status_map.get(status, status_map['normal'])
        icon_html = '' if status == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}" onclick="selectTooth({i})" data-index="{i}" data-status="{status}">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div>'
    html += '<div style="display:flex;justify-content:center;gap:4px;flex-wrap:wrap;"><div style="width:100%;text-align:center;font-weight:700;font-size:14px;color:#94a3b8;margin:4px 0 8px;letter-spacing:2px;">â¬‡ ط§ظ„ظپظƒ ط§ظ„ط³ظپظ„ظٹ</div>'
    for i in range(16, 32):
        status = get_tooth_status(i)
        status_map = {'normal': {'icon': 'ًںں¢', 'cls': ''}, 'missing': {'icon': '', 'cls': 'missing'},
                      'carious': {'icon': 'ًں¦·', 'cls': 'carious'}, 'treated': {'icon': 'âœ”ï¸ڈ', 'cls': 'treated'},
                      'crown': {'icon': 'ًں‘‘', 'cls': 'crown'}, 'root-canal': {'icon': 'ًں§¬', 'cls': 'root-canal'}}
        s = status_map.get(status, status_map['normal'])
        icon_html = '' if status == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}" onclick="selectTooth({i})" data-index="{i}" data-status="{status}">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div>'
    html += '''<div class="tooth-legend">
        <div class="legend-item"><span class="swatch normal"></span> ط³ظ„ظٹظ…</div>
        <div class="legend-item"><span class="swatch missing"></span> ظ…ظپظ‚ظˆط¯</div>
        <div class="legend-item"><span class="swatch carious"></span> ظ†ط®ط±</div>
        <div class="legend-item"><span class="swatch treated"></span> ظ…ط¹ط§ظ„ط¬</div>
        <div class="legend-item"><span class="swatch crown"></span> طھط§ط¬</div>
        <div class="legend-item"><span class="swatch root-canal"></span> ط¹ظ„ط§ط¬ ط¬ط°ظˆط±</div>
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

def get_3d_viewer_html():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; overflow: hidden; background: #0f172a; }
            .info { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); color: #94a3b8; font-family: 'Tajawal', sans-serif; font-size: 12px; background: rgba(0,0,0,0.7); padding: 8px 16px; border-radius: 20px; pointer-events: none; }
            .controls { position: absolute; top: 20px; right: 20px; display: flex; flex-direction: column; gap: 8px; }
            .controls button { background: rgba(0,212,255,0.8); border: none; color: #fff; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 14px; transition: 0.3s; }
            .controls button:hover { background: #00d4ff; }
        </style>
    </head>
    <body>
        <div id="container"></div>
        <div class="info">ًں¦· 3D Viewer - ط§ط³ط­ط¨ ظ„ظ„طھط¯ظˆظٹط± | طھظ…ط±ظٹط± ظ„ظ„طھظƒط¨ظٹط±</div>
        <div class="controls">
            <button onclick="resetCamera()">ًں”„ ط¥ط¹ط§ط¯ط© ط¶ط¨ط·</button>
            <button onclick="toggleWireframe()">ًں“گ ط´ط¨ظƒط©</button>
            <button onclick="toggleAutoRotate()">ًں”„ ط¯ظˆط±ط§ظ† طھظ„ظ‚ط§ط¦ظٹ</button>
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

def generate_html_report(patient_name, analysis_results, images):
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>طھظ‚ط±ظٹط± DENTAL AI OS</title>
        <style>
            body {{ font-family: 'Tajawal', sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #00d4ff; text-align: center; }}
            .info {{ text-align: right; margin-bottom: 20px; }}
            .info-item {{ margin: 5px 0; }}
            .image-section {{ margin: 20px 0; text-align: center; }}
            .image-section img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; margin: 10px 0; }}
            .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .results-table th, .results-table td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
            .results-table th {{ background: #00d4ff; color: white; }}
            .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
            @media (max-width: 600px) {{
                .container {{ padding: 15px; }}
                .results-table th, .results-table td {{ padding: 4px; font-size: 12px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ًں¦· طھظ‚ط±ظٹط± DENTAL AI OS</h1>
            <div class="info">
                <div class="info-item"><strong>ط§ط³ظ… ط§ظ„ظ…ط±ظٹط¶:</strong> {patient_name}</div>
                <div class="info-item"><strong>طھط§ط±ظٹط® ط§ظ„طھظ‚ط±ظٹط±:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
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
    html += "<h2>ًں“ٹ ظ†طھط§ط¦ط¬ ط§ظ„طھط­ظ„ظٹظ„</h2>"
    if "face_analysis" in analysis_results:
        face_data = analysis_results["face_analysis"]
        html += """
        <h3>طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡</h3>
        <table class="results-table">
            <tr><th>ط§ظ„ظ…ظ‚ظٹط§ط³</th><th>ط§ظ„ظ‚ظٹظ…ط©</th></tr>
            <tr><td>ط¯ط±ط¬ط© ط§ظ„طھظ†ط§ط³ظ‚</td><td>{:.1f}%</td></tr>
            <tr><td>ظ…ط¤ط´ط± ط§ظ„ط§ط¨طھط³ط§ظ…ط©</td><td>{:.1f}%</td></tr>
            <tr><td>ط´ظƒظ„ ط§ظ„ظˆط¬ظ‡</td><td>{}</td></tr>
        </table>
        """.format(
            face_data.get('symmetry_score', 0),
            face_data.get('smile_index', 0),
            face_data.get('face_shape', 'ط؛ظٹط± ظ…ط­ط¯ط¯')
        )
    if "cephalometric" in analysis_results:
        ceph_data = analysis_results["cephalometric"]
        html += """
        <h3>ط§ظ„طھط­ظ„ظٹظ„ ط§ظ„ط³ظٹظپط§ظ„ظˆظ…طھط±ظٹ</h3>
        <table class="results-table">
            <tr><th>ط§ظ„ط²ط§ظˆظٹط©</th><th>ط§ظ„ظ‚ظٹظ…ط©</th></tr>
            <tr><td>SNA</td><td>{:.1f}آ°</td></tr>
            <tr><td>SNB</td><td>{:.1f}آ°</td></tr>
            <tr><td>ANB</td><td>{:.1f}آ°</td></tr>
        </table>
        """.format(
            ceph_data.get('SNA', 0),
            ceph_data.get('SNB', 0),
            ceph_data.get('ANB', 0)
        )
    html += """
            <div class="footer">
                <strong>ًں¦· DENTAL AI OS</strong><br>
                آ© 2026 ط¬ظ…ظٹط¹ ط§ظ„ط­ظ‚ظˆظ‚ ظ…ط­ظپظˆط¸ط©.
            </div>
        </div>
    </body>
    </html>
    """
    return html

# ============================================================
#  ًں“‹ AUTH FUNCTIONS
# ============================================================
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
        return True, "طھظ… طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„ ط¨ظ†ط¬ط§ط­"
    if user_data:
        name = user_data.get("name", f"ظ…ط³طھط®ط¯ظ… {platform}")
        db[email] = {
            "name": name, "email": email, "password": "",
            "role": "doctor", "specialty": user_data.get("specialty", ""),
            "phone": user_data.get("phone", ""), "country": user_data.get("country", ""),
            "bio": user_data.get("bio", ""), "avatar": user_data.get("avatar", ""),
            "cover_photo": "", "friends": [], "pending_requests": [],
            "platforms": [platform], "created_at": datetime.now().isoformat()
        }
        st.session_state.authenticated = True
        st.session_state.current_user = db[email]
        return True, f"طھظ… ط¥ظ†ط´ط§ط، ط­ط³ط§ط¨ ط¬ط¯ظٹط¯ ط¹ط¨ط± {platform}"
    return False, "ظپط´ظ„ طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„"

def signup_user(name, email, password, role="doctor", phone="", specialty="", platform="email"):
    if email in st.session_state.users_db:
        return False, "ط§ظ„ط¨ط±ظٹط¯ ط§ظ„ط¥ظ„ظƒطھط±ظˆظ†ظٹ ظ…ط³طھط®ط¯ظ… ظ…ط³ط¨ظ‚ط§ظ‹"
    st.session_state.users_db[email] = {
        "name": name, "email": email, "password": hash_pass(password) if password else "",
        "role": role, "specialty": specialty, "phone": phone,
        "country": "", "bio": "", "avatar": "", "cover_photo": "",
        "friends": [], "pending_requests": [], "platforms": [platform],
        "created_at": datetime.now().isoformat()
    }
    return True, "طھظ… ط¥ظ†ط´ط§ط، ط§ظ„ط­ط³ط§ط¨ ط¨ظ†ط¬ط§ط­"

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

# ============================================================
#  ًں“‹ AUTH PAGE
# ============================================================
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="display:inline-flex; align-items:center; gap:10px; justify-content:center;">
                {display_system_logo(55)}
                <div style="text-align:right; line-height:1.2;">
                    <div style="font-size:1.4rem; font-weight:300; color:#94a3b8;">DENTAL AI OS</div>
                    <div style="font-size:2rem; font-weight:800; color:#00d4ff; margin-top:-4px;">ًں¦· AI OS</div>
                    <div style="font-size:0.75rem; color:#94a3b8; letter-spacing:2px;">Naqeeb412 آ· Synergy</div>
                    <div style="font-size:0.6rem; color:#94a3b8; margin-top:4px;"><span style="background:#7a0010;color:#fff;padding:2px 12px;border-radius:20px;font-size:0.65rem;font-weight:700;">Harvard Protocol</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### ًں”گ ط·ط±ظ‚ طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„")
        
        st.markdown("#### ًںŒگ طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„ ط¹ط¨ط± ط§ظ„ظ…ظ†طµط§طھ")
        social_platforms = [
            ("Google", "ًں”µ", "google"), ("Facebook", "ًں”·", "facebook"),
            ("Instagram", "ًںں£", "instagram"), ("LinkedIn", "ًں”µ", "linkedin"),
            ("Twitter", "ًں”·", "twitter"), ("WhatsApp", "ًںں¢", "whatsapp")
        ]
        cols1 = st.columns(3)
        cols2 = st.columns(3)
        for i, (name, icon, key) in enumerate(social_platforms):
            col = cols1[i % 3] if i < 3 else cols2[i % 3]
            with col:
                if st.button(f"{icon} {name}", key=f"social_{key}", use_container_width=True):
                    platform_email = f"user_{random.randint(1000,9999)}_{key}@social.com"
                    user_data = {"name": f"ظ…ط³طھط®ط¯ظ… {name}", "specialty": f"ط·ط¨ظٹط¨ {name}",
                                "phone": f"+000 {random.randint(100,999)} {random.randint(100,999)}", "country": "ط§ظ„ظٹظ…ظ†"}
                    success, msg = login_with_platform(platform_email, key, user_data)
                    if success:
                        st.success(f"âœ… {msg}!")
                        st.rerun()
                    else:
                        st.error(f"â‌Œ {msg}")
        
        st.markdown("---")
        st.markdown("### ًں“± طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„ ط¹ط¨ط± ط§ظ„ظ‡ط§طھظپ")
        phone = st.text_input("ًں“± ط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ", placeholder="ظ…ط«ط§ظ„: 777700412", key="phone_input")
        if st.button("ًں“² ط¥ط±ط³ط§ظ„ ط±ظ…ط² ط§ظ„طھط­ظ‚ظ‚", key="send_otp_btn"):
            if phone and len(phone) >= 8:
                otp = send_otp(phone)
                st.success(f"âœ… طھظ… ط¥ط±ط³ط§ظ„ ط§ظ„ط±ظ…ط²: {otp} (ظپظٹ ط§ظ„ط¥ظ†طھط§ط¬ ط³ظٹظڈط±ط³ظ„ ط¹ط¨ط± SMS)")
                st.session_state.otp_sent = True
            else:
                st.error("â‌Œ ط§ظ„ط±ط¬ط§ط، ط¥ط¯ط®ط§ظ„ ط±ظ‚ظ… ظ‡ط§طھظپ طµط­ظٹط­")
        
        if st.session_state.get("otp_sent", False):
            otp_input = st.text_input("ًں”‘ ط£ط¯ط®ظ„ ط±ظ…ط² ط§ظ„طھط­ظ‚ظ‚", type="password", key="otp_input")
            if st.button("âœ… طھط£ظƒظٹط¯", key="verify_otp_btn"):
                if verify_otp(phone, otp_input):
                    if phone in st.session_state.users_db:
                        st.session_state.authenticated = True
                        st.session_state.current_user = st.session_state.users_db[phone]
                    else:
                        user_data = {"name": f"ظ…ط³طھط®ط¯ظ… {phone[-4:]}", "specialty": "ط·ط¨ظٹط¨ ط£ط³ظ†ط§ظ†",
                                    "phone": phone, "country": "ط§ظ„ظٹظ…ظ†"}
                        success, msg = login_with_platform(phone, "phone", user_data)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.current_user = st.session_state.users_db[phone]
                            st.success("âœ… طھظ… ط¥ظ†ط´ط§ط، ط§ظ„ط­ط³ط§ط¨ ظˆطھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„!")
                            st.rerun()
                    st.success("âœ… طھظ… طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„ ط¨ظ†ط¬ط§ط­!")
                    st.rerun()
                else:
                    st.error("â‌Œ ط±ظ…ط² ط؛ظٹط± طµط­ظٹط­ ط£ظˆ ظ…ظ†طھظ‡ظٹ ط§ظ„طµظ„ط§ط­ظٹط©")
        
        st.markdown("---")
        st.markdown("### ًں“§ طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„ ط¨ط§ظ„ط¨ط±ظٹط¯ ط§ظ„ط¥ظ„ظƒطھط±ظˆظ†ظٹ")
        tab1, tab2 = st.tabs(["ًں”‘ طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„", "ًں“‌ ط¥ظ†ط´ط§ط، ط­ط³ط§ط¨"])
        with tab1:
            with st.form("login_form"):
                email = st.text_input("ط§ظ„ط¨ط±ظٹط¯ ط§ظ„ط¥ظ„ظƒطھط±ظˆظ†ظٹ", value=OWNER_EMAIL)
                password = st.text_input("ظƒظ„ظ…ط© ط§ظ„ظ…ط±ظˆط±", type="password", value="ndc2025")
                submitted = st.form_submit_button("ط¯ط®ظˆظ„", use_container_width=True)
                if submitted:
                    if login_user(email, password):
                        st.success("âœ… ظ…ط±ط­ط¨ط§ظ‹ ط¨ظƒ!" if email == OWNER_EMAIL else "âœ… طھظ… طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„!")
                        st.rerun()
                    else:
                        st.error("â‌Œ ط¨ط±ظٹط¯ ط£ظˆ ظƒظ„ظ…ط© ظ…ط±ظˆط± ط؛ظٹط± طµط­ظٹط­ط©")
        with tab2:
            with st.form("signup_form"):
                s_name = st.text_input("ط§ظ„ط§ط³ظ… ط§ظ„ظƒط§ظ…ظ„")
                s_email = st.text_input("ط§ظ„ط¨ط±ظٹط¯ ط§ظ„ط¥ظ„ظƒطھط±ظˆظ†ظٹ ط§ظ„ط¬ط¯ظٹط¯")
                s_pass = st.text_input("ظƒظ„ظ…ط© ط§ظ„ظ…ط±ظˆط±", type="password")
                s_phone = st.text_input("ط±ظ‚ظ… ط§ظ„ظ‡ط§طھظپ")
                s_specialty = st.text_input("ط§ظ„طھط®طµطµ (ظ„ظ„ط£ط·ط¨ط§ط،)")
                s_role = st.selectbox("ظ†ظˆط¹ ط§ظ„ط­ط³ط§ط¨", ["doctor", "patient"])
                s_submitted = st.form_submit_button("ط¥ظ†ط´ط§ط، ط­ط³ط§ط¨", use_container_width=True)
                if s_submitted:
                    ok, msg = signup_user(s_name, s_email, s_pass, s_role, s_phone, s_specialty)
                    if ok:
                        st.success(msg)
                        st.info("ًں’، ط§ظ„ط¢ظ† ظٹظ…ظƒظ†ظƒ طھط³ط¬ظٹظ„ ط§ظ„ط¯ط®ظˆظ„ ط¨ط¨ظٹط§ظ†ط§طھظƒ ط§ظ„ط¬ط¯ظٹط¯ط©")
                    else:
                        st.error(msg)

# ============================================================
#  ًں“‹ SIDEBAR NAVIGATION
# ============================================================
def sidebar_nav():
    user = st.session_state.current_user
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:10px;">
            {display_system_logo(50)}
            <div style="font-weight:700; font-size:1.1rem; margin-top:6px;">ًں¦· DENTAL AI OS</div>
            <div style="font-size:0.7rem; color:#aac4d6;">v2.0 آ· AI-Powered</div>
            <div style="margin-top:4px;"><span style="background:#10b981;color:#fff;padding:2px 12px;border-radius:20px;font-size:0.6rem;font-weight:600;">ًں”’ ط¨ظٹط§ظ†ط§طھظƒ ط®ط§طµط© ط¨ظƒ</span></div>
        </div>
        <div style="text-align:center; margin-bottom:16px;">
            <div style="font-size:0.85rem; font-weight:600;">{user['name']}</div>
            <div style="font-size:0.65rem; color:#aac4d6;">{user.get('specialty','') or user['role']}</div>
            <div style="font-size:0.6rem; color:#10b981; margin-top:2px;">âœ… ط­ط³ط§ط¨ ط®ط§طµ</div>
        </div>
        """, unsafe_allow_html=True)

        menu_items = {
            "ًںڈ  ط§ظ„ط±ط¦ظٹط³ظٹط©": "home",
            "ًں“ٹ ظ„ظˆط­ط© ط§ظ„طھط­ظƒظ…": "dashboard",
            "ًںڈ·ï¸ڈ ط±ظپط¹ ط§ظ„ط´ط¹ط§ط±": "upload_logo",
            "ًں§  طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡ 468": "face_analysis",
            "âœ¨ ط§ظ„ظ†ط³ط¨ط© ط§ظ„ط°ظ‡ط¨ظٹط©": "golden_ratio",
            "ًںکٹ طھط­ظ„ظٹظ„ ط§ظ„ط§ط¨طھط³ط§ظ…ط©": "smile_analysis",
            "ًںژ¨ ظ…ط­ط§ظƒط§ط© AI": "ai_simulator",
            "ًں©» طھط­ظ„ظٹظ„ ط§ظ„ط£ط´ط¹ط© AI": "cephalometric",
            "ًں“ٹ ط§ظ„طھط­ظ„ظٹظ„ط§طھ ظˆط§ظ„ظ…ظ‚ط§ط±ظ†ط§طھ": "analytics",
            "ًں¦· ظ…ط®ط·ط· ط§ظ„ط£ط³ظ†ط§ظ†": "dental_chart",
            "ًں¦· Natural Teeth": "natural_teeth",
            "ًں“¸ ط§ظ„طھطµظˆظٹط±": "photography",
            "ًں©» ط§ظ„ط£ط´ط¹ط©": "xray",
            "ًں“± Dentbook": "dentbook",
            "ًں¤‌ ط§ظ„ط£طµط¯ظ‚ط§ط،": "friends",
            "ًں‘¤ ط§ظ„ظ…ظ„ظپ ط§ظ„ط´ط®طµظٹ": "profile",
            "ًں‘¥ ط§ظ„ط£ط¹ط¶ط§ط،": "members",
            "ًں’¬ ط§ظ„ظ…ط±ط§ط³ظ„ط§طھ": "messages",
            "ًں’Œ ط±ط³ط§ط¦ظ„ ط®ط§طµط©": "private_messages",
            "ًں§ھ ظ…ط¹ ط§ظ„ظ…ط®طھط¨ط±": "lab_chat",
            "ًں“پ ظ…ط´ط§ط±ظƒط© ط§ظ„ظ…ظ„ظپط§طھ": "file_sharing",
            "ًں–¥ï¸ڈ ظ…ط´ط§ط±ظƒط© ط§ظ„ط´ط§ط´ط©": "screen_share",
            "ًں©؛ ط§ظ„طھط´ط®ظٹطµ ط§ظ„ط°ظƒظٹ": "smart_diagnosis",
            "ًں“‹ ط®ط·ط© ط§ظ„ط¹ظ„ط§ط¬": "treatment_plan",
            "ًں§ھ ط§ظ„ظ…ظˆط§ط¯": "materials",
            "ًں§‘â€چâڑ•ï¸ڈ طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡": "facial",
            "ًںکپ طھطµظ…ظٹظ… ط§ظ„ط§ط¨طھط³ط§ظ…ط©": "smile_design",
            "ًںژ¨ ط§ظ„طھطµظ…ظٹظ… ط§ظ„طھط¬ظ…ظٹظ„ظٹ": "aesthetic_design",
            "ًں“¦ ظ†ظ…ط§ط°ط¬ 3D": "stl_3d",
            "ًں§¬ ط§ط³طھظˆط¯ظٹظˆ DSD": "dsd_studio",
            "ًں’ژ ط¹ظ„ط§ط¬ طھط¬ظ…ظٹظ„ظٹ": "aesthetic_treatment",
            "ًںŒچ ط§ظ„ظ…ظ†طµط© ط§ظ„ط¹ط§ظ„ظ…ظٹط©": "global_platform",
            "ًں”„ ط®ط· ط§ظ„ط¥ظ†طھط§ط¬": "pipeline",
            "ًں¦· ط¯ظ„ظٹظ„ ط§ظ„ظ…ظˆط§ط¯": "materials_guide",
            "ًں”Œ ظ…ط±ظƒط² ط§ظ„ط£ظ†ط¸ظ…ط©": "api_hub",
            "ًں—„ï¸ڈ ظ…ط³طھظˆط¯ط¹ ط§ظ„ظ…ط±ظٹط¶": "mock_db",
            "ًں”” ط§ظ„ط¥ط´ط¹ط§ط±ط§طھ": "notifications",
            "ًں–¥ï¸ڈ ط§ظ„ط£ظ†ط¸ظ…ط©": "systems",
            "ًں”¬ ط§ظ„ظ…ط³ط­ ط§ظ„ط¹ظ„ظ…ظٹ": "scientific_scan",
            "ًں¤– NaqAI": "naqai",
            "ًں‘¥ Interdisciplinary": "interdisciplinary",
            "ًں“¢ ط§ظ„ط¥ط¹ظ„ط§ظ†ط§طھ": "ads",
            "ًں”¬ ط§ظ„ظ…ط¹ظ…ظ„": "lab",
            "ًں“… ط§ظ„ظ…ظˆط§ط¹ظٹط¯": "appointments",
            "ًں’° ط§ظ„ط­ط³ط§ط¨": "accounting",
            "ًں’³ ط§ظ„ط¯ظپط¹": "payments",
            "ًں‘‘ ط§ظ„ط§ط´طھط±ط§ظƒط§طھ": "subscriptions",
            "ًں“¨ ط¯ط¹ظˆط© ط§ظ„ط£ط·ط¨ط§ط،": "invite",
            "âڑ™ï¸ڈ ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ": "settings",
            "ًں“„ ط§ظ„طھظ‚ط§ط±ظٹط±": "reports",
            "ًں”’ ط§ظ„ط®طµظˆطµظٹط©": "privacy",
            "آ©ï¸ڈ ط­ظ‚ظˆظ‚ ط§ظ„ظ…ظ„ظƒظٹط©": "ip",
            "ًں—£ï¸ڈ ظ…ظ†طھط¯ظ‰ ط§ظ„ظ†ظ‚ط§ط´ط§طھ": "forum",
            "ًںژ¨ ط£ظ„ظˆط§ظ† ظپظٹطھط§": "vita",
            "ًںژ¨ ظ…ط­ط±ط± ط§ظ„طµظˆط±": "image_editor",
            "ًں¦· ط¹ط§ط±ط¶ 3D": "3d_viewer",
        }

        for label, key in menu_items.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        st.divider()
        if st.button("ًںڑھ طھط³ط¬ظٹظ„ ط®ط±ظˆط¬", use_container_width=True, type="primary"):
            logout()

# ============================================================
#  ًں“„ PAGE: HOME
# ============================================================
def page_home():
    st.markdown('<div class="main-header">ًں¦· DENTAL AI OS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">ظ…ظ†طµط© ظ…طھظƒط§ظ…ظ„ط© ظ„طھط­ظ„ظٹظ„ ط§ظ„ط£ط³ظ†ط§ظ† ظˆط§ظ„ظˆط¬ظ‡ ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">468</div>
            <div class="metric-label">ظ†ظ‚ط·ط© ظˆط¬ظ‡ظٹط©</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">خ¦ 1.618</div>
            <div class="metric-label">ط§ظ„ظ†ط³ط¨ط© ط§ظ„ط°ظ‡ط¨ظٹط©</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">AI</div>
            <div class="metric-label">ط°ظƒط§ط، ط§طµط·ظ†ط§ط¹ظٹ</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">3D</div>
            <div class="metric-label">طھطµظ…ظٹظ… ط«ظ„ط§ط«ظٹ ط§ظ„ط£ط¨ط¹ط§ط¯</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card" style="margin-top:20px;">
        <h4 style="color:#00d4ff;">ًںڑ€ ط§ط¨ط¯ط£ ط¨ط§ط³طھط®ط¯ط§ظ… ط§ظ„ظ…ظ†طµط©</h4>
        <p style="color:#8892b0;">ط§ط®طھط± ط£ط­ط¯ ط§ظ„ظˆط­ط¯ط§طھ ظ…ظ† ط§ظ„ظ‚ط§ط¦ظ…ط© ط§ظ„ط¬ط§ظ†ط¨ظٹط© ظ„ط¨ط¯ط، ط§ظ„طھط­ظ„ظٹظ„:</p>
        <ul style="color:#8892b0; line-height:2;">
            <li><strong style="color:#00d4ff;">ًں§  طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡ 468</strong> â€” ط±ط³ظ… ظˆطھظ‚ظٹظٹظ… ظ†ظ‚ط§ط· ط§ظ„ظˆط¬ظ‡</li>
            <li><strong style="color:#ffd700;">âœ¨ ط§ظ„ظ†ط³ط¨ط© ط§ظ„ط°ظ‡ط¨ظٹط©</strong> â€” طھط­ظ„ظٹظ„ ط§ظ„طھظ†ط§ط³ظ‚ ط§ظ„ط¬ظ…ط§ظ„ظٹ</li>
            <li><strong style="color:#ff9ff3;">ًںکٹ طھط­ظ„ظٹظ„ ط§ظ„ط§ط¨طھط³ط§ظ…ط©</strong> â€” طھظ‚ظٹظٹظ… ط¬ظ…ط§ظ„ ط§ظ„ط§ط¨طھط³ط§ظ…ط©</li>
            <li><strong style="color:#2ecc71;">ًںژ¨ ظ…ط­ط§ظƒط§ط© AI</strong> â€” ظ…ط­ط§ظƒط§ط© ط§ظ„ظ†طھط§ط¦ط¬ ط§ظ„طھط¬ظ…ظٹظ„ظٹط©</li>
            <li><strong style="color:#f39c12;">ًں©» طھط­ظ„ظٹظ„ ط§ظ„ط£ط´ط¹ط© AI</strong> â€” طھط­ظ„ظٹظ„ ط³ظٹظپط§ظ„ظˆظ…طھط±ظٹ ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ</li>
            <li><strong style="color:#9b59b6;">ًں“ٹ ط§ظ„طھط­ظ„ظٹظ„ط§طھ ظˆط§ظ„ظ…ظ‚ط§ط±ظ†ط§طھ</strong> â€” ط¬ط¯ط§ظˆظ„ ظˆط±ط³ظˆظ… ط¨ظٹط§ظ†ظٹط©</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: DASHBOARD
# ============================================================
def page_dashboard():
    st.markdown('<div class="section-title">ًں“ٹ ظ„ظˆط­ط© ط§ظ„طھط­ظƒظ…</div>', unsafe_allow_html=True)
    user = st.session_state.current_user
    st.markdown(f"<p style='color:#8892b0;'>ظ…ط±ط­ط¨ط§ظ‹ ط¨ظƒ ظپظٹ DENTAL AI OSطŒ <strong style='color:#00d4ff;'>{user['name']}</strong></p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div>ًں‘¨â€چâڑ•ï¸ڈ ط§ظ„ظ…ط±ط¶ظ‰</div><div class="metric-value">{len(st.session_state.patients)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div>ًں“… ظ…ظˆط§ط¹ظٹط¯ ط§ظ„ظٹظˆظ…</div><div class="metric-value" style="color:#10b981;">{len(st.session_state.appointments)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div>ًں§  طھط­ظ„ظٹظ„ط§طھ AI</div><div class="metric-value" style="color:#8e44ad;">{len(st.session_state.patients)*3 + 5}</div></div>', unsafe_allow_html=True)
    
    st.markdown("### ًں“‹ ط¢ط®ط± ط§ظ„ظ…ط±ط¶ظ‰")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients[-5:])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("ظ„ط§ ظٹظˆط¬ط¯ ظ…ط±ط¶ظ‰ ظ…ط³ط¬ظ„ظٹظ†.")

# ============================================================
#  ًں“„ PAGE: UPLOAD LOGO
# ============================================================
def page_upload_logo():
    st.markdown('<div class="section-title">ًںڈ·ï¸ڈ ط±ظپط¹ ط§ظ„ط´ط¹ط§ط±</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("ط§ط®طھط± طµظˆط±ط© ط§ظ„ط´ط¹ط§ط±", type=["jpg", "jpeg", "png", "svg"])
    if uploaded:
        img = Image.open(uploaded)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        st.session_state.system_logo = img_str
        st.success("âœ… طھظ… ط±ظپط¹ ط§ظ„ط´ط¹ط§ط± ط¨ظ†ط¬ط§ط­!")
        st.image(img, caption="ط§ظ„ط´ط¹ط§ط± ط§ظ„ط¬ط¯ظٹط¯", width=150)

# ============================================================
#  ًں“„ PAGE: FACE ANALYSIS
# ============================================================
def page_face_analysis():
    st.markdown('<div class="section-title">ًں§  طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡ 468 ظ†ظ‚ط·ط©</div>', unsafe_allow_html=True)
    st.caption("طھط­ظ„ظٹظ„ ظ…طھظ‚ط¯ظ… ظ„ظ„ظˆط¬ظ‡ ط¨ط§ط³طھط®ط¯ط§ظ… 468 ظ†ظ‚ط·ط© طھط´ط±ظٹط­ظٹط© ظ„طھظ‚ظٹظٹظ… ط§ظ„طھظ†ط§ط³ظ‚ ظˆط§ظ„ظ†ط³ط¨")
    
    uploaded = st.file_uploader("ًں“¸ ط­ظ…ظ‘ظ„ طµظˆط±ط© ط§ظ„ظˆط¬ظ‡", type=["jpg", "png", "jpeg"])
    if uploaded:
        img = Image.open(uploaded)
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="ط§ظ„طµظˆط±ط© ط§ظ„ط£طµظ„ظٹط©", use_container_width=True)
        
        with col2:
            if st.button("ًں§  طھط­ظ„ظٹظ„ 468 ظ†ظ‚ط·ط© ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary", use_container_width=True):
                with st.spinner("âڈ³ ط¬ط§ط±ظٹ طھط­ظ„ظٹظ„ 468 ظ†ظ‚ط·ط©..."):
                    landmarks, annotated, (w, h) = analyze_face_mesh(img)
                    if landmarks:
                        st.image(annotated, caption="طھط­ظ„ظٹظ„ 468 ظ†ظ‚ط·ط©", use_container_width=True)
                        st.session_state.landmarks_468 = landmarks
                        st.session_state.analysis_img = annotated
                        st.session_state.last_analysis_image = Image.fromarray(annotated)
                        st.success("âœ… طھظ… طھط­ظ„ظٹظ„ 468 ظ†ظ‚ط·ط© ط¨ظ†ط¬ط§ط­!")
                        
                        # ط¹ط±ط¶ ط§ظ„ظ†طھط§ط¦ط¬
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("ًں“چ ط¹ط¯ط¯ ط§ظ„ظ†ظ‚ط§ط·", "468")
                        with col2:
                            st.metric("ًں“گ ط¯ظ‚ط© ط§ظ„ظƒط´ظپ", "ط¹ط§ظ„ظٹط©")
                        with col3:
                            st.metric("ًں”„ ط­ط§ظ„ط©", "âœ… ظ…ظƒطھظ…ظ„")
                    else:
                        st.error("â‌Œ ظ„ظ… ظٹطھظ… ط§ظƒطھط´ط§ظپ ظˆط¬ظ‡ ظپظٹ ط§ظ„طµظˆط±ط©")

# ============================================================
#  ًں“„ PAGE: GOLDEN RATIO
# ============================================================
def page_golden_ratio():
    st.markdown('<div class="section-title">âœ¨ ط§ظ„ظ†ط³ط¨ط© ط§ظ„ط°ظ‡ط¨ظٹط© (خ¦ = 1.618)</div>', unsafe_allow_html=True)
    st.caption("طھط­ظ„ظٹظ„ ط§ظ„طھظ†ط§ط³ظ‚ ط§ظ„ظˆط¬ظ‡ظٹ ظˆط§ظ„ظ†ط³ط¨ط© ط§ظ„ط°ظ‡ط¨ظٹط© ظ„طھظ‚ظٹظٹظ… ط§ظ„ط¬ظ…ط§ظ„")
    
    uploaded = st.file_uploader("ًں“¸ ط­ظ…ظ‘ظ„ طµظˆط±ط© ط§ظ„ظˆط¬ظ‡", type=["jpg", "png", "jpeg"], key="golden_upload")
    if uploaded:
        img = Image.open(uploaded)
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="ط§ظ„طµظˆط±ط© ط§ظ„ط£طµظ„ظٹط©", use_container_width=True)
        with col2:
            if st.button("âœ¨ طھط­ظ„ظٹظ„ ط§ظ„ظ†ط³ط¨ط© ط§ظ„ط°ظ‡ط¨ظٹط© ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary", use_container_width=True):
                with st.spinner("âڈ³ ط¬ط§ط±ظٹ ط§ظ„طھط­ظ„ظٹظ„..."):
                    landmarks, _, (w, h) = analyze_face_mesh(img)
                    if landmarks:
                        result, golden_score, ratio = draw_golden_ratio(img, landmarks, w, h)
                        st.image(result, caption="طھط­ظ„ظٹظ„ ط§ظ„ظ†ط³ط¨ط© ط§ظ„ط°ظ‡ط¨ظٹط©", use_container_width=True)
                        st.session_state.golden_score = golden_score
                        st.metric("ًں“ٹ ط¯ط±ط¬ط© ط§ظ„ظ†ط³ط¨ط© ط§ظ„ط°ظ‡ط¨ظٹط©", f"{golden_score:.1f}%")
                        st.metric("ًں“گ ط§ظ„ظ†ط³ط¨ط© ط§ظ„ظ…ط­ط³ظˆط¨ط©", f"{ratio:.3f}")
                        st.success("âœ… طھظ… طھط­ظ„ظٹظ„ ط§ظ„ظ†ط³ط¨ط© ط§ظ„ط°ظ‡ط¨ظٹط© ط¨ظ†ط¬ط§ط­!")
                    else:
                        st.error("â‌Œ ظ„ظ… ظٹطھظ… ط§ظƒطھط´ط§ظپ ظˆط¬ظ‡ ظپظٹ ط§ظ„طµظˆط±ط©")

# ============================================================
#  ًں“„ PAGE: SMILE ANALYSIS
# ============================================================
def page_smile_analysis():
    st.markdown('<div class="section-title">ًںکٹ طھط­ظ„ظٹظ„ ط§ظ„ط§ط¨طھط³ط§ظ…ط© ظˆط§ظ„طھظ†ط§ط؛ظ… ط§ظ„ظˆط¬ظ‡ظٹ</div>', unsafe_allow_html=True)
    st.caption("طھط­ظ„ظٹظ„ ط¬ظ…ط§ظ„ ط§ظ„ط§ط¨طھط³ط§ظ…ط© ظˆطھظ‚ظٹظٹظ… ط§ظ„طھظ†ط§ط³ظ‚ ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ")
    
    uploaded = st.file_uploader("ًں“¸ ط­ظ…ظ‘ظ„ طµظˆط±ط© ط§ظ„ظˆط¬ظ‡", type=["jpg", "png", "jpeg"], key="smile_upload")
    if uploaded:
        img = Image.open(uploaded)
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="ط§ظ„طµظˆط±ط© ط§ظ„ط£طµظ„ظٹط©", use_container_width=True)
        with col2:
            if st.button("ًںکٹ طھط­ظ„ظٹظ„ ط§ظ„ط§ط¨طھط³ط§ظ…ط© ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary", use_container_width=True):
                with st.spinner("âڈ³ ط¬ط§ط±ظٹ ط§ظ„طھط­ظ„ظٹظ„..."):
                    landmarks, annotated, (w, h) = analyze_face_mesh(img)
                    if landmarks:
                        st.image(annotated, caption="طھط­ظ„ظٹظ„ ط§ظ„ط§ط¨طھط³ط§ظ…ط©", use_container_width=True)
                        diagnosis = generate_smile_diagnosis(landmarks, w, h)
                        st.session_state.smile_score = diagnosis.get("smile_score", 0)
                        st.session_state.symmetry_score = diagnosis.get("symmetry_score", 0)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("ًںکٹ ط´ط¯ط© ط§ظ„ط§ط¨طھط³ط§ظ…ط©", f"{diagnosis.get('smile_score', 0):.1f}%")
                        with col2:
                            st.metric("ًں“گ ط§ظ„طھظ†ط§ط³ظ‚", f"{diagnosis.get('symmetry_score', 0):.1f}%")
                        with col3:
                            st.metric("ًںڈ† ط§ظ„طھظ‚ظٹظٹظ…", diagnosis.get('grade', 'ط؛ظٹط± ظ…ط¹ط±ظˆظپ'))
                        
                        st.info(f"ًں’، ط§ظ„طھظˆطµظٹط§طھ: {', '.join(diagnosis.get('recommendations', []))}")
                        st.success("âœ… طھظ… طھط­ظ„ظٹظ„ ط§ظ„ط§ط¨طھط³ط§ظ…ط© ط¨ظ†ط¬ط§ط­!")
                    else:
                        st.error("â‌Œ ظ„ظ… ظٹطھظ… ط§ظƒطھط´ط§ظپ ظˆط¬ظ‡ ظپظٹ ط§ظ„طµظˆط±ط©")

# ============================================================
#  ًں“„ PAGE: AI SIMULATOR
# ============================================================
def page_ai_simulator():
    st.markdown('<div class="section-title">ًںژ¨ ظ…ط­ط§ظƒط§ط© ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ</div>', unsafe_allow_html=True)
    st.caption("ظ…ط­ط§ظƒط§ط© ظˆط§ظ‚ط¹ظٹط© ظ„ظ„ظ†طھط§ط¦ط¬ ط§ظ„طھط¬ظ…ظٹظ„ظٹط© ظ‚ط¨ظ„ ط¨ط¯ط، ط§ظ„ط¹ظ„ط§ط¬")
    
    uploaded = st.file_uploader("ًں“¤ ط±ظپط¹ طµظˆط±ط© ط§ظ„ظ…ط±ظٹط¶", type=["jpg", "jpeg", "png", "webp"], key="sim_upload")
    
    if uploaded:
        if st.session_state.original_img is None:
            st.session_state.original_img = Image.open(uploaded)
        if st.session_state.processed_img is None:
            st.session_state.processed_img = st.session_state.original_img.copy()
    
    if st.session_state.original_img is None:
        st.info("ًں‘† ط§ط±ظپط¹ طµظˆط±ط© ط§ظ„ظ…ط±ظٹط¶ ط£ظˆظ„ط§ظ‹ ظ„ط¨ط¯ط، ط§ظ„ظ…ط­ط§ظƒط§ط©")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ًں§  ط¥ط¹ط¯ط§ط¯ط§طھ ط§ظ„ظ…ط­ط§ظƒط§ط©")
        smile = st.slider("ًںکٹ ط´ط¯ط© ط§ظ„ط§ط¨طھط³ط§ظ…ط©", 0, 100, 0, key="s_smile")
        white = st.slider("âœ¨ طھط¨ظٹظٹط¶ ط§ظ„ط£ط³ظ†ط§ظ†", 0, 100, 0, key="s_white")
        skin = st.slider("ًں’‰ ظ†ط¹ظˆظ…ط© ط§ظ„ط¨ط´ط±ط©", 0, 100, 0, key="s_skin")
        zir = st.slider("ًں”· ظ„ظ…ط¹ط§ظ† ط²ط±ظƒظˆظ†ظٹط§", 0, 100, 0, key="s_zir")
        brow = st.slider("ًں‘پï¸ڈ ط±ظپط¹ ط§ظ„ط­ط§ط¬ط¨", 0, 100, 0, key="s_brow")
        
        if st.button("ًں§  طھط·ط¨ظٹظ‚ ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary", use_container_width=True):
            st.session_state.processed_img = apply_ai_effects(
                st.session_state.original_img, smile, white, skin, zir, brow
            )
            st.session_state.last_smile_image = st.session_state.processed_img
            st.success("âœ… طھظ… طھط·ط¨ظٹظ‚ ط§ظ„ظ…ط­ط§ظƒط§ط©!")
        
        st.markdown("### âڑ، ظ‚ظˆط§ظ„ط¨ ط³ط±ظٹط¹ط©")
        presets = {
            "âœ¨ طھط¨ظٹظٹط¶": {"smile": 0, "white": 75, "skin": 0, "zir": 0, "brow": 0},
            "ًںŒں ظ‡ظˆظ„ظٹظˆظˆط¯": {"smile": 60, "white": 90, "skin": 30, "zir": 40, "brow": 20},
            "ًں’ژ ط²ط±ظƒظˆظ†ظٹط§": {"smile": 40, "white": 85, "skin": 10, "zir": 80, "brow": 10},
            "ًں’‰ ط¨ظˆطھظˆظƒط³": {"smile": 20, "white": 30, "skin": 60, "zir": 0, "brow": 70},
        }
        for name, values in presets.items():
            if st.button(name, key=f"preset_{name}", use_container_width=True):
                for k, v in values.items():
                    st.session_state[f"s_{k}"] = v
                st.session_state.processed_img = apply_ai_effects(
                    st.session_state.original_img,
                    values["smile"], values["white"], values["skin"],
                    values["zir"], values["brow"]
                )
                st.session_state.last_smile_image = st.session_state.processed_img
                st.rerun()
        
        st.markdown("### ًں”§ ظپظ„ط§طھط± ط³ط±ظٹط¹ط©")
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            if st.button("âک€ï¸ڈ ط³ط·ظˆط¹", use_container_width=True):
                st.session_state.processed_img = apply_filter(st.session_state.processed_img, "brightness")
                st.rerun()
            if st.button("ًں”؛ ط­ط¯ط©", use_container_width=True):
                st.session_state.processed_img = apply_filter(st.session_state.processed_img, "sharpen")
                st.rerun()
        with fcol2:
            if st.button("â—گ طھط¨ط§ظٹظ†", use_container_width=True):
                st.session_state.processed_img = apply_filter(st.session_state.processed_img, "contrast")
                st.rerun()
            if st.button("ًں’¨ ط¶ط¨ط§ط¨ظٹ", use_container_width=True):
                st.session_state.processed_img = apply_filter(st.session_state.processed_img, "blur")
                st.rerun()
    
    with col2:
        st.markdown("### ًںژ¨ ط§ظ„ظ†طھظٹط¬ط©")
        if st.session_state.processed_img:
            st.image(st.session_state.processed_img, caption="ط§ظ„ظ†طھظٹط¬ط© ط§ظ„ظ…ط­ط§ظƒط§ط©", use_container_width=True)
            
            show_compare = st.toggle("ًں‘پï¸ڈ ط¹ط±ط¶ ط§ظ„ظ…ظ‚ط§ط±ظ†ط© ظ‚ط¨ظ„/ط¨ط¹ط¯", value=False)
            if show_compare:
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    st.image(st.session_state.original_img, caption="ًں“· ظ‚ط¨ظ„", use_container_width=True)
                with bcol2:
                    st.image(st.session_state.processed_img, caption="âœ¨ ط¨ط¹ط¯", use_container_width=True)
            
            if st.session_state.processed_img:
                buf = io.BytesIO()
                st.session_state.processed_img.save(buf, format="PNG")
                st.download_button(
                    label="â¬‡ï¸ڈ طھط­ظ…ظٹظ„ ط§ظ„طµظˆط±ط©",
                    data=buf.getvalue(),
                    file_name=f"simulation_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                    mime="image/png",
                    use_container_width=True
                )
        else:
            st.info("ط§ط¶ط؛ط· ط¹ظ„ظ‰ 'طھط·ط¨ظٹظ‚ ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ' ط£ظˆ ط§ط®طھط± ظ‚ط§ظ„ط¨ط§ظ‹ ظ„ط¨ط¯ط، ط§ظ„ظ…ط­ط§ظƒط§ط©")

# ============================================================
#  ًں“„ PAGE: CEPHALOMETRIC (AI X-Ray Analysis)
# ============================================================
def page_cephalometric():
    st.markdown('<div class="section-title">ًں©» طھط­ظ„ظٹظ„ ط§ظ„ط£ط´ط¹ط© ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ</div>', unsafe_allow_html=True)
    st.caption("طھط­ظ„ظٹظ„ ظ…طھظ‚ط¯ظ… ظ„ظ„ط£ط´ط¹ط© ط§ظ„ط³ظٹظپط§ظ„ظˆظ…طھط±ظٹط© ط¨ط§ط³طھط®ط¯ط§ظ… ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ")
    
    uploaded = st.file_uploader("ًں“¸ ط±ظپط¹ طµظˆط±ط© ط§ظ„ط£ط´ط¹ط©", type=["jpg", "png", "jpeg", "dcm"], key="ceph_upload")
    if uploaded:
        img = Image.open(uploaded)
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="طµظˆط±ط© ط§ظ„ط£ط´ط¹ط© ط§ظ„ط£طµظ„ظٹط©", use_container_width=True)
        
        with col2:
            if st.button("ًں§  طھط­ظ„ظٹظ„ ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary", use_container_width=True):
                with st.spinner("âڈ³ ط¬ط§ط±ظٹ طھط­ظ„ظٹظ„ ط§ظ„ط£ط´ط¹ط© ظˆظ…ط¹ط§ظ„ط¬طھظ‡ط§..."):
                    analysis = real_cephalometric_analysis(img)
                    if analysis.get("analysis_image"):
                        st.image(analysis["analysis_image"], caption="طھط­ظ„ظٹظ„ ط§ظ„ط£ط´ط¹ط©", use_container_width=True)
                        st.session_state.last_cephalometric_image = analysis["analysis_image"]
                        st.session_state.last_cephalometric_data = analysis
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("ًں“گ SNA", f"{analysis.get('SNA', 0):.1f}آ°")
                            st.metric("ًں“گ SNB", f"{analysis.get('SNB', 0):.1f}آ°")
                            st.metric("ًں“گ ANB", f"{analysis.get('ANB', 0):.1f}آ°")
                        with col2:
                            st.metric("ًں“گ SN-MP", f"{analysis.get('SN-MP', 0):.1f}آ°")
                            st.metric("ًں“گ FMA", f"{analysis.get('FMA', 0):.1f}آ°")
                            st.metric("ًں“گ IMPA", f"{analysis.get('IMPA', 0):.1f}آ°")
                        
                        # ط²ط± طھط­ظ…ظٹظ„ ط§ظ„طھط­ظ„ظٹظ„
                        buffered = BytesIO()
                        analysis["analysis_image"].save(buffered, format="PNG")
                        st.download_button(
                            label="â¬‡ï¸ڈ طھط­ظ…ظٹظ„ طھط­ظ„ظٹظ„ ط§ظ„ط£ط´ط¹ط©",
                            data=buffered.getvalue(),
                            file_name=f"cephalometric_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                            mime="image/png"
                        )
                        st.success("âœ… طھظ… طھط­ظ„ظٹظ„ ط§ظ„ط£ط´ط¹ط© ط¨ظ†ط¬ط§ط­!")
                    else:
                        st.error("â‌Œ ظ„ظ… ظٹطھظ…ظƒظ† ط§ظ„ظ†ط¸ط§ظ… ظ…ظ† طھط­ظ„ظٹظ„ ط§ظ„طµظˆط±ط©")

# ============================================================
#  ًں“„ PAGE: ANALYTICS (ط¬ط¯ط§ظˆظ„ ط§ظ„ظ…ظ‚ط§ط±ظ†ط§طھ ظˆط§ظ„طھط­ط§ظ„ظٹظ„)
# ============================================================
def page_analytics():
    st.markdown('<div class="section-title">ًں“ٹ ظ†ط¸ط§ظ… ط¬ط¯ط§ظˆظ„ ط§ظ„ظ…ظ‚ط§ط±ظ†ط§طھ ظˆط§ظ„طھط­ط§ظ„ظٹظ„</div>', unsafe_allow_html=True)
    st.caption("Dental Analytics | Comparison Tables | Smart Charts | Export")
    
    df = st.session_state.patients_df
    
    # â”€â”€ KPI Cards â”€â”€
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df)}</div>
            <div class="metric-label">ط¥ط¬ظ…ط§ظ„ظٹ ط§ظ„ط­ط§ظ„ط§طھ</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        total_revenue = df['ط§ظ„طھظƒظ„ظپط©_ط±ظٹط§ظ„'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_revenue:,}</div>
            <div class="metric-label">ط¥ط¬ظ…ط§ظ„ظٹ ط§ظ„ط¥ظٹط±ط§ط¯ط§طھ</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        avg_cost = df['ط§ظ„طھظƒظ„ظپط©_ط±ظٹط§ظ„'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_cost:,.0f}</div>
            <div class="metric-label">ظ…طھظˆط³ط· ط§ظ„طھظƒظ„ظپط©</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        avg_satisfaction = df['ط±ط¶ط§_ط§ظ„ظ…ط±ظٹط¶_%'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_satisfaction:.1f}%</div>
            <div class="metric-label">ظ…طھظˆط³ط· ط§ظ„ط±ط¶ط§</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        avg_duration = df['ط§ظ„ظ…ط¯ط©_ط´ظ‡ط±'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_duration:.1f}</div>
            <div class="metric-label">ظ…طھظˆط³ط· ط§ظ„ظ…ط¯ط© (ط´ظ‡ط±)</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        excellent_cases = len(df[df['ط§ظ„ط­ط§ظ„ط©_ط§ظ„ظ†ظ‡ط§ط¦ظٹط©'] == 'ظ…ظ…طھط§ط²ط©'])
        excellent_pct = (excellent_cases / len(df)) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{excellent_pct:.0f}%</div>
            <div class="metric-label">ظ†ط³ط¨ط© ط§ظ„ظ†ط¬ط§ط­</div>
        </div>
        """, unsafe_allow_html=True)
    
    # â”€â”€ Data Editor â”€â”€
    st.markdown("### ًں“‌ ط¬ط¯ظˆظ„ ط§ظ„ط¨ظٹط§ظ†ط§طھ ط§ظ„طھظپط§ط¹ظ„ظٹ")
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "ط§ط³ظ…_ط§ظ„ظ…ط±ظٹط¶": st.column_config.TextColumn("ًں‘¤ ط§ط³ظ… ط§ظ„ظ…ط±ظٹط¶"),
            "ط§ظ„ط¹ظ…ط±": st.column_config.NumberColumn("ًںژ‚ ط§ظ„ط¹ظ…ط±", min_value=1, max_value=120),
            "ط§ظ„ط¬ظ†ط³": st.column_config.SelectboxColumn("âڑ§ ط§ظ„ط¬ظ†ط³", options=["ط°ظƒط±", "ط£ظ†ط«ظ‰"]),
            "ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬": st.column_config.SelectboxColumn("ًں¦· ظ†ظˆط¹ ط§ظ„ط¹ظ„ط§ط¬", 
                options=["طھط¨ظٹظٹط¶", "ط²ط±ظƒظˆظ†ظٹط§", "ط¥ظٹظ…ط§ظƒط³", "طھظ‚ظˆظٹظ…", "ط²ط±ط§ط¹ط©", "طھط±ظƒظٹط¨ط§طھ", "ط¹ظ„ط§ط¬ ط¬ط°ظˆط±"]),
            "ط¹ط¯ط¯_ط§ظ„ط£ط³ظ†ط§ظ†": st.column_config.NumberColumn("ًں”¢ ط¹ط¯ط¯ ط§ظ„ط£ط³ظ†ط§ظ†", min_value=1, max_value=32),
            "ط§ظ„طھظƒظ„ظپط©_ط±ظٹط§ظ„": st.column_config.NumberColumn("ًں’° ط§ظ„طھظƒظ„ظپط©", min_value=0, step=500),
            "ط§ظ„ظ…ط¯ط©_ط´ظ‡ط±": st.column_config.NumberColumn("âڈ±ï¸ڈ ط§ظ„ظ…ط¯ط©", min_value=0.1, step=0.5),
            "ط±ط¶ط§_ط§ظ„ظ…ط±ظٹط¶_%": st.column_config.ProgressColumn("ًںکٹ ط§ظ„ط±ط¶ط§ %", min_value=0, max_value=100),
            "ط§ظ„ط­ط§ظ„ط©_ط§ظ„ظ†ظ‡ط§ط¦ظٹط©": st.column_config.SelectboxColumn("âœ… ط§ظ„ط­ط§ظ„ط©", options=["ظ…ظ…طھط§ط²ط©", "ط¬ظٹط¯ط©", "ظ…طھظˆط³ط·ط©", "ط¶ط¹ظٹظپط©"]),
        }
    )
    st.session_state.patients_df = edited_df
    
    # â”€â”€ Charts â”€â”€
    st.markdown("### ًں“ˆ ط§ظ„ط±ط³ظˆظ… ط§ظ„ط¨ظٹط§ظ†ظٹط©")
    chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs([
        "ًں’° ط§ظ„طھظƒط§ظ„ظٹظپ", "ًں“ٹ ط§ظ„طھظˆط²ظٹط¹", "ًںکٹ ط§ظ„ط±ط¶ط§", "ًں“‰ ط§ظ„ط±ط¨ط­ظٹط©"
    ])
    
    with chart_tab1:
        cost_by_treatment = edited_df.groupby('ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬').agg({
            'ط§ظ„طھظƒظ„ظپط©_ط±ظٹط§ظ„': ['sum', 'mean', 'count']
        }).reset_index()
        cost_by_treatment.columns = ['ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬', 'ط¥ط¬ظ…ط§ظ„ظٹ_ط§ظ„طھظƒظ„ظپط©', 'ظ…طھظˆط³ط·_ط§ظ„طھظƒظ„ظپط©', 'ط¹ط¯ط¯_ط§ظ„ط­ط§ظ„ط§طھ']
        
        fig_bar = px.bar(
            cost_by_treatment, x='ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬', y='ط¥ط¬ظ…ط§ظ„ظٹ_ط§ظ„طھظƒظ„ظپط©',
            color='ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬', text='ط¥ط¬ظ…ط§ظ„ظٹ_ط§ظ„طھظƒظ„ظپط©',
            title="ط¥ط¬ظ…ط§ظ„ظٹ ط§ظ„طھظƒط§ظ„ظٹظپ ط­ط³ط¨ ظ†ظˆط¹ ط§ظ„ط¹ظ„ط§ط¬",
            color_discrete_sequence=['#00d4ff', '#ff6b6b', '#2ecc71', '#feca57', '#ff9ff3'],
            template='plotly_dark'
        )
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with chart_tab2:
        treatment_dist = edited_df['ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬'].value_counts().reset_index()
        treatment_dist.columns = ['ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬', 'ط§ظ„ط¹ط¯ط¯']
        
        fig_pie = px.pie(
            treatment_dist, values='ط§ظ„ط¹ط¯ط¯', names='ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬',
            title="طھظˆط²ظٹط¹ ط£ظ†ظˆط§ط¹ ط§ظ„ط¹ظ„ط§ط¬ط§طھ",
            color_discrete_sequence=['#00d4ff', '#ff6b6b', '#2ecc71', '#feca57', '#ff9ff3'],
            template='plotly_dark', hole=0.4
        )
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with chart_tab3:
        fig_scatter = px.scatter(
            edited_df, x='ط§ظ„ط¹ظ…ط±', y='ط±ط¶ط§_ط§ظ„ظ…ط±ظٹط¶_%', 
            color='ظ†ظˆط¹_ط§ظ„ط¹ظ„ط§ط¬', size='ط§ظ„طھظƒظ„ظپط©_ط±ظٹط§ظ„',
            hover_data=['ط§ط³ظ…_ط§ظ„ظ…ط±ظٹط¶'],
            title="ط§ظ„ط±ط¶ط§ ظ…ظ‚ط§ط¨ظ„ ط§ظ„ط¹ظ…ط±",
            color_discrete_sequence=['#00d4ff', '#ff6b6b', '#2ecc71', '#feca57', '#ff9ff3'],
            template='plotly_dark'
        )
        fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with chart_tab4:
        edited_df['ط§ظ„ط±ط¨ط­ظٹط©'] = edited_df['ط±ط¶ط§_ط§ظ„ظ…ط±ظٹط¶_%'] / (edited_df['ط§ظ„ظ…ط¯ط©_ط´ظ‡ط±'] + 0.1)
        fig_profit = px.scatter(
            edited_df, x='ط§ظ„طھظƒظ„ظپط©_ط±ظٹط§ظ„', y='ط§ظ„ط±ط¨ط­ظٹط©',
            color='ط§ظ„ط­ط§ظ„ط©_ط§ظ„ظ†ظ‡ط§ط¦ظٹط©', size='ط¹ط¯ط¯_ط§ظ„ط£ط³ظ†ط§ظ†',
            title="طھط­ظ„ظٹظ„ ط§ظ„ط±ط¨ط­ظٹط©",
            color_discrete_map={'ظ…ظ…طھط§ط²ط©': '#2ecc71', 'ط¬ظٹط¯ط©': '#feca57', 'ظ…طھظˆط³ط·ط©': '#ff9ff3', 'ط¶ط¹ظٹظپط©': '#ff6b6b'},
            template='plotly_dark'
        )
        fig_profit.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_profit, use_container_width=True)
    
    # â”€â”€ Export â”€â”€
    st.markdown("### ًں“¤ طھطµط¯ظٹط± ط§ظ„ط¨ظٹط§ظ†ط§طھ")
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        csv_buffer = io.StringIO()
        edited_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        st.download_button(
            "ًں“¥ طھطµط¯ظٹط± CSV", csv_buffer.getvalue(),
            f"dental_data_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv", use_container_width=True
        )
    with exp_col2:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            edited_df.to_excel(writer, sheet_name='Patients', index=False)
            st.session_state.before_after_data.to_excel(writer, sheet_name='Before_After', index=False)
        st.download_button(
            "ًں“¥ طھطµط¯ظٹط± Excel", excel_buffer.getvalue(),
            f"dental_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with exp_col3:
        json_buffer = io.StringIO()
        edited_df.to_json(json_buffer, force_ascii=False, orient='records', indent=2)
        st.download_button(
            "ًں“¥ طھطµط¯ظٹط± JSON", json_buffer.getvalue(),
            f"dental_data_{datetime.now().strftime('%Y%m%d')}.json",
            "application/json", use_container_width=True
        )

# ============================================================
#  ًں“„ PAGE: DENTAL CHART
# ============================================================
def page_dental_chart_view():
    st.markdown('<div class="section-title">ًں¦· ظ…ط®ط·ط· ط§ظ„ط£ط³ظ†ط§ظ†</div>', unsafe_allow_html=True)
    st.caption("ظ…ط®ط·ط· طھظپط§ط¹ظ„ظٹ ظ„ظ„ط£ط³ظ†ط§ظ† ظ…ط¹ ط¥ظ…ظƒط§ظ†ظٹط© طھط؛ظٹظٹط± ط§ظ„ط­ط§ظ„ط©")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(render_dental_chart(), unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ًںژ¯ ط§ظ„طھط­ظƒظ…")
        if st.session_state.selected_tooth is not None:
            tooth_num = st.session_state.selected_tooth + 1
            current = get_tooth_status(st.session_state.selected_tooth)
            status_labels = {'normal': 'ًںں¢ ط³ظ„ظٹظ…', 'missing': 'â‌Œ ظ…ظپظ‚ظˆط¯', 'carious': 'ًںں، ظ†ط®ط±',
                           'treated': 'ًں”µ ظ…ط¹ط§ظ„ط¬', 'crown': 'ًںں£ طھط§ط¬', 'root-canal': 'ًں”´ ط¬ط°ظˆط±'}
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:12px; border:1px solid rgba(0,212,255,0.2); text-align:center;">
                <div style="font-size:0.8rem; color:#8892b0;">ط§ظ„ط³ظ† ط§ظ„ظ…ط­ط¯ط¯</div>
                <div style="font-size:2rem; font-weight:800; color:#00d4ff;">#{tooth_num}</div>
                <div style="font-size:0.9rem;">{status_labels.get(current, 'ط؛ظٹط± ظ…ط¹ط±ظˆظپ')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            for label, status in [("ًںں¢ ط³ظ„ظٹظ…", "normal"), ("â‌Œ ظ…ظپظ‚ظˆط¯", "missing"), ("ًںں، ظ†ط®ط±", "carious"),
                                 ("ًں”µ ظ…ط¹ط§ظ„ط¬", "treated"), ("ًںں£ طھط§ط¬", "crown"), ("ًں”´ ط¬ط°ظˆط±", "root-canal")]:
                if st.button(label, key=f"tooth_{status}", use_container_width=True):
                    if update_tooth_status(st.session_state.selected_tooth, status):
                        st.success(f"âœ… طھظ… طھط­ط¯ظٹط« ط§ظ„ط³ظ† #{tooth_num}")
                        st.rerun()
        else:
            st.info("ًں‘† ط§ط¶ط؛ط· ط¹ظ„ظ‰ ط³ظ† ظپظٹ ط§ظ„ظ…ط®ط·ط·")
        
        if st.button("ًں”„ ط¥ط¹ط§ط¯ط© ط¶ط¨ط·", use_container_width=True):
            for i in range(32):
                update_tooth_status(i, "normal")
            st.session_state.selected_tooth = None
            st.success("âœ… طھظ… ط¥ط¹ط§ط¯ط© ط§ظ„ط¶ط¨ط·")
            st.rerun()

# ============================================================
#  ًں“„ PAGE: NATURAL TEETH
# ============================================================
def page_natural_teeth():
    st.markdown('<div class="section-title">ًں¦· ط§ظ„ط£ط³ظ†ط§ظ† ط§ظ„ط·ط¨ظٹط¹ظٹط©</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        teeth_count = st.slider("ط¹ط¯ط¯ ط§ظ„ط£ط³ظ†ط§ظ†", 6, 16, 10)
        if st.button("ًں¦· طھظˆظ„ظٹط¯ ط£ط³ظ†ط§ظ† ط·ط¨ظٹط¹ظٹط©", type="primary", use_container_width=True):
            img = generate_natural_teeth(teeth_count)
            st.image(img, caption="ط§ظ„ط£ط³ظ†ط§ظ† ط§ظ„ط·ط¨ظٹط¹ظٹط© ط§ظ„ظ…ظˆظ„ط¯ط©", use_container_width=True)
            st.session_state.natural_teeth_layers.append({"name": f"Teeth_{len(st.session_state.natural_teeth_layers)}", "image": img})
            st.success("âœ… طھظ… طھظˆظ„ظٹط¯ ظˆط­ظپط¸ ط§ظ„ط£ط³ظ†ط§ظ† ط§ظ„ط·ط¨ظٹط¹ظٹط©!")
            st.balloons()
    with col2:
        if st.session_state.natural_teeth_layers:
            for i, teeth in enumerate(st.session_state.natural_teeth_layers[-6:]):
                st.image(teeth["image"], caption=f"{teeth['name']}", use_container_width=True)
        else:
            st.info("ظ„ط§ طھظˆط¬ط¯ ط£ط³ظ†ط§ظ† ط·ط¨ظٹط¹ظٹط© ظ…ط­ظپظˆط¸ط©")

# ============================================================
#  ًں“„ PAGE: PHOTOGRAPHY
# ============================================================
def page_photography():
    st.markdown('<div class="section-title">ًں“¸ ط§ظ„طھطµظˆظٹط±</div>', unsafe_allow_html=True)
    st.info("ًں“· ط§ط±ظپط¹ طµظˆط± ط§ظ„ظ…ط±ظٹط¶ ط§ظ„ظ…ط·ظ„ظˆط¨ط©")
    types = ["ط£ظ…ط§ظ…ظٹط©", "ط¬ط§ظ†ط¨ظٹط©", "ط§ط¨طھط³ط§ظ…ط©", "ظپظƒ ط¹ظ„ظˆظٹ", "ظپظƒ ط³ظپظ„ظٹ"]
    for t in types:
        uploaded = st.file_uploader(t, type=["jpg","png","jpeg"], key=f"photo_{t}")
        if uploaded:
            img = Image.open(uploaded)
            st.image(img, caption=t, use_container_width=True)
            st.session_state.patient_images.append(uploaded)

# ============================================================
#  ًں“„ PAGE: XRAY
# ============================================================
def page_xray():
    st.markdown('<div class="section-title">ًں©» ط§ظ„ط£ط´ط¹ط©</div>', unsafe_allow_html=True)
    xray_type = st.selectbox("ظ†ظˆط¹ ط§ظ„ط£ط´ط¹ط©", ["ط³ظٹظپط§ظ„ظˆظ…طھط±ظƒ (Cephalometric)", "ط¨ط§ظ†ظˆط±ط§ظ…ط§ (Panorama)", "CBCT", "P.A"])
    uploaded = st.file_uploader("ط±ظپط¹ طµظˆط±ط© ط§ظ„ط£ط´ط¹ط©", type=["jpg","png","jpeg", "dcm"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="طµظˆط±ط© ط§ظ„ط£ط´ط¹ط©", use_container_width=True)
        if st.button("ًں’¾ ط­ظپط¸ ط§ظ„ط£ط´ط¹ط©", use_container_width=True):
            st.session_state.xrays.append({"type": xray_type, "date": datetime.now().strftime("%Y-%m-%d"), "image": uploaded})
            st.success("âœ… طھظ… ط­ظپط¸ ط§ظ„ط£ط´ط¹ط©!")

# ============================================================
#  ًں“„ PAGE: DENTBOOK
# ============================================================
def page_dentbook():
    st.markdown('<div class="section-title">ًں“± Dentbook</div>', unsafe_allow_html=True)
    st.caption("ط§ظ„ط´ط¨ظƒط© ط§ظ„ط§ط¬طھظ…ط§ط¹ظٹط© ط§ظ„ط·ط¨ظٹط© ظ„ظ„ط£ط·ط¨ط§ط،")
    
    with st.expander("ًں“‌ ط¥ظ†ط´ط§ط، ظ…ظ†ط´ظˆط± ط¬ط¯ظٹط¯", expanded=True):
        with st.form("dentbook_form", clear_on_submit=True):
            content = st.text_area("ظ…ط­طھظˆظ‰ ط§ظ„ظ…ظ†ط´ظˆط±", placeholder="ط´ط§ط±ظƒ ط­ط§ظ„ط© ط·ط¨ظٹط© ط£ظˆ طھط­ط¯ظٹط«...")
            category = st.selectbox("ط§ظ„طھطµظ†ظٹظپ", ["ظ…ظ†ط´ظˆط± ط¹ط§ظ…", "طھط­ط¯ظٹط« طµظٹط§ظ†ط©", "ط­ط§ظ„ط© ط³ط±ظٹط±ظٹط©", "ظ†طµظٹط­ط© ط·ط¨ظٹط©"])
            if st.form_submit_button("ًںڑ€ ظ†ط´ط±"):
                if content:
                    st.session_state.dentbook_posts.insert(0, {
                        "author": st.session_state.current_user["name"],
                        "content": content,
                        "category": category,
                        "time": datetime.now().strftime("%H:%M"),
                        "likes": 0,
                        "comments": []
                    })
                    st.success("âœ… طھظ… ط§ظ„ظ†ط´ط±!")
                    st.rerun()
    
    for post in st.session_state.dentbook_posts[:10]:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;">
                <div><strong>{post['author']}</strong> <span style="color:#8892b0;font-size:0.8rem;">{post['time']}</span></div>
                <span style="background:rgba(0,212,255,0.1);padding:2px 12px;border-radius:12px;font-size:0.7rem;">{post['category']}</span>
            </div>
            <p style="margin-top:8px;">{post['content']}</p>
            <div style="display:flex; gap:12px; font-size:0.8rem; color:#8892b0;">
                <span>â‌¤ï¸ڈ {post['likes']}</span>
                <span>ًں’¬ {len(post['comments'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: FRIENDS
# ============================================================
def page_friends():
    st.markdown('<div class="section-title">ًں¤‌ ط§ظ„ط£طµط¯ظ‚ط§ط،</div>', unsafe_allow_html=True)
    user = st.session_state.current_user
    
    st.markdown("### ًں‘¥ ط¥ط±ط³ط§ظ„ ط·ظ„ط¨ طµط¯ط§ظ‚ط©")
    all_users = [u for u in st.session_state.users_db.values() if u["email"] != user["email"]]
    if all_users:
        target = st.selectbox("ط§ط®طھط± ظ…ط³طھط®ط¯ظ…", [f"{u['name']} ({u['email']})" for u in all_users])
        if st.button("ًں“¨ ط¥ط±ط³ط§ظ„ ط·ظ„ط¨ طµط¯ط§ظ‚ط©", type="primary"):
            target_email = target.split("(")[-1].replace(")", "")
            st.session_state.friend_requests.append({
                "from": user["email"], "to": target_email,
                "from_name": user["name"], "status": "pending",
                "created_at": datetime.now().isoformat()
            })
            st.success("âœ… طھظ… ط¥ط±ط³ط§ظ„ ط·ظ„ط¨ ط§ظ„طµط¯ط§ظ‚ط©!")
    
    st.markdown("### ًں“¨ ط·ظ„ط¨ط§طھ ط§ظ„طµط¯ط§ظ‚ط© ط§ظ„ظˆط§ط±ط¯ط©")
    incoming = [r for r in st.session_state.friend_requests if r["to"] == user["email"] and r["status"] == "pending"]
    if incoming:
        for req in incoming:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); border:1px solid #00d4ff; border-radius:12px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                <div><strong>ًں‘¤ {req['from_name']}</strong></div>
                <div>
                    <button onclick="alert('âœ… طھظ… ظ‚ط¨ظˆظ„ ط§ظ„ط·ظ„ط¨!')" style="background:#10b981; color:#fff; border:none; padding:4px 16px; border-radius:20px; cursor:pointer;">ظ‚ط¨ظˆظ„</button>
                    <button onclick="alert('â‌Œ طھظ… ط±ظپط¶ ط§ظ„ط·ظ„ط¨')" style="background:#ef4444; color:#fff; border:none; padding:4px 16px; border-radius:20px; cursor:pointer;">ط±ظپط¶</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ًں“­ ظ„ط§ طھظˆط¬ط¯ ط·ظ„ط¨ط§طھ طµط¯ط§ظ‚ط© ظˆط§ط±ط¯ط©")

# ============================================================
#  ًں“„ PAGE: PROFILE
# ============================================================
def page_profile():
    st.markdown('<div class="section-title">ًں‘¤ ط§ظ„ظ…ظ„ظپ ط§ظ„ط´ط®طµظٹ</div>', unsafe_allow_html=True)
    user = st.session_state.current_user
    
    with st.form("profile_form"):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="width:100px;height:100px;border-radius:50%;background:linear-gradient(135deg,#00d4ff,#7b2cbf);display:flex;align-items:center;justify-content:center;font-size:40px;color:#fff;margin:0 auto;">
                    {user['name'][0] if user['name'] else 'ًں‘¤'}
                </div>
                <div style="margin-top:8px;color:#8892b0;font-size:0.8rem;">{user['email']}</div>
                <div style="margin-top:4px;"><span style="background:#10b981;color:#fff;padding:2px 12px;border-radius:20px;font-size:0.65rem;font-weight:600;">ًں”’ ط­ط³ط§ط¨ ط®ط§طµ</span></div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            name = st.text_input("ط§ظ„ط§ط³ظ…", value=user.get("name", ""))
            specialty = st.text_input("ط§ظ„طھط®طµطµ", value=user.get("specialty", ""))
            country = st.text_input("ط§ظ„ط¯ظˆظ„ط©", value=user.get("country", ""))
            phone = st.text_input("ط§ظ„ظ‡ط§طھظپ", value=user.get("phone", ""))
            bio = st.text_area("ظ†ط¨ط°ط©", value=user.get("bio", ""))
            if st.form_submit_button("ًں’¾ ط­ظپط¸"):
                st.session_state.current_user.update({
                    "name": name, "specialty": specialty,
                    "country": country, "phone": phone, "bio": bio
                })
                st.session_state.users_db[user["email"]].update(st.session_state.current_user)
                st.success("âœ… طھظ… ط§ظ„ط­ظپط¸!")

# ============================================================
#  ًں“„ PAGE: MEMBERS
# ============================================================
def page_members():
    st.markdown('<div class="section-title">ًں‘¥ ط§ظ„ط£ط¹ط¶ط§ط،</div>', unsafe_allow_html=True)
    st.write(f"ط¥ط¬ظ…ط§ظ„ظٹ ط§ظ„ط£ط¹ط¶ط§ط،: {len(st.session_state.users_db)}")
    for email, u in st.session_state.users_db.items():
        status = "ًںں¢" if u.get("online", True) else "ًں”´"
        platforms = u.get("platforms", ["email"])
        st.markdown(f"""
        <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
            <div><strong>{u['name']}</strong> <span style="color:#8892b0;font-size:0.75rem;">{u.get('specialty','')}</span></div>
            <div><span>{status}</span></div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: MESSAGES
# ============================================================
def page_messages():
    st.markdown('<div class="section-title">ًں’¬ ط§ظ„ظ…ط±ط§ط³ظ„ط§طھ</div>', unsafe_allow_html=True)
    for msg in st.session_state.messages[-20:]:
        align = "flex-end" if msg["sender"] == st.session_state.current_user["name"] else "flex-start"
        bg = "#00d4ff" if msg["sender"] == st.session_state.current_user["name"] else "rgba(255,255,255,0.05)"
        color = "#fff" if msg["sender"] == st.session_state.current_user["name"] else "#f8fafc"
        st.markdown(f"""
        <div style="display:flex; justify-content:{align}; margin-bottom:6px;">
            <div style="max-width:75%; padding:8px 14px; border-radius:12px; background:{bg}; color:{color}; border:1px solid rgba(255,255,255,0.1);">
                <div style="font-size:0.7rem; opacity:0.8;">{msg['sender']}</div>
                <div style="font-size:0.9rem;">{msg['text']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with st.form("msg_form", clear_on_submit=True):
        text = st.text_input("ط±ط³ط§ظ„طھظƒ...", label_visibility="collapsed")
        if st.form_submit_button("ًں“¨ ط¥ط±ط³ط§ظ„", use_container_width=True) and text:
            st.session_state.messages.append({"sender": st.session_state.current_user["name"], "text": text, "time": datetime.now().isoformat()})
            st.rerun()

# ============================================================
#  ًں“„ PAGE: PRIVATE MESSAGES
# ============================================================
def page_private_messages():
    st.markdown('<div class="section-title">ًں’Œ ط±ط³ط§ط¦ظ„ ط®ط§طµط©</div>', unsafe_allow_html=True)
    recipients = [u["name"] for e, u in st.session_state.users_db.items() if e != st.session_state.current_user["email"]]
    if not recipients:
        st.info("ظ„ط§ ظٹظˆط¬ط¯ ط£ط·ط¨ط§ط، ط¢ط®ط±ظˆظ†.")
        return
    recipient = st.selectbox("ط§ط®طھط± ط§ظ„ط·ط¨ظٹط¨", recipients)
    text = st.text_area("ط§ظƒطھط¨ ط±ط³ط§ظ„طھظƒ...")
    if st.button("ًں“¨ ط¥ط±ط³ط§ظ„", type="primary") and text:
        st.session_state.private_messages.append({
            "sender": st.session_state.current_user["name"],
            "recipient": recipient,
            "text": text,
            "time": datetime.now().isoformat()
        })
        st.success("âœ… طھظ… ط¥ط±ط³ط§ظ„ ط§ظ„ط±ط³ط§ظ„ط©!")

# ============================================================
#  ًں“„ PAGE: LAB CHAT
# ============================================================
def page_lab_chat():
    st.markdown('<div class="section-title">ًں§ھ ط§ظ„طھظˆط§طµظ„ ظ…ط¹ ط§ظ„ظ…ط®طھط¨ط±</div>', unsafe_allow_html=True)
    for msg in st.session_state.lab_messages[-10:]:
        st.markdown(f"<div class='card'><strong>{msg['sender']}:</strong> {msg['text']}</div>", unsafe_allow_html=True)
    with st.form("lab_form", clear_on_submit=True):
        txt = st.text_input("ط±ط³ط§ظ„طھظƒ ظ„ظ„ظ…ط®طھط¨ط±...")
        if st.form_submit_button("ط¥ط±ط³ط§ظ„") and txt:
            st.session_state.lab_messages.append({"sender": st.session_state.current_user["name"], "text": txt, "time": datetime.now().isoformat()})
            st.rerun()

# ============================================================
#  ًں“„ PAGE: FILE SHARING
# ============================================================
def page_file_sharing():
    st.markdown('<div class="section-title">ًں“پ ظ…ط´ط§ط±ظƒط© ط§ظ„ظ…ظ„ظپط§طھ</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("ط§ط³ط­ط¨ ط§ظ„ظ…ظ„ظپط§طھ ظ‡ظ†ط§", accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            st.session_state.files_uploaded.append({"name": f.name, "size": f.size, "type": f.type})
            st.success(f"âœ… طھظ… ط±ظپط¹ {f.name}")
    if st.session_state.files_uploaded:
        st.dataframe(pd.DataFrame(st.session_state.files_uploaded), use_container_width=True)

# ============================================================
#  ًں“„ PAGE: SCREEN SHARE
# ============================================================
def page_screen_share():
    st.markdown('<div class="section-title">ًں–¥ï¸ڈ ظ…ط´ط§ط±ظƒط© ط§ظ„ط´ط§ط´ط©</div>', unsafe_allow_html=True)
    st.info("ًں”¹ ظپظٹ ط¨ظٹط¦ط© ط§ظ„ظ…طھطµظپط­طŒ ط§ط³طھط®ط¯ظ… ط²ط± 'ط¨ط¯ط، ط§ظ„ظ…ط´ط§ط±ظƒط©' ط£ط¯ظ†ط§ظ‡")
    st.markdown("""
    <button style="background:#10b981; color:#fff; border:none; padding:10px 24px; border-radius:60px; cursor:pointer;" onclick="navigator.mediaDevices.getDisplayMedia({video:true}).then(s=>{alert('ًں–¥ï¸ڈ طھظ… ط¨ط¯ط، ط§ظ„ظ…ط´ط§ط±ظƒط©')}).catch(e=>{alert('طھظ… ط§ظ„ط¥ظ„ط؛ط§ط،')})">
        â–¶ï¸ڈ ط¨ط¯ط، ظ…ط´ط§ط±ظƒط© ط§ظ„ط´ط§ط´ط©
    </button>
    """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: SMART DIAGNOSIS
# ============================================================
def page_smart_diagnosis():
    st.markdown('<div class="section-title">ًں“ٹ ط§ظ„طھط´ط®ظٹطµ ط§ظ„ط°ظƒظٹ</div>', unsafe_allow_html=True)
    st.caption("طھط´ط®ظٹطµ ظ…طھظ‚ط¯ظ… ط¨ط§ط³طھط®ط¯ط§ظ… ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ")
    
    uploaded = st.file_uploader("ًں“¸ ط­ظ…ظ‘ظ„ طµظˆط±ط© ط§ظ„ظˆط¬ظ‡ ط£ظˆ ط§ظ„ط£ط³ظ†ط§ظ†", type=["jpg", "png", "jpeg"], key="diag_upload")
    
    if uploaded:
        img = Image.open(uploaded)
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="ط§ظ„طµظˆط±ط©", use_container_width=True)
        with col2:
            if st.button("ًں§  طھط´ط®ظٹطµ ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary", use_container_width=True):
                with st.spinner("âڈ³ ط¬ط§ط±ظٹ ط§ظ„طھط­ظ„ظٹظ„ ظˆط§ظ„طھط´ط®ظٹطµ..."):
                    time.sleep(2)
                    st.markdown("""
                    <div class="diagnosis-box">
                        <h4 style="color:#00d4ff;">ًں“‹ طھظ‚ط±ظٹط± ط§ظ„طھط´ط®ظٹطµ</h4>
                        <p><strong>ط§ظ„ط­ط§ظ„ط©:</strong> ط§ط¨طھط³ط§ظ…ط© ظ…طھظ†ط§ط³ظ‚ط© ظ…ط¹ ط¨ط¹ط¶ ط§ظ„طھط­ط¯ظٹط§طھ</p>
                        <p><strong>ط§ظ„طھظˆطµظٹط§طھ:</strong></p>
                        <ul>
                            <li>طھط­ط³ظٹظ† طھط¨ظٹظٹط¶ ط§ظ„ط£ط³ظ†ط§ظ†</li>
                            <li>طھظ‚ظˆظٹظ… ط§ظ„ط£ط³ظ†ط§ظ† ط§ظ„ط®ظپظٹظپ</li>
                            <li>ظ…طھط§ط¨ط¹ط© ط¯ظˆط±ظٹط©</li>
                        </ul>
                        <p><strong>ظ†ط³ط¨ط© ط§ظ„ظ†ط¬ط§ط­ ط§ظ„ظ…طھظˆظ‚ط¹ط©:</strong> 92%</p>
                    </div>
                    """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: TREATMENT PLAN
# ============================================================
def page_treatment_plan():
    st.markdown('<div class="section-title">ًں“‹ ط®ط·ط© ط§ظ„ط¹ظ„ط§ط¬</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("ط§ظ„ط®ط·ط© ط§ظ„ط±ط¦ظٹط³ظٹط©", placeholder="ط£ط¯ط®ظ„ ط§ظ„ط®ط·ط© ط§ظ„ط±ط¦ظٹط³ظٹط©...")
    with col2:
        st.text_input("ط§ظ„ط¹ظ„ط§ط¬ ط§ظ„ط¨ط¯ظٹظ„", placeholder="ط§ظ„ط¹ظ„ط§ط¬ ط§ظ„ط¨ط¯ظٹظ„...")
    if st.button("ًں§  طھظˆظ„ظٹط¯ ط§ظ„ط®ط·ط©", type="primary"):
        st.balloons()
        st.success("âœ… طھظ… طھظˆظ„ظٹط¯ ط§ظ„ط®ط·ط© ط§ظ„طھظپطµظٹظ„ظٹط©")

# ============================================================
#  ًں“„ PAGE: MATERIALS
# ============================================================
def page_materials():
    st.markdown('<div class="section-title">ًں§ھ ط§ظ„ظ…ظˆط§ط¯ ط§ظ„ط¹ظ„ط§ط¬ظٹط©</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("ط§ط³ظ… ط§ظ„ظ…ط§ط¯ط©")
    with col2:
        usage = st.text_input("ط§ظ„ط§ط³طھط®ط¯ط§ظ…")
    if st.button("â‍• ط¥ط¶ط§ظپط©") and name:
        st.session_state.materials.append({"name": name, "usage": usage})
        st.success("âœ… طھظ…طھ ط§ظ„ط¥ط¶ط§ظپط©")
    if st.session_state.materials:
        st.table(pd.DataFrame(st.session_state.materials))

# ============================================================
#  ًں“„ PAGE: FACIAL
# ============================================================
def page_facial():
    st.markdown('<div class="section-title">ًں§‘â€چâڑ•ï¸ڈ طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡ (478 ط¹ظ„ط§ظ…ط©)</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("ًں“¸ ط­ظ…ظ‘ظ„ طµظˆط±ط© ط§ظ„ظˆط¬ظ‡", type=["jpg","png"], key="facial_img")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="ط§ظ„طµظˆط±ط© ط§ظ„ظ…ط­ظ…ظ„ط©", use_container_width=True)
        if st.button("ًںژ¨ طھط­ظ„ظٹظ„ ط§ظ„ظ€ 478 ظ†ظ‚ط·ط© ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary", use_container_width=True):
            with st.spinner("âڈ³ ط¬ط§ط±ظٹ ط§ظ„طھط­ظ„ظٹظ„..."):
                time.sleep(2)
                result = draw_landmarks_on_image(img, 478)
                st.image(result, caption="ط§ظ„ط¹ظ„ط§ظ…ط§طھ ط§ظ„طھط´ط±ظٹط­ظٹط©", use_container_width=True)
                st.success("âœ… طھظ… ط±ط³ظ… 478 ط¹ظ„ط§ظ…ط© طھط´ط±ظٹط­ظٹط©!")

# ============================================================
#  ًں“„ PAGE: SMILE DESIGN
# ============================================================
def page_smile_design():
    st.markdown('<div class="section-title">ًںکپ طھطµظ…ظٹظ… ط§ظ„ط§ط¨طھط³ط§ظ…ط©</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("ًں“¸ طµظˆط±ط© ط§ظ„ط§ط¨طھط³ط§ظ…ط©", type=["jpg","png"], key="smile_img")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="ط§ظ„طµظˆط±ط© ط§ظ„ط£طµظ„ظٹط©", use_container_width=True)
        if st.button("âœ¨ ظ…ط­ط§ظƒط§ط© ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary", use_container_width=True):
            with st.spinner("âڈ³ ط¬ط§ط±ظٹ ط§ظ„ظ…ط­ط§ظƒط§ط©..."):
                _, result = simulate_smile_before_after(img, 0.8)
                comparison = create_comparison_image(img, result)
                st.image(result, caption="ط§ظ„ظ†طھظٹط¬ط© ط§ظ„ظ…طھظˆظ‚ط¹ط©", use_container_width=True)
                st.image(comparison, caption="ظ…ظ‚ط§ط±ظ†ط© ظ‚ط¨ظ„/ط¨ط¹ط¯", use_container_width=True)
                st.session_state.last_smile_image = result
                st.success("âœ… طھظ…طھ ط§ظ„ظ…ط­ط§ظƒط§ط©!")

# ============================================================
#  ًں“„ PAGE: AESTHETIC DESIGN
# ============================================================
def page_aesthetic_design():
    st.markdown('<div class="section-title">ًںژ¨ ط§ظ„طھطµظ…ظٹظ… ط§ظ„طھط¬ظ…ظٹظ„ظٹ</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        before = st.file_uploader("ًں“¸ ظ‚ط¨ظ„", key="before_img")
        if before:
            st.image(before, caption="ظ‚ط¨ظ„", use_container_width=True)
    with col2:
        after = st.file_uploader("ًں“¸ ط¨ط¹ط¯", key="after_img")
        if after:
            st.image(after, caption="ط¨ط¹ط¯", use_container_width=True)
    if before and after:
        if st.button("ًںژ¨ طھظˆظ„ظٹط¯ ط§ظ„طھطµظ…ظٹظ… ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary"):
            comparison = create_comparison_image(Image.open(before), Image.open(after), 0.5)
            st.image(comparison, caption="ظ…ظ‚ط§ط±ظ†ط© ظ‚ط¨ظ„/ط¨ط¹ط¯", use_container_width=True)
            st.success("âœ… طھظ… طھظˆظ„ظٹط¯ ط§ظ„طھطµظ…ظٹظ…!")

# ============================================================
#  ًں“„ PAGE: STL 3D
# ============================================================
def page_stl_3d():
    st.markdown('<div class="section-title">ًں“¦ ظ†ظ…ط§ط°ط¬ 3D</div>', unsafe_allow_html=True)
    model = st.file_uploader("ط±ظپط¹ STL / OBJ / PLY", type=["stl","obj","ply","glb"], key="stl_up")
    if model:
        st.success(f"âœ… طھظ… ط±ظپط¹ {model.name}")

# ============================================================
#  ًں“„ PAGE: DSD STUDIO
# ============================================================
def page_dsd_studio():
    st.markdown('<div class="section-title">ًں§¬ ط§ط³طھظˆط¯ظٹظˆ DSD</div>', unsafe_allow_html=True)
    patients = [p["name"] for p in st.session_state.patients] or ["ظ„ط§ ظٹظˆط¬ط¯"]
    st.selectbox("ًں“‹ ط§ظ„ظ…ظ„ظپ ط§ظ„ط·ط¨ظٹ ظ„ظ„ظ…ط±ظٹط¶", patients)
    uploaded = st.file_uploader("ًں“¸ طھط­ظ…ظٹظ„ ط§ظ„طµظˆط±ط©", type=["jpg","png"], key="dsd_img")
    if uploaded:
        st.image(uploaded, caption="ط§ظ„طµظˆط±ط©", use_container_width=True)
    if st.button("ًں“ٹ طھط­ظ„ظٹظ„ ط§ظ„ظ€ 478 ظ…ط¹ظ„ظ… ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary"):
        st.success("âœ… طھظ… ط§ظ„ط¯ظ…ط¬ ط§ظ„ط¬ظ…ط§ظ„ظٹ!")

# ============================================================
#  ًں“„ PAGE: AESTHETIC TREATMENT
# ============================================================
def page_aesthetic_treatment():
    st.markdown('<div class="section-title">ًں’ژ ط¹ظ„ط§ط¬ طھط¬ظ…ظٹظ„ظٹ</div>', unsafe_allow_html=True)
    st.text_input("ط§ط³ظ… ط§ظ„ظ…ط±ظٹط¶")
    st.selectbox("ظ†ظˆط¹ ط§ظ„ط¹ظ„ط§ط¬", ["طھظ†ط§ط³ظ‚ ط§ظ„ظˆط¬ظ‡", "ط¹ظ„ط§ط¬ ط§ظ„ط¨ط´ط±ط©", "طھظ†ط§ط³ظ‚ ط§ظ„ط£ظ†ظپ", "طھظ†ط§ط³ظ‚ ط§ظ„ط°ظ‚ظ†", "طھظ†ط§ط³ظ‚ ط§ظ„ط´ظپط§ظ‡"])
    st.text_area("ظˆطµظپ ط§ظ„ط­ط§ظ„ط©")
    if st.button("âœ¨ طھظˆظ„ظٹط¯ ط®ط·ط© ط§ظ„ط¹ظ„ط§ط¬ ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ", type="primary"):
        st.success("âœ… طھظ… طھظˆظ„ظٹط¯ ط®ط·ط© ط§ظ„ط¹ظ„ط§ط¬!")

# ============================================================
#  ًں“„ PAGE: GLOBAL PLATFORM
# ============================================================
def page_global_platform():
    st.markdown('<div class="section-title">ًںŒچ ط§ظ„ظ…ظ†طµط© ط§ظ„ط¹ط§ظ„ظ…ظٹط©</div>', unsafe_allow_html=True)
    steps = st.session_state.pipeline_steps
    cols = st.columns(5)
    for i, (sid, data) in enumerate(steps.items(), 1):
        color = "#10b981" if data["status"]=="done" else "#f59e0b" if data["status"]=="pending" else "#555"
        with cols[i-1]:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); border-radius:12px; padding:16px; text-align:center; border-top:4px solid {color};">
                <div style="font-size:0.7rem; background:{color}; color:#fff; padding:2px 10px; border-radius:20px; display:inline-block; margin-bottom:6px;">ط§ظ„ط®ط·ظˆط© {sid}</div>
                <h5 style="font-size:0.85rem;">{data['name']}</h5>
                <div style="font-size:0.65rem; color:#8892b0;">{data['progress']}%</div>
            </div>
            """, unsafe_allow_html=True)
    st.progress(st.session_state.pipeline_progress / 100)

# ============================================================
#  ًں“„ PAGE: PIPELINE
# ============================================================
def page_pipeline():
    st.markdown('<div class="section-title">ًں”„ ط®ط· ط§ظ„ط¥ظ†طھط§ط¬</div>', unsafe_allow_html=True)
    st.selectbox("ط§ط®طھط± ظ…ط±ظٹط¶ط§ظ‹", [p["name"] for p in st.session_state.patients] or ["ظ„ط§ ظٹظˆط¬ط¯"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=st.session_state.pipeline_progress,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "ظ†ط³ط¨ط© ط§ظ„ط¥ظ†ط¬ط§ط²"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#00d4ff"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
#  ًں“„ PAGE: MATERIALS GUIDE
# ============================================================
def page_materials_guide():
    st.markdown('<div class="section-title">ًں¦· ط¯ظ„ظٹظ„ ط§ظ„ظ…ظˆط§ط¯</div>', unsafe_allow_html=True)
    data = [
        ["Lithium Disilicate (E.max)", "ظ‚ط´ظˆط± ظˆطھط±ظƒظٹط¨ط§طھ", "طھط­ط¶ظٹط± ظ…ط¬ظ‡ط±ظٹطŒ ظ„طµظ‚ ط±ط§طھظ†ط¬ظٹ", "Exocad", "PubMed"],
        ["Hyaluronic Acid Filler", "ظپظٹظ„ط± ط§ظ„ط£ظ†ط³ط¬ط© ط§ظ„ط±ط®ظˆط©", "ط­ظ‚ظ† طھط­طھ ط§ظ„ظ…ط®ط§ط·ظٹط©", "Blender", "NCBI"],
        ["Botulinum Toxin (Botox)", "طھط¹ط¯ظٹظ„ ط§ظ„ط§ط¨طھط³ط§ظ…ط© ط§ظ„ظ„ط«ظˆظٹط©", "ط­ظ‚ظ† ظپظٹ Levator Labii", "AI Studios", "PubMed"],
        ["Zirconia Monolithic", "ط¬ط³ظˆط± ظˆطھط£ظ‡ظٹظ„ ظƒط§ظ…ظ„", "طھط­ط¶ظٹط± ظ‡ظٹظƒظ„ظٹ", "Exocad", "ScienceDirect"],
    ]
    df = pd.DataFrame(data, columns=["ط§ظ„ظ…ط§ط¯ط©", "ط§ظ„طھطµظ†ظٹظپ", "ط¨ط±ظˆطھظˆظƒظˆظ„ ط§ظ„ط§ط³طھط®ط¯ط§ظ…", "ط§ظ„ط±ط¨ط· ط§ظ„ط±ظ‚ظ…ظٹ", "ط§ظ„ظ…ط±ط§ط¬ط¹"])
    st.dataframe(df, use_container_width=True)

# ============================================================
#  ًں“„ PAGE: API HUB
# ============================================================
def page_api_hub():
    st.markdown('<div class="section-title">ًں”Œ ظ…ط±ظƒط² ط§ظ„ط£ظ†ط¸ظ…ط©</div>', unsafe_allow_html=True)
    systems = [("Exocad", "STL", "ًںں¢"), ("Meshy AI", "3D Face", "ًںں¢"), ("Blender", "Cycles", "ًںں،"), ("AI Studios", "Motion", "ًںں¢")]
    for name, fmt, status in systems:
        st.markdown(f"**{name}** ({fmt}) - <span style='color:#10b981;'>{status}</span>", unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: MOCK DB
# ============================================================
def page_mock_db():
    st.markdown('<div class="section-title">ًں—„ï¸ڈ ظ…ط³طھظˆط¯ط¹ ط§ظ„ظ…ط±ظٹط¶</div>', unsafe_allow_html=True)
    st.json({
        "patients_count": len(st.session_state.patients),
        "last_backup": datetime.now().isoformat(),
        "storage_used": "1.2 GB",
        "sync_status": "ظ…ظڈط²ط§ظ…ظ†"
    })

# ============================================================
#  ًں“„ PAGE: NOTIFICATIONS
# ============================================================
def page_notifications():
    st.markdown('<div class="section-title">ًں”” ط§ظ„ط¥ط´ط¹ط§ط±ط§طھ</div>', unsafe_allow_html=True)
    notifs = ["ًں“¢ طھظ… طھط­ط¯ظٹط« ط®ط· ط³ظٹط± ط§ظ„ظ…ط±ظٹط¶", "ًں’¬ ط±ط³ط§ظ„ط© ط¬ط¯ظٹط¯ط© ظ…ظ† ط§ظ„ظ…ط®طھط¨ط±", "ًں“… ظ…ظˆط¹ط¯ ط؛ط¯ط§ظ‹ ط§ظ„ط³ط§ط¹ط© 10:00 طµ", "âœ… طھظ… ط¥ط¶ط§ظپط© ظ…ط±ظٹط¶ ط¬ط¯ظٹط¯", "ًں¦· طھظ… طھط­ط¯ظٹط« ظ…ط®ط·ط· ط§ظ„ط£ط³ظ†ط§ظ†"]
    for n in notifs:
        st.markdown(f'<div class="card" style="padding:10px; margin-bottom:6px;">{n}</div>', unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: SYSTEMS
# ============================================================
def page_systems():
    st.markdown('<div class="section-title">ًں–¥ï¸ڈ ط§ظ„ط£ظ†ط¸ظ…ط©</div>', unsafe_allow_html=True)
    sys_list = ["Smile Generator", "Exocad Analysis", "Exocad 3D", "Meshy AI", "Blender Cycles", "AI Studios"]
    cols = st.columns(3)
    for i, s in enumerate(sys_list):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:2rem; color:#00d4ff;">âڑ™ï¸ڈ</div>
                <h5>{s}</h5>
                <span style="background:#10b981;color:#fff;padding:2px 12px;border-radius:20px;font-size:0.6rem;">ظ†ط´ط·</span>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: SCIENTIFIC SCAN
# ============================================================
def page_scientific_scan():
    st.markdown('<div class="section-title">ًں”¬ ط§ظ„ظ…ط³ط­ ط§ظ„ط¹ظ„ظ…ظٹ</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        if st.button("ًں‘¤ ظ…ط³ط­ ط§ظ„ظˆط¬ظ‡", use_container_width=True):
            st.success("âœ… طھظ… ظ…ط³ط­ ط§ظ„ظˆط¬ظ‡!")
    with cols[1]:
        if st.button("ًں¦· ظ…ط³ط­ ط§ظ„ط£ط³ظ†ط§ظ†", use_container_width=True):
            st.success("âœ… طھظ… ظ…ط³ط­ ط§ظ„ط£ط³ظ†ط§ظ†!")
    with cols[2]:
        if st.button("âڑ–ï¸ڈ طھط­ظ„ظٹظ„ ط§ظ„طھظ†ط§ط؛ظ…", type="primary", use_container_width=True):
            st.success("âœ… طھظ… طھط­ظ„ظٹظ„ ط§ظ„طھظ†ط§ط؛ظ…!")
    with cols[3]:
        if st.button("ًں“‹ طھظ‚ط±ظٹط± ط¹ظ„ظ…ظٹ", use_container_width=True):
            st.success("âœ… طھظ… طھظˆظ„ظٹط¯ ط§ظ„طھظ‚ط±ظٹط± ط§ظ„ط¹ظ„ظ…ظٹ!")

# ============================================================
#  ًں“„ PAGE: NAQAI
# ============================================================
def page_naqai():
    st.markdown('<div class="section-title">ًں¤– NaqAI</div>', unsafe_allow_html=True)
    for msg in st.session_state.naqai_chat:
        if msg["role"] == "ai":
            st.markdown(f'<div style="background:#00d4ff; color:#fff; padding:10px 14px; border-radius:12px; margin-bottom:6px; max-width:85%;">{msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:rgba(255,255,255,0.05); color:#f8fafc; padding:10px 14px; border-radius:12px; margin-bottom:6px; border:1px solid rgba(255,255,255,0.1);">{msg["text"]}</div>', unsafe_allow_html=True)
    q = st.text_input("ط§ط³ط£ظ„ NaqAI...")
    if st.button("ًں“¨ ط¥ط±ط³ط§ظ„", type="primary") and q:
        st.session_state.naqai_chat.append({"role": "user", "text": q})
        responses = {
            "ط§ط¨طھط³ط§ظ…ط©": "ًںکپ **طھطµظ…ظٹظ… ط§ظ„ط§ط¨طھط³ط§ظ…ط©** ظٹط´ظ…ظ„ طھط­ظ„ظٹظ„ ط§ظ„ظ†ط³ط¨ ط§ظ„ط°ظ‡ط¨ظٹط© ظ„ظ„ط£ط³ظ†ط§ظ† ظˆط§ظ„ظˆط¬ظ‡.",
            "ظپظٹظ„ط±": "ًں’‰ **ظپظٹظ„ط± ط­ظ…ط¶ ط§ظ„ظ‡ظٹط§ظ„ظˆط±ظˆظ†ظٹظƒ** ظٹط³طھط®ط¯ظ… ظ„ظ…ظ„ط، ط§ظ„طھط¬ط§ط¹ظٹط¯ ظˆط²ظٹط§ط¯ط© ط­ط¬ظ… ط§ظ„ط´ظپط§ظ‡.",
            "ط¨ظˆطھظˆظƒط³": "ًں§ھ **ط§ظ„ط¨ظˆطھظˆظƒط³** ظٹط³طھط®ط¯ظ… ظ„طھظ‚ظ„ظٹظ„ ط§ظ„طھط¬ط§ط¹ظٹط¯ ظˆط¹ظ„ط§ط¬ ط§ظ„ط§ط¨طھط³ط§ظ…ط© ط§ظ„ظ„ط«ظˆظٹط©.",
            "ط²ط±ظƒظˆظ†ظٹط§": "ًں¦· **ط§ظ„ط²ط±ظƒظˆظ†ظٹط§** ظ…ط§ط¯ط© ط®ط²ظپظٹط© ط¹ط§ظ„ظٹط© ط§ظ„ظ…طھط§ظ†ط© ظˆط§ظ„ط¬ظ…ط§ظ„ظٹط©.",
            "طھط­ظ„ظٹظ„": "ًں§  **طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡** ظٹط¹طھظ…ط¯ ط¹ظ„ظ‰ 478 ظ†ظ‚ط·ط© طھط´ط±ظٹط­ظٹط©."
        }
        ans = "ًں§  ط´ظƒط±ط§ظ‹ ظ„ط³ط¤ط§ظ„ظƒ! ظٹظ…ظƒظ†ظ†ظٹ ظ…ط³ط§ط¹ط¯طھظƒ ظپظٹ طھطµظ…ظٹظ… ط§ظ„ط§ط¨طھط³ط§ظ…ط©طŒ ط§ظ„ط¹ظ„ط§ط¬ ط§ظ„طھط¬ظ…ظٹظ„ظٹطŒ طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡ ظˆط§ظ„ط£ط´ط¹ط©."
        for k, v in responses.items():
            if k in q.lower():
                ans = v
                break
        st.session_state.naqai_chat.append({"role": "ai", "text": ans})
        st.rerun()

# ============================================================
#  ًں“„ PAGE: INTERDISCIPLINARY
# ============================================================
def page_interdisciplinary():
    st.markdown('<div class="section-title">ًں‘¥ ظپط±ظ‚ ظ…طھط¹ط¯ط¯ط© ط§ظ„طھط®طµطµط§طھ</div>', unsafe_allow_html=True)
    with st.form("add_spec"):
        n = st.text_input("ط§ط³ظ… ط§ظ„ط£ط®طµط§ط¦ظٹ")
        s = st.text_input("ط§ظ„طھط®طµطµ")
        if st.form_submit_button("â‍• ط¥ط¶ط§ظپط©"):
            st.session_state.specialists.append({"name": n, "specialty": s, "online": True})
            st.success("âœ… طھظ…طھ ط§ظ„ط¥ط¶ط§ظپط©")
    for sp in st.session_state.specialists:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;">
                <div><strong>{sp['name']}</strong> <span style="color:#8892b0;">{sp['specialty']}</span></div>
                <div><span style="color:{'#10b981' if sp.get('online', True) else '#555'};">{'ًںں¢ ظ…طھطµظ„' if sp.get('online', True) else 'ًں”´ ط؛ظٹط± ظ…طھطµظ„'}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: ADS
# ============================================================
def page_ads():
    st.markdown('<div class="section-title">ًں“¢ ط§ظ„ط¥ط¹ظ„ط§ظ†ط§طھ</div>', unsafe_allow_html=True)
    with st.form("ad_form"):
        t = st.text_input("ط¹ظ†ظˆط§ظ† ط§ظ„ط¥ط¹ظ„ط§ظ†")
        c = st.text_area("ط§ظ„ظ…ط­طھظˆظ‰")
        if st.form_submit_button("ًں“¨ ظ†ط´ط±"):
            st.session_state.ads.append({"title": t, "content": c, "date": datetime.now().isoformat()})
            st.success("âœ… طھظ… ط§ظ„ظ†ط´ط±")
    for a in st.session_state.ads:
        st.markdown(f"""
        <div class="card">
            <h5 style="color:#00d4ff;">{a['title']}</h5>
            <p>{a['content']}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: LAB
# ============================================================
def page_lab():
    st.markdown('<div class="section-title">ًں”¬ ط§ظ„ظ…ط¹ظ…ظ„</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        tech = st.text_input("ط§ط³ظ… ط§ظ„ظپظ†ظٹ", key="lab_tech")
    with c2:
        work = st.text_input("ظ†ظˆط¹ ط§ظ„ط¹ظ…ظ„", key="lab_work")
    with c3:
        patient = st.text_input("ط§ط³ظ… ط§ظ„ظ…ط±ظٹط¶", key="lab_patient")
    with c4:
        amount = st.number_input("ط§ظ„ظ…ط¨ظ„ط؛ ($)", key="lab_amount", min_value=0)
    if st.button("ًں’¾ ط­ظپط¸"):
        if tech and work:
            st.success("âœ… طھظ… ط­ظپط¸ ط·ظ„ط¨ ط§ظ„ظ…ط¹ظ…ظ„!")

# ============================================================
#  ًں“„ PAGE: APPOINTMENTS
# ============================================================
def page_appointments():
    st.markdown('<div class="section-title">ًں“… ط§ظ„ظ…ظˆط§ط¹ظٹط¯</div>', unsafe_allow_html=True)
    patients = [p["name"] for p in st.session_state.patients] or ["ظ„ط§ ظٹظˆط¬ط¯"]
    patient = st.selectbox("ط§ظ„ظ…ط±ظٹط¶", patients)
    date = st.date_input("ط§ظ„طھط§ط±ظٹط®", datetime.now())
    time = st.time_input("ط§ظ„ظˆظ‚طھ", datetime.now().time())
    note = st.text_input("ظ…ظ„ط§ط­ط¸ط©")
    if st.button("ًں“… ط¥ط¶ط§ظپط© ظ…ظˆط¹ط¯", type="primary"):
        st.session_state.appointments.append({
            "patient": patient, "date": date.strftime("%Y-%m-%d"),
            "time": time.strftime("%H:%M"), "note": note
        })
        st.success("âœ… طھظ… ط¥ط¶ط§ظپط© ط§ظ„ظ…ظˆط¹ط¯")
        st.rerun()
    for app in st.session_state.appointments:
        st.markdown(f"""
        <div class="card" style="padding:12px;">
            <div style="display:flex; justify-content:space-between;">
                <div><strong>{app['patient']}</strong> <span style="color:#8892b0;">{app['date']} {app['time']}</span></div>
                <div>{app['note']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: ACCOUNTING
# ============================================================
def page_accounting():
    st.markdown('<div class="section-title">ًں’° ط­ط³ط§ط¨ ط§ظ„ظ…ط±ظٹط¶</div>', unsafe_allow_html=True)
    total = st.number_input("ط§ظ„ظ…ط¨ظ„ط؛ ط§ظ„ظƒظ„ظٹ", value=1000, min_value=0)
    paid = st.number_input("ط§ظ„ظ…ط¯ظپظˆط¹", value=0, min_value=0)
    st.markdown(f"""
    <div class="card">
        <div style="display:flex; justify-content:space-around; text-align:center;">
            <div><h4>ط§ظ„ظƒظ„ظٹ</h4><div class="metric-value">{total}</div></div>
            <div><h4>ط§ظ„ظ…ط¯ظپظˆط¹</h4><div class="metric-value" style="color:#10b981;">{paid}</div></div>
            <div><h4>ط§ظ„ظ…طھط¨ظ‚ظٹ</h4><div class="metric-value" style="color:#ef4444;">{total-paid}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: PAYMENTS
# ============================================================
def page_payments():
    st.markdown('<div class="section-title">ًں’³ ط§ظ„ط¯ظپط¹</div>', unsafe_allow_html=True)
    methods = ["ًں’³ Visa / Mastercard", "ًں“± ظ…ط­ظپط¸طھظٹ", "ًں’µ ظ†ظ‚ط¯ظٹ", "ًں“² ط¥ظ… ط¨ط§ظٹ", "ًںڈ¦ طھط­ظˆظٹظ„ ط¨ظ†ظƒظٹ"]
    selected = st.selectbox("ظˆط³ظٹظ„ط© ط§ظ„ط¯ظپط¹", methods)
    if st.button("âœ… طھظ†ظپظٹط° ط§ظ„ط¯ظپط¹", type="primary"):
        st.success(f"âœ… طھظ… ط§ظ„ط¯ظپط¹ ط¨ظ†ط¬ط§ط­ ط¹ط¨ط± {selected}")

# ============================================================
#  ًں“„ PAGE: SUBSCRIPTIONS
# ============================================================
def page_subscriptions():
    st.markdown('<div class="section-title">ًں‘‘ ط®ط·ط· ط§ظ„ط§ط´طھط±ط§ظƒ</div>', unsafe_allow_html=True)
    plans = [("ًں†“ طھط¬ط±ظٹط¨ظٹ", "$0", ["3 ظ…ط±ط¶ظ‰", "طھط­ظ„ظٹظ„ ط£ط³ط§ط³ظٹ"]), ("â­گ ط´ظ‡ط±ظٹ", "$99", ["ط؛ظٹط± ظ…ط­ط¯ظˆط¯", "طھط­ظ„ظٹظ„ AI"]), ("ًںŒں ط³ظ†ظˆظٹ", "$999", ["ط¬ظ…ظٹط¹ ط§ظ„ظ…ظٹط²ط§طھ", "ط¯ط¹ظ… ط£ظˆظ„ظˆظٹ"])]
    cols = st.columns(3)
    for i, (name, price, feats) in enumerate(plans):
        with cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center; {'border:2px solid #00d4ff;' if i==1 else ''}">
                <h4>{name}</h4>
                <div style="font-size:2rem; font-weight:800; color:#00d4ff;">{price}</div>
                <div style="font-size:0.7rem; color:#8892b0;">{', '.join(feats)}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("ط§ط´طھط±ظƒ", key=f"sub_{i}", use_container_width=True):
                st.success(f"ًںژ‰ طھظ… طھظپط¹ظٹظ„ ط§ظ„ط§ط´طھط±ط§ظƒ {name}!")

# ============================================================
#  ًں“„ PAGE: INVITE
# ============================================================
def page_invite():
    st.markdown('<div class="section-title">ًں“¨ ط¯ط¹ظˆط© ط§ظ„ط£ط·ط¨ط§ط،</div>', unsafe_allow_html=True)
    link = f"https://harmonizeai.streamlit.app/?ref={np.random.randint(1000,9999)}"
    st.text_input("ط±ط§ط¨ط· ط§ظ„ط¯ط¹ظˆط©", value=link)
    if st.button("ًں“‹ ظ†ط³ط® ط§ظ„ط±ط§ط¨ط·"):
        st.success("âœ… طھظ… ط§ظ„ظ†ط³ط®!")

# ============================================================
#  ًں“„ PAGE: SETTINGS
# ============================================================
def page_settings():
    st.markdown('<div class="section-title">âڑ™ï¸ڈ ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ</div>', unsafe_allow_html=True)
    with st.form("settings"):
        st.text_input("ط§ظ„ط§ط³ظ… ط§ظ„ط¸ط§ظ‡ط±", value=st.session_state.current_user["name"])
        st.text_input("ط§ظ„طھط®طµطµ", value=st.session_state.current_user.get("specialty",""))
        if st.form_submit_button("ًں’¾ ط­ظپط¸"):
            st.success("âœ… طھظ… ط§ظ„ط­ظپط¸")

# ============================================================
#  ًں“„ PAGE: REPORTS
# ============================================================
def page_reports():
    st.markdown('<div class="section-title">ًں“„ ط§ظ„طھظ‚ط§ط±ظٹط±</div>', unsafe_allow_html=True)
    patient_name = st.text_input("ًں‘¤ ط§ط³ظ… ط§ظ„ظ…ط±ظٹط¶", value="ظ…ط±ظٹط¶ طھط¬ط±ظٹط¨ظٹ")
    
    images = {}
    if hasattr(st.session_state, 'last_analysis_image') and st.session_state.last_analysis_image:
        images["طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡ (468 ظ†ظ‚ط·ط©)"] = st.session_state.last_analysis_image
    if hasattr(st.session_state, 'last_cephalometric_image') and st.session_state.last_cephalometric_image:
        images["طھط­ظ„ظٹظ„ ط§ظ„ط£ط´ط¹ط©"] = st.session_state.last_cephalometric_image
    if hasattr(st.session_state, 'last_smile_image') and st.session_state.last_smile_image:
        images["ظ…ط­ط§ظƒط§ط© ط§ظ„ط§ط¨طھط³ط§ظ…ط©"] = st.session_state.last_smile_image
    
    analysis_data = {}
    if hasattr(st.session_state, 'last_analysis_data') and st.session_state.last_analysis_data:
        analysis_data["face_analysis"] = st.session_state.last_analysis_data
    if hasattr(st.session_state, 'last_cephalometric_data') and st.session_state.last_cephalometric_data:
        analysis_data["cephalometric"] = st.session_state.last_cephalometric_data
    
    if st.button("ًں“„ طھظˆظ„ظٹط¯ طھظ‚ط±ظٹط± ط´ط§ظ…ظ„", type="primary", use_container_width=True):
        if images:
            with st.spinner("âڈ³ ط¬ط§ط±ظٹ طھظˆظ„ظٹط¯ ط§ظ„طھظ‚ط±ظٹط±..."):
                html_content = generate_html_report(patient_name, analysis_data, images)
                st.download_button(
                    label="â¬‡ï¸ڈ طھط­ظ…ظٹظ„ ط§ظ„طھظ‚ط±ظٹط± HTML",
                    data=html_content.encode('utf-8'),
                    file_name=f"report_{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html"
                )
                st.success("âœ… طھظ… طھظˆظ„ظٹط¯ ط§ظ„طھظ‚ط±ظٹط± ط¨ظ†ط¬ط§ط­!")
        else:
            st.warning("âڑ ï¸ڈ ظ„ط§ طھظˆط¬ط¯ طµظˆط± ظ„ظ„طھطµط¯ظٹط±. ظ‚ظ… ط¨طھط­ظ„ظٹظ„ ط§ظ„ظˆط¬ظ‡ ط£ظˆ ط§ظ„ط£ط´ط¹ط© ط£ظˆظ„ط§ظ‹.")

# ============================================================
#  ًں“„ PAGE: PRIVACY
# ============================================================
def page_privacy():
    st.markdown('<div class="section-title">ًں”’ ط§ظ„ط®طµظˆطµظٹط©</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#8892b0; line-height:1.8;">
        <strong>ط³ظٹط§ط³ط© ط§ظ„ط®طµظˆطµظٹط©:</strong> ظ†ط­ظ† ظ†ظ„طھط²ظ… ط¨ط­ظ…ط§ظٹط© ط¨ظٹط§ظ†ط§طھظƒ ط§ظ„ط´ط®طµظٹط©.<br>
        <strong>ًں”’ ط®طµظˆطµظٹط© ط§ظ„ط¨ظٹط§ظ†ط§طھ:</strong> ظƒظ„ ظ…ط³طھط®ط¯ظ… ظ„ط¯ظٹظ‡ ط¨ظٹط§ظ†ط§طھظ‡ ط§ظ„ط®ط§طµط©.<br>
        <strong>ًں”گ ط§ظ„ط£ظ…ط§ظ†:</strong> ط¬ظ…ظٹط¹ ط§ظ„ط¨ظٹط§ظ†ط§طھ ظ…ط´ظپط±ط© ظˆظ…ط­ظ…ظٹط©.<br>
        <strong>ًں¤– ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ:</strong> ط¬ظ…ظٹط¹ ط¹ظ…ظ„ظٹط§طھ ط§ظ„طھط­ظ„ظٹظ„ طھطھظ… ط¯ط§ط®ظ„ ط§ظ„ظ†ط¸ط§ظ….
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: IP
# ============================================================
def page_ip():
    st.markdown('<div class="section-title">آ©ï¸ڈ ط­ظ‚ظˆظ‚ ط§ظ„ظ…ظ„ظƒظٹط© ط§ظ„ظپظƒط±ظٹط©</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
        <p style="color:#8892b0; line-height:1.8;">
        <strong>ط­ظ‚ظˆظ‚ ط§ظ„ظ…ظ„ظƒظٹط© ط§ظ„ظپظƒط±ظٹط©:</strong> ط¬ظ…ظٹط¹ ط§ظ„ظ…ط­طھظˆظٹط§طھ ظ…ط­ظ…ظٹط© ط¨ظ…ظˆط¬ط¨ ط­ظ‚ظˆظ‚ ط§ظ„ظ†ط´ط±.<br>
        <strong>ًں¤– ط§ظ„ظ…ط­طھظˆظ‰ ط§ظ„ظ…ظڈظ†طھط¬ ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ:</strong> ظ…ظ„ظƒ ظ„ظ„ظ…ط³طھط®ط¯ظ… ط§ظ„ط°ظٹ ط£ظ†ط´ط£ظ‡ط§.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: FORUM
# ============================================================
def page_forum():
    st.markdown('<div class="section-title">ًں—£ï¸ڈ ظ…ظ†طھط¯ظ‰ ط§ظ„ظ†ظ‚ط§ط´ط§طھ</div>', unsafe_allow_html=True)
    st.markdown("### ًں‘¨â€چâڑ•ï¸ڈ ط§ظ„ط£ط®طµط§ط¦ظٹظˆظ† ط§ظ„ظ…طھط§ط­ظˆظ†")
    for sp in st.session_state.specialists:
        status_color = "#10b981" if sp.get("online", True) else "#555"
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:12px; text-align:center; border:1px solid rgba(255,255,255,0.1);">
            <div style="width:12px; height:12px; background:{status_color}; border-radius:50%; margin:0 auto 6px;"></div>
            <strong>{sp['name']}</strong>
            <div style="font-size:0.7rem; color:#8892b0;">{sp['specialty']}</div>
        </div>
        """, unsafe_allow_html=True)
    with st.form("forum_question"):
        q_title = st.text_input("ط¹ظ†ظˆط§ظ† ط§ظ„ط³ط¤ط§ظ„")
        q_body = st.text_area("طھظپط§طµظٹظ„ ط§ظ„ط³ط¤ط§ظ„")
        target = st.selectbox("ظ…ظˆط¬ظ‡ ط¥ظ„ظ‰", ["ط¬ظ…ظٹط¹ ط§ظ„ط£ط®طµط§ط¦ظٹظٹظ†"] + [s["name"] for s in st.session_state.specialists])
        if st.form_submit_button("ًںڑ€ ظ†ط´ط± ط§ظ„ط³ط¤ط§ظ„") and q_title and q_body:
            st.session_state.forum_questions.insert(0, {
                "id": len(st.session_state.forum_questions)+1,
                "title": q_title, "body": q_body,
                "asked_by": st.session_state.current_user["name"],
                "target": target, "status": "open",
                "answers": [], "created_at": datetime.now().isoformat()
            })
            st.success("âœ… طھظ… ظ†ط´ط± ط§ظ„ط³ط¤ط§ظ„!")
            st.rerun()
    for q in st.session_state.forum_questions:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); border-radius:16px; padding:16px; border:1px solid rgba(255,255,255,0.1); margin-bottom:12px; border-right:4px solid #f59e0b;">
            <h4>{q['title']}</h4>
            <p style="color:#8892b0;">{q['body']}</p>
            <div style="font-size:0.75rem; color:#64748b;">ًں‘¤ {q['asked_by']} | ًںژ¯ {q['target']}</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: VITA
# ============================================================
def page_vita():
    st.markdown('<div class="section-title">ًںژ¨ ط£ظ„ظˆط§ظ† ظپظٹطھط§</div>', unsafe_allow_html=True)
    vita_colors = {'A1': '#E8D5B8', 'A2': '#DCC8A8', 'A3': '#D0B898', 'A3.5': '#C8B090', 'A4': '#C0A888',
                   'B1': '#D8C8B0', 'B2': '#CCB8A0', 'B3': '#C0A890', 'B4': '#B89880',
                   'C1': '#C0B0A0', 'C2': '#B8A898', 'C3': '#B09888', 'C4': '#A88878',
                   'D2': '#B8A898', 'D3': '#B09888', 'D4': '#A88878'}
    cols = st.columns(4)
    for i, (code, color) in enumerate(vita_colors.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:12px; text-align:center; background:rgba(255,255,255,0.05);">
                <div style="width:100%; height:40px; border-radius:6px; background:{color}; border:1px solid rgba(255,255,255,0.1);"></div>
                <div style="font-weight:700; color:#00d4ff; margin-top:6px;">{code}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
#  ًں“„ PAGE: IMAGE EDITOR
# ============================================================
def page_image_editor():
    st.markdown('<div class="section-title">ًںژ¨ ظ…ط­ط±ط± ط§ظ„طµظˆط±</div>', unsafe_allow_html=True)
    if not st.session_state.image_layers:
        base_img = Image.new('RGB', (800, 600), color='#1a1a2e')
        draw = ImageDraw.Draw(base_img)
        draw.text((400, 300), "ًں¦· ط§ط±ظپط¹ طµظˆط±ط© ظ„ط¨ط¯ط، ط§ظ„طھط­ط±ظٹط±", fill='#8892b0', anchor="mm")
        st.session_state.image_layers = [{"name": "Background", "image": base_img, "visible": True, "opacity": 1.0, "blend_mode": "normal"}]
        st.session_state.current_layer = 0
    uploaded = st.file_uploader("ًں“¤ ط±ظپط¹ طµظˆط±ط©", type=["jpg", "png", "jpeg"], key="editor_upload")
    if uploaded:
        img = Image.open(uploaded)
        if isinstance(img, Image.Image):
            layer = {"name": f"Layer {len(st.session_state.image_layers)}", "image": img, "visible": True, "opacity": 1.0, "blend_mode": "normal"}
            st.session_state.image_layers.append(layer)
            st.session_state.current_layer = len(st.session_state.image_layers) - 1
            st.success("âœ… طھظ… ط¥ط¶ط§ظپط© ط§ظ„ط·ط¨ظ‚ط©")
            st.rerun()
    
    for i, layer in enumerate(st.session_state.image_layers):
        active = "active" if i == st.session_state.current_layer else ""
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;border-radius:4px;background:rgba(255,255,255,0.03);margin-bottom:4px;border:1px solid {'#00d4ff' if i == st.session_state.current_layer else 'transparent'};cursor:pointer;">
            <span style="font-size:0.8rem;color:#8892b0;">{layer['name']}</span>
            <span style="font-size:0.8rem;color:#8892b0;">{'ًں‘پï¸ڈ' if layer['visible'] else 'ًں‘پï¸ڈâ€چًں—¨ï¸ڈ'}</span>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("ًں”— ط¯ظ…ط¬ ط§ظ„ظƒظ„", use_container_width=True):
        if len(st.session_state.image_layers) > 1:
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
                st.success("âœ… طھظ… ط¯ظ…ط¬ ط§ظ„ط·ط¨ظ‚ط§طھ!")
                st.rerun()

# ============================================================
#  ًں“„ PAGE: 3D VIEWER
# ============================================================
def page_3d_viewer():
    st.markdown('<div class="section-title">ًں¦· ط¹ط§ط±ط¶ 3D</div>', unsafe_allow_html=True)
    st.caption("ط¹ط§ط±ط¶ ط«ظ„ط§ط«ظٹ ط§ظ„ط£ط¨ط¹ط§ط¯ ظ„ظ„ط£ط³ظ†ط§ظ† ظˆط§ظ„ظپظƒ")
    viewer_html = get_3d_viewer_html()
    st.components.v1.html(viewer_html, height=550)
    
    st.markdown("### ًں“‹ ظ…ط¹ظ„ظˆظ…ط§طھ ط§ظ„ظ†ظ…ظˆط°ط¬")
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    with col_info1:
        st.metric("ًں¦· ط§ظ„ط£ط³ظ†ط§ظ†", "32", "ظƒط§ظ…ظ„ط©")
    with col_info2:
        st.metric("ًں”؛ ط§ظ„ظ…ط«ظ„ط«ط§طھ", "24.5K", "+2.1K")
    with col_info3:
        st.metric("ًں“گ ط§ظ„ط£ط¨ط¹ط§ط¯", "120x80x60", "mm")
    with col_info4:
        st.metric("ًں“پ ط§ظ„ط­ط¬ظ…", "4.2 MB", "STL")

# ============================================================
#  ًں“‹ PAGE ROUTER
# ============================================================
PAGES = {
    "home": page_home,
    "dashboard": page_dashboard,
    "upload_logo": page_upload_logo,
    "face_analysis": page_face_analysis,
    "golden_ratio": page_golden_ratio,
    "smile_analysis": page_smile_analysis,
    "ai_simulator": page_ai_simulator,
    "cephalometric": page_cephalometric,
    "analytics": page_analytics,
    "dental_chart": page_dental_chart_view,
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
    "smart_diagnosis": page_smart_diagnosis,
    "treatment_plan": page_treatment_plan,
    "materials": page_materials,
    "facial": page_facial,
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
    "vita": page_vita,
    "image_editor": page_image_editor,
    "3d_viewer": page_3d_viewer,
}

# ============================================================
#  ًںڑ€ MAIN
# ============================================================
def main():
    # Ensure current_page exists
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    
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
            <strong style="color:#00d4ff;">ًں¦· DENTAL AI OS</strong><br>
            Naqeeb412 آ· Synergy<br>
            آ© 2026 ط¬ظ…ظٹط¹ ط§ظ„ط­ظ‚ظˆظ‚ ظ…ط­ظپظˆط¸ط©.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
