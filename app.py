import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import base64
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import hashlib
import random
import time
import requests
import os
import sys

# =============================================================
# 🔑 مفتاح API - يتم إدخاله عبر الواجهة (آمن)
# =============================================================
# لا تضع المفتاح هنا! استخدم الإعدادات في الشريط الجانبي

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
# CSS - RTL & Dark Theme + Dentbook Styles
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
.privacy-badge {
    display: inline-block;
    background: rgba(16,185,129,0.12);
    color: #10b981;
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
}
.card {
    background: #1e293b;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #334155;
    margin-bottom: 16px;
}

/* === Dentbook Styles === */
.dentbook-container {
    max-width: 1200px;
    margin: 0 auto;
}
.dentbook-stories {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding: 12px 0;
    margin-bottom: 16px;
    scrollbar-width: thin;
}
.dentbook-story {
    min-width: 80px;
    text-align: center;
    cursor: pointer;
    transition: transform 0.2s;
}
.dentbook-story:hover {
    transform: scale(1.05);
}
.dentbook-story .story-avatar {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 3px solid #1877f2;
    object-fit: cover;
    margin: 0 auto 4px;
}
.dentbook-story .story-name {
    font-size: 11px;
    color: #94a3b8;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.dentbook-create-post {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #334155;
    margin-bottom: 16px;
}
.dentbook-create-post .post-input-area {
    display: flex;
    gap: 12px;
    align-items: center;
}
.dentbook-create-post .post-input-area img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
}
.dentbook-create-post .post-input-area input {
    flex: 1;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 10px 16px;
    color: #f8fafc;
    outline: none;
    font-size: 14px;
}
.dentbook-create-post .post-input-area input::placeholder {
    color: #64748b;
}
.dentbook-create-post .post-actions-bar {
    display: flex;
    gap: 16px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #334155;
    flex-wrap: wrap;
}
.dentbook-create-post .post-actions-bar span {
    color: #94a3b8;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 6px;
    transition: background 0.2s;
}
.dentbook-create-post .post-actions-bar span:hover {
    background: #334155;
}
.dentbook-create-post .post-actions-bar .publish-btn {
    background: #1877f2;
    color: #fff;
    border: none;
    padding: 6px 20px;
    border-radius: 20px;
    font-weight: 600;
    cursor: pointer;
    margin-right: auto;
    transition: background 0.2s;
}
.dentbook-create-post .post-actions-bar .publish-btn:hover {
    background: #166fe5;
}
.dentbook-filters {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 16px;
}
.dentbook-filters .filter-btn {
    padding: 6px 16px;
    border-radius: 20px;
    border: 1px solid #334155;
    background: #1e293b;
    color: #94a3b8;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
}
.dentbook-filters .filter-btn:hover {
    border-color: #e67e22;
    color: #f8fafc;
}
.dentbook-filters .filter-btn.active {
    background: #e67e22;
    color: #0a0a0a;
    border-color: #e67e22;
}
.dentbook-post {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #334155;
    margin-bottom: 12px;
    transition: box-shadow 0.2s;
}
.dentbook-post:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.dentbook-post .post-header {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 10px;
}
.dentbook-post .post-header img {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    object-fit: cover;
}
.dentbook-post .post-header .post-author {
    flex: 1;
}
.dentbook-post .post-header .post-author h4 {
    margin: 0;
    font-size: 15px;
    color: #f8fafc;
}
.dentbook-post .post-header .post-author .post-meta {
    font-size: 12px;
    color: #94a3b8;
}
.dentbook-post .post-header .post-author .post-category {
    display: inline-block;
    background: rgba(230,126,34,0.15);
    color: #e67e22;
    padding: 0 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
}
.dentbook-post .post-content {
    color: #e2e8f0;
    font-size: 15px;
    line-height: 1.6;
    margin: 8px 0 12px;
}
.dentbook-post .post-image {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
    border-radius: 8px;
    margin: 8px 0 12px;
}
.dentbook-post .post-stats {
    display: flex;
    gap: 20px;
    color: #94a3b8;
    font-size: 13px;
    border-bottom: 1px solid #334155;
    padding-bottom: 10px;
    margin-bottom: 10px;
}
.dentbook-post .post-actions {
    display: flex;
    justify-content: space-around;
}
.dentbook-post .post-actions button {
    background: none;
    border: none;
    color: #94a3b8;
    padding: 6px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: background 0.2s;
}
.dentbook-post .post-actions button:hover {
    background: #334155;
}
.dentbook-post .post-actions .liked {
    color: #1877f2;
}
.dentbook-comments {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #334155;
}
.dentbook-comments .comment-item {
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
}
.dentbook-comments .comment-item img {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    object-fit: cover;
}
.dentbook-comments .comment-item .comment-body {
    background: #0f172a;
    padding: 6px 12px;
    border-radius: 16px;
    flex: 1;
    color: #e2e8f0;
    font-size: 14px;
}
.dentbook-comments .comment-item .comment-body strong {
    color: #f8fafc;
    margin-left: 6px;
}
.dentbook-comments .comment-input-area {
    display: flex;
    gap: 8px;
    margin-top: 8px;
}
.dentbook-comments .comment-input-area input {
    flex: 1;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 6px 14px;
    color: #f8fafc;
    outline: none;
    font-size: 14px;
}
.dentbook-comments .comment-input-area button {
    background: #1877f2;
    color: #fff;
    border: none;
    padding: 6px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 600;
}
.dentbook-sidebar {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #334155;
}
.dentbook-sidebar .sidebar-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    color: #94a3b8;
    cursor: pointer;
    transition: color 0.2s;
    border-bottom: 1px solid #334155;
}
.dentbook-sidebar .sidebar-item:last-child {
    border-bottom: none;
}
.dentbook-sidebar .sidebar-item:hover {
    color: #f8fafc;
}
.dentbook-sidebar .sidebar-item img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
}
.dentbook-sidebar .sidebar-item .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    margin-right: auto;
}
.dentbook-story-viewer {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.95);
    z-index: 9999;
    display: none;
    align-items: center;
    justify-content: center;
}
.dentbook-story-viewer.show {
    display: flex;
}
.dentbook-story-viewer .story-content {
    max-width: 400px;
    width: 90%;
    position: relative;
}
.dentbook-story-viewer .story-content img {
    width: 100%;
    border-radius: 12px;
    max-height: 80vh;
    object-fit: cover;
}
.dentbook-story-viewer .story-content .progress-bar {
    height: 4px;
    background: rgba(255,255,255,0.3);
    border-radius: 4px;
    margin-bottom: 12px;
    overflow: hidden;
}
.dentbook-story-viewer .story-content .progress-bar div {
    height: 100%;
    background: #fff;
    transition: width 0.1s linear;
}
.dentbook-story-viewer .story-content .story-author {
    color: #fff;
    font-weight: bold;
    text-align: center;
    margin-top: 8px;
}
.dentbook-story-viewer .close-story {
    position: absolute;
    top: -40px;
    left: 0;
    background: none;
    border: none;
    color: #fff;
    font-size: 32px;
    cursor: pointer;
}
.dentbook-chat {
    position: fixed;
    bottom: 20px;
    left: 20px;
    width: 320px;
    background: #1e293b;
    border-radius: 16px;
    border: 1px solid #334155;
    box-shadow: 0 4px 30px rgba(0,0,0,0.5);
    z-index: 9998;
    overflow: hidden;
}
.dentbook-chat .chat-header {
    background: #1877f2;
    padding: 12px 16px;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-weight: 600;
}
.dentbook-chat .chat-header .chat-badge {
    background: #e41e3f;
    padding: 0 10px;
    border-radius: 12px;
    font-size: 12px;
    margin-right: auto;
}
.dentbook-chat .chat-body {
    max-height: 300px;
    display: none;
    flex-direction: column;
}
.dentbook-chat .chat-body.open {
    display: flex;
}
.dentbook-chat .chat-messages {
    padding: 12px 16px;
    flex: 1;
    overflow-y: auto;
    max-height: 200px;
}
.dentbook-chat .chat-messages .msg {
    margin-bottom: 8px;
    padding: 8px 12px;
    border-radius: 16px;
    max-width: 85%;
    font-size: 14px;
}
.dentbook-chat .chat-messages .msg.me {
    background: #1877f2;
    color: #fff;
    align-self: flex-end;
    margin-right: auto;
}
.dentbook-chat .chat-messages .msg.contact {
    background: #0f172a;
    color: #f8fafc;
    align-self: flex-start;
}
.dentbook-chat .chat-input-area {
    display: flex;
    padding: 8px 12px;
    border-top: 1px solid #334155;
}
.dentbook-chat .chat-input-area input {
    flex: 1;
    background: #0f172a;
    border: none;
    outline: none;
    padding: 6px 10px;
    color: #f8fafc;
    border-radius: 20px;
    font-size: 14px;
}
.dentbook-chat .chat-input-area button {
    background: #1877f2;
    border: none;
    color: #fff;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    cursor: pointer;
    margin-right: 6px;
}
@media (max-width: 768px) {
    .dentbook-chat {
        width: 280px;
        left: 10px;
        bottom: 10px;
    }
    .dentbook-story {
        min-width: 60px;
    }
    .dentbook-story .story-avatar {
        width: 48px;
        height: 48px;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================
# AI API FUNCTIONS (OpenAI) - آمن
# =============================================================
def call_ai_api(prompt, api_key):
    """استدعاء OpenAI API مع مفتاح آمن"""
    if not api_key:
        return "⚠️ يرجى إدخال مفتاح OpenAI API في الإعدادات"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "أنت مساعد طبي متخصص في طب الأسنان التجميلي وتقويم الوجه. أجب باللغة العربية."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"❌ خطأ في API: {response.status_code}"
    
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

# =============================================================
# SYSTEM LOGO FUNCTIONS
# =============================================================
def display_system_logo(width=50):
    return '<div style="background:#e67e22; width:'+str(width)+'px; height:'+str(width)+'px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; color:#0a0a0a;">🦷</div>'

# =============================================================
# AUTHENTICATION SYSTEM
# =============================================================
OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User database
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
            "friends": [],
            "pending_requests": [],
            "created_at": datetime.now().isoformat()
        }
    }

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""

