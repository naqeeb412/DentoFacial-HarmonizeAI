import streamlit as st
import cv2
import numpy as np
from PIL import Image
from analysis_logic import HarmonizeAnalyzer

# إعداد واجهة التطبيق
st.set_page_config(
    page_title="HarmonizeAI - Dentofacial Synergy",
    page_icon="🦷",
    layout="wide"
)

st.title("🦷 HarmonizeAI - Diagnostic & Aesthetic Analysis")
st.write("منظومة التحليل الجمالي والتشخيصي للوجه والأسنان")

# تهيئة المحرك البرمجي
@st.cache_resource
def load_analyzer():
    return HarmonizeAnalyzer()

analyzer = load_analyzer()

# شريط رفع الصور
uploaded_file = st.file_uploader("قم برفع صورة البروفايل للتحليل (JPG / PNG):", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # حفظ الصورة مؤقتاً لقراءتها بواسطة OpenCV
    temp_path = "temp_patient_image.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # معالجة الصورة واستخراج النقاط
    points, image, message = analyzer.process_image(temp_path)

    if points is None:
        st.error(message)
    else:
        st.success(message)

        # حساب النسب التجميلية (مثل E-Line)
        results = analyzer.analyze_e_line(points)

        # رسم النقاط وخط E-Line على الصورة للعرض
        annotated_image = image.copy()
        
        # نقاط الأنف والذقن والشفاه
        if 1 in points and 152 in points:
            # رسم خط Ricketts E-Line بين قمة الأنف والذقن
            cv2.line(annotated_image, points[1], points[152], (255, 0, 0), 2) # خط أزرق
            cv2.circle(annotated_image, points[1], 5, (0, 255, 0), -1)   # قمة الأنف
            cv2.circle(annotated_image, points[152], 5, (0, 255, 0), -1) # الذقن
            
        if 0 in points:
            cv2.circle(annotated_image, points[0], 5, (0, 0, 255), -1)   # الشفة العليا
        if 17 in points:
            cv2.circle(annotated_image, points[17], 5, (0, 0, 255), -1)  # الشفة السفلى

        # تحويل الصورة إلى RGB للعرض في Streamlit
        annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

        # عرض النتائج في عمودين (صورة التخطيط + التقرير)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📷 التخطيط الجمالي للوجه")
            st.image(annotated_image_rgb, use_column_width=True)

        with col2:
            st.subheader("📊 تقرير التحليل السريري")
            if isinstance(results, dict):
                for metric, value in results.items():
                    st.metric(label=metric, value=f"{value} px")
                
                st.info("💡 **ملاحظة سريرية:** القيم المعروضة تبين البعد الأفقي للشفاه عن خط E-Line المرجعي.")
            else:
                st.warning(results)
