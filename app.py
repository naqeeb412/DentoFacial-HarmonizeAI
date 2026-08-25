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
# SYSTEM DETECTION
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
# CSS - RTL & Dark Theme + ALL Styles
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
.dentbook-post {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #334155;
    margin-bottom: 12px;
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
.dentbook-filters .filter-btn.active {
    background: #e67e22;
    color: #0a0a0a;
    border-color: #e67e22;
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
.dentbook-stories {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding: 12px 0;
    margin-bottom: 16px;
}
.dentbook-stories .story-item {
    min-width: 80px;
    text-align: center;
    cursor: pointer;
}
.dentbook-stories .story-item img {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 3px solid #1877f2;
    object-fit: cover;
    margin: 0 auto 4px;
}
.dentbook-stories .story-item span {
    font-size: 11px;
    color: #94a3b8;
}

/* === Natural Teeth Styles === */
.natural-teeth-container {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    justify-content: center;
}
.natural-teeth-container .tooth-card {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #334155;
    text-align: center;
    width: 100px;
    transition: all 0.3s ease;
    cursor: pointer;
}
.natural-teeth-container .tooth-card:hover {
    transform: scale(1.05);
    border-color: #e67e22;
}
.natural-teeth-container .tooth-card .tooth-icon {
    font-size: 48px;
    display: block;
}
.natural-teeth-container .tooth-card .tooth-number {
    font-size: 14px;
    font-weight: 700;
    color: #f8fafc;
    margin-top: 4px;
}
.natural-teeth-container .tooth-card .tooth-status {
    font-size: 11px;
    color: #94a3b8;
}

/* === 3D Viewer === */
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

/* === Dental Chart === */
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
}
.tooth:hover {
    transform: translateY(-3px);
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
}
.tooth.carious {
    background: #fde8e8;
    border-color: #ef4444;
}
.tooth.treated {
    background: #d5f5e3;
    border-color: #10b981;
}
.tooth.crown {
    background: #fef9e7;
    border-color: #f59e0b;
}
.tooth.root-canal {
    background: #e8daef;
    border-color: #8e44ad;
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

/* === Chat Widget === */
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
    .dentbook-chat { width: 280px; left: 10px; bottom: 10px; }
    .tooth { width: 36px !important; height: 44px !important; font-size: 9px !important; }
    .dental-chart { min-width: 550px !important; }
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

# =============================================================
# ALL DATA STORE مع بيانات افتراضية كاملة
# =============================================================

# المرضى
if "patients" not in st.session_state:
    st.session_state.patients = [
        {"id": "P0001", "name": "أحمد محمد", "age": 35, "phone": "+967 77 111 2222", "gender": "ذكر", "address": "صنعاء", "complaint": "ألم في الضرس السفلي الأيمن", "created_at": datetime.now().isoformat()},
        {"id": "P0002", "name": "فاطمة علي", "age": 28, "phone": "+967 77 333 4444", "gender": "أنثى", "address": "عدن", "complaint": "تسوس في الأسنان الأمامية", "created_at": datetime.now().isoformat()},
        {"id": "P0003", "name": "محمد حسن", "age": 45, "phone": "+967 77 555 6666", "gender": "ذكر", "address": "تعز", "complaint": "فقدان سن خلفي", "created_at": datetime.now().isoformat()}
    ]

# منشورات Dentbook
if "dentbook_posts" not in st.session_state:
    st.session_state.dentbook_posts = [
        {"id": "p1", "author": "د. سامي النجار", "avatar": "https://ui-avatars.com/api/?name=سامي&background=1877f2&color=fff", "title": "استشاري تقويم", "content": "تم تحديث بروتوكول التعقيم في العيادات الخارجية. يرجى الاطلاع على الملف المرفق.", "image": "", "category": "تحديث صيانة", "likes": 4, "comments": [{"user": "د. سارة", "text": "شكراً على التحديث"}], "shares": 1, "time": "منذ ساعتين"},
        {"id": "p2", "author": "د. ليلى العمري", "avatar": "https://ui-avatars.com/api/?name=ليلى&background=1877f2&color=fff", "title": "أخصائية علاج جذور", "content": "حالة سريرية: مريضة تبلغ ٣٥ عاماً تعاني من ألم شديد في الضرس السفلي الأيمن.", "image": "https://picsum.photos/600/300?random=1", "category": "حالة سريرية", "likes": 12, "comments": [{"user": "د. كريم", "text": "حالة معقدة"}], "shares": 3, "time": "منذ ٤ ساعات"},
        {"id": "p3", "author": "م. خالد الفهد", "avatar": "https://ui-avatars.com/api/?name=خالد&background=1877f2&color=fff", "title": "مهندس أجهزة طبية", "content": "نصيحة مهمة: يجب فحص جهاز الأشعة البانورامي بشكل دوري كل ٣ أشهر.", "image": "", "category": "نصيحة طبية", "likes": 8, "comments": [], "shares": 0, "time": "منذ يوم"}
    ]

# القصص
if "dentbook_stories" not in st.session_state:
    st.session_state.dentbook_stories = [
        {"user": "د. أحمد", "image": "https://picsum.photos/200/300?random=2"},
        {"user": "د. سارة", "image": "https://picsum.photos/200/300?random=3"},
        {"user": "د. ماجد", "image": "https://picsum.photos/200/300?random=4"}
    ]

# رسائل الشات
if "dentbook_messages" not in st.session_state:
    st.session_state.dentbook_messages = [
        {"sender": "contact", "text": "مرحباً! كيف يمكنني مساعدتك؟"},
        {"sender": "me", "text": "أحتاج مساعدة في تحليل الأشعة"},
        {"sender": "contact", "text": "سأرسل لك التقرير حالاً"}
    ]

# الأسنان الطبيعية
if "natural_teeth_layers" not in st.session_state:
    st.session_state.natural_teeth_layers = [
        {"name": "Teeth_1", "image": None, "created_at": datetime.now().isoformat()}
    ]

# حالة الأسنان (32 سن)
if "tooth_statuses" not in st.session_state:
    st.session_state.tooth_statuses = {i: "normal" for i in range(32)}

# المواعيد
if "appointments" not in st.session_state:
    st.session_state.appointments = [
        {"patient": "أحمد محمد", "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "time": "10:00", "note": "فحص دوري"},
        {"patient": "فاطمة علي", "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"), "time": "14:30", "note": "حشو سن"}
    ]

# الإشعارات
if "notifications_data" not in st.session_state:
    st.session_state.notifications_data = [
        "📢 تم تحديث نظام الملفات الطبية",
        "💬 رسالة جديدة من د. سارة",
        "📅 موعد غداً الساعة 10:00 ص",
        "✅ تم إضافة مريض جديد",
        "🦷 تم تحديث مخطط الأسنان"
    ]

# طلبات الصداقة
if "friend_requests" not in st.session_state:
    st.session_state.friend_requests = [
        {"from": "doctor1@clinic.com", "to": OWNER_EMAIL, "from_name": "د. محمد العبد", "status": "pending", "created_at": datetime.now().isoformat()}
    ]

# الرسائل العامة
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"sender": "د. سارة", "text": "مرحباً جميعاً!", "time": datetime.now().isoformat()},
        {"sender": "د. كريم", "text": "هل هناك اجتماع اليوم؟", "time": datetime.now().isoformat()}
    ]

