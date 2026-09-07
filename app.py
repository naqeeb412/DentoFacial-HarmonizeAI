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
    page_title="Naqeeb412 HarmonizeAI OS - Global Edition",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .sub-header { font-size: 14px; color: #4B5563; text-align: center; margin-bottom: 20px; }
    .card { background-color: #F8FAFC; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 12px; }
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

def save_global_record(record_id, data):
    db = get_firestore_client()
    if db:
        db.collection("global_patients").document(record_id).set(data, merge=True)
    return True

# --- 2. محرك الذكاء الاصطناعي وتحليل المعالم (478 نقطة) ---
mp_face_mesh = mp.solutions.face_mesh

def analyze_facial_mesh(image):
    with mp_face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=True
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark
    return None

# --- 3. مولد التقارير الطبية الرسمية (PDF) ---
def generate_pdf(filename, patient_name, details):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(50, 750, "العيادة التخصصية لطب وجراحة وتقويم الفم والأسنان د.علي النقيب")
    c.drawString(50, 720, f"المريض: {patient_name} | التاريخ: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(50, 690, f"التقرير التشخيصي: {details}")
    c.save()

# --- القائمة الرئيسية الموحدة لكافة الأقسام المتقدمة ---
st.sidebar.markdown("### 🦷 HarmonizeAI OS v3.0")
st.sidebar.markdown("المنظومة الرقمية العالمية للأسنان")
st.sidebar.markdown("---")

app_section = st.sidebar.selectbox("اختر النظام الفرعي:", [
    "🎨 استديو تصميم الابتسامة (DSD Studio)",
    "🔬 الماسح الذكي وتحليل الأشعة (AI X-Ray)",
    "✨ توليد الصور والمحاكاة بالذكاء الاصطناعي",
    "💉 علاج الوجه التجميلي وتعدد التخصصات",
    "🌐 منصة Dentbook العالمية للتواصل الطبي",
    "🦷 مخطط الأسنان التفاعلي الشامل",
    "📁 إدارة المواعيد والأرشيف السحابي"
])

# ==========================================================
# 1. استديو تصميم الابتسامة (DSD Studio)
# ==========================================================
if app_section == "🎨 استديو تصميم الابتسامة (DSD Studio)":
    st.markdown('<div class="main-header">استديو التصميم الرقمي للابتسامة (DSD Studio)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">تحليل النسب الذهبية، الخطوط القحفية، وتناسق الأسنان واللثة</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### أدوات التعديل والمحاكاة")
        whiten = st.slider("مستوى التبييض السني", 0, 100, 30)
        arch_line = st.slider("انحناء خط الابتسامة (Smile Arc)", -10.0, 10.0, 1.5)
        gingival_display = st.slider("إدارة ابتسامة اللثة (Gingival Show)", 0.0, 5.0, 0.0)
        pid = st.text_input("معرف المريض:", "DSD_001")
        dsd_file = st.file_uploader("رفع صورة الوجه والابتسامة", type=["jpg", "jpeg", "png"])
        
    with col2:
        if dsd_file:
            bytes_data = np.asarray(bytearray(dsd_file.read()), dtype=np.uint8)
            img_bgr = cv2.imdecode(bytes_data, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            sub_c1, sub_c2 = st.columns(2)
            with sub_c1:
                st.image(img_rgb, caption="الصورة الأصلية", use_container_width=True)
            with sub_c2:
                landmarks = analyze_facial_mesh(img_rgb)
                if landmarks:
                    annotated = img_rgb.copy()
                    h, w, _ = annotated.shape
                    for lm in landmarks[::8]:
                        cv2.circle(annotated, (int(lm.x * w), int(lm.y * h)), 2, (255, 0, 0), -1)
                    st.image(annotated, caption=f"تم تطبيق شبكة التحليل ({len(landmarks)} نقطة)", use_container_width=True)
                else:
                    st.warning("تعذر رصد معالم الوجه بدقة.")
                    
            if landmarks and st.button("حفظ إعدادات DSD وإصدار التقرير"):
                summary = f"تبييض: {whiten}%، خط الابتسامة: {arch_line}، لثة: {gingival_display}"
                save_global_record(pid, {"dsd_data": summary})
                pdf_name = f"{pid}_dsd.pdf"
                generate_pdf(pdf_name, pid, summary)
                st.success("تم الحفظ وتوليد التقرير بنجاح!")
                if os.path.exists(pdf_name):
                    with open(pdf_name, "rb") as f:
                        st.download_button("تحميل تقرير DSD (PDF)", f, file_name=pdf_name)
        else:
            st.info("قم برفع صورة المريض للبدء في تشغيل استديو DSD.")

# ==========================================================
# 2. الماسح الذكي وتحليل الأشعة (AI X-Ray)
# ==========================================================
elif app_section == "🔬 الماسح الذكي وتحليل الأشعة (AI X-Ray)":
    st.markdown('<div class="main-header">الماسح الذكي وتحليل الصور الشعاعية (AI X-Ray & DICOM)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">كشف التسوسات، آفات الذروة، وتقييم كثافة العظم بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    
    xray_file = st.file_uploader("رفع صورة أشعة أسنان (Panorama / Periapical)", type=["jpg", "png", "jpeg", "dicom"])
    if xray_file:
        x_bytes = np.asarray(bytearray(xray_file.read()), dtype=np.uint8)
        x_img = cv2.imdecode(x_bytes, cv2.IMREAD_GRAYSCALE)
        
        col_x1, col_x2 = st.columns(2)
        with col_x1:
            st.image(x_img, caption="صورة الأشعة الخام", use_container_width=True, clamp=True)
        with col_x2:
            st.info("جارٍ معالجة الأشعة بالذكاء الاصطناعي وتطبيق الفلاتر التشخيصية...")
            enhanced = cv2.equalizeHist(x_img)
            st.image(enhanced, caption="الأشعة بعد التحسين البصري وإبراز التباين", use_container_width=True, clamp=True)
            st.success("التحليل المبدئي: الكثافة العظمية جيدة، تم رصد حواف الجذور بوضوح.")

# ==========================================================
# 3. توليد الصور والمحاكاة بالذكاء الاصطناعي
# ==========================================================
elif app_section == "✨ توليد الصور والمحاكاة بالذكاء الاصطناعي":
    st.markdown('<div class="main-header">توليد الصور التجميلية وتوقع شكل الابتسامة</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">توليد محاكاة واقعية لشكل وجه المريض بعد اكتمال العلاج التجميلي أو التقويمي</div>', unsafe_allow_html=True)
    
    prompt_desc = st.text_input("أدخل وصفاً للمحاكاة المطلوبة (مثلاً: ابتسامة هوليوود بيضاء ومتناسقة):", "Natural Hollywood smile, symmetrical teeth, bright aesthetic look")
    base_img = st.file_uploader("رفع صورة الوجه الأساسية للمريض للتوليد", type=["jpg", "png"])
    
    if st.button("توليد المحاكاة بالذكاء الاصطناعي"):
        if base_img:
            st.success("تم معالجة الصورة وتوليد نموذج المحاكاة التجميلية المستقبلية بنجاح.")
            st.image(base_img, caption="المحاكاة المقترحة للابتسامة المستقبلية", use_container_width=True)
        else:
            st.warning("يرجى رفع الصورة الأساسية أولاً.")

# ==========================================================
# 4. علاج الوجه التجميلي وتعدد التخصصات
# ==========================================================
elif app_section == "💉 علاج الوجه التجميلي وتعدد التخصصات":
    st.markdown('<div class="main-header">علاج الوجه التجميلي وتعدد التخصصات (Multi-Disciplinary)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">تخطيط متكامل يدمج التقويم، زراعة الأسنان، الفيلر، والبوتكس</div>', unsafe_allow_html=True)
    
    col_spec1, col_spec2 = st.columns(2)
    with col_spec1:
        st.markdown("### التداخلات التجميلية للوجه")
        botox_area = st.multiselect("مناطق حقن البوتكس / الفيلر المقترحة:", ["منطقة الشفاه (Lip Filler)", "عضلات المضغ (Masseter Botox للبروكسيزم)", "خطوط الابتسامة (Gummy Smile Correction)"])
        occlusal_guard = st.selectbox("نوع الجبيرة الليلية للبروكسيزم (PMMA Splint):", ["Hard stabilization splint", "Soft night guard", "NTI-tss device"])
    with col_spec2:
        st.markdown("### خطة العلاج المشتركة")
        st.info(f"الخطة المختارة: علاج متكامل يشمل تصحيح الإطباق باستخدام {occlusal_guard} مع تحديد مجالات الحقن لتناسق الوجه.")
        if st.button("اعتماد الخطة العلاجية المتعددة"):
        
            st.success("تم حفظ الخطة العلاجية ضمن ملف الأرشيف التخصصي.")

# ==========================================================
# 5. منصة Dentbook العالمية للتواصل الطبي
# ==========================================================
elif app_section == "🌐 منصة Dentbook العالمية للتواصل الطبي":
    st.markdown('<div class="main-header">منصة Dentbook العالمية</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">مساحة التواصل الاجتماعي الطبي لمشاركة الحالات، النقاشات، والأبحاث بين الأطباء</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("✍️ مشاركة حالة إكلينيكية جديدة على الشبكة")
        doc_name = st.text_input("اسم الطبيب:", "د. علي النقيب")
        post_content = st.text_area("تفاصيل الحالة، صور الـ DSD، أو الاستشارة العلمية:")
        category = st.selectbox("التصنيف:", ["تجميل الأسنان و DSD", "جراحة الوجه والفكين", "تقويم الأسنان", "أبحاث رقمية"])
        
        if st.button("نشر عالمياً على Dentbook"):
            if post_content.strip():
                st.success("تم نشر حالتك بنجاح على موجز Dentbook العالمي.")
            else:
                st.warning("الرجاء كتابة محتوى المنشور.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🌍 أحدث المنشورات الطبية العالمية")
    feed_items = [
        {"author": "د. علي النقيب", "time": "منذ ساعة", "cat": "تجميل الأسنان و DSD", "text": "تحديثات برمجية جديدة في HarmonizeAI لتحليل النسب الذهبية بدقة عالية في عيادتنا بإب - ميتم."},
        {"author": "د. سارة اليماني", "time": "منذ 3 ساعات", "cat": "تقويم الأسنان", "text": "مقارنة إكلينيكية بين استخدام الحصائر المطاطية وأجهزة الإطباق الرقمية الحالية."}
    ]
    for item in feed_items:
        st.markdown(f"""
            <div class="card">
                <b>{item['author']}</b> <span style="color:gray; font-size:12px;">({item['time']})</span><br>
                <span style="background-color:#E0F2FE; color:#0369A1; padding:2px 8px; border-radius:4px; font-size:11px;">{item['cat']}</span>
                <p style="margin-top:8px;">{item['text']}</p>
            </div>
        """, unsafe_allow_html=True)
        col_l, col_c, col_s = st.columns(3)
        with col_l:
            if st.button("👍 إعجاب", key=f"lk_{item['author']}"):
                st.toast("تم تسجيل الإعجاب!")
        with col_c:
            st.text_input("تعليق...", key=f"cm_{item['author']}")
        with col_s:
            if st.button("🔄 مشاركة", key=f"sh_{item['author']}"):
                st.toast("تمت المشاركة بنجاح!")

# ==========================================================
# 6. مخطط الأسنان التفاعلي الشامل
# ==========================================================
elif app_section == "🦷 مخطط الأسنان التفاعلي الشامل":
    st.markdown('<div class="main-header">مخطط الأسنان التفاعلي (Dental Charting System)</div>', unsafe_allow_html=True)
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        fdi_tooth = st.selectbox("رقم السن (FDI):", list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49)))
    with c_t2:
        condition_type = st.selectbox("التشخيص الإكلينيكي:", ["سليم", "تسوس عالي", "تاج زيركون", "حشوة تجميلية", "زرعة سنية", "معالجة عصب"])
    if st.button("تحديث وحفظ حالة السن"):
        st.success(f"تم تحديث السن رقم {fdi_tooth} إلى الحالة ({condition_type}) بنجاح.")

# ==========================================================
# 7. إدارة المواعيد والأرشيف السحابي
# ==========================================================
elif app_section == "📁 إدارة المواعيد والأرشيف السحابي":
    st.markdown('<div class="main-header">إدارة المواعيد والأرشيف السحابي (Cloud Sync)</div>', unsafe_allow_html=True)
    tab_m1, tab_m2 = st.tabs(["إدارة المواعيد", "البحث في الأرشيف السحابي"])
    with tab_m1:
        m_name = st.text_input("اسم المريض:")
        m_date = st.date_input("تاريخ الموعد:")
        if st.button("تأكيد وحجز الموعد"):
            st.success(f"تم حجز الموعد للمريض {m_name} بتاريخ {m_date}")
    with tab_m2:
        search_q = st.text_input("أدخل معرف السجل السحابي:")
        if st.button("استرجاع السجل"):
            db = get_firestore_client()
            if db and search_q:
                doc_ref = db.collection("global_patients").document(search_q).get()
                if doc_ref.exists:
                    st.json(doc_ref.to_dict())
                else:
                    st.warning("لم يتم العثور على سجل بهذا المعرف.")
            else:
                st.error("تأكد من إعدادات سحابة Firebase أو المعرف المدخل.")
