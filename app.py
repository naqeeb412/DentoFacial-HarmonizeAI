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
import random
import string
import time

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
def load_css():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
    }
    
    .main-header {
        text-align: center;
        padding: 40px 0;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 20px;
        margin-bottom: 30px;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #e67e22, #f39c12);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-top: 10px;
    }
    
    .metric-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #e67e22;
        margin: 10px 0;
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    
    .feature-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #334155;
        margin: 10px 0;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 15px;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 10px;
    }
    
    .feature-description {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #e67e22, #d35400);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Cairo', sans-serif;
        font-size: 1rem;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(230,126,34,0.4);
    }
    
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 5px;
    }
    
    .status-active {
        background: rgba(16,185,129,0.1);
        color: #10b981;
        border: 1px solid rgba(16,185,129,0.3);
    }
    
    .status-pending {
        background: rgba(245,158,11,0.1);
        color: #f59e0b;
        border: 1px solid rgba(245,158,11,0.3);
    }
    
    .upload-area {
        border: 2px dashed #4a5568;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        background: #1a202c;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #e67e22;
        background: #1e293b;
    }
    
    .tooth-grid {
        display: grid;
        grid-template-columns: repeat(8, 1fr);
        gap: 5px;
        padding: 10px;
        background: #1a202c;
        border-radius: 10px;
    }
    
    .tooth {
        background: #2d3748;
        border: 2px solid #4a5568;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #e2e8f0;
    }
    
    .tooth:hover {
        background: #3d4a5c;
        border-color: #e67e22;
    }
    
    .tooth.selected {
        background: #e67e22;
        border-color: #d35400;
        color: white;
    }
    
    .tooth.missing {
        background: #4a1a1a;
        border-color: #ef4444;
        opacity: 0.6;
    }
    
    .tooth.treated {
        background: #1a4a2a;
        border-color: #10b981;
    }
    </style>
    """

st.markdown(load_css(), unsafe_allow_html=True)

# =============================================================
# SESSION STATE INITIALIZATION
# =============================================================
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "users_db" not in st.session_state:
        st.session_state.users_db = {
            "demo@harmonize.ai": {
                "name": "د. علي النقيب",
                "email": "demo@harmonize.ai",
                "password": "demo123",
                "role": "owner",
                "specialty": "طب أسنان تجميلي",
                "phone": "+967 77 123 4567",
                "bio": "مؤسس منصة HarmonizeAI™",
                "created_at": datetime.now().isoformat()
            }
        }
    if "patients" not in st.session_state:
        st.session_state.patients = []
    if "dental_chart" not in st.session_state:
        st.session_state.dental_chart = ["normal"] * 32
    if "appointments" not in st.session_state:
        st.session_state.appointments = []
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "smile_results" not in st.session_state:
        st.session_state.smile_results = []
    if "cephalometric_data" not in st.session_state:
        st.session_state.cephalometric_data = {
            "SNA": 82, "SNB": 80, "ANB": 2,
            "SN-MP": 32, "FMA": 25, "IMPA": 90,
            "Overjet": 3, "Overbite": 2
        }

init_session_state()

# =============================================================
# AUTHENTICATION FUNCTIONS
# =============================================================
def login_user(email, password):
    if email in st.session_state.users_db:
        user = st.session_state.users_db[email]
        if user["password"] == password:
            st.session_state.authenticated = True
            st.session_state.current_user = user
            return True, "تم تسجيل الدخول بنجاح"
    return False, "البريد الإلكتروني أو كلمة المرور غير صحيحة"

def signup_user(name, email, password, role, specialty=""):
    if email in st.session_state.users_db:
        return False, "هذا البريد الإلكتروني مسجل بالفعل"
    
    st.session_state.users_db[email] = {
        "name": name,
        "email": email,
        "password": password,
        "role": role,
        "specialty": specialty,
        "phone": "",
        "bio": "",
        "created_at": datetime.now().isoformat()
    }
    return True, "تم إنشاء الحساب بنجاح"

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()

# =============================================================
# IMAGE PROCESSING FUNCTIONS
# =============================================================
def create_smile_simulation(image, intensity=0.7):
    """محاكاة بسيطة لتحسين الابتسامة"""
    if isinstance(image, Image.Image):
        img = image.copy()
    else:
        img = Image.open(image)
    
    # تحويل إلى RGB
    img = img.convert('RGB')
    
    # تحسين السطوع والتباين
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1 + intensity * 0.2)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1 + intensity * 0.15)
    
    # تحسين الألوان
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1 + intensity * 0.1)
    
    return img

def create_comparison_image(original, enhanced, split_position=0.5):
    """إنشاء صورة مقارنة قبل وبعد"""
    if original.size != enhanced.size:
        enhanced = enhanced.resize(original.size)
    
    w, h = original.size
    split = int(w * split_position)
    
    result = Image.new('RGB', (w, h))
    result.paste(original.crop((0, 0, split, h)), (0, 0))
    result.paste(enhanced.crop((split, 0, w, h)), (split, 0))
    
    draw = ImageDraw.Draw(result)
    draw.line([(split, 0), (split, h)], fill='#e67e22', width=3)
    
    return result

# =============================================================
# DENTAL CHART FUNCTIONS
# =============================================================
def render_dental_chart():
    teeth = st.session_state.dental_chart
    html = '<div class="tooth-grid">'
    
    for i in range(32):
        status = teeth[i] if i < len(teeth) else 'normal'
        css_class = ''
        if status == 'missing':
            css_class = 'missing'
        elif status == 'treated':
            css_class = 'treated'
        
        icon = '🦷'
        if status == 'missing':
            icon = '❌'
        elif status == 'carious':
            icon = '🔴'
        elif status == 'treated':
            icon = '✅'
        elif status == 'crown':
            icon = '👑'
        
        html += f'<div class="tooth {css_class}" data-index="{i}">{icon}<br><small>{i+1}</small></div>'
    
    html += '</div>'
    return html

# =============================================================
# PAGE: HOME
# =============================================================
def page_home():
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🦷 HarmonizeAI™</h1>
        <p class="subtitle">منصة Dentofacial Synergy المتكاملة لطب الأسنان الرقمي</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">478</div>
            <div class="metric-label">نقطة قياس وجهي</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">32</div>
            <div class="metric-label">سن قابل للتتبع</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">3D</div>
            <div class="metric-label">تحويل ثلاثي الأبعاد</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        patients_count = len(st.session_state.patients)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{patients_count}</div>
            <div class="metric-label">مريض مسجل</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Features
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## المميزات الرئيسية")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">😊</div>
            <div class="feature-title">محاكي الابتسامة</div>
            <div class="feature-description">
                تقنية متقدمة لمحاكاة تحسين الابتسامة باستخدام الذكاء الاصطناعي
                وتحليل 478 نقطة وجهية
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🦷</div>
            <div class="feature-title">المخطط السني التفاعلي</div>
            <div class="feature-description">
                مخطط سني تفاعلي كامل لتتبع حالة كل سن
                مع إمكانية تحديث الحالة في الوقت الفعلي
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📐</div>
            <div class="feature-title">التحليل السيفالومتري</div>
            <div class="feature-description">
                تحليل دقيق لقياسات الرأس والأسنان
                مع مقارنة تلقائية بالقيم الطبيعية
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================
# PAGE: AUTH
# =============================================================
def page_auth():
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🔐 تسجيل الدخول</h1>
        <p class="subtitle">مرحباً بك في منصة HarmonizeAI™</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("البريد الإلكتروني")
                password = st.text_input("كلمة المرور", type="password")
                submit = st.form_submit_button("تسجيل الدخول", use_container_width=True)
                
                if submit:
                    success, message = login_user(email, password)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
            
            st.markdown("---")
            st.info("💡 للتجربة: demo@harmonize.ai / demo123")
        
        with tab2:
            with st.form("signup_form"):
                name = st.text_input("الاسم الكامل")
                email = st.text_input("البريد الإلكتروني", key="signup_email")
                password = st.text_input("كلمة المرور", type="password", key="signup_password")
                confirm_password = st.text_input("تأكيد كلمة المرور", type="password")
                
                col1, col2 = st.columns(2)
                with col1:
                    role = st.selectbox("نوع الحساب", ["doctor", "patient"])
                with col2:
                    specialty = st.text_input("التخصص (اختياري)")
                
                submit = st.form_submit_button("إنشاء الحساب", use_container_width=True)
                
                if submit:
                    if password != confirm_password:
                        st.error("كلمات المرور غير متطابقة")
                    elif len(password) < 6:
                        st.error("كلمة المرور يجب أن تكون 6 أحرف على الأقل")
                    else:
                        success, message = signup_user(name, email, password, role, specialty)
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)

# =============================================================
# PAGE: SMILE SIMULATOR
# =============================================================
def page_smile_simulator():
    st.markdown('<h2>😊 محاكي الابتسامة</h2>', unsafe_allow_html=True)
    st.caption("ارفع صورة الوجه لتجربة تحسين الابتسامة")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "ارفع صورة الوجه",
            type=['jpg', 'jpeg', 'png'],
            key="smile_upload"
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="الصورة الأصلية", use_container_width=True)
            
            intensity = st.slider(
                "شدة التحسين",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1
            )
            
            if st.button("تحسين الابتسامة", type="primary", use_container_width=True):
                with st.spinner("جاري المعالجة..."):
                    enhanced = create_smile_simulation(image, intensity)
                    comparison = create_comparison_image(image, enhanced)
                    
                    st.session_state.smile_results.append({
                        "original": image,
                        "enhanced": enhanced,
                        "comparison": comparison,
                        "timestamp": datetime.now()
                    })
                    
                    st.success("تم تحسين الابتسامة بنجاح!")
    
    with col2:
        st.markdown("### النتائج")
        
        if st.session_state.smile_results:
            latest = st.session_state.smile_results[-1]
            
            st.image(latest["comparison"], caption="مقارنة قبل وبعد", use_container_width=True)
            
            st.markdown("### السجل")
            for i, result in enumerate(st.session_state.smile_results):
                with st.expander(f"نتيجة {i+1} - {result['timestamp'].strftime('%H:%M:%S')}"):
                    st.image(result["comparison"], use_container_width=True)
        else:
            st.info("لم يتم إجراء أي تحسينات بعد")

# =============================================================
# PAGE: DENTAL CHART
# =============================================================
def page_dental_chart():
    st.markdown('<h2>🦷 المخطط السني التفاعلي</h2>', unsafe_allow_html=True)
    st.caption("اضغط على السن لتغيير حالته")
    
    # Render dental chart
    st.markdown(render_dental_chart(), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### تحديث حالة السن")
        
        tooth_number = st.number_input("رقم السن (1-32)", min_value=1, max_value=32, value=1)
        
        status_options = {
            "سليم": "normal",
            "مفقود": "missing",
            "نخر": "carious",
            "معالج": "treated",
            "تاج": "crown",
            "علاج جذور": "root-canal"
        }
        
        status_label = st.selectbox("الحالة", list(status_options.keys()))
        
        if st.button("تحديث الحالة", type="primary"):
            st.session_state.dental_chart[tooth_number - 1] = status_options[status_label]
            st.success(f"تم تحديث السن رقم {tooth_number}")
            st.rerun()
    
    with col2:
        st.markdown("### إحصائيات")
        
        teeth = st.session_state.dental_chart
        stats = {
            "سليم": teeth.count("normal"),
            "مفقود": teeth.count("missing"),
            "نخر": teeth.count("carious"),
            "معالج": teeth.count("treated"),
            "تاج": teeth.count("crown"),
            "علاج جذور": teeth.count("root-canal")
        }
        
        df = pd.DataFrame({
            "الحالة": list(stats.keys()),
            "العدد": list(stats.values())
        })
        
        fig = px.bar(
            df,
            x="الحالة",
            y="العدد",
            color="الحالة",
            title="توزيع حالات الأسنان"
        )
        
        st.plotly_chart(fig, use_container_width=True)

# =============================================================
# PAGE: CEPHALOMETRIC ANALYSIS
# =============================================================
def page_cephalometric():
    st.markdown('<h2>📐 التحليل السيفالومتري</h2>', unsafe_allow_html=True)
    st.caption("تحليل قياسات الرأس والأسنان")
    
    normal_values = {
        "SNA": 82, "SNB": 80, "ANB": 2,
        "SN-MP": 32, "FMA": 25, "IMPA": 90,
        "Overjet": 3, "Overbite": 2
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### إدخال القياسات")
        
        measurements = {}
        for key in normal_values.keys():
            measurements[key] = st.number_input(
                key,
                min_value=0.0,
                max_value=180.0,
                value=float(st.session_state.cephalometric_data.get(key, normal_values[key])),
                step=0.5
            )
        
        if st.button("حفظ وتحليل", type="primary"):
            st.session_state.cephalometric_data = measurements
            st.success("تم حفظ القياسات وتحليلها")
    
    with col2:
        st.markdown("### نتائج التحليل")
        
        comparison_data = []
        for key in normal_values.keys():
            current = st.session_state.cephalometric_data.get(key, normal_values[key])
            normal = normal_values[key]
            diff = current - normal
            
            if abs(diff) < 1:
                status = "✅ طبيعي"
            elif abs(diff) < 3:
                status = "⚠️ انحراف بسيط"
            else:
                status = "❌ انحراف كبير"
            
            comparison_data.append({
                "القياس": key,
                "القيمة الحالية": current,
                "القيمة الطبيعية": normal,
                "الفرق": round(diff, 1),
                "الحالة": status
            })
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
        
        # Chart
        fig = go.Figure()
        
        for row in comparison_data:
            fig.add_trace(go.Bar(
                name=row["القياس"],
                x=[row["القياس"]],
                y=[row["الفرق"]],
                text=[f"{row['الفرق']:+.1f}"],
                textposition='auto'
            ))
        
        fig.update_layout(
            title="انحرافات القياسات عن القيم الطبيعية",
            yaxis_title="الفرق",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# =============================================================
# PAGE: PATIENTS
# =============================================================
def page_patients():
    st.markdown('<h2>👥 إدارة المرضى</h2>', unsafe_allow_html=True)
    
    # Add new patient
    with st.expander("➕ إضافة مريض جديد", expanded=False):
        with st.form("add_patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("اسم المريض")
                age = st.number_input("العمر", min_value=0, max_value=120, value=30)
                phone = st.text_input("رقم الهاتف")
            
            with col2:
                gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
                email = st.text_input("البريد الإلكتروني (اختياري)")
                complaint = st.text_area("الشكوى الرئيسية")
            
            submit = st.form_submit_button("إضافة المريض", use_container_width=True)
            
            if submit:
                if name:
                    patient = {
                        "id": f"P{len(st.session_state.patients) + 1:04d}",
                        "name": name,
                        "age": age,
                        "phone": phone,
                        "gender": gender,
                        "email": email,
                        "complaint": complaint,
                        "created_at": datetime.now().isoformat()
                    }
                    st.session_state.patients.append(patient)
                    st.success(f"تم إضافة المريض {name} بنجاح")
                    st.rerun()
                else:
                    st.error("يرجى إدخال اسم المريض")
    
    # Display patients
    if st.session_state.patients:
        st.markdown("### قائمة المرضى")
        
        # Search
        search = st.text_input("🔍 بحث عن مريض", placeholder="ابحث بالاسم أو رقم الهاتف...")
        
        filtered_patients = st.session_state.patients
        if search:
            filtered_patients = [
                p for p in st.session_state.patients
                if search.lower() in p["name"].lower() or search in p["phone"]
            ]
        
        if filtered_patients:
            df = pd.DataFrame(filtered_patients)
            
            # Reorder columns
            columns_order = ["id", "name", "age", "phone", "gender", "complaint"]
            df = df[columns_order]
            
            # Rename columns
            df.columns = ["ID", "الاسم", "العمر", "الهاتف", "الجنس", "الشكوى"]
            
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            st.markdown("### إحصائيات")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("إجمالي المرضى", len(st.session_state.patients))
            
            with col2:
                males = len([p for p in st.session_state.patients if p["gender"] == "ذكر"])
                st.metric("الذكور", males)
            
            with col3:
                females = len([p for p in st.session_state.patients if p["gender"] == "أنثى"])
                st.metric("الإناث", females)
        else:
            st.info("لا توجد نتائج مطابقة للبحث")
    else:
        st.info("لا يوجد مرضى مسجلين بعد")

# =============================================================
# SIDEBAR
# =============================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🦷 HarmonizeAI™")
        st.markdown("---")
        
        if st.session_state.authenticated and st.session_state.current_user:
            # User info
            st.markdown(f"### مرحباً، {st.session_state.current_user['name']}")
            if st.session_state.current_user.get('specialty'):
                st.caption(f"*{st.session_state.current_user['specialty']}*")
            
            st.markdown("---")
            
            # Navigation
            st.markdown("### 📋 القائمة الرئيسية")
            
            pages = {
                "🏠 الرئيسية": "home",
                "😊 محاكي الابتسامة": "smile",
                "🦷 المخطط السني": "dental",
                "📐 التحليل السيفالومتري": "ceph",
                "👥 المرضى": "patients"
            }
            
            for page_name, page_id in pages.items():
                if st.button(page_name, key=f"nav_{page_id}", use_container_width=True):
                    st.session_state.current_page = page_id
                    st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 تسجيل الخروج", use_container_width=True):
                logout()
        else:
            st.info("يرجى تسجيل الدخول للوصول إلى جميع الميزات")
            
            if st.button("🔐 تسجيل الدخول", use_container_width=True):
                st.session_state.current_page = "auth"
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 💎 الإصدار التجريبي")
        st.caption("HarmonizeAI™ v1.0.0")
        st.caption("© 2024 جميع الحقوق محفوظة")

# =============================================================
# MAIN APP
# =============================================================
def main():
    render_sidebar()
    
    # Main content
    if not st.session_state.authenticated:
        page_auth()
    else:
        current_page = st.session_state.get("current_page", "home")
        
        if current_page == "home":
            page_home()
        elif current_page == "smile":
            page_smile_simulator()
        elif current_page == "dental":
            page_dental_chart()
        elif current_page == "ceph":
            page_cephalometric()
        elif current_page == "patients":
            page_patients()
        else:
            page_home()

if __name__ == "__main__":
    main()