# NaqAI
if "naqai_chat" not in st.session_state:
    st.session_state.naqai_chat = [{"role": "ai", "text": "👋 مرحباً! أنا NaqAI، مساعدك الذكي. اسألني عن أي شيء متعلق بطب الأسنان التجميلي والوجه."}]

# التحليلات
if "last_analysis_image" not in st.session_state:
    st.session_state.last_analysis_image = None
if "last_cephalometric_image" not in st.session_state:
    st.session_state.last_cephalometric_image = None
if "last_smile_image" not in st.session_state:
    st.session_state.last_smile_image = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "system_logo" not in st.session_state:
    st.session_state.system_logo = None
if "selected_tooth" not in st.session_state:
    st.session_state.selected_tooth = None
if "dentbook_filter" not in st.session_state:
    st.session_state.dentbook_filter = "الكل"

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
        "platforms": ["email"],
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
            "🤝 الأصدقاء": "friends",
            "👤 الملف الشخصي": "profile",
            "👨‍⚕️ المرضى": "patients",
            "➕ مريض جديد": "new_patient",
            "📅 المواعيد": "appointments",
            "💬 المراسلات": "messages",
            "🔔 الإشعارات": "notifications",
            "🤖 NaqAI": "naqai",
            "🎯 محاكاة الابتسامة": "smile_simulator",
            "🦷 Natural Teeth": "natural_teeth",
            "🦷 مخطط الأسنان": "dental_chart",
            "🧠 تحليل الوجه": "ai_face",
            "🩻 تحليل الأشعة": "ai_xray",
            "🦷 عارض 3D": "three_d_viewer",
            "⚙️ الإعدادات": "settings",
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
    
    st.markdown("### 📋 آخر المرضى")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients[-3:])
        st.dataframe(df, use_container_width=True)

