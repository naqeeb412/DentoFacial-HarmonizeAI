import streamlit as st
import google.generativeai as genai

# إعداد الربط (الآن النظام سيقرأ المفتاح من إعدادات الـ Secrets التي حفظتها)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="HarmoniDent AI", page_icon="✨", layout="wide")
st.title("✨ HarmoniDent-AI Assistant")

# تهيئة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# منطقة إدخال المستخدم
if prompt := st.chat_input("اطرح استفسارك السريري..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # طلب الرد من Gemini
        with st.spinner("جاري التحليل السريري..."):
            response = model.generate_content(f"أنت دكتور أسنان خبير. أجب على هذا الاستفسار السريري: {prompt}")
            st.markdown(response.text)
        
        # خيار إرسال التقرير عبر واتساب
        with st.expander("إرسال التقرير للمريض 📲"):
            p_phone = st.text_input("رقم هاتف المريض (مثال: 967777700412)")
            if st.button("تجهيز رابط الواتساب"):
                msg = f"أهلاً، تقريرك الطبي من عيادة د. علي النقيب: {response.text}"
                whatsapp_link = f"https://wa.me/{p_phone}?text={msg}"
                st.markdown(f"**[اضغط هنا لفتح واتساب وإرسال التقرير]({whatsapp_link})**")
    
    st.session_state.messages.append({"role": "assistant", "content": response.text})
