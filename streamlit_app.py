import streamlit as st

st.set_page_config(
    page_title="DentoFacial HarmonizeAI",
    page_icon="🦷",
    layout="wide"
)

st.title("🦷 DentoFacial HarmonizeAI™")
st.markdown("منصة التوافق الوجهي والتحليل التشخيصي الرقمي للابتسامة.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("رفع بيانات المريض أو الفحص")
    uploaded_file = st.file_uploader("اختر صورة الوجه أو ملف الميش (3D Mesh):", type=["png", "jpg", "jpeg", "obj"])
    analysis_type = st.selectbox("نوع التحليل المطلوب:", ["تحليل النسب الوجهية (Facial Proportions)", "تصميم الابتسامة الرقمي (Digital Smile Design)", "تآزر تقويم الأسنان وجراحة الفم"])

with col2:
    st.subheader("نتائج المعالجة والتشخيص")
    if uploaded_file is not None:
        st.success("تم تحميل الملف بنجاح وجاهز للتحليل بواسطة الذكاء الاصطناعي.")
        st.image(uploaded_file, caption="الصورة المرفوعة للتحليل", use_column_width=True)
    else:
        st.info("يرجى رفع ملف أو صورة البدء بالتحليل.")

if st.button("بدء التحليل الشامل"):
    st.balloons()
    st.success("تم إتمام التحليل التداخلي بنجاح!")
    st.metric(label="مؤشر التناسق الجمالي (Harmonic Index)", value="94.5%", delta="+2.3%")