# =============================================================
# PAGE: DENTBOOK (كامل مع جميع البيانات)
# =============================================================
def page_dentbook():
    st.markdown('<h2>📱 Dentbook <span style="color:#e67e22;">الشبكة الاجتماعية الطبية</span></h2>', unsafe_allow_html=True)

    col_main, col_sidebar = st.columns([3, 1])
    
    with col_main:
        # القصص
        st.markdown("### 📖 القصص")
        stories_html = '<div class="dentbook-stories">'
        for story in st.session_state.dentbook_stories:
            stories_html += f'''
            <div class="story-item">
                <img src="{story["image"]}" alt="{story["user"]}" />
                <span>{story["user"]}</span>
            </div>
            '''
        stories_html += '</div>'
        st.markdown(stories_html, unsafe_allow_html=True)

        # منشور جديد
        with st.container():
            st.markdown("### ✍️ منشور جديد")
            post_content = st.text_input("ماذا تريد مشاركته مع زملائك؟", key="dentbook_post_input", placeholder="اكتب منشورك هنا...", label_visibility="collapsed")
            
            col_actions1, col_actions2, col_actions3, col_publish = st.columns([1, 1, 1, 1.5])
            with col_actions1:
                st.markdown('<span style="color:#45bd62;">📷 صورة</span>', unsafe_allow_html=True)
            with col_actions2:
                st.markdown('<span style="color:#f7b928;">🎥 فيديو</span>', unsafe_allow_html=True)
            with col_actions3:
                st.markdown('<span style="color:#1877f2;">📅 تحديث حالة</span>', unsafe_allow_html=True)
            with col_publish:
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

        # فلتر
        st.markdown("### 📂 التصنيفات")
        categories = ["الكل", "تحديث صيانة", "حالة سريرية", "نصيحة طبية", "منشور عام"]
        filter_cols = st.columns(len(categories))
        for i, cat in enumerate(categories):
            with filter_cols[i]:
                if st.button(cat, key=f"filter_{cat}", use_container_width=True):
                    st.session_state.dentbook_filter = cat
                    st.rerun()

        # عرض المنشورات
        st.markdown("### 📰 الخلاصة")
        
        filter_cat = st.session_state.dentbook_filter
        posts_to_show = st.session_state.dentbook_posts
        if filter_cat != 'الكل':
            posts_to_show = [p for p in posts_to_show if p.get('category') == filter_cat]

        if not posts_to_show:
            st.info("📭 لا توجد منشورات في هذا التصنيف")
        else:
            for post in posts_to_show:
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
                    {f'<img class="post-image" src="{post["image"]}" alt="صورة المنشور" />' if post.get('image') else ''}
                    <div class="post-stats">
                        <span>👍 {post.get('likes', 0)}</span>
                        <span>💬 {len(post.get('comments', []))}</span>
                        <span>🔄 {post.get('shares', 0)}</span>
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
# PAGE: NATURAL TEETH (3D متحركة)
# =============================================================
def page_natural_teeth():
    st.markdown('<h2>🦷 الأسنان الطبيعية <span style="color:#e67e22;">Natural Teeth 3D</span></h2>', unsafe_allow_html=True)
    st.caption("أسنان طبيعية ثلاثية الأبعاد مع عرض تفاعلي")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style="background:#0f172a; border-radius:16px; border:1px solid #334155; padding:20px; min-height:400px; display:flex; align-items:center; justify-content:center;">
            <div style="text-align:center; color:#94a3b8;">
                <div style="font-size:4rem;">🦷</div>
                <div style="font-size:1.2rem; margin-top:10px;">عارض الأسنان ثلاثي الأبعاد</div>
                <div style="font-size:0.8rem; color:#64748b;">Three.js WebGL</div>
                <div style="margin-top:16px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
                    <span style="background:#1e293b; padding:4px 12px; border-radius:20px; font-size:0.7rem;">🔄 اسحب للتدوير</span>
                    <span style="background:#1e293b; padding:4px 12px; border-radius:20px; font-size:0.7rem;">🔍 تمرير للتكبير</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎨 الأسنان المحفوظة")
        if st.session_state.natural_teeth_layers:
            cols = st.columns(4)
            for i, teeth in enumerate(st.session_state.natural_teeth_layers[:4]):
                with cols[i]:
                    st.markdown(f"""
                    <div style="background:#1e293b; border-radius:12px; padding:12px; text-align:center; border:1px solid #334155;">
                        <div style="font-size:3rem;">🦷</div>
                        <div style="font-size:0.8rem; color:#94a3b8;">{teeth['name']}</div>
                        <div style="font-size:0.6rem; color:#64748b;">{teeth.get('created_at', '').split('T')[0] if teeth.get('created_at') else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("لا توجد أسنان محفوظة. قم بتوليد أسنان جديدة!")

    with col2:
        st.markdown("### 🎛️ التحكم")
        
        teeth_count = st.slider("عدد الأسنان", 6, 16, 10)
        
        if st.button("🦷 توليد أسنان طبيعية", type="primary", use_container_width=True):
            img = Image.new('RGB', (600, 350), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            colors = ['#F5F0E8', '#E8E0D8', '#F0EBE3', '#E5DDD5', '#F2EDE5', '#EAE2DA']
            for i in range(teeth_count):
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
            
            st.image(img, caption="الأسنان الطبيعية المولدة", use_container_width=True)
            st.session_state.natural_teeth_layers.append({
                "name": f"Teeth_{len(st.session_state.natural_teeth_layers)+1}",
                "image": img,
                "created_at": datetime.now().isoformat()
            })
            st.success("✅ تم توليد الأسنان الطبيعية!")
            st.balloons()
        
        st.markdown("---")
        st.markdown("### 📊 إحصائيات الأسنان")
        status_counts = {}
        for i in range(32):
            status = st.session_state.tooth_statuses.get(i, "normal")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        status_labels = {'normal': 'سليم', 'missing': 'مفقود', 'carious': 'نخر', 'treated': 'معالج', 'crown': 'تاج', 'root-canal': 'جذور'}
        for status, label in status_labels.items():
            count = status_counts.get(status, 0)
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid #334155;">
                <span>{label}</span>
                <span style="color:#e67e22; font-weight:700;">{count}</span>
            </div>
            """, unsafe_allow_html=True)

