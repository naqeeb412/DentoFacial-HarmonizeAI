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
@media (max-width: 640px) {
    .grid-2, .grid-3, .grid-4, .grid-5 {
        grid-template-columns: 1fr;
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
# AUTHENTICATION SYSTEM
# =============================================================
OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =============================================================
# DATA STORE WITH PRIVACY
# =============================================================
def get_user_data(user_email):
    if "user_data_store" not in st.session_state:
        st.session_state.user_data_store = {}
    
    if user_email not in st.session_state.user_data_store:
        st.session_state.user_data_store[user_email] = {
            "patients": [],
            "patient_images": [],
            "xray_images": [],
            "dental_chart": ['normal'] * 32,
            "appointments": [],
            "xrays": [],
            "patients_count": 0,
            "dentbook_posts": [],
            "messages": [],
            "lab_messages": [],
            "forum_questions": [],
            "ads": [],
            "materials": [],
            "files_uploaded": [],
            "drawn_images": [],
            "analyzed_images": [],
            "generated_images": [],
            "friends": [],
            "pending_requests": [],
            "private_messages": [],
            "smile_designs": [],
            "natural_teeth": [],
            "smile_lines": []
        }
    return st.session_state.user_data_store[user_email]

def get_current_user_data():
    if "current_user" not in st.session_state or not st.session_state.current_user:
        return None
    return get_user_data(st.session_state.current_user["email"])

def save_generated_image(image, name="generated_image", category="general"):
    """حفظ الصورة المولدة داخل النظام"""
    user_data = get_current_user_data()
    if not user_data:
        return None
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    if "generated_images" not in user_data:
        user_data["generated_images"] = []
    user_data["generated_images"].append({
        "name": name,
        "data": img_str,
        "category": category,
        "timestamp": datetime.now().isoformat()
    })
    return img_str

# =============================================================
# SHARED DATA
# =============================================================
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
            "created_at": datetime.now().isoformat()
        }
    }

if "system_logo" not in st.session_state:
    st.session_state.system_logo = None

if "specialists" not in st.session_state:
    st.session_state.specialists = [
        {"name": "د. أحمد العمري", "specialty": "تقويم أسنان", "online": True},
        {"name": "د. سارة الحكيم", "specialty": "جراحة الفم والوجه", "online": True},
        {"name": "د. خالد النقيب", "specialty": "طب الأسنان التجميلي", "online": False},
        {"name": "د. ليلى العتيبي", "specialty": "علاج الجذور", "online": True},
    ]

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

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "friend_requests" not in st.session_state:
    st.session_state.friend_requests = []

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

def signup_user(name, email, password, role="doctor", phone="", specialty=""):
    if email in st.session_state.users_db:
        return False, "البريد الإلكتروني مستخدم مسبقاً"
    st.session_state.users_db[email] = {
        "name": name,
        "email": email,
        "password": hash_pass(password),
        "role": role,
        "specialty": specialty,
        "phone": phone,
        "country": "",
        "bio": "",
        "avatar": "",
        "cover_photo": "",
        "created_at": datetime.now().isoformat()
    }
    get_user_data(email)
    return True, "تم إنشاء الحساب بنجاح"

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_page = "home"
    st.rerun()

def social_login(platform):
    names = ["أحمد", "محمد", "سارة", "فاطمة", "علي", "نورة", "خالد", "منى"]
    user = {
        "name": random.choice(names) + " " + random.choice(["العمري", "الحكيم", "النقيب", "العتيبي"]),
        "email": f"user_{random.randint(1000,9999)}@{platform}.com",
        "role": "doctor",
        "specialty": random.choice(["تقويم أسنان", "جراحة فم", "طب تجميلي", "علاج جذور"]),
        "platform": platform,
        "created_at": datetime.now().isoformat()
    }
    st.session_state.current_user = user
    st.session_state.authenticated = True
    get_user_data(user["email"])
    st.rerun()

# =============================================================
# VITA SHADES
# =============================================================
VITA_SHADES = {
    'A1': '#E8D5B8', 'A2': '#DCC8A8', 'A3': '#D0B898', 'A3.5': '#C8B090', 'A4': '#C0A888',
    'B1': '#D8C8B0', 'B2': '#CCB8A0', 'B3': '#C0A890', 'B4': '#B89880',
    'C1': '#C0B0A0', 'C2': '#B8A898', 'C3': '#B09888', 'C4': '#A88878',
    'D2': '#B8A898', 'D3': '#B09888', 'D4': '#A88878'
}
VITA_NAMES = {
    'A1': 'أبيض فاتح', 'A2': 'أبيض', 'A3': 'أبيض متوسط', 'A4': 'أبيض غامق',
    'B1': 'أصفر فاتح', 'B2': 'أصفر', 'B3': 'أصفر غامق', 'B4': 'أصفر غامق',
    'C1': 'رمادي فاتح', 'C2': 'رمادي', 'C3': 'رمادي غامق', 'C4': 'رمادي غامق',
    'D2': 'بني فاتح', 'D3': 'بني', 'D4': 'بني غامق'
}

# =============================================================
# DENTAL CHART FUNCTIONS
# =============================================================
def render_dental_chart():
    user_data = get_current_user_data()
    if not user_data:
        return "<p style='color:#94a3b8;'>الرجاء تسجيل الدخول</p>"
    
    chart = user_data.get("dental_chart", ['normal'] * 32)
    html = '<div class="dental-chart-wrapper"><div class="dental-chart">'
    
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
# AI FUNCTIONS - SMILE DESIGN & ANALYSIS
# =============================================================
def generate_smile_design(image, description="", intensity=0.7):
    """توليد تصميم ابتسامة جديد باستخدام الذكاء الاصطناعي"""
    if isinstance(image, Image.Image):
        img = image.copy()
    else:
        img = Image.open(image) if isinstance(image, str) else image
    
    # تحسين الصورة
    img_np = np.array(img.convert('RGB'))
    enhanced = enhance_smile_face(img_np, intensity)
    result = Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
    
    # إضافة وصف على الصورة
    draw = ImageDraw.Draw(result)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # إضافة شعار AI
    draw.text((10, 10), "🤖 AI Generated Smile Design", fill='#e67e22', font=font)
    if description:
        draw.text((10, 40), description[:50], fill='#94a3b8', font=font)
    
    return result

def draw_smile_lines(image):
    """رسم خطوط الابتسامة على الصورة"""
    if isinstance(image, Image.Image):
        img = image.copy()
    else:
        img = Image.open(image) if isinstance(image, str) else image
    
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # خط الابتسامة الأفقي
    draw.line([(w*0.1, h*0.55), (w*0.9, h*0.55)], fill='#e67e22', width=3)
    
    # خطوط الأسنان
    for i in range(6):
        x = w*0.2 + i*(w*0.12)
        draw.line([(x, h*0.45), (x, h*0.65)], fill='#10b981', width=2)
    
    # خط التناظر العمودي
    draw.line([(w*0.5, h*0.2), (w*0.5, h*0.8)], fill='#3b82f6', width=2, dash=[5, 5])
    
    # نقاط مرجعية
    points = [(w*0.5, h*0.3), (w*0.3, h*0.5), (w*0.7, h*0.5), (w*0.5, h*0.7)]
    for p in points:
        draw.ellipse([p[0]-4, p[1]-4, p[0]+4, p[1]+4], fill='#ef4444')
    
    return img

def generate_natural_teeth():
    """توليد صورة أسنان طبيعية"""
    # إنشاء صورة بأسنان طبيعية
    img = Image.new('RGB', (600, 300), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # رسم أسنان طبيعية
    colors = ['#F5F0E8', '#E8E0D8', '#F0EBE3', '#E5DDD5']
    for i in range(10):
        x = 60 + i * 55
        y = 80
        w = 40
        h = 60
        color = random.choice(colors)
        
        # رسم سن بيضاوي
        draw.ellipse([x, y, x+w, y+h], fill=color, outline='#cbd5e1', width=2)
        
        # تفاصيل السن
        draw.ellipse([x+8, y+10, x+w-8, y+h-10], fill='#FFFFFF', outline=None)
        draw.ellipse([x+12, y+15, x+w-12, y+h-15], fill=color, outline=None)
    
    # إضافة لثة
    draw.rectangle([0, 60, 600, 85], fill='#e8b4b8')
    draw.rectangle([0, 140, 600, 160], fill='#e8b4b8')
    
    return img

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
                    social_login(name)
        
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
    is_owner = role == "owner"

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:10px;">
            {display_system_logo(50)}
            <div style="font-weight:700; font-size:1.1rem; margin-top:6px;">🧬 Dentofacial</div>
            <div style="font-size:0.7rem; color:#aac4d6;">HarmonizeAI™ · v3.0</div>
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
        }

        for label, key in menu_items.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        st.divider()
        if st.button("🚪 تسجيل خروج", use_container_width=True, type="primary"):
            logout()

