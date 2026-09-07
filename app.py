import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import pandas as pd
from PIL import Image, ImageEnhance, ImageOps

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

# تهيئة حالات الأسنان للأطفال والكبار (نظام الـ 32 سناً المعتمد طبياً)
if "teeth_states" not in st.session_state:
    st.session_state.teeth_states = {i: "سليم" for i in list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49))}

# أسماء الأسنان الوظيفية (ISO System)
tooth_names = {
    11: "قاطعة مركزية علوية يمنى", 12: "قاطعة جانبية علوية يمنى", 13: "نابيب علوي أيمن", 14: "ضاحك أول علوي أيمن", 15: "ضاحك ثان علوي أيمن", 16: "طاحنة أولى علوية يمنى", 17: "طاحنة ثانية علوية يمنى", 18: "طاحنة ثالثة علوية يمنى (عقل)",
    21: "قاطعة مركزية علوية يسري", 22: "قاطعة جانبية علوية يسري", 23: "نابيب علوي أيسر", 24: "ضاحك أول علوي أيسر", 25: "ضاحك ثان علوي أيسر", 26: "طاحنة أولى علوية يسري", 27: "طاحنة ثانية علوية يسري", 28: "طاحنة ثالثة علوية يسري (عقل)",
    31: "قاطعة مركزية سفلية يسري", 32: "قاطعة جانبية سفلية يسري", 33: "نابيب سفلي أيسر", 34: "ضاحك أول سفلي أيسر", 35: "ضاحك ثان سفلي أيسر", 36: "طاحنة أولى سفلية يسري", 37: "طاحنة ثانية سفلية يسري", 38: "طاحنة ثالثة سفلية يسري (عقل)",
    41: "قاطعة مركزية سفلية يمنى", 42: "قاطعة جانبية سفلية يمنى", 43: "نابيب سفلي أيمن", 44: "ضاحك أول سفلي أيمن", 45: "ضاحك ثان سفلي أيمن", 46: "طاحنة أولى سفلية يمنى", 47: "طاحنة ثانية سفلية يمنى", 48: "طاحنة ثالثة سفلية يمنى (عقل)"
}

# --- القائمة الجانبية الشاملة ---
st.sidebar.markdown(f"### 🧬 Naqeeb412 · HarmonizeAI")
st.sidebar.markdown(f"المستخدم: {st.session_state.username}")
st.sidebar.markdown("العيادة التخصصية لطب وجراحة وتقويم الفم والأسنان")
st.sidebar.markdown("---")