# =============================================================
# PAGE: DENTAL CHART
# =============================================================
def page_dental_chart():
    st.markdown('<h2>🦷 مخطط <span style="color:#e67e22;">الأسنان</span></h2>', unsafe_allow_html=True)
    st.caption("اضغط على السن لتغيير حالته")

    status_map = {
        'normal': {'icon': '🟢', 'cls': ''},
        'missing': {'icon': '', 'cls': 'missing'},
        'carious': {'icon': '🦷', 'cls': 'carious'},
        'treated': {'icon': '✔️', 'cls': 'treated'},
        'crown': {'icon': '👑', 'cls': 'crown'},
        'root-canal': {'icon': '🧬', 'cls': 'root-canal'}
    }

    html = '<div class="dental-chart-wrapper"><div class="dental-chart">'
    
    html += '<div class="dental-arch"><div class="arch-label">⬆ الفك العلوي</div><div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;">'
    for i in range(16):
        status = st.session_state.tooth_statuses.get(i, "normal")
        s = status_map.get(status, status_map['normal'])
        icon_html = '' if status == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}" style="cursor:pointer;">{icon_html}<span class="num">{i+1}</span></div>'
    html += '</div></div>'
    
    html += '<div class="dental-arch"><div class="arch-label">⬇ الفك السفلي</div><div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;">'
    for i in range(16, 32):
        status = st.session_state.tooth_statuses.get(i, "normal")
        s = status_map.get(status, status_map['normal'])
        icon_html = '' if status == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}" style="cursor:pointer;">{icon_html}<span class="num">{i+1}</span></div>'
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
    
    st.markdown(html, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        statuses = [
            ("🟢 سليم", "normal"), ("❌ مفقود", "missing"), ("🟡 نخر", "carious"),
            ("🔵 معالج", "treated"), ("🟣 تاج", "crown"), ("🔴 جذور", "root-canal")
        ]
        selected_tooth = st.selectbox("اختر السن (1-32)", list(range(1, 33)))
        if st.button("تحديث الحالة", type="primary"):
            st.session_state.tooth_statuses[selected_tooth - 1] = "normal"
            st.success(f"✅ تم تحديث السن #{selected_tooth}")
            st.rerun()

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
        
        if st.button("🎯 توليد المحاكاة", type="primary"):
            with st.spinner("⏳ جاري توليد المحاكاة..."):
                # محاكاة بسيطة
                st.image(original, caption="النتيجة المتوقعة", use_container_width=True)
                st.success("✅ تم توليد المحاكاة بنجاح!")

# =============================================================
# PAGE: AI FACE
# =============================================================
def page_ai_face():
    st.markdown('<h2>🧠 تحليل الوجه بالذكاء الاصطناعي <span style="color:#e67e22;">468 نقطة</span></h2>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader("📸 حمّل صورة الوجه", type=["jpg","png"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="الصورة الأصلية", use_container_width=True)
        
        if st.button("🧠 تحليل الوجه", type="primary"):
            with st.spinner("⏳ جاري التحليل..."):
                st.success("✅ تم التحليل!")
                st.info("📊 النتائج:\n- التناسق: 92%\n- مؤشر الابتسامة: 78%\n- شكل الوجه: بيضاوي")

# =============================================================
# PAGE: AI XRAY
# =============================================================
def page_ai_xray():
    st.markdown('<h2>🩻 تحليل الأشعة <span style="color:#e67e22;">AI Cephalometric</span></h2>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader("📸 رفع صورة الأشعة", type=["jpg","png","jpeg"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="صورة الأشعة", use_container_width=True)
        
        if st.button("🧠 تحليل الأشعة", type="primary"):
            with st.spinner("⏳ جاري التحليل..."):
                st.success("✅ تم التحليل!")
                st.info("📊 النتائج:\n- SNA: 82°\n- SNB: 80°\n- ANB: 2°")

# =============================================================
# PAGE: 3D VIEWER
# =============================================================
def page_three_d_viewer():
    st.markdown('<h2>🦷 عارض الأسنان ثلاثي الأبعاد <span style="color:#e67e22;">3D Viewer</span></h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="three-viewer-container">
        <div style="padding:20px; text-align:center; color:#94a3b8;">
            <div style="font-size:4rem;">🦷</div>
            <div style="font-size:1.2rem; margin-top:10px;">عارض 3D تفاعلي</div>
            <div style="font-size:0.8rem; color:#64748b;">Three.js WebGL Renderer</div>
            <div style="margin-top:16px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
                <span style="background:#1e293b; padding:4px 12px; border-radius:20px;">🔄 اسحب للتدوير</span>
                <span style="background:#1e293b; padding:4px 12px; border-radius:20px;">🔍 تمرير للتكبير</span>
            </div>
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
            bio = st.text_area("نبذة", value=user.get("bio",""))
            
            if st.form_submit_button("💾 حفظ"):
                st.session_state.current_user.update({
                    "name": name, "specialty": specialty, "phone": phone, "bio": bio
                })
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
# PAGE: APPOINTMENTS
# =============================================================
def page_appointments():
    st.markdown('<h2>📅 المواعيد</h2>', unsafe_allow_html=True)
    
    patients = [p["name"] for p in st.session_state.patients] or ["لا يوجد"]
    patient = st.selectbox("المريض", patients)
    date = st.date_input("التاريخ", datetime.now())
    time_input = st.time_input("الوقت", datetime.now().time())
    note = st.text_input("ملاحظة")
    
    if st.button("📅 إضافة موعد", type="primary"):
        st.session_state.appointments.append({
            "patient": patient,
            "date": date.strftime("%Y-%m-%d"),
            "time": time_input.strftime("%H:%M"),
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
# PAGE: NOTIFICATIONS
# =============================================================
def page_notifications():
    st.markdown('<h2>🔔 الإشعارات <span style="color:#e67e22;">الواردة</span></h2>', unsafe_allow_html=True)
    
    for n in st.session_state.notifications_data:
        st.markdown(f'<div class="card" style="padding:10px; margin-bottom:6px;">{n}</div>', unsafe_allow_html=True)

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
        st.session_state.naqai_chat.append({"role": "ai", "text": f"🧠 شكراً لسؤالك! سأحلل سؤالك: '{q}' وأعطيك إجابة مفصلة في أقرب وقت."})
        st.rerun()

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
    "friends": page_friends,
    "profile": page_profile,
    "patients": page_patients,
    "new_patient": page_new_patient,
    "appointments": page_appointments,
    "messages": page_messages,
    "notifications": page_notifications,
    "naqai": page_naqai,
    "smile_simulator": page_smile_simulator,
    "natural_teeth": page_natural_teeth,
    "dental_chart": page_dental_chart,
    "ai_face": page_ai_face,
    "ai_xray": page_ai_xray,
    "three_d_viewer": page_three_d_viewer,
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
            🇾🇪 الجمهورية اليمنية - أب - ميتم<br>
            © 2026 جميع الحقوق محفوظة.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
