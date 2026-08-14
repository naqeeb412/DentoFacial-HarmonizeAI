import streamlit as st
import cv2
import numpy as np
import pandas as pd
from analysis_engine import HarmonizeAnalyzer
import db_manager as db
from config import PAGE_CONFIG

# 1. تهيئة الصفحة
st.set_page_config(**PAGE_CONFIG)

st.title("🦷 DentoFacial-HarmonizeAI™")
st.markdown("##### المنصة الذكية لتحليل الوجه وتناسق الابتسامة (478 Landmark Detection)")

# 2. تحميل المحرك وقاعدة البيانات
@st.cache_resource
def load_analyzer():
    return HarmonizeAnalyzer()

analyzer = load_analyzer()
db.init_db()

# 3. القائمة الجانبية
st.sidebar.header("لوحة التحكم الإكلينيكية")
menu_option = st.sidebar.radio(
    "انتقل إلى:",
    ["📷 التحليل التشريحي للوجه", "📋 إدارة المرضى (Dentbook)", "📊 التقارير والتصدير (Pandas)"]
)

# --- القسم الأول: التحليل التشريحي ---
if menu_option == "📷 التحليل التشريحي للوجه":
    st.subheader("تحليل معالم الوجه والابتسامة الرقمي")
    
    uploaded_file = st.file_uploader("قم برفع صورة الوجه (JPG / PNG)", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        raw_image = cv2.imdecode(file_bytes, 1)

        col1, col2 = st.columns(2)

        with col1:
            st.image(cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB), caption="الصورة الأصلية", use_container_width=True)

        with st.spinner("جاري تحليل المعالم التشريحية للوجه..."):
            annotated_img, metrics, metrics_df = analyzer.process_image(raw_image)

        if annotated_img is not None:
            with col2:
                st.image(annotated_img, caption="تحليل المعالم التشريحية (478 نقطة)", use_container_width=True)
            
            st.success("تم التعرّف على المعالم واستخراج القياسات بنجاح!")
            
            st.markdown("---")
            st.markdown("### 📈 جدولة المؤشرات الإكلينيكية (Pandas Table)")
            
            # عرض جدول Pandas للنتائج
            st.dataframe(metrics_df, use_container_width=True)

            # خيار تنزيل التقرير بصيغة CSV بواسطة Pandas
            csv_data = metrics_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل التقرير الإكلينيكي (CSV)",
                data=csv_data,
                file_name="clinical_analysis_report.csv",
                mime="text/csv"
            )
        else:
            st.error("لم يتم العثور على معالم الوجه في الصورة. يرجى التأكد من وضوح الإضاءة وزاوية التقاط الصورة.")

# --- القسم الثاني: إدارة المرضى ---
elif menu_option == "📋 إدارة المرضى (Dentbook)":
    st.subheader("سجلات المرضى وحفظ الحالات")
    
    with st.form("add_patient_form"):
        st.write("إضافة مريض جديد")
        name = st.text_input("اسم المريض الكامل")
        age = st.number_input("العمر", min_value=1, max_value=120, value=25)
        phone = st.text_input("رقم الهاتف")
        submit = st.form_submit_button("حفظ المريض")
        
        if submit and name:
            p_id = db.add_patient(name, age, phone)
            st.success(f"تم حفظ بيانات المريض {name} بنجاح (رقم الملف: #{p_id})")

    st.markdown("---")
    st.write("### قائمة المرضى المسجلين (Pandas Integration)")
    
    # عرض جدول المرضى بـ Pandas
    patients_df = db.get_patients_df()
    if not patients_df.empty:
        st.dataframe(patients_df, use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلون حالياً.")

# --- القسم الثالث: التقارير والتصدير ---
elif menu_option == "📊 التقارير والتصدير (Pandas)":
    st.subheader("إدارة وتصدير بيانات العيادة الشاملة")
    
    patients_df = db.get_patients_df()
    if not patients_df.empty:
        st.write("#### إحصائيات سريعة للمرضى:")
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("إجمالي المرضى", len(patients_df))
        col_s2.metric("متوسط العمر", f"{round(patients_df['العمر'].mean(), 1)} سنة")
        
        st.markdown("---")
        # تصدير سجل المرضى كاملاً إلى Excel/CSV
        csv_export = patients_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📊 تصدير قاعدة بيانات المرضى بالكامل (CSV)",
            data=csv_export,
            file_name="all_patients_database.csv",
            mime="text/csv"
        )
    else:
        st.info("قم بإضافة مرضى أولاً لاستعراض التقرير الإحصائي.")
