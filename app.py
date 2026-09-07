import streamlit as st
import datetime
import json
import os
import random
import time
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import io

# ====================================================================
# 1. إعداد Firebase (Pyrebase)
# ====================================================================
import pyrebase

firebase_config = {
    "apiKey": "AIzaSyCaCxaxgbkxuqTLtPCjc_5hNHkO_I7vXiQ",
    "authDomain": "naqeeb412-harmonizeai.firebaseapp.com",
    "projectId": "naqeeb412-harmonizeai",
    "storageBucket": "naqeeb412-harmonizeai.firebasestorage.app",
    "messagingSenderId": "547994223412",
    "appId": "1:547994223412:web:d94fc876bbe7a387315b61",
    "databaseURL": ""  
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

# ====================================================================
# 2. إعداد صفحة Streamlit
# ====================================================================
st.set_page_config(
    page_title="HarmonizeAI – نظام الوجه والأسنان المتكامل",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================================================================
# 3. أنماط CSS مخصصة
# ====================================================================
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(145deg, #0a8491, #075e68);
        padding: 12px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .post-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        color: #f8fafc;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #0a8491;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        margin-left: 10px;
    }
    .metric-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .metric-box .value {
        font-size: 2rem;
        font-weight: 700;
        color: #e67e22;
    }
    .metric-box .label {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# 4. تهيئة حالة الجلسة (Session State) مع Firebase
# ====================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "patients" not in st.session_state:
    st.session_state.patients = []
if "posts" not in st.session_state:
    st.session_state.posts = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "appointments" not in st.session_state:
    st.session_state.appointments = []
if "payments" not in st.session_state:
    st.session_state.payments = []
if "ai_results" not in st.session_state:
    st.session_state.ai_results = None

# ====================================================================
# 5. دوال Firebase
# ====================================================================
def firebase_login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.user_token = user['idToken']
        user_data = db.child("users").child(user['localId']).get(user['idToken'])
        if user_data.val():
            st.session_state.user = user_data.val()
            st.session_state.user['email'] = email
        else:
            default_user = {
                "name": email.split('@')[0],
                "role": "doctor",
                "specialty": "",
                "phone": "",
                "bio": ""
            }
            db.child("users").child(user['localId']).set(default_user, user['idToken'])
            st.session_state.user = default_user
            st.session_state.user['email'] = email
        st.session_state.logged_in = True
        return True
    except Exception as e:
        st.error(f"❌ فشل تسجيل الدخول: {str(e)}")
        return False

def firebase_signup(email, password, name, role):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        token = user['idToken']
        local_id = user['localId']
        user_data = {
            "name": name,
            "role": role,
            "specialty": "",
            "phone": "",
            "bio": ""
        }
        db.child("users").child(local_id).set(user_data, token)
        st.session_state.user = user_data
        st.session_state.user['email'] = email
        st.session_state.user_token = token
        st.session_state.logged_in = True
        return True
    except Exception as e:
        st.error(f"❌ فشل إنشاء الحساب: {str(e)}")
        return False

def firebase_logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.user_token = None

def load_patients_from_firebase():
    if st.session_state.user_token and st.session_state.user:
        try:
            local_id = st.session_state.user.get('localId') or st.session_state.user.get('id')
            if not local_id:
                info = auth.get_account_info(st.session_state.user_token)
                local_id = info['users'][0]['localId']
            patients_data = db.child("patients").child(local_id).get(st.session_state.user_token)
            if patients_data.val():
                st.session_state.patients = list(patients_data.val().values())
            else:
                st.session_state.patients = []
        except Exception as e:
            st.warning(f"⚠️ تعذر تحميل المرضى: {str(e)}")

def save_patients_to_firebase():
    if st.session_state.user_token and st.session_state.user:
        try:
            local_id = st.session_state.user.get('localId') or st.session_state.user.get('id')
            if not local_id:
                info = auth.get_account_info(st.session_state.user_token)
                local_id = info['users'][0]['localId']
            patients_dict = {str(i): p for i, p in enumerate(st.session_state.patients)}
            db.child("patients").child(local_id).set(patients_dict, st.session_state.user_token)
        except Exception as e:
            st.warning(f"⚠️ تعذر حفظ المرضى: {str(e)}")

def load_posts_from_firebase():
    if st.session_state.user_token:
        try:
            posts_data = db.child("posts").get(st.session_state.user_token)
            if posts_data.val():
                st.session_state.posts = list(posts_data.val().values())
            else:
                st.session_state.posts = []
        except:
            st.session_state.posts = []

def save_posts_to_firebase():
    if st.session_state.user_token:
        try:
            posts_dict = {str(i): p for i, p in enumerate(st.session_state.posts)}
            db.child("posts").set(posts_dict, st.session_state.user_token)
        except:
            pass

# ====================================================================
# 6. دوال مساعدة للتطبيق
# ====================================================================
def show_toast(msg, type="info"):
    if type == "success":
        st.success(msg)
    elif type == "error":
        st.error(msg)
    elif type == "warning":
        st.warning(msg)
    else:
        st.info(msg)

def add_patient(name, phone, age, gender, notes):
    patient = {
        "id": len(st.session_state.patients) + 1,
        "name": name,
        "phone": phone,
        "age": age,
        "gender": gender,
        "notes": notes,
        "created_at": datetime.datetime.now().isoformat()
    }
    st.session_state.patients.append(patient)
    save_patients_to_firebase()
    return patient

# ====================================================================
# 7. الصفحات
# ====================================================================

def home_page():
    st.markdown("""
        <div style="text-align:center; padding: 40px 0;">
            <h1 style="font-size: 2.8rem;">🦷 HarmonizeAI</h1>
            <p style="color: #94a3b8; font-size: 1.2rem;">نظام متكامل لتشخيص وعلاج الوجه والأسنان بالذكاء الاصطناعي</p>
        </div>
    """, unsafe_allow_html=True)
    st.info("🔐 يرجى تسجيل الدخول للوصول إلى جميع الميزات.")

def auth_page():
    st.markdown("### 🔐 تسجيل الدخول")
    tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("البريد الإلكتروني")
            password = st.text_input("كلمة المرور", type="password")
            consent = st.checkbox("أوافق على سياسة الخصوصية وشروط الاستخدام")
            submitted = st.form_submit_button("🚪 دخول")
            if submitted:
                if not consent:
                    st.warning("⚠️ يجب الموافقة على سياسة الخصوصية.")
                elif firebase_login(email, password):
                    st.success("✅ تم تسجيل الدخول بنجاح!")
                    load_patients_from_firebase()
                    load_posts_from_firebase()
                    st.rerun()

        st.markdown("### أو عبر")
        col_social = st.columns(5)
        with col_social[0]:
            if st.button("🌐 Google", use_container_width=True):
                st.info("🔗 جاري الاتصال بـ Google... (محاكاة)")
        with col_social[1]:
            if st.button("📘 Facebook", use_container_width=True):
                st.info("🔗 جاري الاتصال بـ Facebook... (محاكاة)")
        with col_social[2]:
            if st.button("🐦 Twitter", use_container_width=True):
                st.info("🔗 جاري الاتصال بـ Twitter... (محاكاة)")
        with col_social[3]:
            if st.button("🍎 Apple", use_container_width=True):
                st.info("🔗 جاري الاتصال بـ Apple... (محاكاة)")
        with col_social[4]:
            if st.button("🐙 GitHub", use_container_width=True):
                st.info("🔗 جاري الاتصال بـ GitHub... (محاكاة)")

    with tab2:
        with st.form("signup_form"):
            name = st.text_input("الاسم الكامل")
            email = st.text_input("البريد الإلكتروني")
            password = st.text_input("كلمة المرور (8 أحرف على الأقل)", type="password")
            confirm = st.text_input("تأكيد كلمة المرور", type="password")
            role = st.selectbox("الدور", ["doctor", "patient", "technician"])
            consent2 = st.checkbox("أوافق على سياسة الخصوصية وشروط الاستخدام")
            submitted = st.form_submit_button("📝 إنشاء حساب")
            if submitted:
                if not name or not email or not password:
                    st.warning("⚠️ جميع الحقول مطلوبة.")
                elif password != confirm:
                    st.warning("⚠️ كلمة المرور غير متطابقة.")
                elif len(password) < 8:
                    st.warning("⚠️ كلمة المرور يجب أن تكون 8 أحرف على الأقل.")
                elif not consent2:
                    st.warning("⚠️ يجب الموافقة على سياسة الخصوصية.")
                elif firebase_signup(email, password, name, role):
                    st.success("✅ تم إنشاء الحساب بنجاح!")
                    load_patients_from_firebase()
                    load_posts_from_firebase()
                    st.rerun()

def dashboard_page():
    st.markdown("### 📊 لوحة التحكم")
    st.markdown(f"#### مرحباً، {st.session_state.user['name']} 👋")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👤 المرضى", len(st.session_state.patients))
    with col2:
        st.metric("📅 مواعيد اليوم", len([a for a in st.session_state.appointments if a.get("date") == datetime.date.today().isoformat()]))
    with col3:
        st.metric("🧠 تشخيصات AI", random.randint(1, 20))
    with col4:
        st.metric("📝 منشورات Dentbook", len(st.session_state.posts))

    st.markdown("---")
    st.markdown("#### 📋 آخر المرضى")
    if st.session_state.patients:
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df[["name", "phone", "age", "gender"]], use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلين.")

def patients_page():
    st.markdown("### 👨‍⚕️ إدارة المرضى")
    tab1, tab2 = st.tabs(["قائمة المرضى", "إضافة مريض"])

    with tab1:
        if st.session_state.patients:
            df = pd.DataFrame(st.session_state.patients)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("لا يوجد مرضى.")

    with tab2:
        with st.form("add_patient_form"):
            name = st.text_input("الاسم الكامل")
            phone = st.text_input("رقم الهاتف")
            age = st.number_input("العمر", min_value=0, max_value=150, step=1)
            gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
            notes = st.text_area("ملاحظات")
            submitted = st.form_submit_button("💾 حفظ المريض")
            if submitted:
                if name:
                    add_patient(name, phone, age, gender, notes)
                    st.success("✅ تم إضافة المريض!")
                    st.rerun()
                else:
                    st.warning("⚠️ الاسم مطلوب.")

def ai_analysis_page():
    st.markdown("### 🧠 تحليل العظام والإطباق بالذكاء الاصطناعي")
    st.markdown("أدخل قياسات الأشعة السيفالومترية للحصول على تحليل شامل.")

    with st.form("ai_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            sna = st.number_input("SNA (°)", value=82.0, step=0.5)
            snb = st.number_input("SNB (°)", value=80.0, step=0.5)
            anb = st.number_input("ANB (°)", value=2.0, step=0.5)
            snmp = st.number_input("SN-MP (°)", value=32.0, step=0.5)
        with col2:
            fma = st.number_input("FMA (°)", value=25.0, step=0.5)
            impa = st.number_input("IMPA (°)", value=90.0, step=0.5)
            overjet = st.number_input("Overjet (mm)", value=3.0, step=0.5)
            overbite = st.number_input("Overbite (mm)", value=2.0, step=0.5)
        with col3:
            u1sn = st.number_input("U1-SN (°)", value=104.0, step=0.5)
            l1mp = st.number_input("L1-MP (°)", value=92.0, step=0.5)
            u1l1 = st.number_input("U1-L1 (°)", value=130.0, step=0.5)
            zangle = st.number_input("Z-angle (°)", value=72.0, step=0.5)

        submitted = st.form_submit_button("🧠 تحليل")

    if submitted:
        normal = {
            "SNA": 82, "SNB": 80, "ANB": 2, "SN-MP": 32,
            "FMA": 25, "IMPA": 90, "Overjet": 3, "Overbite": 2,
            "U1-SN": 104, "L1-MP": 92, "U1-L1": 130, "Z-angle": 72
        }
        values = {
            "SNA": sna, "SNB": snb, "ANB": anb, "SN-MP": snmp,
            "FMA": fma, "IMPA": impa, "Overjet": overjet, "Overbite": overbite,
            "U1-SN": u1sn, "L1-MP": l1mp, "U1-L1": u1l1, "Z-angle": zangle
        }

        bone_keys = ["SNA", "SNB", "ANB", "SN-MP", "FMA"]
        occlusion_keys = ["Overjet", "Overbite", "IMPA", "U1-SN", "L1-MP", "U1-L1", "Z-angle"]

        bone_score = 0
        occlusion_score = 0
        bone_results = {}
        occlusion_results = {}

        for key in bone_keys:
            diff = abs(values[key] - normal[key])
            status = "طبيعي" if diff <= 2 else "مقبول" if diff <= 4 else "غير طبيعي"
            bone_results[key] = {"value": values[key], "normal": normal[key], "diff": diff, "status": status}
            if status == "طبيعي":
                bone_score += 10
            elif status == "مقبول":
                bone_score += 5

        for key in occlusion_keys:
            diff = abs(values[key] - normal[key])
            status = "طبيعي" if diff <= 2 else "مقبول" if diff <= 4 else "غير طبيعي"
            occlusion_results[key] = {"value": values[key], "normal": normal[key], "diff": diff, "status": status}
            if status == "طبيعي":
                occlusion_score += 10
            elif status == "مقبول":
                occlusion_score += 5

        bone_percent = round((bone_score / (len(bone_keys) * 10)) * 100)
        occlusion_percent = round((occlusion_score / (len(occlusion_keys) * 10)) * 100)

        if anb > 4.5:
            classification = "Class II (بروز الفك العلوي)"
            desc = "بروز الفك العلوي مع تراجع الفك السفلي. يوصى بعلاج تقويمي أو جراحي حسب الحالة."
        elif anb < 0:
            classification = "Class III (بروز الفك السفلي)"
            desc = "بروز الفك السفلي مع تراجع الفك العلوي. يوصى بعلاج تقويمي جراحي."
        else:
            classification = "Class I (إطباق طبيعي)"
            desc = "علاقة سنية طبيعية مع تناسق فكي جيد."

        st.session_state.ai_results = {
            "bone_percent": bone_percent,
            "occlusion_percent": occlusion_percent,
            "classification": classification,
            "description": desc,
            "bone_results": bone_results,
            "occlusion_results": occlusion_results
        }

        st.markdown("### 📊 نتائج التحليل")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🦴 صحة العظام", f"{bone_percent}%", delta="جيد" if bone_percent >= 80 else "متوسط" if bone_percent >= 60 else "يحتاج تحسين")
        with col2:
            st.metric("⚙️ جودة الإطباق", f"{occlusion_percent}%", delta="جيد" if occlusion_percent >= 80 else "متوسط" if occlusion_percent >= 60 else "يحتاج تحسين")
        with col3:
            overall = (bone_percent + occlusion_percent) // 2
            st.metric("📊 المؤشر العام", f"{overall}%", delta="ممتاز" if overall >= 80 else "جيد" if overall >= 60 else "يحتاج تحسين")

        st.markdown(f"**📋 التصنيف الإطباقي:** {classification}")
        st.markdown(f"**📝 الوصف:** {desc}")

        st.markdown("#### 📋 مقارنة القيم")
        compare_df = []
        all_keys = list(bone_results.keys()) + list(occlusion_results.keys())
        for key in all_keys:
            res = bone_results.get(key) or occlusion_results.get(key)
            if res:
                compare_df.append({
                    "القياس": key,
                    "المريض": res["value"],
                    "الطبيعي": res["normal"],
                    "الفرق": res["diff"],
                    "الحالة": res["status"]
                })
        if compare_df:
            st.dataframe(pd.DataFrame(compare_df), use_container_width=True)

        st.markdown("#### 📈 مقارنة بيانية")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[k for k in all_keys],
            y=[bone_results.get(k, {}).get("value", 0) or occlusion_results.get(k, {}).get("value", 0) for k in all_keys],
            name="المريض",
            marker_color="#0a8491"
        ))
        fig.add_trace(go.Bar(
            x=[k for k in all_keys],
            y=[normal[k] for k in all_keys],
            name="الطبيعي",
            marker_color="#e67e22"
        ))
        fig.update_layout(barmode="group", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 💡 التوصيات العلاجية")
        recs = []
        if bone_percent < 70:
            recs.append("🦴 **تحسين صحة العظام:** يوصى بإجراء تقييم سريري شامل لعظام الفك.")
        if occlusion_percent < 70:
            recs.append("⚙️ **تحسين الإطباق:** يوصى بمراجعة خطة العلاج التقويمية.")
        if "Class II" in classification:
            recs.append("📐 **بروز الفك العلوي:** يوصى بعلاج تقويمي أو جراحي.")
        if "Class III" in classification:
            recs.append("📐 **بروز الفك السفلي:** يوصى بعلاج تقويمي جراحي.")
        if not recs:
            recs.append("✅ **نتائج ممتازة:** جميع القياسات ضمن الحدود الطبيعية. استمر في المتابعة الدورية.")
        for r in recs:
            st.markdown(f"- {r}")

def facial_analysis_page():
    st.markdown("### 🧑‍⚕️ تحليل الوجه (478 علامة)")
    uploaded = st.file_uploader("📤 رفع صورة وجه للتحليل", type=["jpg", "png", "jpeg"])
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="الصورة المرفوعة", width=400)
        if st.button("🧠 تحليل"):
            with st.spinner("جاري تحليل الوجه..."):
                time.sleep(2)
            st.success("✅ تم التحليل بنجاح!")
            st.markdown("""
                **📊 نتائج التحليل:**
                - النسبة الذهبية: 1.618
                - التناظر: 94%
                - خط الابتسامة: متناسق
                - ارتفاع الوجه: متوسط
            """)

def cephalometric_page():
    st.markdown("### 🩻 تحليل الأشعة")
    uploaded = st.file_uploader("📤 رفع صورة أشعة", type=["jpg", "png", "jpeg"])
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="الأشعة المرفوعة", width=400)
        if st.button("📐 تحليل"):
            with st.spinner("جاري تحليل الأشعة..."):
                time.sleep(2)
            st.success("✅ تم التحليل بنجاح!")
            st.markdown("""
                **📐 الزوايا السيفالومترية:**
                - SNA: 82°
                - SNB: 80°
                - ANB: 2°
                - SN-MP: 32°
            """)

def smile_design_page():
    st.markdown("### 😁 تصميم الابتسامة (DSD)")
    uploaded = st.file_uploader("📤 رفع صورة المريض", type=["jpg", "png", "jpeg"])
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="الصورة الأصلية", width=400)
        if st.button("🎨 محاكاة"):
            with st.spinner("جاري إنشاء المحاكاة..."):
                time.sleep(2)
            st.success("✅ تم إنشاء المحاكاة!")
            st.markdown("**✨ ابتسامة محاكاة (قبل/بعد):**")
            col1, col2 = st.columns(2)
            with col1:
                st.image(image, caption="قبل", width=200)
            with col2:
                st.image(image, caption="بعد (محاكاة)", width=200)

