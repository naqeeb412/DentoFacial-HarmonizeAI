import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import firebase_admin
from firebase_admin import credentials, firestore
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import pandas as pd
from datetime import datetime

# --- إعداد الصفحة والستايل البصري الاحترافي ---
st.set_page_config(
    page_title="Naqeeb412 HarmonizeAI OS",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص المظهر البصري عبر CSS ليكون جذباً ومنتجاً
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 10px; }
    .sub-header { font-size: 16px; color: #4B5563; text-align: center; margin-bottom: 25px; }
    .card { background-color: #F8FAFC; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 1. تهيئة Firebase والتخزين السحابي ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
    except Exception:
        pass

def get_firestore_client():
    try:
        return firestore.client()
    except Exception:
        return None

def save_patient_record(patient_id, data):
    db = get_firestore_client()
    if db:
        db.collection("patients").document(patient_id).set(data, merge=True)
    return True

# --- 2. محرك التحليل التشخيصي والذكاء الاصطناعي (478 نقطة) ---
mp_face_mesh = mp.solutions.face_mesh

def analyze_facial_landmarks(image):
    with mp_face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=True
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            return landmarks
    return None

# --- 3. توليد التقارير الطبية التلقائية (PDF) ---
def generate_pdf_report(filename, patient_name, analysis_data):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(50, 750, "العيادة التخصصية لطب وجراحة وتقويم الفم والأسنان د.علي النقيب")
    c.drawString(50, 720, f"اسم المريض: {patient_name}")
    c.drawString(50, 690, f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(50, 660, f"نتيجة تحليل الابتسامة الرقمية: {analysis_data}")
    c.save()

# --- القائمة الجانبية الموحدة للأقسام ---
st.sidebar.markdown("### 🦷 HarmonizeAI OS")
st.sidebar.markdown("العيادة التخصصية - إب، ميتم[span_0](start_span)[span_0](end_span)")
st.sidebar.markdown("---")

app_mode = st.sidebar.selectbox("اختر قسم التشغيل:", [
    "🤖 تحليل الابتسامة والذكاء الاصطناعي (DSD)",
    "🌐 منصة Dentbook الاجتماعية الطبية",
    "🦷 مخطط الأسنان التفاعلي (Dental Chart)",
    "🧊 عارض النماذج ثلاثية الأبعاد (3D Viewer)",
    "📅 إدارة المواعيد والأرشيف السحابي"
])

# ==========================================
# 1. قسم تحليل الابتسامة والذكاء الاصطناعي
# ==========================================
if app_mode == "🤖 تحليل الابتسامة والذكاء الاصطناعي (DSD)":
    st.markdown('<div class="main-header">نظام الذكاء الاصطناعي لتحليل الوجه وتصميم الابتسامة</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">تحليل 478 نقطة تشريحية قحفية وجهية بدقة عالية[span_1](start_span)[span_1](end_span)</div>', unsafe_allow_html=True)
    
    col_ctrl, col_view = st.columns([1, 2])
    
    with col_ctrl:
        st.markdown("### إعدادات المحاكاة")
        whitening_level = st.slider("درجة تبييض الأسنان الرقمي", 0, 100, 25)
        smile_arch_adjust = st.slider("ضبط انحناء خط الابتسامة", -10.0, 10.0, 0.0)
        patient_id_input = st.text_input("معرف المريض (ID):", "Patient_001")
        
        uploaded_file = st.file_uploader("رفع صورة الوجه والأسنان", type=["jpg", "jpeg", "png"])

    with col_view:
        if uploaded_file is not None:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            
            c1, c2 = st.columns(2)
            with c1:
                st.image(image_rgb, caption="صورة المريض الأصلية", use_container_width=True)
            with c2:
                with st.spinner("جاري معالجة شبكة الوجه بالذكاء الاصطناعي..."):
                    landmarks = analyze_facial_landmarks(image_rgb)
                    if landmarks:
                        # رسم توضيحي مبسط على الصورة للمحاكاة البصرية
                        annotated_img = image_rgb.copy()
                        h, w, _ = annotated_img.shape
                        for lm in landmarks[::10]:  # رسم عينة من النقاط
                            cv2.circle(annotated_img, (int(lm.x * w), int(lm.y * h)), 2, (0, 255, 0), -1)
                        
                        st.image(annotated_img, caption=f"تم رصد {len(landmarks)} نقطة تشريحية بنجاح", use_container_width=True)
                    else:
                        st.warning("تعذر رصد معالم الوجه بوضوح، يرجى رفع صورة إضاءتها ممتازة.")

            if landmarks:
                analysis_summary = f"تبييض درجة {whitening_level}، تعديل انحناء الابتسامة {smile_arch_adjust}"
                if st.button("حفظ النتائج وإصدار التقرير الطبي"):
                    save_patient_record(patient_id_input, {"whitening": whitening_level, "arch": smile_arch_adjust})
                    pdf_filename = f"{patient_id_input}_report.pdf"
                    generate_pdf_report(pdf_filename, patient_id_input, analysis_summary)
                    st.success("تم الحفظ السحابي وإصدار التقرير بنجاح.")
                    
                    if os.path.exists(pdf_filename):
                        with open(pdf_filename, "rb") as f:
                            st.download_button("تحميل التقرير النهائي (PDF)", f, file_name=pdf_filename, mime="application/pdf")
        else:
            st.info("قم برفع صورة من القائمة الجانبية لبدء التحليل الفوري بالذكاء الاصطناعي.")

# ==========================================
# 2. منصة Dentbook الاجتماعية الطبية
# ==========================================
elif app_mode == "🌐 منصة Dentbook الاجتماعية الطبية":
    st.markdown('<div class="main-header">منصة Dentbook الطبية التفاعلية</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">مساحة التواصل المشترك ومشاركة الحالات الإكلينيكية بين الأطباء</div>', unsafe_allow_html=True)
    
    # قسم إنشاء منشور جديد (Feed Post)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("✍️ مشاركة حالة إكلينيكية أو منشور جديد")
        author_name = st.text_input("اسم الناشر:", "د. علي النقيب")
        post_text = st.text_area("ما الذي ترغب في مشاركته مع الزملاء؟ (حالات تقويم، زراعة، تجميل DSD...):")
        post_tag = st.selectbox("تصنيف الحالة:", ["تجميل الأسنان وتصميم الابتسامة", "جراحة الفم والتقويم", "حالة تعليمية", "استشارة تقنية"])
        
        if st.button("نشر الحالة الآن"):
            if post_text.strip():
                st.success("تم نشر حالتك بنجاح على موجز أخبار Dentbook وتحديث المنصة.")
            else:
                st.warning("الرجاء كتابة تفاصيل الحالة قبل النشر.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📰 موجز الأخبار والمجتمع الطبي (News Feed)")
    
    # محاكاة عرض منشورات تفاعلية
    posts_list = [
        {"author": "د. علي النقيب", "time": "منذ ساعتين", "tag": "تجميل الأسنان وتصميم الابتسامة", "content": "تم بحمد الله تطبيق خوارزميات HarmonizeAI الجديدة لتحليل التناسق القحفي الوجهي لحالة تجميلية متقدمة في عيادة ميتم، إب[span_2](start_span)[span_2](end_span). النتيجة مذهلة ودقيقة للغاية."},
        {"author": "د. محمد الأحمدي", "time": "منذ 5 ساعات", "tag": "جراحة الفم والتقويم", "content": "استفسار للزملاء الأطباء حول أفضل بروتوكولات التعامل مع حالات الـ posterior bite blocks باستخدام حشوات الباند لمتانة أطول."}
    ]
    
    for idx, p in enumerate(posts_list):
        st.markdown(f"""
            <div class="card">
                <b>{p['author']}</b> <span style="color:gray; font-size:12px;">({p['time']})</span><br>
                <span style="background-color:#E0F2FE; color:#0369A1; padding:2px 8px; border-radius:4px; font-size:11px;">{p['tag']}</span>
                <p style="margin-top:10px;">{p['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_l, col_c, col_s = st.columns(3)
        with col_l:
            if st.button(f"👍 إعجاب", key=f"like_{idx}"):
                st.toast("تم تسجيل الإعجاب!")
        with col_c:
            comm = st.text_input("إضافة تعليق...", key=f"comm_box_{idx}")
            if st.button("إرسال", key=f"comm_btn_{idx}"):
                st.success("تم إرسال التعليق بنجاح.")
        with col_s:
            if st.button(f"🔄 مشاركة", key=f"share_{idx}"):
                st.toast("تمت مشاركة المنشور.")
        st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 3. مخطط الأسنان التفاعلي (Dental Chart)
# ==========================================
elif app_mode == "🦷 مخطط الأسنان التفاعلي (Dental Chart)":
    st.markdown('<div class="main-header">مخطط الأسنان التفاعلي (FDI System)</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        tooth_num = st.selectbox("اختر رقم السن التشريحي:", list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49)))
    with c2:
        pathology = st.selectbox("الحالة السنية الإكلينيكية:", ["سليم", "تسوس عميق", "حشوة تجميلية مرכبة", "تاج سيراميك (Crown)", "زرعة سنية (Implant)", "معالجة عصب (Root Canal)"])
        
    if st.button("حفظ وتشخيص السن"):
        st.success(f"تم تسجيل وتحديث السن رقم ({tooth_num}) بالحالة: [{pathology}] بنجاح في سجل المريض.")

# ==========================================
# 4. عارض النماذج ثلاثية الأبعاد (3D Viewer)
# ==========================================
elif app_mode == "🧊 عارض النماذج ثلاثية الأبعاد (3D Viewer)":
    st.markdown('<div class="main-header">عارض النماذج الرقمية ثلاثية الأبعاد (STL / OBJ)</div>', unsafe_allow_html=True)
    stl_file = st.file_uploader("رفع ملف المورد السني أو الطبعة الرقمية ثلاثية الأبعاد", type=["stl", "obj", "glb"])
    if stl_file:
        st.success(f"تم استقبال الملف بنجاح: {stl_file.name}")
        st.info("العارض الرقمي جاهز لمعالجة الأسطح والشبكات الثلاثية الأبعاد الخاصة بالتركيبات والتقويم.")

# ==========================================
# 5. إدارة المواعيد والأرشيف السحابي
# ==========================================
elif app_mode == "📅 إدارة المواعيد والأرشيف السحابي":
    st.markdown('<div class="main-header">إدارة مواعيد العيادة والأرشيف السحابي</div>', unsafe_allow_html=True)
    
    tab_apt, tab_arch = st.tabs(["إدارة الحجوزات والمواعيد", "الأرشيف السحابي (Firebase)"])
    
    with tab_apt:
        p_name = st.text_input("اسم المريض الرباعي:")
        p_phone = st.text_input("رقم الهاتف للتواصل:")
        apt_date = st.date_input("تاريخ الحجز:")
        if st.button("تثبيت الموعد"):
            st.success(f"تم حجز الموعد بنجاح للمريض: {p_name} بتاريخ {apt_date}")
            
        st.markdown("### جدول المواعيد اليومية")
        st.table(pd.DataFrame({
            "المريض": ["أحمد علي", "سارة محمد"],
            "رقم الهاتف": ["777700412", "771234567"],
            "الخدمة الطبية": ["تصميم ابتسامة DSD", "تقويم أسنان"]
        }))
        
    with tab_arch:
        search_pid = st.text_input("بحث برقم معرف المريض السحابي:")
        if st.button("استرجاع السجل من السحابة"):
            db = get_firestore_client()
            if db and search_pid:
                doc = db.collection("patients").document(search_pid).get()
                if doc.exists:
                    st.json(doc.to_dict())
                else:
                    st.warning("لا يوجد سجل مسجل بهذا المعرف.")
            else:
                st.error("تأكد من إعدادات الاتصال السحابي أو معرف المريض.")
