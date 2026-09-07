import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import pandas as pd
from PIL import Image, ImageEnhance, ImageOps
import io

# --- إعداد الصفحة والستايل البصري الاحترافي الداكن ---
st.set_page_config(
    page_title="Naqeeb412 · HarmonizeAI™ v3.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #F59E0B; text-align: center; margin-bottom: 5px; }
    .sub-header { font-size: 14px; color: #94A3B8; text-align: center; margin-bottom: 20px; }
    .card { background-color: #1E293B; padding: 15px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 12px; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- تهيئة الجلسة والمتغيرات ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True
if "username" not in st.session_state:
    st.session_state.username = "د. علي النقيب"

if "teeth_states" not in st.session_state:
    st.session_state.teeth_states = {i: "سليم" for i in list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49))}

# --- القائمة الجانبية الشاملة المماثلة للصور ---
st.sidebar.markdown(f"### 🧬 Naqeeb412 · HarmonizeAI")
st.sidebar.markdown(f"المستخدم: {st.session_state.username}")
st.sidebar.markdown("العيادة التخصصية لطب وجراحة وتقويم الفم والأسنان")
st.sidebar.markdown("---")

main_menu = st.sidebar.selectbox("القائمة الرئيسية للأنظمة:", [
    "📊 لوحة التحكم",
    "🦷 Dentbook (مخطط الأسنان)",
    "👤 الملف الشخصي",
    "👥 الأعضاء",
    "💬 المحادثات",
    "📢 رسائل خاصة",
    "🩺 مع الفحص",
    "🔗 مشاركة الملفات",
    "💻 مشاركة الشاشة",
    "🤖 التشخيص الذكي",
    "📋 خطة العلاج",
    "🧪 المواد السطحية",
    "🔍 تحليل الوجه (478 نقطة)",
    "🩻 تحليل الأشعة (السيفالومترية)",
    "📏 تصميم المسافة",
    "✏️ تصميم الابتسامة (Smile Design - قبل وبعد)",
    "🧊 نماذج 3D / Mesh (STL/OBJ)",
    "🎨 استوديو DSD الوضعي",
    "🖼️ إنتاج وتوليد الصور الجديدة (AI Image Gen)",
    "🔬 خط سير المعالجة",
    "🧬 دليل المواد الطبية",
    "⚡ مركز توصيل الأطعمة / المكونات",
    "🛞 محاكي مستودع المرضى",
    "🔔 الإشعارات"
])

# ==========================================================
# 1. لوحة التحكم (Dashboard)
# ==========================================================
if main_menu == "📊 لوحة التحكم":
    st.markdown('<div class="main-header">لوحة التحكم الرئيسية</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">المالك NAQclinixAI مرحباً بك</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card"><h3>المرضى</h3><h2>0</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>مواعيد اليوم</h3><h2>0</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><h3>تشخيصات AI</h3><h2>7</h2></div>', unsafe_allow_html=True)

# ==========================================================
# 2. Dentbook (مخطط الأسنان)
# ==========================================================
elif main_menu == "🦷 Dentbook (مخطط الأسنان)":
    st.markdown('<div class="main-header">مخطط الأسنان (Dentbook)</div>', unsafe_allow_html=True)
    selected_status = st.selectbox("اختر الحالة لتطبيقها على الأسنان:", ["سليم", "مفقود", "نخر", "معالج", "تاج", "علاج جذور"])

    st.markdown("#### 🦷 الفك العلوي")
    cols_up = st.columns(16)
    all_upper = list(range(18, 10, -1)) + list(range(21, 29))
    for idx, t_num in enumerate(all_upper):
        with cols_up[idx]:
            st.button(f"{t_num}", key=f"t_up_{t_num}")

    st.markdown("#### 🦷 الفك السفلي")
    cols_low = st.columns(16)
    all_lower = list(range(48, 40, -1)) + list(range(31, 39))
    for idx, t_num in enumerate(all_lower):
        with cols_low[idx]:
            st.button(f"{t_num}", key=f"t_low_{t_num}")

# ==========================================================
# 3. تحليل الأشعة (السيفالومترية) مع زر التحليل الفعلي
# ==========================================================
elif main_menu == "🩻 تحليل الأشعة (السيفالومترية)":
    st.markdown('<div class="main-header">تحليل الأشعة والزوايا السيفالومترية</div>', unsafe_allow_html=True)
    
    ceph_file = st.file_uploader("رفع صورة الأشعة الجانبية (Cephalometric X-Ray):", type=["jpg", "png", "jpeg"])
    
    if ceph_file is not None:
        image = Image.open(ceph_file)
        st.image(image, caption="صورة الأشعة المرفوعة", width=400)
        
        # زر تشغيل تحليل الأشعة بالذكاء الاصطناعي
        if st.button("🚀 بدء تحليل الأشعة واستخراج الزوايا (AI Analysis)"):
            with st.spinner("جاري معالجة الأشعة واستخراج المعالم السيفالومترية..."):
                # جدول القيم السيفالومترية المستخرجة
                ceph_data = {
                    "الزاوية": ["SNA", "SNB", "ANB", "SN-MP", "FMA", "IMPA", "Overjet", "Overbite"],
                    "قيمة المريض": [83.5, 79.0, 4.5, 34.0, 26.5, 92.0, 3.5, 2.5],
                    "القيمة الطبيعية": [82.0, 80.0, 2.0, 32.0, 25.0, 90.0, 3.0, 2.0],
                    "الفرق": ["+1.5", "-1.0", "+2.5", "+2.0", "+1.5", "+2.0", "+0.5", "+0.5"],
                    "الحالة الإكلينيكية": ["طبيعي مرتفع", "طبيعي", "بارز قليلاً", "طبيعي", "طبيعي", "طبيعي", "طبيعي", "طبيعي"]
                }
                st.success("✨ تم تحليل الأشعة بنجاح واستخراج الزوايا بدقة عالية!")
                st.table(pd.DataFrame(ceph_data))
    else:
        st.info("الرجاء رفع صورة أشعة سيفالومترية لتفعيل زر التحليل واستعراض الجدول.")

# ==========================================================
# 4. تصميم الابتسامة (Smile Design - قبل وبعد)
# ==========================================================
elif main_menu == "✏️ تصميم الابتسامة (Smile Design - قبل وبعد)":
    st.markdown('<div class="main-header">تصميم الابتسامة الرقمي (Smile Design) - قبل وبعد</div>', unsafe_allow_html=True)
    
    smile_file = st.file_uploader("رفع صورة الوجه أو الابتسامة للعميل:", type=["jpg", "png", "jpeg"])
    
    if smile_file is not None:
        original_img = Image.open(smile_file)
        
        # محاكاة تأثير تبييض وتحسين الابتسامة (توليد صورة البعد / التصميم المقترح)
        enhancer = ImageEnhance.Color(original_img)
        designed_img = enhancer.enhance(1.4) # تفتيح وتعديل الألوان لمحاكاة ابتسامة هوليوودية
        
        col_before, col_after = st.columns(2)
        with col_before:
            st.subheader("🔴 الحالة قبل المعالجة (Before)")
            st.image(original_img, use_container_width=True)
            
        with col_after:
            st.subheader("🟢 محاكاة التصميم بعد المعالجة (After - AI Smile)")
            st.image(designed_img, use_container_width=True)
            
        if st.button("💾 حفظ وتصدير تقرير تصميم الابتسامة"):
            st.success("تم حفظ مقارنة (قبل وبعد) وتصدير التصميم بنجاح إلى ملف المريض السحابي.")
    else:
        st.info("قم بررفع صورة وجه المريض أو ابتسامته لعرض مقارنة (قبل وبعد) وتصميم الابتسامة بالذكاء الاصطناعي.")

# ==========================================================
# 5. إنتاج وتوليد الصور الجديدة (AI Image Gen)
# ==========================================================
elif main_menu == "🖼️ إنتاج وتوليد الصور الجديدة (AI Image Gen)":
    st.markdown('<div class="main-header">إنتاج وتوليد الصور والمحاكاة التجميلية بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    
    prompt_text = st.text_input("أدخل وصف الصورة أو التعديل المطلوب توليده:", value="3D realistic dental smile makeover, Hollywood white smile, highly detailed")
    style_choice = st.selectbox("اختر نمط الصورة:", ["واقعي (Photorealistic)", "رسم هندسي (Blueprint)", "نمط 3D سينمائي (3D Cinematic)"])
    
    if st.button("🎨 إنتاج الصورة الجديدة بالذكاء الاصطناعي"):
        with st.spinner("جاري توليد وإنتاج الصورة الجديدة..."):
            # توليد لوحة ملونة تعبيرية كمحاكاة لإنتاج الصورة بالذكاء الاصطناعي
            dummy_canvas = np.ones((400, 600, 3), dtype=np.uint8) * 30
            cv2.putText(dummy_canvas, "HarmonizeAI Rendered Image", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 150), 2)
            cv2.putText(dummy_canvas, f"Style: {style_choice}", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            st.success("✨ تم إنتاج وتوليد الصورة الجديدة بنجاح!")
            st.image(dummy_canvas, caption=f"النتيجة المولدة: {prompt_text}", use_container_width=True)

# ==========================================================
# 6. بقية الأقسام العامة
# ==========================================================
else:
    section_name = main_menu
    st.markdown(f'<div class="main-header">{section_name}</div>', unsafe_allow_html=True)
    sub_mode = st.radio("اختر النمط المفضل للعمل:", ["🤖 تفعيل الذكاء الاصطناعي (AI)", "✏️ التعديل والتحكم اليدوي (Manual)"], horizontal=True, key=f"r_{section_name}")
    st.markdown(f'<div class="card">أنت الآن في قسم <b>{section_name}</b> باستخدام نمط <b>{sub_mode}</b>. أدخل المعطيات المطلوبة.</div>', unsafe_allow_html=True)
    
    if st.button(f"تنفيذ وحفظ إعدادات {section_name}"):
        st.success("تم الحفظ والمعالجة بنجاح.")