# =============================================================
# DATA STORE
# =============================================================
if "patients" not in st.session_state:
    st.session_state.patients = []
if "dentbook_posts" not in st.session_state:
    st.session_state.dentbook_posts = [
        {
            "id": "p1",
            "author": "د. سامي النجار",
            "avatar": "https://ui-avatars.com/api/?name=سامي&background=1877f2&color=fff",
            "title": "استشاري تقويم",
            "content": "تم تحديث بروتوكول التعقيم في العيادات الخارجية.",
            "image": "",
            "category": "تحديث صيانة",
            "likes": 4,
            "comments": [{"user": "د. سارة", "text": "شكراً على التحديث"}],
            "shares": 1,
            "time": "منذ ساعتين"
        },
        {
            "id": "p2",
            "author": "د. ليلى العمري",
            "avatar": "https://ui-avatars.com/api/?name=ليلى&background=1877f2&color=fff",
            "title": "أخصائية علاج جذور",
            "content": "حالة سريرية: مريضة تبلغ ٣٥ عاماً تعاني من ألم شديد",
            "image": "https://picsum.photos/600/300?random=1",
            "category": "حالة سريرية",
            "likes": 12,
            "comments": [{"user": "د. كريم", "text": "حالة معقدة"}],
            "shares": 3,
            "time": "منذ ٤ ساعات"
        }
    ]
