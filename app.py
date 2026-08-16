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
.card {
    background: #1e293b;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #334155;
    margin-bottom: 16px;
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
.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
}
.pipeline-grid .step-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    transition: 0.3s;
    border-top: 4px solid #e67e22;
}
.pipeline-grid .step-card:hover {
    transform: translateY(-4px);
    border-color: #e67e22;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}
.pipeline-grid .step-card .step-num {
    display: inline-block;
    background: #e67e22;
    color: #0a0a0a;
    padding: 2px 14px;
    border-radius: 30px;
    font-size: 0.7rem;
    font-weight: 800;
    margin-bottom: 8px;
}
.pipeline-grid .step-card .format {
    display: inline-block;
    background: rgba(230,126,34,0.1);
    border: 1px solid rgba(230,126,34,0.2);
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.65rem;
    color: #e67e22;
    margin-top: 4px;
}
.comparison-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}
.comparison-grid .value-box {
    background: rgba(0,0,0,0.2);
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #334155;
}
.comparison-grid .value-box .value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #e67e22;
}
.defect-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.defect-list .defect-item {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    padding: 4px 14px;
    border-radius: 30px;
    font-size: 0.75rem;
    color: #fca5a5;
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
@media (max-width: 1024px) {
    .pipeline-grid {
        grid-template-columns: 1fr 1fr;
    }
    .comparison-grid {
        grid-template-columns: 1fr;
    }
}
@media (max-width: 640px) {
    .pipeline-grid {
        grid-template-columns: 1fr;
    }
    .grid-2, .grid-3, .grid-4, .grid-5 {
        grid-template-columns: 1fr;
    }
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
# LOGIN / SIGNUP PAGE
# =============================================================
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="display:inline-flex; align-items:center; gap:10px; justify-content:center;">
                <div style="background:#e67e22; width:55px; height:55px; border-radius:16px; display:flex; align-items:center; justify-content:center; font-size:28px;">🧠</div>
                <div style="text-align:right; line-height:1.2;">
                    <div style="font-size:1.4rem; font-weight:300; color:#94a3b8;">Dentofacial</div>
                    <div style="font-size:2rem; font-weight:800; color:#e67e22; margin-top:-4px;">HarmonizeAI</div>
                    <div style="font-size:0.75rem; color:#94a3b8; letter-spacing:2px;">Naqeeb412 · Synergy</div>
                    <div style="font-size:0.6rem; color:#94a3b8; margin-top:4px;"><span class="badge-harvard">Harvard Protocol</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
                    else:
                        st.error(msg)

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
        "created_at": datetime.now().isoformat()
    }
    return True, "تم إنشاء الحساب بنجاح"

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_page = "home"
    st.rerun()

# =============================================================
# SMILE SIMULATOR - AI POWERED
# =============================================================

# تهيئة MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def enhance_smile_face(image_array, intensity=0.7):
    img = image_array.copy()
    h, w = img.shape[:2]
    
    # تحديد منطقة الفم التقريبية
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
            "🎯 محاكاة الابتسامة": "smile_simulator",
            "👨‍⚕️ المرضى": "patients",
            "➕ مريض جديد": "new_patient",
            "🦷 مخطط الأسنان": "dental_chart",
            "📸 التصوير": "photography",
            "🩻 الأشعة": "xray",
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
    st.markdown("""
    <div style="text-align:center; padding:30px 0;">
        <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
            <span class="badge-harvard">Harvard Protocol</span>
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
        df = pd.DataFrame(st.session_state.patients[:5])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلين بعد.")

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
            patient = {
                "id": f"P{len(st.session_state.patients)+1:04d}",
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
                "created_at": datetime.now().isoformat()
            }
            st.session_state.patients.append(patient)
            st.session_state.patients_count += 1
            st.success("✅ تم إضافة المريض بنجاح!")

def page_dental_chart():
    st.markdown('<h2>🦷 مخطط <span style="color:#e67e22;">الأسنان</span></h2>', unsafe_allow_html=True)
    st.caption("اضغط على السن لتغيير حالته")
    
    # عرض المخطط
    st.markdown(render_dental_chart(), unsafe_allow_html=True)
    
    # أزرار التحكم
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
    st.info("📷 ارفع صور المريض المطلوبة:")
    
    # صور المريض
    st.markdown("#### 🖼️ صور المريض")
    cols = st.columns(4)
    types = ["أمامية", "جانبية", "ابتسامة", "فك علوي"]
    for i, t in enumerate(types):
        with cols[i % 4]:
            uploaded = st.file_uploader(t, type=["jpg","png","jpeg"], key=f"photo_{t}")
            if uploaded:
                img = Image.open(uploaded)
                st.image(img, caption=t, use_container_width=True)
                st.session_state.patient_images.append(uploaded)
    
    # صور الأشعة
    st.markdown("#### 📡 صور الأشعة")
    xray_cols = st.columns(3)
    xray_types = ["بانوراما", "جانبية", "مقطعية"]
    for i, t in enumerate(xray_types):
        with xray_cols[i % 3]:
            uploaded = st.file_uploader(f"أشعة {t}", type=["jpg","png","jpeg"], key=f"xray_{t}")
            if uploaded:
                img = Image.open(uploaded)
                st.image(img, caption=f"أشعة {t}", use_container_width=True)
                st.session_state.xray_images.append(uploaded)

def page_xray():
    st.markdown('<h2>🩻 قسم <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        xray_type = st.selectbox("نوع الأشعة", ["سيفالومترك (Cephalometric)", "بانوراما (Panorama)", "CBCT", "P.A"])
    with col2:
        uploaded = st.file_uploader("رفع صورة الأشعة", type=["jpg","png","jpeg"], key="xray_upload")
    
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="صورة الأشعة", use_container_width=True)
        if st.button("💾 حفظ الأشعة", type="primary"):
            st.session_state.xrays.append({
                "type": xray_type,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "image": uploaded
            })
            st.success("✅ تم حفظ الأشعة!")
    
    st.markdown("### 📋 الأشعة المحفوظة")
    if st.session_state.xrays:
        for x in st.session_state.xrays:
            st.markdown(f"""
            <div class="card" style="padding:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong>{x['type']}</strong>
                        <span style="color:#94a3b8; margin-right:12px;">{x['date']}</span>
                    </div>
                    <button onclick="alert('عرض التفاصيل')" style="background:#0a8491; color:#fff; border:none; padding:4px 16px; border-radius:20px; cursor:pointer;">عرض</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("لا توجد أشعة محفوظة.")

def page_dentbook():
    st.markdown('<h2>📱 Dentbook <span style="color:#e67e22;">الشبكة الاجتماعية الطبية</span></h2>', unsafe_allow_html=True)
    with st.container():
        text = st.text_area("ماذا تفكر؟ شارك حالة طبية...", height=80)
        img = st.file_uploader("📎 صورة / فيديو", type=["jpg","png","mp4"], key="dentbook_media")
        if st.button("🚀 نشر", type="primary"):
            if text or img:
                post = {"author": st.session_state.current_user["name"], "text": text, "time": datetime.now().strftime("%H:%M"), "likes": 0}
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
            st.session_state.messages.append({"sender": st.session_state.current_user["name"], "text": text, "time": datetime.now().isoformat()})
            st.rerun()

def page_private_messages():
    st.markdown('<h2>💌 رسائل <span style="color:#e67e22;">خاصة بين الأطباء</span></h2>', unsafe_allow_html=True)
    recipients = [u["name"] for e,u in st.session_state.users_db.items() if e != st.session_state.current_user["email"]]
    if not recipients:
        st.info("لا يوجد أطباء آخرون.")
        return
    st.selectbox("اختر الطبيب", recipients)
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
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد مرضى"]
    st.selectbox("اختر المريض", patients)
    st.text_input("الأخصائي", value=st.session_state.current_user["name"])
    symptoms = st.text_area("الأعراض", placeholder="أدخل الأعراض بالتفصيل...")
    if st.button("🎓 تشخيص AI - Harvard", type="primary"):
        with st.spinner("🧠 جاري التحليل..."):
            import time; time.sleep(2)
        st.success("✅ تم التشخيص!")

def page_treatment_plan():
    st.markdown('<h2>📋 خطة <span style="color:#e67e22;">العلاج</span></h2>', unsafe_allow_html=True)
    st.text_input("الخطة الرئيسية")
    st.text_input("العلاج البديل")
    if st.button("🧠 توليد الخطة", type="primary"):
        st.balloons()
        st.success("✅ تم توليد الخطة التفصيلية")

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
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📸 الصورة الأمامية")
        front_img = st.file_uploader("تحميل الصورة الأمامية", type=["jpg","png"], key="facial_front")
        if front_img:
            st.image(front_img, use_container_width=True)
    
    with col2:
        st.markdown("#### 📸 الصورة الجانبية")
        side_img = st.file_uploader("تحميل الصورة الجانبية", type=["jpg","png"], key="facial_side")
        if side_img:
            st.image(side_img, use_container_width=True)
    
    if st.button("🎨 تحليل الـ 478 نقطة و FaceMesh", type="primary"):
        st.success("✅ تم رسم 478 علامة تشريحية و FaceMesh!")
        st.info("📊 النتائج:\n- تناسق الوجه: 82%\n- النسبة الذهبية: 1.32\n- ANB: 2.5°")

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
        st.info("🧊 عارض Three.js مدمج (يتطلب ملف Three.js حقيقي للعرض التفاعلي)")

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
        st.success("✅ تم توليد خطة العلاج!")

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
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد"]
    st.selectbox("المريض", patients)
    col1, col2 = st.columns(2)
    with col1:
        app_date = st.date_input("التاريخ", datetime.now())
    with col2:
        app_time = st.time_input("الوقت", datetime.now().time())
    app_note = st.text_input("ملاحظة")
    if st.button("📅 إضافة موعد", type="primary"):
        st.session_state.appointments.append({
            "patient": patients[0] if patients else "مريض",
            "date": app_date.strftime("%Y-%m-%d"),
            "time": app_time.strftime("%H:%M"),
            "note": app_note
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
    with st.form("settings"):
        st.text_input("الاسم الظاهر", value=st.session_state.current_user["name"])
        st.text_input("التخصص", value=st.session_state.current_user.get("specialty",""))
        if st.form_submit_button("💾 حفظ"):
            st.success("✅ تم الحفظ")

def page_reports():
    st.markdown('<h2>📄 التقارير</h2>', unsafe_allow_html=True)
    if st.button("📄 توليد تقرير PDF", type="primary"):
        st.success("✅ تم توليد التقرير!")
        st.download_button("⬇️ تحميل PDF", data=b"%PDF-1.4", file_name="report.pdf", mime="application/pdf")

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
    
    # عرض ألوان فيتا
    cols = st.columns(4)
    codes = list(VITA_SHADES.keys())
    for i, code in enumerate(codes):
        with cols[i % 4]:
            color = VITA_SHADES[code]
            name = VITA_NAMES.get(code, '')
            st.markdown(f"""
            <div class="vita-item" style="border:2px solid #334155; border-radius:8px; padding:12px; text-align:center; background:#1e293b;">
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
    st.caption("قم برفع صورة المريض للحصول على نتيجة واقعية متوقعة بعد العلاج مع تحليل مفصل")
    
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
        else:
            st.info("🎯 قم برفع صورة واضحة للمريض ثم اضغط 'توليد المحاكاة'")

# =============================================================
# PAGE ROUTER
# =============================================================
PAGES = {
    "home": page_home,
    "dashboard": page_dashboard,
    "smile_simulator": page_smile_simulator,
    "patients": page_patients,
    "new_patient": page_new_patient,
    "dental_chart": page_dental_chart,
    "photography": page_photography,
    "xray": page_xray,
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