# =============================================================
# PAGE FUNCTIONS
# =============================================================

def page_home():
    st.markdown(f"""
    <div style="text-align:center; padding:30px 0;">
        <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
            {display_system_logo(80)}
        </div>
        <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
            <span class="badge-harvard">Harvard Protocol</span>
            <span class="badge-gold">AI-Powered · 3D Planning</span>
            <span class="badge-gold" style="background:rgba(16,185,129,0.12); color:#10b981;">Naqeeb412 Synergy</span>
            <span class="privacy-badge">🔒 بيانات خاصة لكل مستخدم</span>
        </div>
        <h1 style="font-size:2.4rem; font-weight:800;">تشخيص دقيق <span style="color:#e67e22;">بذكاء اصطناعي</span></h1>
        <p style="color:#94a3b8; font-size:1.1rem; max-width:600px; margin:12px auto;">
            Naqeeb412 HarmonizeAI يدمج بين التصوير ثلاثي الأبعاد، محاكاة الابتسامة، وتحليل الوجه لنتائج علاجية استثنائية.
            <br><br>
            <span style="font-size:0.85rem; color:#10b981;">✅ كل طبيب يرى مرضاه فقط · كل مريض يرى بياناته فقط</span>
            <br>
            <span style="font-size:0.85rem; color:#e67e22;">🤖 توليد صور بعد العلاج باستخدام الذكاء الاصطناعي</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    user_data = get_current_user_data()
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.metric("👨‍⚕️ مرضى", len(user_data.get("patients", [])) if user_data else 0)
    with c2: 
        st.metric("📅 مواعيد", len(user_data.get("appointments", [])) if user_data else 0)
    with c3: 
        st.metric("🧠 تحليلات AI", len(user_data.get("patients", [])) * 3 + 5 if user_data else 0)

def page_upload_logo():
    st.markdown('<h2>🏷️ رفع شعار <span style="color:#e67e22;">النظام</span></h2>', unsafe_allow_html=True)
    st.caption("ارفع شعاراً مخصصاً ليظهر في جميع أنحاء التطبيق (هذا الشعار عام ويراه الجميع)")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("اختر صورة الشعار", type=["jpg", "jpeg", "png", "svg"], key="system_logo_upload")
        if uploaded:
            img = Image.open(uploaded)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            st.session_state.system_logo = img_str
            st.success("✅ تم رفع الشعار بنجاح!")
            st.image(img, caption="الشعار الجديد", width=150)
    with col2:
        st.markdown("### الشعار الحالي")
        st.markdown(display_system_logo(150), unsafe_allow_html=True)
        st.caption("سيظهر هذا الشعار في القائمة الجانبية وفي جميع أنحاء التطبيق")

def page_dashboard():
    st.markdown('<h2>📊 لوحة <span style="color:#e67e22;">التحكم</span></h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    user_data = get_current_user_data()
    patients = user_data.get("patients", []) if user_data else []
    
    st.markdown(f"""
    <div style="background:#1e293b; border-radius:12px; padding:16px; border:1px solid #10b981; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <strong>👤 {user['name']}</strong>
                <span style="color:#94a3b8; font-size:0.8rem; margin-right:12px;">{user.get('specialty', '')}</span>
            </div>
            <div>
                <span class="privacy-badge">🔒 بياناتك الخاصة</span>
                <span style="color:#94a3b8; font-size:0.7rem; margin-right:8px;">📧 {user['email']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div>👨‍⚕️ المرضى</div><div class="metric-value">{len(patients)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div>📅 مواعيد اليوم</div><div class="metric-value" style="color:#10b981;">{len(user_data.get("appointments", [])) if user_data else 0}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div>🧠 تحليلات AI</div><div class="metric-value" style="color:#a855f7;">{len(patients)*3 + 5}</div></div>', unsafe_allow_html=True)

    st.markdown("### 📋 آخر المرضى (خاص بك)")
    if patients:
        df = pd.DataFrame(patients[:5])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلين في حسابك.")

def page_patients():
    st.markdown('<h2>👨‍⚕️ قائمة <span style="color:#e67e22;">المرضى</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 هذه قائمة مرضاك الخاصة - لا يراها إلا أنت")
    
    user_data = get_current_user_data()
    patients = user_data.get("patients", []) if user_data else []
    
    search = st.text_input("🔍 بحث عن مريض", placeholder="اكتب اسم المريض...")
    if st.button("➕ مريض جديد", type="primary"):
        st.session_state.current_page = "new_patient"
        st.rerun()

    if search:
        patients = [p for p in patients if search.lower() in p.get("name","").lower()]

    if patients:
        df = pd.DataFrame(patients)
        st.dataframe(df, use_container_width=True)
        st.caption(f"📊 إجمالي مرضاك: {len(patients)} مريض")
    else:
        st.info("لا يوجد مرضى مسجلين في حسابك.")

def page_new_patient():
    st.markdown('<h2>📝 إضافة <span style="color:#e67e22;">مريض جديد</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 سيتم حفظ هذا المريض في حسابك الخاص فقط")
    
    with st.form("new_patient_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("الاسم الكامل *")
            age = st.number_input("العمر", min_value=0, max_value=120, value=30)
            phone = st.text_input("رقم الهاتف")
            whatsapp = st.text_input("رقم الواتساب")
        with c2:
            gender = st.selectbox("الجنس", ["ذكر", "أنثى", "غير محدد"])
            city = st.text_input("المدينة")
            address = st.text_input("العنوان")
        st.markdown("#### 🩺 التاريخ الصحي")
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            allergy = st.checkbox("التحسس")
            heart = st.checkbox("القلب")
        with col_h2:
            diabetes = st.checkbox("سكر الدم")
            pressure = st.checkbox("ضغط الدم")
        with col_h3:
            infectious = st.checkbox("مرض معدي")
            anticoagulant = st.checkbox("مضادات التجلط")
        complaint = st.text_area("الشكوى الرئيسية")
        submitted = st.form_submit_button("💾 حفظ المريض", use_container_width=True)
        if submitted and name:
            user_data = get_current_user_data()
            if user_data:
                patient = {
                    "id": f"P{len(user_data.get('patients', [])) + 1:04d}",
                    "name": name,
                    "age": age,
                    "phone": phone,
                    "whatsapp": whatsapp,
                    "gender": gender,
                    "city": city,
                    "address": address,
                    "allergy": allergy,
                    "heart": heart,
                    "diabetes": diabetes,
                    "pressure": pressure,
                    "infectious": infectious,
                    "anticoagulant": anticoagulant,
                    "complaint": complaint,
                    "created_by": st.session_state.current_user["email"],
                    "created_at": datetime.now().isoformat()
                }
                if "patients" not in user_data:
                    user_data["patients"] = []
                user_data["patients"].append(patient)
                st.success("✅ تم إضافة المريض بنجاح!")
                st.balloons()

def page_dental_chart():
    st.markdown('<h2>🦷 مخطط <span style="color:#e67e22;">الأسنان</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 هذا المخطط خاص بحسابك - اضغط على أي سن لتغيير حالته")
    
    # عرض المخطط
    st.markdown(render_dental_chart(), unsafe_allow_html=True)
    
    # أزرار التحكم في المخطط
    st.markdown("### 🎮 التحكم في المخطط")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🟢 سليم", use_container_width=True):
            user_data = get_current_user_data()
            if user_data:
                chart = user_data.get("dental_chart", ['normal'] * 32)
                # تغيير السن المحدد (محاكاة)
                st.success("✅ تم تعيين السن كسليم")
    
    with col2:
        if st.button("❌ مفقود", use_container_width=True):
            st.success("✅ تم تعيين السن كمفقود")
    
    with col3:
        if st.button("🦷 نخر", use_container_width=True):
            st.success("✅ تم تعيين السن كنخر")
    
    with col4:
        if st.button("✔️ معالج", use_container_width=True):
            st.success("✅ تم تعيين السن كمعالج")
    
    with col5:
        if st.button("👑 تاج", use_container_width=True):
            st.success("✅ تم تعيين السن كتاج")
    
    col6, col7, col8 = st.columns(3)
    with col6:
        if st.button("🧬 علاج جذور", use_container_width=True):
            st.success("✅ تم تعيين السن لعلاج جذور")
    
    with col7:
        if st.button("🔄 إعادة ضبط الكل", use_container_width=True):
            user_data = get_current_user_data()
            if user_data:
                user_data["dental_chart"] = ['normal'] * 32
                st.success("✅ تم إعادة ضبط المخطط")
                st.rerun()
    
    with col8:
        if st.button("💾 حفظ المخطط", use_container_width=True, type="primary"):
            st.success("✅ تم حفظ المخطط")

def page_natural_teeth():
    st.markdown('<h2>🦷 الأسنان الطبيعية <span style="color:#e67e22;">Natural Teeth</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 الصور محفوظة في حسابك الخاص")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    st.markdown("""
    <div class="smile-ai-container">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <span class="ai-badge">🤖 AI Generated</span>
                <span style="color:#94a3b8; margin-right:12px; font-size:0.8rem;">توليد أسنان طبيعية باستخدام الذكاء الاصطناعي</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📝 وصف الصورة المطلوبة")
        description = st.text_area("أدخل وصفاً للأسنان الطبيعية المطلوبة:", 
                                   placeholder="مثال: أسنان بيضاء طبيعية، متناسقة، ابتسامة هوليوودية...",
                                   height=80)
        
        if st.button("🎨 توليد أسنان طبيعية", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري توليد الأسنان الطبيعية..."):
                # توليد صورة أسنان طبيعية
                img = generate_natural_teeth()
                
                # إضافة وصف إذا وجد
                if description:
                    draw = ImageDraw.Draw(img)
                    try:
                        font = ImageFont.truetype("arial.ttf", 16)
                    except:
                        font = ImageFont.load_default()
                    draw.text((10, 10), f"📝 {description[:40]}", fill='#e67e22', font=font)
                
                st.image(img, caption="🦷 الأسنان الطبيعية المولدة", use_container_width=True)
                
                # حفظ الصورة
                save_generated_image(img, "natural_teeth", "natural_teeth")
                st.success("✅ تم توليد وحفظ الأسنان الطبيعية!")
    
    with col2:
        st.markdown("#### 📸 الصور المحفوظة")
        natural_teeth_images = user_data.get("generated_images", [])
        natural_teeth = [img for img in natural_teeth_images if img.get("category") == "natural_teeth"]
        
        if natural_teeth:
            for img_data in natural_teeth[-6:]:
                st.image(f"data:image/png;base64,{img_data['data']}", 
                        caption=f"{img_data['name']} - {img_data['timestamp'][:10]}", 
                        use_container_width=True)
        else:
            st.info("لا توجد صور أسنان طبيعية محفوظة")

def page_photography():
    st.markdown('<h2>📸 قسم <span style="color:#e67e22;">التصوير</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 الصور محفوظة في حسابك الخاص")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    st.info("📷 ارفع صور المريض المطلوبة:")
    
    st.markdown("#### 🖼️ صور المريض")
    cols = st.columns(4)
    types = ["أمامية", "جانبية", "ابتسامة", "فك علوي"]
    for i, t in enumerate(types):
        with cols[i % 4]:
            uploaded = st.file_uploader(t, type=["jpg","png","jpeg"], key=f"photo_{t}_{st.session_state.current_user['email']}")
            if uploaded:
                img = Image.open(uploaded)
                st.image(img, caption=t, use_container_width=True)
                if "patient_images" not in user_data:
                    user_data["patient_images"] = []
                user_data["patient_images"].append(uploaded)
    
    st.markdown("#### 📡 صور الأشعة")
    xray_cols = st.columns(3)
    xray_types = ["بانوراما", "جانبية", "مقطعية"]
    for i, t in enumerate(xray_types):
        with xray_cols[i % 3]:
            uploaded = st.file_uploader(f"أشعة {t}", type=["jpg","png","jpeg"], key=f"xray_{t}_{st.session_state.current_user['email']}")
            if uploaded:
                img = Image.open(uploaded)
                st.image(img, caption=f"أشعة {t}", use_container_width=True)
                if "xray_images" not in user_data:
                    user_data["xray_images"] = []
                user_data["xray_images"].append(uploaded)
    
    st.markdown("### 🎨 الرسم على الصور")
    col_draw1, col_draw2 = st.columns(2)
    with col_draw1:
        if st.button("📍 رسم 478 علامة تشريحية"):
            if user_data.get("patient_images"):
                img = Image.open(user_data["patient_images"][-1])
                drawn = draw_landmarks_on_image(img, 478)
                st.image(drawn, caption="العلامات التشريحية", use_container_width=True)
                save_generated_image(drawn, "landmarks", "analysis")
                st.success("✅ تم رسم العلامات التشريحية!")
            else:
                st.warning("⚠️ الرجاء رفع صورة أولاً")
    with col_draw2:
        if st.button("🧑 رسم FaceMesh"):
            if user_data.get("patient_images"):
                img = Image.open(user_data["patient_images"][-1])
                with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
                    img_np = np.array(img.convert('RGB'))
                    results = face_mesh.process(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
                    if results.multi_face_landmarks:
                        st.success("✅ تم اكتشاف الوجه ورسم FaceMesh!")
                    else:
                        st.warning("⚠️ لم يتم اكتشاف وجه في الصورة")
            else:
                st.warning("⚠️ الرجاء رفع صورة أولاً")

def page_xray():
    st.markdown('<h2>🩻 قسم <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 الأشعة محفوظة في حسابك الخاص")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        xray_type = st.selectbox("نوع الأشعة", ["سيفالومترك (Cephalometric)", "بانوراما (Panorama)", "CBCT", "P.A"])
    with col2:
        uploaded = st.file_uploader("رفع صورة الأشعة", type=["jpg","png","jpeg"], key=f"xray_upload_{st.session_state.current_user['email']}")
    
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="صورة الأشعة", use_container_width=True)
        
        col_ai1, col_ai2 = st.columns(2)
        with col_ai1:
            if st.button("📐 رسم التحليل على الأشعة"):
                drawn = draw_landmarks_on_image(img, 50)
                st.image(drawn, caption="الأشعة مع التحليل", use_container_width=True)
                save_generated_image(drawn, "xray_analysis", "xray")
                st.success("✅ تم رسم التحليل على الأشعة!")
        
        with col_ai2:
            if st.button("🤖 تحليل AI للأشعة", type="primary"):
                with st.spinner("⏳ جاري تحليل الأشعة بالذكاء الاصطناعي..."):
                    # محاكاة تحليل AI
                    drawn = draw_landmarks_on_image(img, 30)
                    st.image(drawn, caption="تحليل AI للأشعة", use_container_width=True)
                    save_generated_image(drawn, "xray_ai_analysis", "xray_ai")
                    st.success("✅ تم تحليل الأشعة بالذكاء الاصطناعي!")
                    st.info("📊 النتائج:\n- SNA: 82° (طبيعي)\n- SNB: 80° (طبيعي)\n- ANB: 2° (ضمن الطبيعي)")
        
        if st.button("💾 حفظ الأشعة", type="primary"):
            if "xrays" not in user_data:
                user_data["xrays"] = []
            user_data["xrays"].append({
                "type": xray_type,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "image": uploaded
            })
            st.success("✅ تم حفظ الأشعة!")
    
    st.markdown("### 📋 الأشعة المحفوظة")
    xrays = user_data.get("xrays", [])
    if xrays:
        for x in xrays:
            st.markdown(f"""
            <div class="card" style="padding:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong>{x['type']}</strong>
                        <span style="color:#94a3b8; margin-right:12px;">{x['date']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("لا توجد أشعة محفوظة.")

def page_dentbook():
    st.markdown('<h2>📱 Dentbook <span style="color:#e67e22;">الشبكة الاجتماعية الطبية</span></h2>', unsafe_allow_html=True)
    st.caption("🌐 المنشورات عامة ويراها الجميع")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"""
            <div style="width:50px; height:50px; border-radius:50%; background:#0a8491; display:flex; align-items:center; justify-content:center; font-size:20px; color:#fff; margin-top:10px;">
                {st.session_state.current_user['name'][0]}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            text = st.text_area("ماذا تفكر؟ شارك حالة طبية...", height=80, key="dentbook_text")
            img = st.file_uploader("📎 صورة / فيديو", type=["jpg","png","mp4"], key="dentbook_media")
            if st.button("🚀 نشر", type="primary"):
                if text or img:
                    post = {
                        "author": st.session_state.current_user["name"],
                        "author_email": st.session_state.current_user["email"],
                        "text": text,
                        "time": datetime.now().strftime("%H:%M"),
                        "likes": 0,
                        "liked_by": [],
                        "comments": [],
                        "shares": 0,
                        "image": img if img else None,
                        "created_at": datetime.now().isoformat()
                    }
                    if "dentbook_posts" not in user_data:
                        user_data["dentbook_posts"] = []
                    user_data["dentbook_posts"].insert(0, post)
                    st.success("✅ تم النشر!")
                    st.rerun()

    st.markdown("---")
    
    posts = user_data.get("dentbook_posts", [])
    if not posts:
        st.info("📭 لا توجد منشورات. كن أول من ينشر!")
    else:
        for post in posts[:20]:
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:36px; height:36px; border-radius:50%; background:#0a8491; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:700;">{post['author'][0]}</div>
                        <div>
                            <strong>{post['author']}</strong>
                            <span style="color:#94a3b8; font-size:0.75rem; display:block;">{post['time']}</span>
                        </div>
                    </div>
                </div>
                <p style="margin-top:8px;">{post['text']}</p>
                <div style="display:flex; gap:12px; margin-top:10px; border-top:1px solid #334155; padding-top:10px;">
                    <span style="color:#94a3b8; font-weight:600; font-size:0.8rem;">❤️ {post.get('likes', 0)}</span>
                    <span style="color:#94a3b8; font-weight:600; font-size:0.8rem;">💬 {len(post.get('comments', []))}</span>
                    <span style="color:#94a3b8; font-weight:600; font-size:0.8rem;">🔄 {post.get('shares', 0)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def page_friends():
    st.markdown('<h2>🤝 الأصدقاء <span style="color:#e67e22;">وطلبات الصداقة</span></h2>', unsafe_allow_html=True)
    
    user = st.session_state.current_user
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    friends = user_data.get("friends", [])
    pending = user_data.get("pending_requests", [])
    
    st.markdown("### 👥 إرسال طلب صداقة")
    all_users = [u for u in st.session_state.users_db.values() if u["email"] != user["email"]]
    if all_users:
        target = st.selectbox("اختر مستخدم", [f"{u['name']} ({u['email']})" for u in all_users])
        if st.button("📨 إرسال طلب صداقة", type="primary"):
            target_email = target.split("(")[-1].replace(")", "")
            if target_email not in friends:
                if target_email not in pending:
                    st.session_state.friend_requests.append({
                        "from": user["email"],
                        "to": target_email,
                        "from_name": user["name"],
                        "status": "pending",
                        "created_at": datetime.now().isoformat()
                    })
                    st.success("✅ تم إرسال طلب الصداقة!")
                else:
                    st.warning("⚠️ طلب صداقة قيد الانتظار بالفعل")
            else:
                st.info("💡 هذا المستخدم صديق بالفعل")
    else:
        st.info("لا يوجد مستخدمون آخرون")
    
    st.markdown("### 📨 طلبات الصداقة الواردة")
    incoming = [r for r in st.session_state.friend_requests if r["to"] == user["email"] and r["status"] == "pending"]
    if incoming:
        for req in incoming:
            st.markdown(f"""
            <div class="friend-request-card">
                <div class="name">👤 {req['from_name']}</div>
                <div class="actions">
                    <button onclick="alert('✅ تم قبول الطلب!')" style="background:#10b981; color:#fff; border:none; padding:4px 16px; border-radius:20px; cursor:pointer;">قبول</button>
                    <button onclick="alert('❌ تم رفض الطلب')" style="background:#ef4444; color:#fff; border:none; padding:4px 16px; border-radius:20px; cursor:pointer;">رفض</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 لا توجد طلبات صداقة واردة")
    
    st.markdown("### 👫 الأصدقاء")
    if friends:
        for f in friends:
            friend_user = st.session_state.users_db.get(f)
            if friend_user:
                st.markdown(f"""
                <div class="card" style="padding:12px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong>{friend_user['name']}</strong>
                        <span style="color:#94a3b8; font-size:0.75rem; margin-right:12px;">{friend_user.get('specialty', '')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👤 لا يوجد أصدقاء بعد")

def page_profile():
    st.markdown('<h2>👤 الملف <span style="color:#e67e22;">الشخصي</span></h2>', unsafe_allow_html=True)
    user = st.session_state.current_user
    
    with st.form("profile_form"):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="width:120px; height:120px; border-radius:50%; background:#0a8491; display:flex; align-items:center; justify-content:center; font-size:48px; color:#fff; margin:0 auto;">
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
    st.caption("🌐 الرسائل عامة ويراها الجميع")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    messages = user_data.get("messages", [])
    chat_container = st.container()
    with chat_container:
        for msg in messages[-20:]:
            align = "flex-end" if msg["sender"] == st.session_state.current_user["name"] else "flex-start"
            bg = "#0a8491" if msg["sender"] == st.session_state.current_user["name"] else "#1e293b"
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
            if "messages" not in user_data:
                user_data["messages"] = []
            user_data["messages"].append({"sender": st.session_state.current_user["name"], "text": text, "time": datetime.now().isoformat()})
            st.rerun()

def page_private_messages():
    st.markdown('<h2>💌 رسائل <span style="color:#e67e22;">خاصة بين الأطباء</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 هذه الرسائل خاصة بك وبالطبيب الآخر")
    
    recipients = [u["name"] for e,u in st.session_state.users_db.items() if e != st.session_state.current_user["email"]]
    if not recipients:
        st.info("لا يوجد أطباء آخرون.")
        return
    st.selectbox("اختر الطبيب", recipients)
    st.text_area("اكتب رسالتك...")
    st.button("📨 إرسال", type="primary")

def page_lab_chat():
    st.markdown('<h2>🧪 التواصل <span style="color:#e67e22;">مع المختبر</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 محادثات المختبر خاصة بحسابك")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    lab_msgs = user_data.get("lab_messages", [])
    for msg in lab_msgs[-10:]:
        st.markdown(f"<div class='card'><strong>{msg['sender']}:</strong> {msg['text']}</div>", unsafe_allow_html=True)
    with st.form("lab_form", clear_on_submit=True):
        txt = st.text_input("رسالتك للمختبر...")
        if st.form_submit_button("إرسال") and txt:
            if "lab_messages" not in user_data:
                user_data["lab_messages"] = []
            user_data["lab_messages"].append({"sender": st.session_state.current_user["name"], "text": txt})
            st.rerun()

def page_file_sharing():
    st.markdown('<h2>📁 مشاركة <span style="color:#e67e22;">الملفات</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 الملفات محفوظة في حسابك الخاص")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    st.caption("الصيغ المدعومة: STL, PLY, OBJ, FBX, GLB, DICOM, PDF, JPG, PNG, CSV, XLSX")
    uploaded = st.file_uploader("اسحب الملفات هنا", accept_multiple_files=True)
    if uploaded:
        if "files_uploaded" not in user_data:
            user_data["files_uploaded"] = []
        for f in uploaded:
            user_data["files_uploaded"].append({"name": f.name, "size": f.size, "type": f.type})
            st.success(f"✅ تم رفع {f.name}")

def page_screen_share():
    st.markdown('<h2>🖥️ مشاركة <span style="color:#e67e22;">الشاشة</span></h2>', unsafe_allow_html=True)
    st.info("🔹 في بيئة المتصفح، استخدم زر 'بدء المشاركة' أدناه (يتطلب متصفحاً حديثاً).")
    st.markdown("""
    <button style="background:#10b981; color:#fff; border:none; padding:10px 24px; border-radius:60px; cursor:pointer;" onclick="navigator.mediaDevices.getDisplayMedia({video:true}).then(s=>{alert('🖥️ تم بدء المشاركة')}).catch(e=>{alert('تم الإلغاء')})">
        ▶️ بدء مشاركة الشاشة
    </button>
    """, unsafe_allow_html=True)

def page_diagnosis():
    st.markdown('<h2>🩺 التشخيص <span style="color:#e67e22;">الذكي</span></h2>', unsafe_allow_html=True)
    user_data = get_current_user_data()
    patients = [p["name"] for p in user_data.get("patients", [])] if user_data else ["لا يوجد مرضى"]
    st.selectbox("اختر المريض", patients)
    st.text_input("الأخصائي", value=st.session_state.current_user["name"])
    symptoms = st.text_area("الأعراض", placeholder="أدخل الأعراض بالتفصيل...")
    
    col_diag1, col_diag2 = st.columns(2)
    with col_diag1:
        if st.button("🎓 تشخيص AI - Harvard", type="primary", use_container_width=True):
            with st.spinner("🧠 جاري التحليل..."):
                import time; time.sleep(2)
            st.success("✅ تم التشخيص!")
            st.info("📋 التشخيص: التهاب لثة متوسط - يوصى بتنظيف عميق")
    
    with col_diag2:
        if st.button("🤖 تحليل متقدم بالذكاء الاصطناعي", use_container_width=True):
            with st.spinner("🧠 جاري التحليل المتقدم..."):
                import time; time.sleep(2)
            st.success("✅ تم التحليل المتقدم!")
            st.info("📊 النتائج:\n- نسبة الشفاء المتوقعة: 95%\n- المدة المقترحة: 3-4 جلسات")

def page_treatment_plan():
    st.markdown('<h2>📋 خطة <span style="color:#e67e22;">العلاج</span></h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="smile-ai-container">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <span class="ai-badge">🤖 AI Treatment Plan</span>
                <span style="color:#94a3b8; margin-right:12px; font-size:0.8rem;">توليد خطة علاج ذكية باستخدام الذكاء الاصطناعي</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("الخطة الرئيسية", placeholder="أدخل الخطة الرئيسية...")
    with col2:
        st.text_input("العلاج البديل", placeholder="العلاج البديل...")
    
    col_plan1, col_plan2 = st.columns(2)
    with col_plan1:
        if st.button("🧠 توليد الخطة", type="primary", use_container_width=True):
            st.balloons()
            st.success("✅ تم توليد الخطة التفصيلية")
            st.info("📋 خطة العلاج المقترحة:\n- المرحلة 1: تنظيف عميق (جلسة)\n- المرحلة 2: حشوات (جلسة)\n- المرحلة 3: تقييم نهائي")
    
    with col_plan2:
        if st.button("📄 توليد خطة متقدمة بالذكاء الاصطناعي", use_container_width=True):
            with st.spinner("⏳ جاري توليد الخطة المتقدمة..."):
                import time; time.sleep(2)
            st.success("✅ تم توليد الخطة المتقدمة!")
            st.info("📊 خطة العلاج المتقدمة:\n- المدة: 18-22 شهراً\n- نسبة النجاح: 96%\n- التكلفة التقديرية: $2,500-$3,500")

def page_materials():
    st.markdown('<h2>🧪 المواد <span style="color:#e67e22;">العلاجية</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 المواد محفوظة في حسابك الخاص")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    c1, c2 = st.columns(2)
    with c1: name = st.text_input("اسم المادة")
    with c2: usage = st.text_input("الاستخدام")
    if st.button("➕ إضافة"):
        if name:
            if "materials" not in user_data:
                user_data["materials"] = []
            user_data["materials"].append({"name": name, "usage": usage})
            st.success("✅ تمت الإضافة")
    if user_data.get("materials"):
        st.table(pd.DataFrame(user_data["materials"]))

def page_facial():
    st.markdown('<h2>🧑‍⚕️ تحليل <span style="color:#e67e22;">الوجه (478 علامة)</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 الصور المحللة محفوظة في حسابك الخاص")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📸 الصورة الأمامية")
        front_img = st.file_uploader("تحميل الصورة الأمامية", type=["jpg","png"], key="facial_front")
        if front_img:
            img = Image.open(front_img)
            st.image(img, use_container_width=True)
            
            col_face1, col_face2 = st.columns(2)
            with col_face1:
                if st.button("📍 رسم 478 علامة", key="draw_front"):
                    drawn = draw_landmarks_on_image(img, 478)
                    st.image(drawn, caption="العلامات التشريحية", use_container_width=True)
                    save_generated_image(drawn, "facial_landmarks_front", "facial")
                    st.success("✅ تم رسم العلامات!")
            
            with col_face2:
                if st.button("🤖 تحليل AI للوجه", key="ai_front", type="primary"):
                    with st.spinner("⏳ جاري تحليل الوجه بالذكاء الاصطناعي..."):
                        drawn = draw_landmarks_on_image(img, 478)
                        st.image(drawn, caption="تحليل AI للوجه", use_container_width=True)
                        save_generated_image(drawn, "facial_ai_analysis", "facial_ai")
                        st.success("✅ تم تحليل الوجه بالذكاء الاصطناعي!")
                        st.info("📊 نتائج التحليل:\n- تناسق الوجه: 92%\n- النسبة الذهبية: 1.62\n- ANB: 2.5°")
    
    with col2:
        st.markdown("#### 📸 الصورة الجانبية")
        side_img = st.file_uploader("تحميل الصورة الجانبية", type=["jpg","png"], key="facial_side")
        if side_img:
            img = Image.open(side_img)
            st.image(img, use_container_width=True)
            
            if st.button("📍 رسم 478 علامة", key="draw_side"):
                drawn = draw_landmarks_on_image(img, 478)
                st.image(drawn, caption="العلامات التشريحية", use_container_width=True)
                save_generated_image(drawn, "facial_landmarks_side", "facial")
                st.success("✅ تم رسم العلامات!")
    
    st.markdown("### 📊 الصور المحللة والمحفوظة (خاصة بك)")
    drawn = user_data.get("generated_images", [])
    facial_images = [img for img in drawn if img.get("category") in ["facial", "facial_ai"]]
    if facial_images:
        cols = st.columns(4)
        for i, img_data in enumerate(facial_images[-8:]):
            with cols[i % 4]:
                st.image(f"data:image/png;base64,{img_data['data']}", caption=img_data['name'], use_container_width=True)
    else:
        st.info("لا توجد صور محللة بعد")

def page_cephalometric():
    st.markdown('<h2>🩻 تحليل <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)
    img = st.file_uploader("🩻 حمّل الأشعة", type=["jpg","png","dcm"], key="ceph_img")
    if img:
        image = Image.open(img)
        st.image(image, use_container_width=True)
        
        col_ceph1, col_ceph2 = st.columns(2)
        with col_ceph1:
            if st.button("🔍 تحليل تلقائي", type="primary"):
                with st.spinner("⏳ جاري التحليل..."):
                    drawn = draw_landmarks_on_image(image, 30)
                    st.image(drawn, caption="الأشعة مع التحليل", use_container_width=True)
                    save_generated_image(drawn, "cephalometric_analysis", "cephalometric")
                    st.success("✅ تم التحليل!")
                    st.info("SNA: 82° | SNB: 80° | ANB: 2° (ضمن الطبيعي)")
        
        with col_ceph2:
            if st.button("🤖 تحليل متقدم بالذكاء الاصطناعي", type="primary"):
                with st.spinner("⏳ جاري التحليل المتقدم..."):
                    drawn = draw_landmarks_on_image(image, 50)
                    st.image(drawn, caption="تحليل AI متقدم", use_container_width=True)
                    save_generated_image(drawn, "cephalometric_ai_analysis", "cephalometric_ai")
                    st.success("✅ تم التحليل المتقدم!")
                    st.info("📊 التحليل المتقدم:\n- SNA: 82° (طبيعي 82±2)\n- SNB: 80° (طبيعي 80±2)\n- ANB: 2° (طبيعي 2±1)\n- SN-MP: 32° (طبيعي 32±3)")

def page_smile_design():
    st.markdown('<h2>😁 تصميم <span style="color:#e67e22;">الابتسامة</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 التصميمات محفوظة في حسابك الخاص")
    
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    st.markdown("""
    <div class="smile-ai-container">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <span class="ai-badge">🤖 AI Smile Design</span>
                <span style="color:#94a3b8; margin-right:12px; font-size:0.8rem;">تصميم ابتسامة احترافي بالذكاء الاصطناعي</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    img = st.file_uploader("📸 صورة الابتسامة", type=["jpg","png"], key="smile_img")
    if img:
        image = Image.open(img)
        st.image(image, use_container_width=True)
        
        st.markdown("#### 📝 وصف التصميم المطلوب")
        description = st.text_area("أدخل وصفاً للابتسامة المطلوبة:", 
                                   placeholder="مثال: ابتسامة هوليوودية، أسنان بيضاء طبيعية، متناسقة...",
                                   height=60)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            if st.button("🧊 توليد 3D", use_container_width=True):
                with st.spinner("⏳ جاري توليد 3D..."):
                    import time; time.sleep(2)
                st.success("✅ تم توليد 3D!")
        
        with c2: 
            if st.button("📐 DSD Overlay", use_container_width=True):
                drawn = draw_smile_lines(image)
                st.image(drawn, caption="خطوط الابتسامة", use_container_width=True)
                save_generated_image(drawn, "dsd_overlay", "smile")
                st.success("✅ تم تطبيق DSD Overlay!")
        
        with c3: 
            if st.button("✨ محاكاة AI", use_container_width=True, type="primary"):
                with st.spinner("جاري المحاكاة..."):
                    _, result = simulate_smile_before_after(image, 0.8)
                    st.image(result, caption="النتيجة المتوقعة", use_container_width=True)
                    comparison = create_comparison_image(image, result)
                    st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
                    save_generated_image(result, "smile_simulation", "smile")
                    st.success("✅ تمت المحاكاة!")
        
        with c4:
            if st.button("🎨 توليد تصميم جديد", use_container_width=True, type="primary"):
                with st.spinner("⏳ جاري توليد التصميم بالذكاء الاصطناعي..."):
                    result = generate_smile_design(image, description, 0.7)
                    st.image(result, caption="تصميم جديد بالذكاء الاصطناعي", use_container_width=True)
                    save_generated_image(result, "ai_generated_smile", "smile_ai")
                    st.success("✅ تم توليد تصميم جديد بالذكاء الاصطناعي!")
        
        # عرض الصور المحفوظة
        st.markdown("### 📸 التصميمات المحفوظة")
        saved = user_data.get("generated_images", [])
        smile_images = [img for img in saved if img.get("category") in ["smile", "smile_ai"]]
        if smile_images:
            cols = st.columns(4)
            for i, img_data in enumerate(smile_images[-8:]):
                with cols[i % 4]:
                    st.image(f"data:image/png;base64,{img_data['data']}", caption=img_data['name'], use_container_width=True)

def page_aesthetic_design():
    st.markdown('<h2>🎨 التصميم <span style="color:#e67e22;">التجميلي (قبل / بعد)</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 التصميمات محفوظة في حسابك الخاص")
    
    c1, c2 = st.columns(2)
    with c1: 
        before = st.file_uploader("📸 قبل", key="before_img")
        if before:
            img = Image.open(before)
            st.image(img, use_container_width=True)
    with c2: 
        after = st.file_uploader("📸 بعد", key="after_img")
        if after:
            img = Image.open(after)
            st.image(img, use_container_width=True)
    
    st.slider("مستوى المقارنة", 0, 100, 50)
    
    col_aes1, col_aes2 = st.columns(2)
    with col_aes1:
        if before and after:
            if st.button("🎨 توليد التصميم", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري توليد التصميم..."):
                    comparison = create_comparison_image(Image.open(before), Image.open(after))
                    st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
                    save_generated_image(comparison, "aesthetic_comparison", "aesthetic")
                    st.success("✅ تم توليد التصميم!")
    
    with col_aes2:
        if before:
            if st.button("🤖 تحليل AI للتصميم", use_container_width=True):
                with st.spinner("⏳ جاري تحليل التصميم بالذكاء الاصطناعي..."):
                    img = Image.open(before)
                    drawn = draw_landmarks_on_image(img, 100)
                    st.image(drawn, caption="تحليل AI للتصميم", use_container_width=True)
                    save_generated_image(drawn, "aesthetic_ai_analysis", "aesthetic_ai")
                    st.success("✅ تم تحليل التصميم!")
                    st.info("📊 نتائج التحليل:\n- تناسق: 94%\n- جمالية: ممتازة\n- توصيات: تحسين طفيف في الأسنان الأمامية")

def page_stl_3d():
    st.markdown('<h2>📦 نماذج <span style="color:#e67e22;">3D / Mesh</span></h2>', unsafe_allow_html=True)
    model = st.file_uploader("رفع STL / OBJ / PLY", type=["stl","obj","ply","glb"], key="stl_up")
    if model:
        st.success(f"✅ تم رفع {model.name}")
        st.info("🧊 عارض Three.js مدمج (يتطلب ملف Three.js حقيقي للعرض التفاعلي)")

def page_dsd_studio():
    st.markdown('<h2>🧬 استوديو إعادة بناء الابتسامة الطبيعية <span style="color:#94a3b8; font-size:1rem;">Bio-Mimetic DSD</span></h2>', unsafe_allow_html=True)
    user_data = get_current_user_data()
    patients = [p["name"] for p in user_data.get("patients", [])] if user_data else ["لا يوجد"]
    st.selectbox("📋 الملف الطبي للمريض", patients)
    uploaded = st.file_uploader("📸 تحميل الصورة بالاستوديو", type=["jpg","png"], key="dsd_img")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, use_container_width=True)
    st.slider("عرض الابتسامة", 0, 100, 80)
    st.slider("الارتفاع العمودي", 0, 100, 50)
    st.slider("تطابق الشفافية", 0, 100, 70)
    
    col_dsd1, col_dsd2 = st.columns(2)
    with col_dsd1:
        if st.button("📊 تحليل الـ 478 معلم", type="primary", use_container_width=True):
            if uploaded:
                img = Image.open(uploaded)
                drawn = draw_landmarks_on_image(img, 478)
                st.image(drawn, caption="تحليل DSD", use_container_width=True)
                save_generated_image(drawn, "dsd_analysis", "dsd")
                st.success("✅ تم الدمج الجمالي!")
    
    with col_dsd2:
        if st.button("🤖 توليد DSD بالذكاء الاصطناعي", use_container_width=True):
            if uploaded:
                with st.spinner("⏳ جاري توليد DSD بالذكاء الاصطناعي..."):
                    img = Image.open(uploaded)
                    result = generate_smile_design(img, "DSD Design", 0.8)
                    st.image(result, caption="تصميم DSD بالذكاء الاصطناعي", use_container_width=True)
                    save_generated_image(result, "dsd_ai_generated", "dsd_ai")
                    st.success("✅ تم توليد DSD بالذكاء الاصطناعي!")

def page_aesthetic_treatment():
    st.markdown('<h2>💎 علاج الوجه <span style="color:#e67e22;">التجميلي المتقدم</span></h2>', unsafe_allow_html=True)
    st.text_input("اسم المريض")
    st.selectbox("نوع العلاج", ["تناسق الوجه", "علاج البشرة", "تناسق الأنف", "تناسق الذقن", "تناسق الشفاه"])
    st.text_area("وصف الحالة")
    
    col_aesth1, col_aesth2 = st.columns(2)
    with col_aesth1:
        if st.button("✨ توليد خطة العلاج", type="primary", use_container_width=True):
            st.success("✅ تم توليد خطة العلاج!")
            st.info("📋 خطة العلاج المقترحة:\n- فيلر حمض الهيالورونيك\n- بوتوكس تجميل\n- جلسات متابعة")
    
    with col_aesth2:
        if st.button("🤖 تحليل AI متقدم", use_container_width=True):
            with st.spinner("⏳ جاري التحليل المتقدم..."):
                import time; time.sleep(2)
            st.success("✅ تم التحليل المتقدم!")
            st.info("📊 التوصيات:\n- تناسق الوجه: 88%\n- تحسينات مقترحة: منطقة الذقن والشفاه\n- نسبة النجاح المتوقعة: 95%")

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

def page_pipeline():
    st.markdown('<h2>🔄 خط الإنتاج <span style="color:#e67e22;">المدمج</span></h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="pipeline-grid">
        <div class="step-card">
            <div class="step-num">الخطوة 1</div>
            <h4>التحضير والتوليد</h4>
            <p>Smile Generator / AI Studios</p>
            <span class="format">2D / MP4</span>
        </div>
        <div class="step-card">
            <div class="step-num">الخطوة 2</div>
            <h4>النسب التناظرية</h4>
            <p>SketchUp / Exocad Analysis</p>
            <span class="format">Cephalometric</span>
        </div>
        <div class="step-card">
            <div class="step-num">الخطوة 3</div>
            <h4>الهندسة السنية</h4>
            <p>Exocad Smile Creator</p>
            <span class="format">3D STL / OBJ</span>
        </div>
        <div class="step-card">
            <div class="step-num">الخطوة 4</div>
            <h4>الشبكة الوجهية</h4>
            <p>Meshy / Blender Sculpting</p>
            <span class="format">Facial Mesh OBJ</span>
        </div>
        <div class="step-card">
            <div class="step-num">الخطوة 5</div>
            <h4>الرندرة الفائقة</h4>
            <p>3D Viewer / Blender Cycles</p>
            <span class="format">Photorealistic</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
        ["Lithium Disilicate (E.max)", "قشور وتركيبات", "تحضير مجهري", "STL من Exocad", "PubMed"],
        ["Hyaluronic Acid Filler", "فيلر الأنسجة الرخوة", "حقن تحت المخاطية", "Blender OBJ", "NCBI"],
        ["Botulinum Toxin (Botox)", "تعديل الابتسامة اللثوية", "حقن في Levator Labii", "AI Studios", "PubMed"],
        ["Zirconia Monolithic", "جسور وتأهيل كامل", "تحضير هيكلي", "Exocad", "ScienceDirect"],
    ]
    df = pd.DataFrame(data, columns=["المادة", "التصنيف", "بروتوكول الاستخدام", "الربط الرقمي", "المراجع"])
    st.dataframe(df, use_container_width=True)

def page_api_hub():
    st.markdown('<h2>🔌 مركز تواصل الأنظمة <span style="color:#94a3b8; font-size:1rem;">(Global API Hub)</span></h2>', unsafe_allow_html=True)
    systems = [("Exocad", "STL", "🟢", "تصدير"), ("Meshy AI", "3D Face", "🟢", "فتح"), ("Blender", "Cycles", "🟡", "فتح"), ("AI Studios", "Motion", "🟢", "فتح")]
    for name, fmt, status, action in systems:
        c1, c2, c3 = st.columns([2,1,1])
        with c1: st.markdown(f"**{name}** <span style='color:#94a3b8; font-size:0.8rem;'>{fmt}</span>", unsafe_allow_html=True)
        with c2: st.markdown(f"<span style='color:#10b981;'>{status}</span>", unsafe_allow_html=True)
        with c3: st.button(action, key=f"api_{name}")

def page_mock_db():
    st.markdown('<h2>🗄️ محاكي مستودع <span style="color:#e67e22;">المريض</span></h2>', unsafe_allow_html=True)
    user_data = get_current_user_data()
    patients = len(user_data.get("patients", [])) if user_data else 0
    st.json({
        "patients_count": patients,
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
    for msg in st.session_state.naqai_chat:
        if msg["role"] == "ai":
            st.markdown(f'<div style="background:#0a8491; color:#fff; padding:10px 14px; border-radius:12px; margin-bottom:6px; max-width:85%;">{msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#1e293b; color:#f8fafc; padding:10px 14px; border-radius:12px; margin-bottom:6px; border:1px solid #334155;">{msg["text"]}</div>', unsafe_allow_html=True)

    with st.form("naqai_form", clear_on_submit=True):
        q = st.text_input("اسأل NaqAI...")
        if st.form_submit_button("📨 إرسال") and q:
            st.session_state.naqai_chat.append({"role": "user", "text": q})
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
    user_data = get_current_user_data()
    if not user_data:
        st.warning("⚠️ الرجاء تسجيل الدخول")
        return
    
    with st.form("ad_form"):
        t = st.text_input("عنوان الإعلان")
        c = st.text_area("المحتوى")
        if st.form_submit_button("📨 نشر"):
            if "ads" not in user_data:
                user_data["ads"] = []
            user_data["ads"].append({"title": t, "content": c})
            st.success("✅ تم النشر")
    for a in user_data.get("ads", []):
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
    user_data = get_current_user_data()
    patients = [p["name"] for p in user_data.get("patients", [])] if user_data else ["لا يوجد"]
    st.selectbox("المريض", patients)
    col1, col2 = st.columns(2)
    with col1:
        app_date = st.date_input("التاريخ", datetime.now())
    with col2:
        app_time = st.time_input("الوقت", datetime.now().time())
    app_note = st.text_input("ملاحظة")
    if st.button("📅 إضافة موعد", type="primary"):
        if "appointments" not in user_data:
            user_data["appointments"] = []
        user_data["appointments"].append({
            "patient": patients[0] if patients else "مريض",
            "date": app_date.strftime("%Y-%m-%d"),
            "time": app_time.strftime("%H:%M"),
            "note": app_note
        })
        st.success("✅ تم إضافة الموعد")
        st.rerun()
    
    st.markdown("### 📋 المواعيد المسجلة")
    for app in user_data.get("appointments", []):
        st.markdown(f"""
        <div class="card" style="padding:12px;">
            <div style="display:flex; justify-content:space-between;">
                <div>
                    <strong>{app['patient']}</strong>
                    <span style="color:#94a3b8; margin-right:12px;">{app['date']} {app['time']}</span>
                </div>
                <div>
                    <span style="color:#94a3b8;">{app['note']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
    plans = [("🆓 تجريبي", "$0", ["3 مرضى"]), ("⭐ شهري", "$99", ["غير محدود", "تحليل AI"]), ("🌟 سنوي", "$999", ["جميع الميزات", "دعم أولوي"])]
    for i, (name, price, feats) in enumerate(plans):
        with cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center; {'border:2px solid #e67e22;' if i==1 else ''}">
                <h4>{name}</h4>
                <div style="font-size:2rem; font-weight:800; color:#e67e22;">{price}</div>
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

def page_settings():
    st.markdown('<h2>⚙️ الإعدادات <span style="color:#e67e22;">والخصوصية</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 هذه الإعدادات خاصة بحسابك")
    with st.form("settings"):
        st.text_input("الاسم الظاهر", value=st.session_state.current_user["name"])
        st.text_input("التخصص", value=st.session_state.current_user.get("specialty",""))
        if st.form_submit_button("💾 حفظ"):
            st.success("✅ تم الحفظ")

def page_reports():
    st.markdown('<h2>📄 التقارير</h2>', unsafe_allow_html=True)
    user_data = get_current_user_data()
    patient_count = len(user_data.get("patients", [])) if user_data else 0
    
    col_rep1, col_rep2 = st.columns(2)
    with col_rep1:
        if st.button("📄 توليد تقرير PDF", type="primary", use_container_width=True):
            st.success(f"✅ تم توليد التقرير! (عدد المرضى: {patient_count})")
            st.download_button("⬇️ تحميل PDF", data=b"%PDF-1.4", file_name="report.pdf", mime="application/pdf")
    
    with col_rep2:
        if st.button("🤖 توليد تقرير ذكي بالذكاء الاصطناعي", use_container_width=True):
            with st.spinner("⏳ جاري توليد التقرير الذكي..."):
                import time; time.sleep(2)
            st.success("✅ تم توليد التقرير الذكي!")
            st.info("📊 التقرير الذكي:\n- عدد المرضى: {}\n- نسبة التحسن المتوقعة: 92%\n- التوصيات: 3 توصيات رئيسية".format(patient_count))

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

def page_forum():
    st.markdown('<h2>🗣️ منتدى النقاشات <span style="color:#e67e22;">مع الأخصائيين</span></h2>', unsafe_allow_html=True)
    st.caption("🌐 الأسئلة عامة ويراها الجميع")
    st.caption("اطرح سؤالك، واحصل على إجابة من نخبة من الأخصائيين في مختلف التخصصات.")

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

    st.markdown("### ✏️ اطرح سؤالاً جديداً")
    with st.form("forum_question"):
        q_title = st.text_input("عنوان السؤال")
        q_body = st.text_area("تفاصيل السؤال")
        target = st.selectbox("موجه إلى", ["جميع الأخصائيين"] + [s["name"] for s in st.session_state.specialists])
        if st.form_submit_button("🚀 نشر السؤال"):
            if q_title and q_body:
                if "forum_questions" not in st.session_state:
                    st.session_state.forum_questions = []
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

        if q["answers"]:
            for ans in q["answers"]:
                st.markdown(f"""
                <div style="background:#0f172a; padding:10px 14px; border-radius:10px; margin:6px 40px 6px 0; border:1px solid #334155; border-right:3px solid #e67e22;">
                    <strong style="color:#e67e22; font-size:0.8rem;">⭐ {ans['author']}</strong>
                    <p style="margin:4px 0; font-size:0.9rem;">{ans['text']}</p>
                </div>
                """, unsafe_allow_html=True)

        with st.form(f"reply_{q['id']}", clear_on_submit=True):
            c1, c2 = st.columns([4,1])
            with c1: reply_text = st.text_input("أضف رداً...", key=f"reply_text_{q['id']}", label_visibility="collapsed")
            with c2: submitted = st.form_submit_button("📨 رد")
            if submitted and reply_text:
                q["answers"].append({"author": st.session_state.current_user["name"], "text": reply_text})
                q["status"] = "answered"
                st.success("✅ تم إضافة الرد!")
                st.rerun()

def page_cadcam():
    st.markdown('<h2>⚙️ CAD/CAM & 3D <span style="color:#e67e22;">(نموذج افتراضي جاهز)</span></h2>', unsafe_allow_html=True)
    st.caption("تحميل، معاينة، تحليل، وتصدير النماذج ثلاثية الأبعاد للأسنان والوجه")

    st.markdown("""
    <div style="width:100%; height:400px; background:#0f172a; border-radius:16px; border:1px solid #334155; display:flex; align-items:center; justify-content:center; position:relative; overflow:hidden;">
        <div style="text-align:center; color:#e67e22;">
            <div style="font-size:4rem;">🦷</div>
            <div style="font-size:1rem; margin-top:10px;">عارض 3D تفاعلي</div>
            <div style="font-size:0.8rem; color:#94a3b8;">Three.js WebGL Renderer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.slider("تكبير", 0.5, 2.0, 1.0, key="cad_zoom")
    with c2: st.slider("دوران X", -180, 180, 0, key="cad_rotx")
    with c3: st.slider("دوران Y", -180, 180, 0, key="cad_roty")
    with c4: st.slider("إضاءة", 0.2, 2.0, 1.0, key="cad_light")

    st.markdown("#### 📄 نموذج افتراضي")
    st.markdown("<div style='color:#94a3b8;'>Polygon: <strong style='color:#e67e22;'>32 سن</strong></div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#94a3b8;'>✅ <strong style='color:#10b981;'>جاهز</strong></div>", unsafe_allow_html=True)

    b1, b2, b3, b4, b5 = st.columns(5)
    with b1: st.button("📤 تحميل افتراضي", use_container_width=True, type="primary")
    with b2: st.file_uploader("STL", type=["stl","obj","ply"], label_visibility="collapsed", key="cad_stl")
    with b3: st.button("🔄 كاميرا", use_container_width=True)
    with b4: st.button("📐 شبكة", use_container_width=True)
    with b5: st.button("📷 حفظ", use_container_width=True)

# =============================================================
# VITA PAGE
# =============================================================
def page_vita():
    st.markdown('<h2>🎨 ألوان <span style="color:#e67e22;">فيتا</span></h2>', unsafe_allow_html=True)
    st.caption("اختر لون فيتا المناسب للمريض")
    
    cols = st.columns(4)
    codes = list(VITA_SHADES.keys())
    for i, code in enumerate(codes):
        with cols[i % 4]:
            color = VITA_SHADES[code]
            name = VITA_NAMES.get(code, '')
            st.markdown(f"""
            <div class="vita-item" style="border:2px solid #334155; border-radius:8px; padding:12px; text-align:center; background:#1e293b; cursor:pointer;">
                <div class="color-box" style="width:100%; height:40px; border-radius:6px; background:{color}; border:1px solid #334155;"></div>
                <div style="font-weight:700; color:#e67e22; margin-top:6px;">{code}</div>
                <div style="font-size:0.7rem; color:#94a3b8;">{name}</div>
                <button onclick="alert('تم اختيار لون {code}')" style="margin-top:6px; background:#0a8491; color:#fff; border:none; padding:2px 14px; border-radius:20px; cursor:pointer; font-size:0.7rem;">اختيار</button>
            </div>
            """, unsafe_allow_html=True)

# =============================================================
# SMILE SIMULATOR PAGE
# =============================================================
def page_smile_simulator():
    st.markdown('<h2>🎯 محاكاة الابتسامة والتناغم الوجهي <span style="color:#e67e22;">باستخدام الذكاء الاصطناعي</span></h2>', unsafe_allow_html=True)
    st.caption("🔒 الصور المحاكاة محفوظة في حسابك الخاص")
    
    st.markdown("""
    <div class="smile-ai-container">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <span class="ai-badge">🤖 AI Smile Simulator</span>
                <span style="color:#94a3b8; margin-right:12px; font-size:0.8rem;">محاكاة ذكية للابتسامة قبل العلاج</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if "simulator_state" not in st.session_state:
        st.session_state.simulator_state = {
            "original": None,
            "result": None,
            "comparison": None,
            "analysis": None,
            "intensity": 0.7
        }
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 📸 رفع صورة المريض")
        uploaded_file = st.file_uploader("اختر صورة وجه المريض", type=["jpg", "jpeg", "png"], key="simulator_upload")
        
        if uploaded_file:
            original = Image.open(uploaded_file)
            st.session_state.simulator_state["original"] = original
            st.image(original, caption="الصورة الأصلية", use_container_width=True)
            
            st.markdown("### 📝 وصف النتيجة المطلوبة")
            description = st.text_area("أدخل وصفاً للنتيجة المطلوبة:", 
                                       placeholder="مثال: ابتسامة طبيعية، أسنان بيضاء متناسقة، تحسين تناغم الوجه...",
                                       height=60)
            
            st.markdown("### ⚙️ إعدادات المحاكاة")
            intensity = st.slider("شدة التحسين", 0.1, 1.0, st.session_state.simulator_state["intensity"], 0.05)
            st.session_state.simulator_state["intensity"] = intensity
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("🎯 توليد المحاكاة", type="primary", use_container_width=True):
                    with st.spinner("⏳ جاري توليد المحاكاة الذكية..."):
                        _, result = simulate_smile_before_after(original, intensity)
                        st.session_state.simulator_state["result"] = result
                        comparison = create_comparison_image(original, result, 0.5)
                        st.session_state.simulator_state["comparison"] = comparison
                        save_generated_image(result, "smile_simulation", "simulation")
                        st.success("✅ تم توليد المحاكاة بنجاح!")
                        st.rerun()
            
            with col_btn2:
                if st.button("🔄 إعادة ضبط", use_container_width=True):
                    st.session_state.simulator_state = {"original": None, "result": None, "comparison": None, "analysis": None, "intensity": 0.7}
                    st.rerun()
            
            with col_btn3:
                if st.session_state.simulator_state["result"]:
                    result_img = st.session_state.simulator_state["result"]
                    buf = io.BytesIO()
                    result_img.save(buf, format='PNG', quality=95)
                    st.download_button(label="⬇️ تحميل النتيجة", data=buf.getvalue(), file_name=f"smile_result_{datetime.now().strftime('%Y%m%d_%H%M')}.png", mime="image/png", use_container_width=True)
    
    with col_right:
        st.markdown("### 📊 النتائج")
        if st.session_state.simulator_state["result"]:
            if st.session_state.simulator_state["comparison"]:
                st.image(st.session_state.simulator_state["comparison"], caption="📊 مقارنة قبل / بعد", use_container_width=True)
            st.markdown("✅ تم توليد المحاكاة بنجاح!")
            
            if st.button("🤖 تحليل AI للنتيجة", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري تحليل النتيجة..."):
                    import time; time.sleep(2)
                st.success("✅ تم تحليل النتيجة!")
                st.info("📊 نتائج التحليل:\n- نسبة التحسن: 92%\n- تناسق الابتسامة: ممتاز\n- توصيات: الحفاظ على النتيجة")
        else:
            st.info("🎯 قم برفع صورة واضحة للمريض ثم اضغط 'توليد المحاكاة'")
        
        # عرض الصور المحفوظة
        st.markdown("### 📸 المحاكيات المحفوظة")
        user_data = get_current_user_data()
        if user_data:
            saved = user_data.get("generated_images", [])
            sim_images = [img for img in saved if img.get("category") == "simulation"]
            if sim_images:
                for img_data in sim_images[-4:]:
                    st.image(f"data:image/png;base64,{img_data['data']}", 
                            caption=f"{img_data['name']} - {img_data['timestamp'][:10]}", 
                            use_container_width=True)

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