if "dentbook_stories" not in st.session_state:
    st.session_state.dentbook_stories = [
        {"user": "د. أحمد", "image": "https://picsum.photos/200/300?random=2"},
        {"user": "د. سارة", "image": "https://picsum.photos/200/300?random=3"}
    ]
if "dentbook_filter" not in st.session_state:
    st.session_state.dentbook_filter = "الكل"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "friend_requests" not in st.session_state:
    st.session_state.friend_requests = []
if "appointments" not in st.session_state:
    st.session_state.appointments = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

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
        "password": hash_pass(password) if password else "",
        "role": role,
        "specialty": specialty,
        "phone": phone,
        "country": "",
        "bio": "",
        "friends": [],
        "pending_requests": [],
        "created_at": datetime.now().isoformat()
    }
    return True, "تم إنشاء الحساب بنجاح"

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_page = "home"
    st.rerun()

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

        st.markdown("### 🔐 تسجيل الدخول")

        tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("البريد الإلكتروني", value="ndcdental2025@outlook.com")
                password = st.text_input("كلمة المرور", type="password", value="ndc2025")
                submitted = st.form_submit_button("دخول", use_container_width=True)
                if submitted:
                    if login_user(email, password):
                        st.success("✅ مرحباً بك!")
                        st.rerun()
                    else:
                        st.error("❌ بريد أو كلمة مرور غير صحيحة")

        with tab2:
            with st.form("signup_form"):
                s_name = st.text_input("الاسم الكامل")
                s_email = st.text_input("البريد الإلكتروني الجديد")
                s_pass = st.text_input("كلمة المرور", type="password")
                s_phone = st.text_input("رقم الهاتف")
                s_specialty = st.text_input("التخصص")
                s_role = st.selectbox("نوع الحساب", ["doctor", "patient"])
                s_submitted = st.form_submit_button("إنشاء حساب", use_container_width=True)
                if s_submitted:
                    ok, msg = signup_user(s_name, s_email, s_pass, s_role, s_phone, s_specialty)
                    if ok:
                        st.success(msg)
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
            <div style="font-size:0.7rem; color:#aac4d6;">HarmonizeAI™</div>
        </div>
        <div style="text-align:center; margin-bottom:16px;">
            <div style="font-size:0.85rem; font-weight:600;">{user['name']}</div>
            <div style="font-size:0.65rem; color:#aac4d6;">{user.get('specialty','') or user['role']}</div>
        </div>
        """, unsafe_allow_html=True)

        menu_items = {
            "🏠 الرئيسية": "home",
            "📊 لوحة التحكم": "dashboard",
            "📱 Dentbook": "dentbook",
            "🤖 الذكاء الاصطناعي": "ai_section",
            "🤝 الأصدقاء": "friends",
            "👤 الملف الشخصي": "profile",
            "👨‍⚕️ المرضى": "patients",
            "➕ مريض جديد": "new_patient",
            "📅 المواعيد": "appointments",
            "💬 المراسلات": "messages",
            "🔔 الإشعارات": "notifications",
            "⚙️ الإعدادات": "settings",
        }

        for label, key in menu_items.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        st.divider()
        
        # 🔑 إدخال مفتاح API بشكل آمن
        with st.expander("🔑 إعدادات API", expanded=True):
            api_key = st.text_input("مفتاح OpenAI API", type="password", value=st.session_state.openai_api_key)
            if st.button("💾 حفظ المفتاح", use_container_width=True):
                if api_key:
                    st.session_state.openai_api_key = api_key
                    st.success("✅ تم حفظ المفتاح!")
                    st.rerun()
                else:
                    st.warning("⚠️ يرجى إدخال مفتاح صحيح")
        
        # عرض حالة API
        if st.session_state.openai_api_key:
            st.markdown("""
            <div style="background: #10b981; padding: 8px 12px; border-radius: 8px; text-align: center; font-size: 0.8rem;">
                ✅ API متصل
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #ef4444; padding: 8px 12px; border-radius: 8px; text-align: center; font-size: 0.8rem;">
                ❌ API غير متصل
            </div>
            """, unsafe_allow_html=True)
        
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
        st.markdown(f'<div class="metric-card"><div>📅 المواعيد</div><div class="metric-value" style="color:#10b981;">{len(st.session_state.appointments)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div>📱 منشورات Dentbook</div><div class="metric-value" style="color:#a855f7;">{len(st.session_state.dentbook_posts)}</div></div>', unsafe_allow_html=True)

# =============================================================
# PAGE: AI SECTION
# =============================================================
def page_ai_section():
    st.markdown('<h2>🤖 الذكاء الاصطناعي <span style="color:#e67e22;">المدمج</span></h2>', unsafe_allow_html=True)
    st.caption("استخدم الذكاء الاصطناعي لتحليل الحالات وتصميم الابتسامات")

    if not st.session_state.openai_api_key:
        st.warning("⚠️ يرجى إدخال مفتاح OpenAI API في الإعدادات (الجانب الأيسر)")
    
    tab1, tab2 = st.tabs(["🔬 تحليل الحالة", "😁 تصميم الابتسامة"])
    
    with tab1:
        st.markdown("### 🔬 تحليل حالة طبية")
        symptoms = st.text_area("الأعراض والشكوى", height=100)
        
        if st.button("🔬 تحليل بالذكاء الاصطناعي", type="primary"):
            if not st.session_state.openai_api_key:
                st.error("❌ يرجى إدخال مفتاح API")
            elif symptoms:
                with st.spinner("⏳ جاري التحليل..."):
                    result = call_ai_api(f"حلل هذه الحالة: {symptoms}", st.session_state.openai_api_key)
                    st.markdown(f"""
                    <div class="card">
                        <h4>📋 نتائج التحليل</h4>
                        <div style="white-space: pre-wrap; color: #e2e8f0;">{result}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ يرجى إدخال الأعراض")
    
    with tab2:
        st.markdown("### 😁 تصميم الابتسامة بالذكاء الاصطناعي")
        design_complaint = st.text_area("الشكوى التجميلية", height=80)
        
        if st.button("🎨 توليد تصميم الابتسامة", type="primary"):
            if not st.session_state.openai_api_key:
                st.error("❌ يرجى إدخال مفتاح API")
            elif design_complaint:
                with st.spinner("⏳ جاري توليد التصميم..."):
                    result = call_ai_api(f"صمم ابتسامة لـ: {design_complaint}", st.session_state.openai_api_key)
                    st.markdown(f"""
                    <div class="card">
                        <h4>✨ تصميم الابتسامة المقترح</h4>
                        <div style="white-space: pre-wrap; color: #e2e8f0;">{result}</div>
                    </div>
                    """, unsafe_allow_html=True)

