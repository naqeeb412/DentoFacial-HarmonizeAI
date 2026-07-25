import streamlit as st
import cv2
from analysis_logic import HarmonizeAnalyzer

st.set_page_config(page_title="HarmonizeAI - Dentofacial Synergy", page_icon="🦷", layout="wide")
st.title("🦷 HarmonizeAI - Comprehensive Dentofacial Analysis")

@st.cache_resource
def load_analyzer():
    return HarmonizeAnalyzer()

analyzer = load_analyzer()

uploaded_file = st.file_uploader("قم برفع صورة البروفايل أو المنظر الأمامي (JPG / PNG):", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    temp_path = "temp_patient_image.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    points, image, message = analyzer.process_image(temp_path)

    if points is None:
        st.error(message)
    else:
        st.success(message)
        report = analyzer.generate_full_clinical_report(points)

        # رسم الخطوط والتخطيط السريري
        annotated_image = image.copy()
        
        # رسم مثلث البروفايل وخط E-Line
        if 10 in points and 2 in points and 152 in points:
            cv2.line(annotated_image, points[10], points[2], (0, 255, 255), 2)
            cv2.line(annotated_image, points[2], points[152], (0, 255, 255), 2)
        if 1 in points and 152 in points:
            cv2.line(annotated_image, points[1], points[152], (255, 0, 0), 2)

        annotated_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📷 التخطيط السريري للوجه")
            st.image(annotated_rgb, use_column_width=True)

        with col2:
            st.subheader("📊 القياسات والنسب التجميلية")
            for metric, val in report.items():
                if metric != "Diagnoses":
                    st.metric(label=metric, value=str(val))

            st.markdown("---")
            st.subheader("🩺 التشخيص والتقييم السريري التلقائي:")
            for diag in report.get("Diagnoses", []):
                st.warning(f"• {diag}")