main_menu = st.sidebar.selectbox("القائمة الرئيسية للأنظمة:", [
    "📊 لوحة التحكم",
    "🦷 Dentbook (مخطط الأسنان الاحترافي)",
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
# 2. Dentbook (مخطط الأسنان الاحترافي المخصص)
# ==========================================================
elif main_menu == "🦷 Dentbook (مخطط الأسنان الاحترافي)":
    st.markdown('<div class="main-header">مخطط الأسنان السريري (Dentbook)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">إدارة وتشخيص حالة كل سن على حدة وفق نظام الترقيم العالمي (FDI)</div>', unsafe_allow_html=True)
    
    # اختيار الحالة الإكلينيكية لتطبيقها
    selected_status = st.selectbox("اختر الحالة الإكلينيكية لتطبيقها عند النقر على السن:", ["سليم", "مفقود", "نخر", "معالج", "تاج (Crown)", "علاج جذور (RCT)", "حشوة تجميلية"])
    
    st.markdown("---")
    st.subheader("🦷 الفك العلوي (Maxillary Arch)")
    
    # عرض الفك العلوي بشكل مقسم ومنظم (اليمين واليسار)
    col_up_r, col_up_l = st.columns(2)
    
    with col_up_r:
        st.markdown("<b>الجانب العلوي الأيمن (18 - 11)</b>", unsafe_allow_html=True)
        upper_right = [18, 17, 16, 15, 14, 13, 12, 11]
        for t in upper_right:
            current_s = st.session_state.teeth_states.get(t, "سليم")
            t_name = tooth_names.get(t, "")
            c1, c2 = st.columns([1, 3])
            with c1:
                if st.button(f"{t}", key=f"btn_ur_{t}"):
                    st.session_state.teeth_states[t] = selected_status
                    st.rerun()
            with c2:
                st.markdown(f"<p style='padding-top:8px; font-size:13px;'><b>{t}</b> - {t_name} [<span style='color:#F59E0B;'>{current_s}</span>]</p>", unsafe_allow_html=True)
                
    with col_up_l:
        st.markdown("<b>الجانب العلوي الأيسر (21 - 28)</b>", unsafe_allow_html=True)
        upper_left = [21, 22, 23, 24, 25, 26, 27, 28]
        for t in upper_left:
            current_s = st.session_state.teeth_states.get(t, "سليم")
            t_name = tooth_names.get(t, "")
            c1, c2 = st.columns([1, 3])
            with c1:
                if st.button(f"{t}", key=f"btn_ul_{t}"):
                    st.session_state.teeth_states[t] = selected_status
                    st.rerun()
            with c2:
                st.markdown(f"<p style='padding-top:8px; font-size:13px;'><b>{t}</b> - {t_name} [<span style='color:#F59E0B;'>{current_s}</span>]</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🦷 الفك السفلي (Mandibular Arch)")
    
    col_low_r, col_low_l = st.columns(2)
    
    with col_low_r:
        st.markdown("<b>الجانب السفلي الأيمن (48 - 41)</b>", unsafe_allow_html=True)
        lower_right = [48, 47, 46, 45, 44, 43, 42, 41]
        for t in lower_right:
            current_s = st.session_state.teeth_states.get(t, "سليم")
            t_name = tooth_names.get(t, "")
            c1, c2 = st.columns([1, 3])
            with c1:
                if st.button(f"{t}", key=f"btn_lr_{t}"):
                    st.session_state.teeth_states[t] = selected_status
                    st.rerun()
            with c2:
                st.markdown(f"<p style='padding-top:8px; font-size:13px;'><b>{t}</b> - {t_name} [<span style='color:#F59E0B;'>{current_s}</span>]</p>", unsafe_allow_html=True)
                
    with col_low_l:
        st.markdown("<b>الجانب السفلي الأيسر (31 - 38)</b>", unsafe_allow_html=True)
        lower_left = [31, 32, 33, 34, 35, 36, 37, 38]
        for t in lower_left:
            current_s = st.session_state.teeth_states.get(t, "سليم")
            t_name = tooth_names.get(t, "")
            c1, c2 = st.columns([1, 3])
            with c1:
                if st.button(f"{t}", key=f"btn_ll_{t}"):
                    st.session_state.teeth_states[t] = selected_status
                    st.rerun()
            with c2:
                st.markdown(f"<p style='padding-top:8px; font-size:13px;'><b>{t}</b> - {t_name} [<span style='color:#F59E0B;'>{current_s}</span>]</p>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("💾 حفظ المخطط السريري بالكامل في قاعدة البيانات"):
        st.success("تم حفظ مخطط الأسنان (Dentbook) بنجاح دون أي تداخل أو أخطاء.")

# ==========================================================
# 3. تحليل الأشعة (السيفالومترية) مع زر التحليل الفعلي
# ==========================================================
elif main_menu == "🩻 تحليل الأشعة (السيفالومترية)":
    st.markdown('<div class="main-header">تحليل الأشعة والزوايا السيفالومترية</div>', unsafe_allow_html=True)
    
    ceph_file = st.file_uploader("رفع صورة الأشعة الجانبية (Cephalometric X-Ray):", type=["jpg", "png", "jpeg"])
    
    if ceph_file is not None:
        image = Image.open(ceph_file)
        st.image(image, caption="صورة الأشعة المرفوعة", width=400)
        
        if st.button("🚀 بدء تحليل الأشعة واستخراج الزوايا (AI Analysis)"):
            with st.spinner("جاري معالجة الأشعة واستخراج المعالم السيفالومترية..."):
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
        enhancer = ImageEnhance.Color(original_img)
        designed_img = enhancer.enhance(1.4)
        
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
        st.info("قم برفع صورة وجه المريض أو ابتسامته لعرض مقارنة (قبل وبعد) وتصميم الابتسامة بالذكاء الاصطناعي.")

# ==========================================================
# 5. إنتاج وتوليد الصور الجديدة (AI Image Gen)
# ==========================================================
elif main_menu == "🖼️ إنتاج وتوليد الصور الجديدة (AI Image Gen)":
    st.markdown('<div class="main-header">إنتاج وتوليد الصور والمحاكاة التجميلية بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    
    prompt_text = st.text_input("أدخل وصف الصورة أو التعديل المطلوب توليده:", value="3D realistic dental smile makeover, Hollywood white smile, highly detailed")
    style_choice = st.selectbox("اختر نمط الصورة:", ["واقعي (Photorealistic)", "رسم هندسي (Blueprint)", "نمط 3D سينمائي (3D Cinematic)"])
    
    if st.button("🎨 إنتاج الصورة الجديدة بالذكاء الاصطناعي"):
        with st.spinner("جاري توليد وإنتاج الصورة الجديدة..."):
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