# =============================================================
# PAGE: DENTBOOK
# =============================================================
def page_dentbook():
    st.markdown('<h2>📱 Dentbook <span style="color:#e67e22;">الشبكة الاجتماعية الطبية</span></h2>', unsafe_allow_html=True)

    col_main, col_sidebar = st.columns([3, 1])
    
    with col_main:
        # قصص
        st.markdown("### 📖 القصص")
        stories_html = '<div class="dentbook-stories">'
        for story in st.session_state.dentbook_stories:
            stories_html += f'''
            <div class="dentbook-story">
                <img class="story-avatar" src="{story["image"]}" alt="{story["user"]}" />
                <div class="story-name">{story["user"]}</div>
            </div>
            '''
        stories_html += '</div>'
        st.markdown(stories_html, unsafe_allow_html=True)

        # منشور جديد
        with st.container():
            st.markdown("### ✍️ منشور جديد")
            post_content = st.text_input("ماذا تريد مشاركته؟", key="dentbook_post_input", placeholder="اكتب منشورك هنا...", label_visibility="collapsed")
            
            if st.button("🚀 نشر", key="dentbook_publish", use_container_width=True, type="primary"):
                if post_content.strip():
                    new_post = {
                        "id": f"p{len(st.session_state.dentbook_posts) + 1}",
                        "author": st.session_state.current_user["name"],
                        "avatar": "https://ui-avatars.com/api/?name=" + st.session_state.current_user["name"] + "&background=1877f2&color=fff",
                        "title": st.session_state.current_user.get("specialty", "طبيب"),
                        "content": post_content,
                        "image": "",
                        "category": "منشور عام",
                        "likes": 0,
                        "comments": [],
                        "shares": 0,
                        "time": "الآن"
                    }
                    st.session_state.dentbook_posts.insert(0, new_post)
                    st.success("✅ تم نشر المنشور!")
                    st.rerun()

        # عرض المنشورات
        st.markdown("### 📰 الخلاصة")
        for post in st.session_state.dentbook_posts[:10]:
            st.markdown(f"""
            <div class="dentbook-post">
                <div class="post-header">
                    <img src="{post.get('avatar')}" alt="{post['author']}" />
                    <div class="post-author">
                        <h4>{post['author']} <span class="post-category">{post.get('category', 'عام')}</span></h4>
                        <div class="post-meta">{post.get('title', '')} · {post.get('time', '')}</div>
                    </div>
                </div>
                <div class="post-content">{post['content']}</div>
                <div class="post-stats">
                    <span>👍 {post.get('likes', 0)}</span>
                    <span>💬 {len(post.get('comments', []))}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_sidebar:
        st.markdown("### 👥 جهات الاتصال")
        contacts = []
        for email, user in st.session_state.users_db.items():
            if email != st.session_state.current_user["email"]:
                contacts.append(user)
        
        for contact in contacts[:5]:
            st.markdown(f"""
            <div class="dentbook-sidebar">
                <div class="sidebar-item">
                    <img src="https://ui-avatars.com/api/?name={contact['name']}&background=1877f2&color=fff" alt="{contact['name']}" />
                    <div>
                        <div style="font-weight:600; color:#f8fafc; font-size:14px;">{contact['name']}</div>
                        <div style="font-size:11px; color:#94a3b8;">{contact.get('specialty', 'طبيب')}</div>
                    </div>
                    <div class="status-dot"></div>
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
        target = st.selectbox("اختر مستخدم", [f"{u['name']}" for u in all_users])
        if st.button("📨 إرسال طلب صداقة", type="primary"):
            st.success("✅ تم إرسال طلب الصداقة!")

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
            </div>
            """, unsafe_allow_html=True)
        with col2:
            name = st.text_input("الاسم", value=user.get("name",""))
            specialty = st.text_input("التخصص", value=user.get("specialty",""))
            phone = st.text_input("الهاتف", value=user.get("phone",""))
            
            if st.form_submit_button("💾 حفظ"):
                st.session_state.current_user.update({"name": name, "specialty": specialty, "phone": phone})
                st.session_state.users_db[user["email"]].update(st.session_state.current_user)
                st.success("✅ تم الحفظ!")

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
    else:
        st.info("لا يوجد مرضى مسجلين.")

# =============================================================
# PAGE: NEW PATIENT
# =============================================================
def page_new_patient():
    st.markdown('<h2>📝 إضافة <span style="color:#e67e22;">مريض جديد</span></h2>', unsafe_allow_html=True)
    
    with st.form("new_patient_form"):
        name = st.text_input("الاسم الكامل *")
        age = st.number_input("العمر", min_value=0, max_value=120, value=30)
        phone = st.text_input("رقم الهاتف")
        complaint = st.text_area("الشكوى الرئيسية")
        
        submitted = st.form_submit_button("💾 حفظ المريض", use_container_width=True)
        if submitted and name:
            st.session_state.patients.append({
                "id": f"P{len(st.session_state.patients)+1:04d}",
                "name": name,
                "age": age,
                "phone": phone,
                "complaint": complaint,
                "created_at": datetime.now().isoformat()
            })
            st.success("✅ تم إضافة المريض بنجاح!")
            st.rerun()

# =============================================================
# PAGE: APPOINTMENTS
# =============================================================
def page_appointments():
    st.markdown('<h2>📅 المواعيد</h2>', unsafe_allow_html=True)
    
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد"]
    patient = st.selectbox("المريض", patients)
    date = st.date_input("التاريخ", datetime.now())
    note = st.text_input("ملاحظة")
    
    if st.button("📅 إضافة موعد", type="primary"):
        st.session_state.appointments.append({
            "patient": patient,
            "date": date.strftime("%Y-%m-%d"),
            "note": note
        })
        st.success("✅ تم إضافة الموعد")
        st.rerun()

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
            <div style="max-width:75%; padding:8px 14px; border-radius:12px; background:{bg}; color:{color};">
                <div style="font-size:0.7rem; opacity:0.8;">{msg['sender']}</div>
                <div style="font-size:0.9rem;">{msg['text']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.form("msg_form", clear_on_submit=True):
        text = st.text_input("رسالتك...", label_visibility="collapsed")
        if st.form_submit_button("📨 إرسال", use_container_width=True) and text:
            st.session_state.messages.append({
                "sender": st.session_state.current_user["name"],
                "text": text,
                "time": datetime.now().isoformat()
            })
            st.rerun()

# =============================================================
# PAGE: NOTIFICATIONS
# =============================================================
def page_notifications():
    st.markdown('<h2>🔔 الإشعارات <span style="color:#e67e22;">الواردة</span></h2>', unsafe_allow_html=True)
    
    notifs = [
        "📢 تم تحديث خط سير المريض",
        "💬 رسالة جديدة من المختبر",
        "📅 موعد غداً الساعة 10:00 ص",
        "✅ تم إضافة مريض جديد"
    ]
    
    for n in notifs:
        st.markdown(f'<div class="card" style="padding:10px; margin-bottom:6px;">{n}</div>', unsafe_allow_html=True)

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
# PAGE ROUTER
# =============================================================
PAGES = {
    "home": page_home,
    "dashboard": page_dashboard,
    "dentbook": page_dentbook,
    "ai_section": page_ai_section,
    "friends": page_friends,
    "profile": page_profile,
    "patients": page_patients,
    "new_patient": page_new_patient,
    "appointments": page_appointments,
    "messages": page_messages,
    "notifications": page_notifications,
    "settings": page_settings,
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
            © 2026 جميع الحقوق محفوظة.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
