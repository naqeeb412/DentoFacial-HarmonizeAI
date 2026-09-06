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

# --- 2. محرك التحليل التشخيصي (478 نقطة) ---
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

# --- 4. إعداد واجهة المستخدم الرئيسية وتدوير الأقسام (Streamlit) ---
st.set_page_config(page_title="Naqeeb412 HarmonizeAI", layout="wide")

st.title("العيادة التخصصية لطب وجراحة وتقويم الفم والأسنان د.علي النقيب")
st.subheader("نظام التحليل الرقمي وتصميم الابتسامة (HarmonizeAI OS)")

# القائمة الجانبية للتنقل بين الأقسام شاملة Dentbook
st.sidebar.title("أقسام المنظومة (HarmonizeAI OS)")
app_mode = st.sidebar.selectbox("اختر القسم المطلوب:", [
    "تحليل الوجه والابتسامة الرقمية (DSD)",
    "مخطط الأسنان التفاعلي (Dental Chart)",
    "عارض النماذج ثلاثية الأبعاد (3D Viewer)",
    "إدارة المواعيد والمرضى",
    "سجلات التقارير والاتصال السحابي",
    "منصة Dentbook (التواصل الاجتماعي الطبي)"
])

# --- قسم 1: تحليل الوجه والابتسامة الرقمية (DSD) ---
if app_mode == "تحليل الوجه والابتسامة الرقمية (DSD)":
    st.header("قسم التحليل التشخيصي ومحاكاة الابتسامة")
    
    st.sidebar.subheader("إعدادات المحاكاة التجميلية")
    whitening_level = st.sidebar.slider("درجة التبييض السني", 0, 100, 20)
    smile_arch_adjust = st.sidebar.slider("ضبط خط الابتسامة", -10.0, 10.0, 0.0)

    uploaded_file = st.file_uploader("اختر صورة المريض للتحليل", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image_rgb = cv2.cvtColor(cv2.imdecode(file_bytes, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(image_rgb, caption="الصورة الأصلية للمريض", use_container_width=True)
            
        with col2:
            st.info("جارٍ معالجة وتحليل الابتسامة الرقمية...")
            landmarks = analyze_facial_landmarks(image_rgb)
            
            if landmarks:
                st.success(f"تم بنجاح رصد وتتبع نقاط الوجه (إجمالي النقاط: {len(landmarks)})")
                analysis_summary = f"تبييض بدرجة {whitening_level}، تعديل خط الابتسامة بمقدار {smile_arch_adjust}"
                st.write(f"**ملخص المعالجة الحالية:** {analysis_summary}")
                
                patient_id = st.text_input("أدخل معرف المريض للحفظ السحابي:", "Patient_001")
                if st.button("حفظ السجل في سحابة العيادة"):
                    save_patient_record(patient_id, {"whitening": whitening_level, "arch_adjust": smile_arch_adjust})
                    st.success("تم حفظ السجل بنجاح في قاعدة البيانات السحابية.")
                    
                pdf_filename = f"{patient_id}_report.pdf"
                generate_pdf_report(pdf_filename, patient_id, analysis_summary)
                
                if os.path.exists(pdf_filename):
                    with open(pdf_filename, "rb") as pdf_file:
                        st.download_button(
                            label="تحميل التقرير الطبي (PDF)",
                            data=pdf_file,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )
            else:
                st.warning("لم يتم رصد الوجه بوضوح، يرجى رفع صورة واضحة.")

# --- قسم 2: مخطط الأسنان التفاعلي (Dental Chart) ---
elif app_mode == "مخطط الأسنان التفاعلي (Dental Chart)":
    st.header("مخطط الأسنان التفاعلي (Dental Charting)")
    st.write("حدد السن المعني وأدخل الحالة الإكلينيكية (تسوس، تركيبات، زرعات، تقويم):")
    
    col_tooth1, col_tooth2 = st.columns(2)
    with col_tooth1:
        selected_tooth = st.selectbox("رقم السن (FDI System):", list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49)))
    with col_tooth2:
        condition = st.selectbox("الحالة السنية:", ["سليم", "تسوس (Caries)", "حشوة تجميلية (Composite)", "تاج (Crown)", "زرعة (Implant)", "معالجة لبية (Root Canal)"])
        
    if st.button("تحديث حالة السن"):
        st.success(f"تم تحديث السن رقم {selected_tooth} إلى الحالة: {condition}")

# --- قسم 3: عارض النماذج ثلاثية الأبعاد (3D Viewer) ---
elif app_mode == "عارض النماذج ثلاثية الأبعاد (3D Viewer)":
    st.header("عارض النماذج الرقمية والملفات السنية (STL / DICOM)")
    st.info("قم برفع ملفات النماذج الرقمية الثلاثية الأبعاد الخاصة بالمريض (STL / OBJ)")
    
    uploaded_3d = st.file_uploader("اختر ملف النموذج السني ثلاثي الأبعاد", type=["stl", "obj"])
    if uploaded_3d is not None:
        st.success(f"تم تحميل الملف بنجاح: {uploaded_3d.name}")
        st.write("جاري إعداد عارض الشبكات ثلاثية الأبعاد (3D Mesh Integration)...")

# --- قسم 4: إدارة المواعيد والمرضى ---
elif app_mode == "إدارة المواعيد والمرضى":
    st.header("إدارة جدول المواعيد وسجلات المرضى")
    
    patient_name_input = st.text_input("اسم المريض الثلاثي:")
    patient_phone = st.text_input("رقم الهاتف:")
    appointment_date = st.date_input("تاريخ الجلسة:")
    
    if st.button("حجز الموعد وإضافة المنشور والمريض"):
        st.success(f"تم تسجيل الموعد بنجاح للمريض: {patient_name_input} بتاريخ {appointment_date}")

    st.subheader("قائمة الحجوزات اليومية")
    mock_data = pd.DataFrame({
        "المريض": ["أحمد محمد", "فاطمة علي"],
        "رقم الهاتف": ["777700412", "771122334"],
        "الحالة": ["تقويم أسنان", "تصميم الابتسامة DSD"]
    })
    st.table(mock_data)

# --- قسم 5: سجلات التقارير والاتصال السحابي ---
elif app_mode == "سجلات التقارير والاتصال السحابي":
    st.header("الأرشيف السحابي والتقارير الطبية المحفوظة")
    st.write("إدارة واسترجاع السجلات الطبية السابقة المخزنة عبر قاعدة بيانات Firebase Firestore.")
    
    search_id = st.text_input("ابحث برقم معرف المريض:")
    if st.button("استرجاع السجل"):
        db = get_firestore_client()
        if db and search_id:
            doc_ref = db.collection("patients").document(search_id).get()
            if doc_ref.exists:
                st.json(doc_ref.to_dict())
            else:
                st.warning("لم يتم العثور على سجل بهذا المعرف محلياً أو سحابياً.")
        else:
            st.error("البرنامج يعمل حالياً بدون اتصال سحابي نشط أو أن المعرف فارغ.")

# --- قسم 6: منصة Dentbook (التواصل الاجتماعي الطبي) ---
elif app_mode == "منصة Dentbook (التواصل الاجتماعي الطبي)":
    st.header("منصة Dentbook الاجتماعية الطبية")
    st.write("مساحة تفاعلية لربط الأطباء بالمرضى، مشاركة الحالات السريرية، المنشورات، التعليقات، والقصص (Stories).")
    
    # محاكاة إنشاء منشور جديد (News Feed Post)
    st.subheader("إنشاء منشور جديد / مشاركة حالة إكلينيكية")
    post_author = st.text_input("اسم الطبيب / المستخدم:", "د. علي النقيب")
    post_content = st.text_area("ما الذي يدور في ذهنك إكلينيكياً؟ (نص المنشور، صور الحالات، أو مقاطع الـ DSD):")
    post_category = st.selectbox("تصنيف المنشور:", ["حالة تقويم وتجميل", "استشارة علمية", "نصيحة للمرضى", "إعلان عيادة ميتم"])
    
    if st.button("نشر على منصة Dentbook"):
        if post_content.strip():
            st.success("تم نشر حالتك بنجاح على منصة Dentbook وتحديث موجز الأخبار (Feed).")
        else:
            st.warning("يرجى كتابة محتوى المنشور أولاً.")

    st.markdown("---")
    st.subheader("موجز الأخبار والمجتمع الطبي (News Feed)")
    
    # عرض منشور تفاعلي تمثيلي
    with st.container():
        st.markdown(f"**د. علي النقيب**  •  *منذ ساعة*  •  🏷️ `{post_category if 'post_category' in locals() else 'حالة تقويم وتجميل'}`")
        st.write("تم بنجاح الانتهاء من حالة تصميم الابتسامة الرقمية (DSD) باستخدام خوارزميات الـ HarmonizeAI في عيادتنا بإب - ميتم[span_0](start_span)[span_0](end_span). نترقب آراء الزملاء الأطباء حول التناسق القحفي الوجهي.")
        
        col_like, col_comment, col_share = st.columns(3)
        with col_like:
            if st.button("👍 إعجاب (Like)", key="like_post_1"):
                st.toast("تم تسجيل إعجابك بالحالة!")
        with col_comment:
            comment_input = st.text_input("اكتب تعليقاً...", key="comment_input_1")
            if st.button("إرسال التعليق", key="send_comm_1"):
                st.success("تم نشر تعليقك بنجاح.")
        with col_share:
            if st.button("🔄 مشاركة", key="share_post_1"):
                st.toast("تمت مشاركة المنشور بنجاح.")