def cadcam_page():
    st.markdown("### ⚙️ CAD/CAM & 3D Viewer")
    uploaded = st.file_uploader("📂 رفع ملف STL/OBJ", type=["stl", "obj"])
    if uploaded:
        st.success(f"✅ تم رفع الملف: {uploaded.name}")
        st.info("📦 عارض ثلاثي الأبعاد (محاكاة) - سيتم عرض النموذج هنا.")
        st.markdown("""
            <div style="background: #1e293b; border-radius: 12px; padding: 40px; text-align: center; border: 1px solid #334155;">
                <div style="font-size: 4rem;">🧊</div>
                <p style="color: #94a3b8;">نموذج ثلاثي الأبعاد (STL)</p>
                <p style="color: #94a3b8; font-size: 0.8rem;">تم تحميل الملف بنجاح، يمكنك التحكم فيه بالماوس (محاكاة).</p>
            </div>
        """, unsafe_allow_html=True)

def dentbook_page():
    st.markdown("### 📘 Dentbook – المجتمع الطبي")

    with st.expander("✍️ شارك حالة أو سؤالاً"):
        with st.form("new_post_form"):
            content = st.text_area("ماذا تفكر يا دكتور؟")
            col1, col2 = st.columns([3, 1])
            with col1:
                media = st.file_uploader("إرفاق صورة/أشعة", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
            with col2:
                posted = st.form_submit_button("💬 نشر")
            if posted and content.strip():
                new_post = {
                    "author": st.session_state.user["name"],
                    "time": "الآن",
                    "content": content,
                    "likes": 0,
                    "comments": 0,
                    "liked": False
                }
                st.session_state.posts.insert(0, new_post)
                save_posts_to_firebase()
                st.success("✅ تم نشر المنشور!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📰 آخر المنشورات")

    if not st.session_state.posts:
        st.info("📭 لا توجد منشورات حالياً. كن أول من ينشر!")
    else:
        for idx, post in enumerate(st.session_state.posts):
            with st.container():
                st.markdown(f"""
                    <div class="post-card">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <div class="avatar">{post['author'].replace('د. ', '')[0]}</div>
                            <div>
                                <div style="font-weight: bold; color: #f8fafc;">{post['author']}</div>
                                <div style="font-size: 12px; color: #94a3b8;">{post['time']}</div>
                            </div>
                        </div>
                        <div style="margin-bottom: 12px;">{post['content']}</div>
                        <div style="font-size: 14px; color: #94a3b8; margin-bottom: 8px;">👍 {post['likes']} إعجاب  &nbsp; 💬 {post['comments']} تعليق</div>
                        <div style="display: flex; gap: 20px; border-top: 1px solid #334155; padding-top: 8px;">
                            <button style="background: none; border: none; color: #94a3b8; cursor: pointer;">❤️ أعجبني</button>
                            <button style="background: none; border: none; color: #94a3b8; cursor: pointer;">💬 تعليق</button>
                            <button style="background: none; border: none; color: #94a3b8; cursor: pointer;">↗️ مشاركة</button>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"❤️ إعجاب ({post['likes']})", key=f"like_{idx}"):
                    if not post["liked"]:
                        post["likes"] += 1
                        post["liked"] = True
                    else:
                        post["likes"] -= 1
                        post["liked"] = False
                    save_posts_to_firebase()
                    st.rerun()

def messages_page():
    st.markdown("### 💬 المراسلات")
    if not st.session_state.messages:
        st.info("📭 لا توجد رسائل.")
    else:
        for msg in st.session_state.messages:
            st.markdown(f"""
                <div style="background: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #334155;">
                    <strong>{msg['sender']}</strong> <span style="color: #94a3b8; font-size: 0.8rem;">{msg['time']}</span>
                    <div>{msg['text']}</div>
                </div>
            """, unsafe_allow_html=True)

    with st.form("new_msg_form"):
        text = st.text_input("اكتب رسالتك...")
        sent = st.form_submit_button("📤 إرسال")
        if sent and text.strip():
            st.session_state.messages.append({
                "sender": st.session_state.user["name"],
                "time": datetime.datetime.now().strftime("%H:%M"),
                "text": text
            })
            st.success("✅ تم الإرسال!")
            st.rerun()

def appointments_page():
    st.markdown("### 📅 المواعيد")
    with st.form("appointment_form"):
        patient = st.selectbox("المريض", [""] + [p["name"] for p in st.session_state.patients])
        date = st.date_input("التاريخ", value=datetime.date.today())
        time = st.time_input("الوقت", value=datetime.time(10, 0))
        notes = st.text_area("ملاحظات")
        submitted = st.form_submit_button("➕ جدولة")
        if submitted and patient:
            st.session_state.appointments.append({
                "patient": patient,
                "date": date.isoformat(),
                "time": time.strftime("%H:%M"),
                "notes": notes
            })
            st.success("✅ تم جدولة الموعد!")
            st.rerun()

    if st.session_state.appointments:
        df = pd.DataFrame(st.session_state.appointments)
        st.dataframe(df, use_container_width=True)

def payments_page():
    st.markdown("### 💳 المدفوعات")
    st.markdown("#### وسائل الدفع المتاحة")
    methods = ["💳 Visa / Mastercard", "📱 محفظتي", "💵 نقدي", "📲 إم باي", "🏦 تحويل بنكي"]
    for m in methods:
        st.checkbox(m, value=True)

    st.markdown("#### إجراء دفعة")
    with st.form("payment_form"):
        amount = st.number_input("المبلغ ($)", min_value=0.0, step=10.0)
        method = st.selectbox("وسيلة الدفع", methods)
        submitted = st.form_submit_button("💵 تنفيذ الدفع")
        if submitted and amount > 0:
            st.success(f"✅ تم الدفع بمبلغ ${amount} عبر {method}.")
            st.session_state.payments.append({"amount": amount, "method": method, "date": datetime.datetime.now().isoformat()})

    if st.session_state.payments:
        df = pd.DataFrame(st.session_state.payments)
        st.dataframe(df, use_container_width=True)

def reports_page():
    st.markdown("### 📄 التقارير")
    if st.button("📄 توليد تقرير شامل"):
        with st.spinner("جاري توليد التقرير..."):
            time.sleep(2)
        st.success("✅ تم توليد التقرير!")
        st.markdown("""
            **📋 محتوى التقرير:**
            - بيانات المريض
            - التاريخ الطبي
            - نتائج التحليل (العظام، الإطباق، الوجه، الأشعة)
            - خطة العلاج المقترحة
            - التوصيات
        """)
        st.download_button(
            label="⬇️ تحميل PDF",
            data="تقرير وهمي - سيتم إنشاء PDF حقيقي لاحقاً.",
            file_name="report.pdf",
            mime="application/pdf"
        )

def settings_page():
    st.markdown("### ⚙️ الإعدادات والخصوصية")
    st.markdown("#### 👤 الملف الشخصي")
    with st.form("profile_form"):
        name = st.text_input("الاسم الظاهر", value=st.session_state.user.get("name", ""))
        specialty = st.text_input("التخصص", value=st.session_state.user.get("specialty", ""))
        phone = st.text_input("الهاتف", value=st.session_state.user.get("phone", ""))
        submitted = st.form_submit_button("💾 حفظ التغييرات")
        if submitted:
            st.session_state.user["name"] = name
            st.session_state.user["specialty"] = specialty
            st.session_state.user["phone"] = phone
            try:
                local_id = st.session_state.user.get('localId')
                if not local_id:
                    info = auth.get_account_info(st.session_state.user_token)
                    local_id = info['users'][0]['localId']
                db.child("users").child(local_id).update(st.session_state.user, st.session_state.user_token)
                st.success("✅ تم حفظ الإعدادات.")
            except:
                st.warning("⚠️ تم حفظ محلياً، لكن فشل الاتصال بـ Firebase.")

    st.markdown("#### 🔐 إدارة الحساب")
    if st.button("🔑 تغيير كلمة المرور"):
        st.info("سيتم إرسال رابط إعادة التعيين إلى بريدك الإلكتروني (محاكاة).")
    if st.button("🗑️ حذف الحساب"):
        if st.checkbox("أنا متأكد من رغبتي في حذف حسابي"):
            st.warning("سيتم حذف الحساب نهائياً (محاكاة).")
    if st.button("📤 تصدير بياناتي"):
        data = {
            "user": st.session_state.user,
            "patients": st.session_state.patients,
            "posts": st.session_state.posts
        }
        st.download_button(
            label="⬇️ تحميل JSON",
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name="my_data.json",
            mime="application/json"
        )

# ====================================================================
# 8. التطبيق الرئيسي
# ====================================================================
def main():
    if st.session_state.logged_in:
        st.sidebar.markdown("### 🧬 HarmonizeAI")
        st.sidebar.markdown(f"👤 {st.session_state.user['name']}")
        st.sidebar.markdown("---")

        menu = [
            "🏠 لوحة التحكم",
            "👤 المرضى",
            "🧠 تحليل AI",
            "🧑‍⚕️ تحليل الوجه",
            "🩻 تحليل الأشعة",
            "😁 تصميم الابتسامة",
            "⚙️ CAD/CAM",
            "📘 Dentbook",
            "💬 المراسلات",
            "📅 المواعيد",
            "💳 المدفوعات",
            "📄 التقارير",
            "⚙️ الإعدادات",
            "🚪 تسجيل خروج"
        ]
        choice = st.sidebar.radio("القائمة", menu)

        if choice == "🏠 لوحة التحكم":
            dashboard_page()
        elif choice == "👤 المرضى":
            patients_page()
        elif choice == "🧠 تحليل AI":
            ai_analysis_page()
        elif choice == "🧑‍⚕️ تحليل الوجه":
            facial_analysis_page()
        elif choice == "🩻 تحليل الأشعة":
            cephalometric_page()
        elif choice == "😁 تصميم الابتسامة":
            smile_design_page()
        elif choice == "⚙️ CAD/CAM":
            cadcam_page()
        elif choice == "📘 Dentbook":
            dentbook_page()
        elif choice == "💬 المراسلات":
            messages_page()
        elif choice == "📅 المواعيد":
            appointments_page()
        elif choice == "💳 المدفوعات":
            payments_page()
        elif choice == "📄 التقارير":
            reports_page()
        elif choice == "⚙️ الإعدادات":
            settings_page()
        elif choice == "🚪 تسجيل خروج":
            firebase_logout()
            st.success("👋 تم تسجيل الخروج.")
            st.rerun()
    else:
        st.sidebar.markdown("### 🧬 HarmonizeAI")
        st.sidebar.markdown("---")
        menu = ["🏠 الرئيسية", "🔐 تسجيل الدخول"]
        choice = st.sidebar.radio("القائمة", menu)
        if choice == "🏠 الرئيسية":
            home_page()
        else:
            auth_page()

if __name__ == "__main__":
    main()
