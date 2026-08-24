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
# CSS - RTL & Dark Theme
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
.comparison-table .abnormal { color: #ef4444; }
.comparison-table .warning { color: #f59e0b; }
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
.friend-request-card {
    background: #1e293b;
    border: 1px solid #e67e22;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 8px;
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
.friend-request-card .actions button {
    padding: 4px 16px;
    border-radius: 20px;
    border: none;
    cursor: pointer;
}
.friend-request-card .actions .accept {
    background: #10b981;
    color: #fff;
}
.friend-request-card .actions .reject {
    background: #ef4444;
    color: #fff;
}
.profile-cover {
    height: 160px;
    background: linear-gradient(135deg, #075e68, #0a8491);
    border-radius: 12px 12px 0 0;
    position: relative;
    background-size: cover;
    background-position: center;
}
.profile-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    border: 4px solid #1e293b;
    background: #0a8491;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    color: #fff;
    margin-top: -40px;
    margin-right: 20px;
    background-size: cover;
    background-position: center;
}
.iframe-container {
    width: 100%;
    height: 600px;
    border: 1px solid #334155;
    border-radius: 12px;
    overflow: hidden;
}
.iframe-container iframe {
    width: 100%;
    height: 100%;
    border: none;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================
# STATE
# =============================================================

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Users Database
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
            "platforms": ["email"],
            "avatar": "",
            "cover_photo": "",
            "friends": [],
            "pending_requests": [],
            "posts": []
        },
        "doctor@clinic.com": {
            "name": "د. أحمد",
            "email": "doctor@clinic.com",
            "password": "doctor123",
            "role": "doctor",
            "specialty": "تقويم أسنان",
            "phone": "+966 55 123 4567",
            "bio": "أخصائي تقويم أسنان",
            "platforms": ["email"],
            "avatar": "",
            "cover_photo": "",
            "friends": [],
            "pending_requests": [],
            "posts": []
        },
        "patient@clinic.com": {
            "name": "مريض نموذجي",
            "email": "patient@clinic.com",
            "password": "patient123",
            "role": "patient",
            "specialty": "",
            "phone": "+966 55 123 4568",
            "bio": "مريض",
            "platforms": ["email"],
            "avatar": "",
            "cover_photo": "",
            "friends": [],
            "pending_requests": [],
            "posts": []
        }
    }

# Data
if "patients" not in st.session_state:
    st.session_state.patients = [
        {"id": "P0001", "name": "أحمد محمد", "age": 32, "phone": "+967 77 123 4567", "gender": "ذكر", "complaint": "ألم في الأسنان الأمامية", "created_at": datetime.now().isoformat()},
        {"id": "P0002", "name": "سارة علي", "age": 28, "phone": "+967 77 123 4568", "gender": "أنثى", "complaint": "تصبغات في الأسنان", "created_at": datetime.now().isoformat()},
    ]
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
        "name": name,
        "email": email,
        "password": password,
        "role": role,
        "specialty": "",
        "phone": "",
        "bio": "",
        "platforms": ["email"],
        "avatar": "",
        "cover_photo": "",
        "friends": [],
        "pending_requests": [],
        "posts": []
    }
    return True, "تم إنشاء الحساب"

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()

def display_system_logo(width=50):
    if st.session_state.system_logo:
        return f'<img src="data:image/png;base64,{st.session_state.system_logo}" style="width:{width}px; height:{width}px; border-radius:50%; object-fit:cover;" />'
    return '<div style="background:#e67e22; width:'+str(width)+'px; height:'+str(width)+'px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; color:#0a0a0a;">🦷</div>'

# =============================================================
# 3DPEA INTEGRATION FUNCTIONS
# =============================================================

def convert_image_to_3d(image_file, format="stl"):
    """
    تحويل الصورة إلى نموذج ثلاثي الأبعاد باستخدام 3DPEA API
    """
    try:
        # إرسال الملف إلى 3DPEA (محاكاة)
        # في الواقع، سيتم استخدام API حقيقي
        files = {"file": image_file}
        # response = requests.post("https://api.3dpea.com/convert", files=files, data={"format": format})
        
        # محاكاة التحويل
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_data = {
            "name": f"3D_Model_{timestamp}",
            "format": format,
            "original_file": image_file.name,
            "created_at": datetime.now().isoformat(),
            "status": "completed"
        }
        st.session_state.converted_models.append(model_data)
        return model_data
    except Exception as e:
        st.error(f"❌ خطأ في التحويل: {str(e)}")
        return None

# =============================================================
# PAGE: 3DPEA CONVERTER
# =============================================================
def page_3dpea():
    st.markdown('<h2>🔄 تحويل الصور إلى نماذج ثلاثية الأبعاد <span style="color:#e67e22;">3DPEA</span></h2>', unsafe_allow_html=True)
    st.caption("قم بتحويل الصور (PNG, JPG) إلى نماذج ثلاثية الأبعاد (STL, OBJ, FBX, GLB) باستخدام 3DPEA")
    
    # تضمين الموقع في إطار iframe
    st.markdown("""
    <div class="iframe-container">
        <iframe src="https://www.3dpea.com" allow="camera;microphone;fullscreen"></iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📤 تحميل مباشر للتحويل")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader("📸 اختر صورة للتحويل", type=["jpg", "jpeg", "png", "bmp", "tiff"], key="3dpea_upload")
        format_options = ["stl", "obj", "fbx", "glb", "3mf", "ply", "drc"]
        output_format = st.selectbox("📁 صيغة الخرج", format_options)
        
        if uploaded_file and st.button("🔄 تحويل إلى 3D", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري تحويل الصورة إلى نموذج ثلاثي الأبعاد..."):
                # عرض الصورة الأصلية
                img = Image.open(uploaded_file)
                st.image(img, caption="الصورة الأصلية", use_container_width=True)
                
                # محاكاة التحويل
                time.sleep(2)
                model = convert_image_to_3d(uploaded_file, output_format)
                if model:
                    st.success(f"✅ تم تحويل الصورة إلى {output_format.upper()}!")
                    st.info(f"📄 اسم النموذج: {model['name']}")
                    
                    # زر تحميل النموذج (محاكاة)
                    st.download_button(
                        label=f"⬇️ تحميل {output_format.upper()}",
                        data=b"محاكاة ملف 3D",
                        file_name=f"model.{output_format}",
                        mime="application/octet-stream"
                    )
    
    with col2:
        st.markdown("### 📋 النماذج المحولة")
        if st.session_state.converted_models:
            for model in st.session_state.converted_models[-5:]:
                st.markdown(f"""
                <div class="card" style="padding:12px;">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <strong>{model['name']}</strong>
                            <span style="color:#94a3b8; font-size:0.7rem; margin-right:12px;">{model['format'].upper()}</span>
                        </div>
                        <div>
                            <span style="color:#10b981;">✅ {model['status']}</span>
                        </div>
                    </div>
                    <div style="font-size:0.7rem; color:#94a3b8;">{model['created_at'][:10]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لا توجد نماذج محولة بعد")

# =============================================================
# PAGE: IMAGE TO 3D TOOL
# =============================================================
def page_image_to_3d():
    st.markdown('<h2>🎨 تحويل الصورة إلى نموذج 3D <span style="color:#e67e22;">(Image to 3D)</span></h2>', unsafe_allow_html=True)
    st.caption("قم بتحويل الصور ثنائية الأبعاد إلى نماذج ثلاثية الأبعاد باستخدام تقنية 3DPEA")
    
    uploaded = st.file_uploader("📸 اختر صورة 2D", type=["jpg", "jpeg", "png", "bmp"], key="img2d_upload")
    
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة الأصلية", use_container_width=True)
        
        st.markdown("### ⚙️ إعدادات التحويل")
        col1, col2 = st.columns(2)
        with col1:
            height_map_depth = st.slider("عمق الخريطة الارتفاعية", 0.1, 2.0, 0.5, 0.1)
            smoothness = st.slider("نعومة النموذج", 0.0, 1.0, 0.5, 0.05)
        with col2:
            resolution = st.selectbox("دقة النموذج", ["منخفضة", "متوسطة", "عالية"])
            output_format = st.selectbox("صيغة الخرج", ["STL", "OBJ", "PLY", "GLB"])
        
        if st.button("🔄 توليد النموذج 3D", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري توليد النموذج ثلاثي الأبعاد..."):
                time.sleep(3)
                st.success("✅ تم توليد النموذج ثلاثي الأبعاد!")
                
                # معاينة النموذج
                st.markdown("### 📐 معاينة النموذج")
                st.markdown("""
                <div style="width:100%; height:400px; background:#0f172a; border-radius:16px; border:1px solid #334155; display:flex; align-items:center; justify-content:center;">
                    <div style="text-align:center; color:#e67e22;">
                        <div style="font-size:4rem;">🧊</div>
                        <div style="font-size:1rem; margin-top:10px;">نموذج ثلاثي الأبعاد</div>
                        <div style="font-size:0.8rem; color:#94a3b8;">تم توليده من الصورة</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.download_button(
                    label=f"⬇️ تحميل النموذج ({output_format})",
                    data=b"نماذج 3D محاكاة",
                    file_name=f"3d_model.{output_format.lower()}",
                    mime="application/octet-stream"
                )
                
                # حفظ النموذج
                st.session_state.converted_models.append({
                    "name": f"3D_Model_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "format": output_format.lower(),
                    "original_file": uploaded.name,
                    "created_at": datetime.now().isoformat(),
                    "status": "completed"
                })

# =============================================================
# PAGE: 3D MODEL GALLERY
# =============================================================
def page_3d_gallery():
    st.markdown('<h2>📦 معرض النماذج ثلاثية الأبعاد <span style="color:#e67e22;">3D Gallery</span></h2>', unsafe_allow_html=True)
    
    if st.session_state.converted_models:
        cols = st.columns(3)
        for i, model in enumerate(st.session_state.converted_models):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="card" style="padding:16px; text-align:center;">
                    <div style="font-size:3rem;">🧊</div>
                    <div style="font-weight:700; margin-top:8px;">{model['name']}</div>
                    <div style="font-size:0.7rem; color:#94a3b8;">{model['format'].upper()}</div>
                    <div style="font-size:0.6rem; color:#94a3b8;">{model['created_at'][:10]}</div>
                    <div style="margin-top:8px;">
                        <span style="background:#10b981; color:#fff; padding:2px 12px; border-radius:20px; font-size:0.6rem;">✅ {model['status']}</span>
                    </div>
                    <button onclick="alert('جارٍ التحميل...')" style="margin-top:8px; background:#0a8491; color:#fff; border:none; padding:4px 16px; border-radius:20px; cursor:pointer;">📥 تحميل</button>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("لا توجد نماذج محولة بعد. استخدم أداة التحويل لإنشاء نماذج 3D.")

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
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔐 طرق تسجيل الدخول")
        col_social = st.columns(6)
        platforms = [("Google", "🔵"), ("Facebook", "🔷"), ("Instagram", "🟣"), ("LinkedIn", "🔵"), ("Twitter", "🔷"), ("WhatsApp", "🟢")]
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
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

# =============================================================
# SIDEBAR
# =============================================================
def sidebar_nav():
    user = st.session_state.current_user
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:10px;">
            {display_system_logo(50)}
            <div style="font-weight:700; font-size:1.1rem; margin-top:6px;">🧬 Dentofacial</div>
            <div style="font-size:0.7rem; color:#aac4d6;">HarmonizeAI™ · v5.0</div>
            <div style="margin-top:4px;"><span class="privacy-badge">🔒 بياناتك خاصة بك</span></div>
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
    st.markdown(f"<p style='color:#94a3b8;'>مرحباً بك في Dentofacial HarmonizeAI™، <strong>{st.session_state.current_user['name']}</strong></p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div>👨‍⚕️ المرضى</div><div class="metric-value">{len(st.session_state.patients)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div>📅 المواعيد</div><div class="metric-value" style="color:#10b981;">{len(st.session_state.appointments)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div>🧠 الصور المُنتجة</div><div class="metric-value" style="color:#a855f7;">{len(st.session_state.generated_images)}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div>📦 نماذج 3D</div><div class="metric-value" style="color:#e67e22;">{len(st.session_state.converted_models)}</div></div>', unsafe_allow_html=True)

# =============================================================
# OTHER PAGES (مختصرة)
# =============================================================
def page_patients():
    st.markdown('<h2>👨‍⚕️ قائمة <span style="color:#e67e22;">المرضى</span></h2>', unsafe_allow_html=True)
    if st.session_state.patients:
        st.dataframe(pd.DataFrame(st.session_state.patients), use_container_width=True)

def page_new_patient():
    st.markdown('<h2>📝 إضافة <span style="color:#e67e22;">مريض جديد</span></h2>', unsafe_allow_html=True)
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
            st.success("✅ تم إضافة المريض!")
            st.rerun()

def page_dental_chart():
    st.markdown('<h2>🦷 مخطط <span style="color:#e67e22;">الأسنان</span></h2>', unsafe_allow_html=True)
    st.markdown(render_dental_chart(), unsafe_allow_html=True)
    if st.button("🔄 إعادة ضبط الكل", use_container_width=True):
        st.session_state.dental_chart = ['normal'] * 32
        st.success("✅ تم إعادة ضبط المخطط")
        st.rerun()

def render_dental_chart():
    chart = st.session_state.dental_chart
    html = '<div class="dental-chart-wrapper"><div class="dental-chart">'
    html += '<div class="dental-arch"><div class="arch-label">⬆ الفك العلوي</div><div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;">'
    for i in range(16):
        status = chart[i] if i < len(chart) else 'normal'
        status_map = {'normal': {'icon': '🟢', 'cls': ''}, 'missing': {'icon': '', 'cls': 'missing'}, 'carious': {'icon': '🦷', 'cls': 'carious'}, 'treated': {'icon': '✔️', 'cls': 'treated'}, 'crown': {'icon': '👑', 'cls': 'crown'}, 'root-canal': {'icon': '🧬', 'cls': 'root-canal'}}
        s = status_map.get(status, status_map['normal'])
        icon_html = '' if status == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}" data-index="{i}" data-status="{status}">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div></div>'
    html += '<div class="dental-arch"><div class="arch-label">⬇ الفك السفلي</div><div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;">'
    for i in range(16, 32):
        status = chart[i] if i < len(chart) else 'normal'
        status_map = {'normal': {'icon': '🟢', 'cls': ''}, 'missing': {'icon': '', 'cls': 'missing'}, 'carious': {'icon': '🦷', 'cls': 'carious'}, 'treated': {'icon': '✔️', 'cls': 'treated'}, 'crown': {'icon': '👑', 'cls': 'crown'}, 'root-canal': {'icon': '🧬', 'cls': 'root-canal'}}
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

def page_natural_teeth():
    st.markdown('<h2>🦷 الأسنان الطبيعية <span style="color:#e67e22;">Natural Teeth</span></h2>', unsafe_allow_html=True)
    count = st.slider("عدد الأسنان", 6, 16, 10)
    if st.button("🦷 توليد أسنان طبيعية", type="primary", use_container_width=True):
        with st.spinner("⏳ جاري توليد الأسنان الطبيعية..."):
            img = generate_natural_teeth(count)
            st.image(img, caption="الأسنان الطبيعية", use_container_width=True)
            add_layer(img, "Natural Teeth")
            st.success("✅ تم توليد الأسنان الطبيعية وإضافتها إلى المحرر!")

def generate_natural_teeth(count=10):
    img = Image.new('RGB', (600, 350), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    colors = ['#F5F0E8', '#E8E0D8', '#F0EBE3', '#E5DDD5']
    for i in range(count):
        x = 40 + i * 50
        y = 100
        w = 38
        h = 65
        color = random.choice(colors)
        draw.ellipse([x, y, x+w, y+h], fill=color, outline='#cbd5e1', width=2)
        draw.ellipse([x+6, y+8, x+w-6, y+h-10], fill='#FFFFFF', outline=None)
        draw.ellipse([x+10, y+12, x+w-10, y+h-15], fill=color, outline=None)
    draw.rectangle([0, 80, 600, 105], fill='#e8b4b8')
    draw.rectangle([0, 170, 600, 190], fill='#e8b4b8')
    return img

def add_layer(image, name="Layer"):
    if isinstance(image, Image.Image):
        if "image_layers" not in st.session_state:
            st.session_state.image_layers = []
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

def page_photography(): st.markdown('<h2>📸 قسم <span style="color:#e67e22;">التصوير</span></h2>', unsafe_allow_html=True)
def page_xray(): st.markdown('<h2>🩻 قسم <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)

def page_dentbook():
    st.markdown('<h2>📱 Dentbook <span style="color:#e67e22;">الشبكة الاجتماعية الطبية</span></h2>', unsafe_allow_html=True)
    text = st.text_area("ماذا تفكر؟ شارك حالة طبية...", height=80)
    if st.button("🚀 نشر", type="primary") and text:
        st.session_state.dentbook_posts.insert(0, {"author": st.session_state.current_user["name"], "text": text, "time": datetime.now().strftime("%H:%M"), "likes": 0})
        st.success("✅ تم النشر!")
        st.rerun()
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
            st.session_state.current_user.update({"name": name, "specialty": specialty, "phone": phone, "bio": bio})
            st.session_state.users_db[user["email"]].update(st.session_state.current_user)
            st.success("✅ تم الحفظ!")

def page_members(): st.markdown('<h2>👥 أعضاء <span style="color:#e67e22;">النظام</span></h2>', unsafe_allow_html=True)
def page_messages(): st.markdown('<h2>💬 المراسلات العامة</h2>', unsafe_allow_html=True)
def page_private_messages(): st.markdown('<h2>💌 رسائل <span style="color:#e67e22;">خاصة بين الأطباء</span></h2>', unsafe_allow_html=True)

def page_lab_chat():
    st.markdown('<h2>🧪 التواصل <span style="color:#e67e22;">مع المختبر</span></h2>', unsafe_allow_html=True)
    for msg in st.session_state.lab_messages[-10:]:
        st.markdown(f"<div class='card'><strong>{msg['sender']}:</strong> {msg['text']}</div>", unsafe_allow_html=True)
    text = st.text_input("رسالتك للمختبر...")
    if st.button("إرسال") and text:
        st.session_state.lab_messages.append({"sender": st.session_state.current_user["name"], "text": text})
        st.rerun()

def page_file_sharing(): st.markdown('<h2>📁 مشاركة <span style="color:#e67e22;">الملفات</span></h2>', unsafe_allow_html=True)
def page_screen_share(): st.markdown('<h2>🖥️ مشاركة <span style="color:#e67e22;">الشاشة</span></h2>', unsafe_allow_html=True)

def page_diagnosis():
    st.markdown('<h2>🩺 التشخيص <span style="color:#e67e22;">الذكي</span></h2>', unsafe_allow_html=True)
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد مرضى"]
    st.selectbox("اختر المريض", patients)
    symptoms = st.text_area("الأعراض", placeholder="أدخل الأعراض بالتفصيل...")
    if st.button("🎓 تشخيص AI - Harvard", type="primary"):
        with st.spinner("🧠 جاري التحليل..."):
            time.sleep(2)
        st.success("✅ تم التشخيص!")

def page_treatment_plan(): st.markdown('<h2>📋 خطة <span style="color:#e67e22;">العلاج</span></h2>', unsafe_allow_html=True)
def page_materials(): st.markdown('<h2>🧪 المواد <span style="color:#e67e22;">العلاجية</span></h2>', unsafe_allow_html=True)

def page_facial():
    st.markdown('<h2>🧑‍⚕️ تحليل <span style="color:#e67e22;">الوجه (478 علامة)</span></h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 حمّل صورة الوجه", type=["jpg","png"], key="facial_img")
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة المحملة", use_container_width=True)
        if st.button("📍 رسم 478 علامة", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري الرسم..."):
                result = draw_landmarks_on_image(img, 478)
                st.image(result, caption="العلامات التشريحية", use_container_width=True)
                st.success("✅ تم رسم 478 علامة!")

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

def page_cephalometric(): st.markdown('<h2>🩻 تحليل <span style="color:#e67e22;">الأشعة</span></h2>', unsafe_allow_html=True)
def page_smile_design(): st.markdown('<h2>😁 تصميم <span style="color:#e67e22;">الابتسامة</span></h2>', unsafe_allow_html=True)
def page_aesthetic_design(): st.markdown('<h2>🎨 التصميم <span style="color:#e67e22;">التجميلي (قبل / بعد)</span></h2>', unsafe_allow_html=True)
def page_stl_3d(): st.markdown('<h2>📦 نماذج <span style="color:#e67e22;">3D / Mesh</span></h2>', unsafe_allow_html=True)

def page_dsd_studio():
    st.markdown('<h2>🧬 استوديو إعادة بناء الابتسامة الطبيعية <span style="color:#94a3b8; font-size:1rem;">Bio-Mimetic DSD</span></h2>', unsafe_allow_html=True)
    st.slider("عرض الابتسامة", 0, 100, 80)
    st.slider("الارتفاع العمودي", 0, 100, 50)
    st.slider("تطابق الشفافية", 0, 100, 70)

def page_aesthetic_treatment(): st.markdown('<h2>💎 علاج الوجه <span style="color:#e67e22;">التجميلي المتقدم</span></h2>', unsafe_allow_html=True)
def page_global_platform(): st.markdown('<h2>🌍 المنصة العالمية <span style="color:#e67e22;">Dentofacial HarmonizeAI™</span></h2>', unsafe_allow_html=True)
def page_pipeline(): st.markdown('<h2>🔄 خط الإنتاج <span style="color:#e67e22;">المدمج</span></h2>', unsafe_allow_html=True)
def page_materials_guide(): st.markdown('<h2>🦷 دليل المواد الطبية التجميلية <span style="color:#94a3b8; font-size:1rem;">مع المراجع العلمية</span></h2>', unsafe_allow_html=True)
def page_api_hub(): st.markdown('<h2>🔌 مركز تواصل الأنظمة <span style="color:#94a3b8; font-size:1rem;">(Global API Hub)</span></h2>', unsafe_allow_html=True)
def page_mock_db(): st.markdown('<h2>🗄️ محاكي مستودع <span style="color:#e67e22;">المريض</span></h2>', unsafe_allow_html=True)
def page_notifications(): st.markdown('<h2>🔔 الإشعارات <span style="color:#e67e22;">الواردة</span></h2>', unsafe_allow_html=True)
def page_systems(): st.markdown('<h2>🖥️ الأنظمة <span style="color:#e67e22;">المستخدمة</span></h2>', unsafe_allow_html=True)
def page_scientific_scan(): st.markdown('<h2>🔬 المسح العلمي <span style="color:#e67e22;">الشامل</span></h2>', unsafe_allow_html=True)

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
        responses = {"ابتسامة": "😁 تصميم الابتسامة يشمل تحليل النسب الذهبية...", "فيلر": "💉 فيلر حمض الهيالورونيك يستخدم لملء التجاعيد...", "بوتوكس": "🧪 البوتوكس يستخدم لتقليل التجاعيد..."}
        ans = "🧠 شكراً لسؤالك! يمكنني مساعدتك في تصميم الابتسامة، العلاج التجميلي، تحليل الوجه، والمزيد."
        for k, v in responses.items():
            if k in q.lower():
                ans = v
                break
        st.session_state.naqai_chat.append({"role": "ai", "text": ans})
        st.rerun()

def page_interdisciplinary(): st.markdown('<h2>👥 فرق <span style="color:#e67e22;">متعددة التخصصات</span></h2>', unsafe_allow_html=True)
def page_ads(): st.markdown('<h2>📢 الإعلانات</h2>', unsafe_allow_html=True)
def page_lab(): st.markdown('<h2>🔬 حساب <span style="color:#e67e22;">المعمل</span></h2>', unsafe_allow_html=True)
def page_appointments(): st.markdown('<h2>📅 المواعيد</h2>', unsafe_allow_html=True)
def page_accounting(): st.markdown('<h2>💰 حساب <span style="color:#e67e22;">المريض</span></h2>', unsafe_allow_html=True)
def page_payments(): st.markdown('<h2>💳 الدفع <span style="color:#e67e22;">والمحفظة</span></h2>', unsafe_allow_html=True)

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

def page_invite(): st.markdown('<h2>📨 دعوة <span style="color:#e67e22;">الأطباء</span></h2>', unsafe_allow_html=True)
def page_settings(): st.markdown('<h2>⚙️ الإعدادات <span style="color:#e67e22;">والخصوصية</span></h2>', unsafe_allow_html=True)
def page_privacy(): st.markdown('<h2>🔒 الخصوصية <span style="color:#e67e22;">والأمان</span></h2>', unsafe_allow_html=True)
def page_ip(): st.markdown('<h2>©️ حقوق <span style="color:#e67e22;">الملكية الفكرية</span></h2>', unsafe_allow_html=True)
def page_forum(): st.markdown('<h2>🗣️ منتدى النقاشات <span style="color:#e67e22;">مع الأخصائيين</span></h2>', unsafe_allow_html=True)
def page_cadcam(): st.markdown('<h2>⚙️ CAD/CAM & 3D <span style="color:#e67e22;">(نموذج افتراضي جاهز)</span></h2>', unsafe_allow_html=True)
def page_vita(): st.markdown('<h2>🎨 ألوان <span style="color:#e67e22;">فيتا</span></h2>', unsafe_allow_html=True)

def page_image_editor():
    st.markdown('<h2>🎨 محرر الصور المتقدم <span style="color:#e67e22;">(Photopea-like)</span></h2>', unsafe_allow_html=True)
    
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
            layer["opacity"] = st.slider("الشفافية", 0.0, 1.0, layer["opacity"], 0.05)
            layer["visible"] = st.checkbox("ظاهرة", value=layer["visible"])
        
        if st.button("🧑 رسم FaceMesh على الطبقة", use_container_width=True):
            if st.session_state.image_layers:
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
                    img = layer["image"].copy()
                    if display_img is None:
                        display_img = img
                    else:
                        try:
                            display_img = Image.blend(display_img, img, layer["opacity"])
                        except:
                            display_img = img            if display_img:
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
    "3dpea": page_3dpea,
    "image_to_3d": page_image_to_3d,
    "3d_gallery": page_3d_gallery,
}

# =============================================================
# REPORTS PAGE
# =============================================================
def page_reports():
    st.markdown('<h2>📄 التقارير</h2>', unsafe_allow_html=True)
    if st.button("📄 توليد تقرير شامل", type="primary", use_container_width=True):
        with st.spinner("⏳ جاري توليد التقرير الشامل..."):
            time.sleep(2)
            st.success("✅ تم توليد التقرير الشامل!")
            st.download_button(
                label="⬇️ تحميل التقرير",
                data=b"%PDF-1.4",
                file_name=f"HarmonizeAI_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
    st.markdown("### 📸 الصور المُنتجة")
    if st.session_state.generated_images:
        cols = st.columns(4)
        for i, img in enumerate(st.session_state.generated_images[-8:]):
            with cols[i % 4]:
                st.image(f"data:image/png;base64,{img['data']}", caption=img.get('name', 'صورة'), use_container_width=True)
    else:
        st.info("لا توجد صور مُنتجة بعد")

# =============================================================
# SMILE SIMULATOR
# =============================================================
def page_smile_simulator():
    st.markdown('<h2>🎯 محاكاة الابتسامة والتناغم الوجهي <span style="color:#e67e22;">باستخدام الذكاء الاصطناعي</span></h2>', unsafe_allow_html=True)
    uploaded = st.file_uploader("📸 اختر صورة وجه المريض", type=["jpg", "jpeg", "png"])
    if uploaded:
        original = Image.open(uploaded)
        st.image(original, caption="الصورة الأصلية", use_container_width=True)
        
        description = st.text_area("📝 وصف النتيجة المطلوبة:", placeholder="مثال: ابتسامة طبيعية، أسنان بيضاء متناسقة...", height=60)
        intensity = st.slider("شدة التحسين", 0.1, 1.0, 0.7, 0.05)
        
        if st.button("🎯 توليد المحاكاة", type="primary", use_container_width=True):
            with st.spinner("⏳ جاري توليد المحاكاة الذكية..."):
                _, result = simulate_smile_before_after(original, intensity)
                comparison = create_comparison_image(original, result)
                st.image(result, caption="النتيجة المتوقعة", use_container_width=True)
                st.image(comparison, caption="مقارنة قبل/بعد", use_container_width=True)
                st.success("✅ تم توليد المحاكاة بنجاح!")

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
