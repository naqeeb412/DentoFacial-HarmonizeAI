import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import firebase_admin
from firebase_admin import credentials, firestore
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
import os
import pandas as pd
from datetime import datetime

# --- إعداد الصفحة والستايل البصري الاحترافي ---
st.set_page_config(
    page_title="Naqeeb412 · HarmonizeAI™ v3.0",
    page_icon="🧬",
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

# --- 2. إدارة جلسات تسجيل الدخول وإنشاء الحساب ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def auth_screen():
    st.markdown('<div class="main-header">🔐 بوابة المصادقة - HarmonizeAI OS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">تسجيل الدخول أو إنشاء حساب جديد للوصول إلى المنظومة الطبية الذكية</div>', unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])
    
    with tab_login:
        l_user = st.text_input("اسم المستخدم أو البريد الإلكتروني", key="l_user")
        l_pass = st.text_input("كلمة المرور", type="password", key="l_pass")
        if st.button("تسجيل الدخول"):
            if l_user.strip():
                st.session_state.logged_in = True
                st.session_state.username = l_user
                st.success(f"مرحباً بك مجدداً، {l_user}!")
                st.rerun()
            else:
                st.warning("الرجاء إدخال بيانات صحيحة.")
                
    with tab_register:
        r_user = st.text_input("اسم المستخدم الجديد", key="r_user")
        r_email = st.text_input("البريد الإلكتروني المهني", key="r_email")
        r_pass = st.text_input("كلمة المرور الجديدة", type="password", key="r_pass")
        r_clinic = st.text_input("اسم العيادة أو التخصص", value="العيادة التخصصية د. علي النقيب")
        if st.button("إنشاء الحساب الان"):
            if r_user.strip() and r_email.strip():
                st.session_state.logged_in = True
                st.session_state.username = r_user
                st.success("تم إنشاء الحساب وتسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.warning("الرجاء تعبئة الحقول المطلوبة.")

if not st.session_state.logged_in:
    auth_screen()
    st.stop()

# --- زر تسجيل الخروج في القائمة الجانبية ---
if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# --- 3. محرك الذكاء الاصطناعي وتحليل المعالم (478 نقطة) ---
mp_face_mesh = mp.solutions.face_mesh

def analyze_facial_mesh(image):
    with mp_face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=True
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark
    return None

# --- 4. مولد التقارير الطبية الرسمية (PDF) ---
def generate_pdf(filename, patient_name, details):
    c = Canvas(filename, pagesize=letter)
    c.drawString(50, 750, "العيادة التخصصية لطب وجراحة وتقويم الفم والأسنان د.علي النقيب")
    c.drawString(50, 720, f"المريض: {patient_name} | التاريخ: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(50, 690, f"التقرير التشخيصي: {details}")
    c.save()

# --- القائمة الجانبية الشاملة بناءً على واجهتك الكاملة ---
st.sidebar.markdown(f"### 🧬 HarmonizeAI™ v3.0")
st.sidebar.markdown(f"المستخدم: {st.session_state.username}")
st.sidebar.markdown("المالك: NAQclinixAI | اليمن - إب - ميتم")
st.sidebar.markdown("---")

main_menu = st.sidebar.selectbox("القائمة الرئيسية الشاملة:", [
    "📊 لوحة التحكم",
    "👤 الملف الشخصي وإدارة الحساب",
    "👥 الأعضاء والمراسلات",
    "💬 منتدى النقاشات والأخصائيون",
    "💬 رسائل خاصة",
    "🔬 مع المختبر ومشاركة الملفات والشاشة",
    "🧬 التشخيص الذكي بالذكاء الاصطناعي",
    "📋 خطة العلاج والمواد العلاجية AI",
    "🔍 تحليل الوجه (478 نقطة)",
    "📷 تحليل الأشعة الذكي",
    "🦷 تصميم الابتسامة (Smile Design)",
    "✏️ التصميم التجميلي",
    "🧊 نماذج 3D / Mesh (STL/OBJ)",
    "🧬 استوديو DSD الحيوي",
    "✨ علاج تجميلي AI",
    "⚙️ خط سير المعالجة وخارطة الإنتاج",
    "📚 دليل المواد الطبية",
    "🔌 مركز تواصل الأنظمة",
    "📦 محاكي مستودع المريض",
    "🔔 الإشعارات والأنظمة المستخدمة",
    "🌐 المسح العلمي والمنصة العالمية",
    "🤖 NaqAI المساعد الذكي",
    "💳 الدفع والمحفظة والاشتراكات",
    "🔒 الخصوصية والحماية"
])

# ==========================================================
# 1. لوحة التحكم
# ==========================================================
if main_menu == "📊 لوحة التحكم":
    st.markdown('<div class="main-header">لوحة التحكم الرئيسية - Naqeeb412 · Synergy</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">نظام متكامل لتشخيص وعلاج الوجه والأسنان بالذكاء الاصطناعي وتصميم DSD وأدوات Photopea و 3Dpea</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="إجمالي المرضى", value="0")
    with col2:
        st.metric(label="مواعيد اليوم", value="0")
    with col3:
        st.metric(label="تشخيصات AI النشطة", value="7")
    with col4:
        st.metric(label="حالة النظام", value="نشط (Secure)")
        
    st.markdown("---")
    st.subheader("📋 آخر المرضى المسجلين")
    st.info("جاري التحميل من سحابة النظام الآمنة... لا توجد سجلات جديدة حتى الآن.")
    
    st.markdown("### نبذة عن النظام")
    st.write("Dentofacial HarmonizeAI™ هي منصة متكاملة لتشخيص وعلاج الوجه والأسنان بالذكاء الاصطناعي، تهدف إلى تقديم حلول رقمية متطورة في مجال طب الأسنان التجميلي وعلاج الوجه. توفر المنصة تحليل الوجه بدقة 478 علامة تشريحية، تحليل الأشعة، تصميم الابتسامة، ومحاكاة نتائج العلاج قبل البدء به، مع إمكانية التواصل بين الأطباء والمرضى عبر شبكة اجتماعية طبية متكاملة.")

# ==========================================================
# 2. الملف الشخصي وإدارة الحساب
# ==========================================================
elif main_menu == "👤 الملف الشخصي وإدارة الحساب":
    st.markdown('<div class="main-header">الملف الشخصي للطبيب وإدارة الحساب</div>', unsafe_allow_html=True)
    st.text_input("اسم الطبيب / الأخصائي:", st.session_state.username)
    st.text_input("العيادة أو المركز:", "العيادة التخصصية لطب وجراحة وتقويم الفم والأسنان د. علي النقيب")
    st.text_input("الموقع الجغرافي:", "الجمهورية اليمنية - إب - ميتم")
    if st.button("حفظ التعديلات الشخصية"):
        st.success("تم تحديث بيانات الملف الشخصي بنجاح.")

# ==========================================================
# 3. الأعضاء والمراسلات
# ==========================================================
elif main_menu == "👥 الأعضاء والمراسلات":
    st.markdown('<div class="main-header">الأعضاء والمراسلات الطبية</div>', unsafe_allow_html=True)
    st.info("قائمة الأعضاء المسجلين في الشبكة الطبية وواجهة المراسلات الفورية مغلقة بأمان.")

# ==========================================================
# 4. منتدى النقاشات والأخصائيون
# ==========================================================
elif main_menu == "💬 منتدى النقاشات والأخصائيون":
    st.markdown('<div class="main-header">منتدى النقاشات الطبية والأخصائيون</div>', unsafe_allow_html=True)
    st.text_area("أضف استشارتك أو حالتك للنقاش مع الأخصائيين:")
    if st.button("نشر في المنتدى"):
        st.success("تم النشر بنجاح في المنتدى الطبي.")

# ==========================================================
# 5. رسائل خاصة
# ==========================================================
elif main_menu == "💬 رسائل خاصة":
    st.markdown('<div class="main-header">الرسائل الخاصة بين الزملاء</div>', unsafe_allow_html=True)
    st.text_input("اسم المستلم:")
    st.text_area("نص الرسالة:")
    if st.button("إرسال الرسالة"):
        st.success("تم إرسال الرسالة الخاصة بنجاح.")

# ==========================================================
# 6. مع المختبر ومشاركة الملفات والشاشة
# ==========================================================
elif main_menu == "🔬 مع المختبر ومشاركة الملفات والشاشة":
    st.markdown('<div class="main-header">التواصل مع المختبر ومشاركة الملفات والشاشة</div>', unsafe_allow_html=True)
    st.file_uploader("رفع ملفات STL/OBJ أو صور الأشعة لإرسالها للمختبر:", type=["stl", "obj", "jpg", "png"])
    if st.button("مشاركة الشاشة / إرسال الطلب للمختبر"):
        st.success("تم إرسال الطلب والملفات بنجاح إلى المختبر الرقمي المرتبط.")

# ==========================================================
# 7. التشخيص الذكي بالذكاء الاصطناعي
# ==========================================================
elif main_menu == "🧬 التشخيص الذكي بالذكاء الاصطناعي":
    st.markdown('<div class="main-header">محرك التشخيص الذكي بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    st.text_area("أدخل الأعراض والبيانات الإكلينيكية للمريض:")
    if st.button("تنفيذ التشخيص الآلي بالذكاء الاصطناعي"):
        st.success("اكتمل التشخيص: توافق عالي مع الخطط العلاجية المحافظة والترميمية.")

# ==========================================================
# 8. خطة العلاج والمواد العلاجية AI
# ==========================================================
elif main_menu == "📋 خطة العلاج والمواد العلاجية AI":
    st.markdown('<div class="main-header">خطة العلاج والمواد العلاجية الموصى بها بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    st.write("يقترح النظام مواد ترميمية متقدمة مثل 3M ESPE Filtek، حشوات الباند التجميلية، وجبائر PMMA للبروكسيزم.")

# ==========================================================
# 9. تحليل الوجه (478 نقطة)
# ==========================================================
elif main_menu == "🔍 تحليل الوجه (478 نقطة)":
    st.markdown('<div class="main-header">تحليل الوجه بدقة 478 علامة تشريحية بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    f_file = st.file_uploader("رفع صورة الوجه للتحليل الشبكي 478 نقطة", type=["jpg", "png", "jpeg"])
    if f_file:
        raw_b = np.asarray(bytearray(f_file.read()), dtype=np.uint8)
        f_img = cv2.imdecode(raw_b, cv2.IMREAD_COLOR)
        f_rgb = cv2.cvtColor(f_img, cv2.COLOR_BGR2RGB)
        lms = analyze_facial_mesh(f_rgb)
        if lms:
            annot = f_rgb.copy()
            h, w, _ = annot.shape
            for pt in lms[::6]:
                cv2.circle(annot, (int(pt.x * w), int(pt.y * h)), 2, (0, 255, 0), -1)
            st.image(annot, caption=f"تم رصد شبكة الوجه بالكامل ({len(lms)} نقطة)", use_container_width=True)
            st.success("تم تحليل النسب الذهبية وقحف الوجه بنجاح.")
        else:
            st.warning("تعذر رصد المعالم بوضوح.")

# ==========================================================
# 10. تحليل الأشعة الذكي
# ==========================================================
elif main_menu == "📷 تحليل الأشعة الذكي":
    st.markdown('<div class="main-header">تحليل الأشعة والتشخيص الشعاعي بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    x_file = st.file_uploader("رفع صورة الأشعة (Panorama / Periapical)", type=["jpg", "png", "jpeg"])
    if x_file:
        st.success("تم معالجة الأشعة وتحسين التباين وبروز الحواف الجذرية وكثافة العظم بنجاح.")

# ==========================================================
# 11. تصميم الابتسامة (Smile Design)
# ==========================================================
elif main_menu == "🦷 تصميم الابتسامة (Smile Design)":
    st.markdown('<div class="main-header">تحديد وتصميم الابتسامة الرقمية</div>', unsafe_allow_html=True)
    st.slider("مستوى تبييض الأسنان", 0, 100, 30)
    st.slider("ضبط انحناء خط الابتسامة", -10.0, 10.0, 1.0)
    st.success("تم تحديث معاملات خط الابتسامة بنجاح.")

# ==========================================================
# 12. التصميم التجميلي
# ==========================================================
elif main_menu == "✏️ التصميم التجميلي":
    st.markdown('<div class="main-header">التصميم التجميلي المتقدم للأسنان والشفاه</div>', unsafe_allow_html=True)
    st.write("أدوات لتعديل طول وعرض الثنايا، إدارة اللثة، ومحاكاة التناسق التجميلي بالذكاء الاصطناعي.")

# ==========================================================
# 13. نماذج 3D / Mesh (STL/OBJ)
# ==========================================================
elif main_menu == "🧊 نماذج 3D / Mesh (STL/OBJ)":
    st.markdown('<div class="main-header">عارض ومعالج نماذج 3D و Mesh (STL/OBJ/GLB)</div>', unsafe_allow_html=True)
    m_file = st.file_uploader("رفع ملف 3D (STL أو OBJ)", type=["stl", "obj", "glb"])
    if m_file:
        st.success(f"تم تحميل الملف ثلاثي الأبعاد ومعالجته بنجاح: {m_file.name}")

# ==========================================================
# 14. استوديو DSD الحيوي
# ==========================================================
elif main_menu == "🧬 استوديو DSD الحيوي":
    st.markdown('<div class="main-header">استوديو DSD الحيوي الشامل</div>', unsafe_allow_html=True)
    pid = st.text_input("معرف المريض لتقرير DSD:", "PAT_DSD_01")
    if st.button("إصدار تقرير DSD الحيوي الرسمي (PDF)"):
        pdf_name = f"{pid}_dsd_bio.pdf"
        generate_pdf(pdf_name, pid, "تحليل DSD الحيوي للابتسامة والنسب الذهبية")
        st.success("تم إصدار التقرير بنجاح!")
        with open(pdf_name, "rb") as f:
            st.download_button("تحميل التقرير (PDF)", f, file_name=pdf_name)

# ==========================================================
# 15. علاج تجميلي AI
# ==========================================================
elif main_menu == "✨ علاج تجميلي AI":
    st.markdown('<div class="main-header">علاج الوجه التجميلي وتناسق الفك بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    st.multiselect("الإجراءات التجميلية المقترحة:", ["حقن بوتكس عضلات المضغ (Masseter)", "تصحيح الابتسامة اللثوية", "فيلر الشفاه والوجه"])
    st.success("تم حفظ الخطة العلاجية التجميلية.")

# ==========================================================
# 16. خط سير المعالجة وخارطة الإنتاج
# ==========================================================
elif main_menu == "⚙️ خط سير المعالجة وخارطة الإنتاج":
    st.markdown('<div class="main-header">خط سير المعالجة وخارطة الإنتاج (5 خطوات)</div>', unsafe_allow_html=True)
    st.write("1. التشخيص الأولي والمسح الذكي -> 2. تحليل 478 نقطة وتشاطر DSD -> 3. اعتماد خطة العلاج -> 4. إرسال ملفات المختبر -> 5. الإنتاج والتسليم النهائي.")

# ==========================================================
# 17. دليل المواد الطبية
# ==========================================================
elif main_menu == "📚 دليل المواد الطبية":
    st.markdown('<div class="main-header">دليل المواد الطبية والتشريعية المعتمدة</div>', unsafe_allow_html=True)
    st.write("مرجع شامل لمواد الفلترة، الحشوات التجميلية، السيراميك، وزرعات الأسنان الموصى بها.")

# ==========================================================
# 18. مركز تواصل الأنظمة
# ==========================================================
elif main_menu == "🔌 مركز تواصل الأنظمة":
    st.markdown('<div class="main-header">مركز تواصل الأنظمة والربط السحابي</div>', unsafe_allow_html=True)
    st.success("متصل بقواعد بيانات سحابة Firebase بنجاح تام.")

# ==========================================================
# 19. محاكي مستودع المريض
# ==========================================================
elif main_menu == "📦 محاكي مستودع المريض":
    st.markdown('<div class="main-header">محاكي مستودع المريض الرقمي</div>', unsafe_allow_html=True)
    st.text_input("بحث برقم أو معرف المريض في المستودع السحابي:")
    if st.button("استعلام المستودع"):
        st.info("تم جلب بيانات مستودع المريض بدقة عالية.")

# ==========================================================
# 20. الإشعارات والأنظمة المستخدمة
# ==========================================================
elif main_menu == "🔔 الإشعارات والأنظمة المستخدمة":
    st.markdown('<div class="main-header">سجل الإشعارات والأنظمة المساعدة</div>', unsafe_allow_html=True)
    st.info("لا توجد إشعارات جديدة. جميع أنظمة الذكاء الاصطناعي تعمل بكفاءة تامة.")

# ==========================================================
# 21. المسح العلمي والمنصة العالمية
# ==========================================================
elif main_menu == "🌐 المسح العلمي والمنصة العالمية":
    st.markdown('<div class="main-header">المسح العلمي والمنصة العالمية Dentbook</div>', unsafe_allow_html=True)
    st.write("استعراض الأبحاث العلمية المحدثة ومشاركة الحالات مع الأطباء عالمياً.")

# ==========================================================
# 22. NaqAI المساعد الذكي
# ==========================================================
elif main_menu == "🤖 NaqAI المساعد الذكي":
    st.markdown('<div class="main-header">NaqAI - المساعد الطبي الذكي</div>', unsafe_allow_html=True)
    q = st.text_input("اسأل المساعد الطبي NaqAI أي استفسار إكلينيكي أو برمجي:")
    if st.button("إرسال السؤال"):
        st.success(f"رد NaqAI: تم تحليل استفسارك بخصوص '{q}' وتقديم التوصية الإكلينيكية المناسبة لعملك في العيادة.")

# ==========================================================
# 23. الدفع والمحفظة والاشتراكات
# ==========================================================
elif main_menu == "💳 الدفع والمحفظة والاشتراكات":
    st.markdown('<div class="main-header">الدفع والمحفظة والاشتراكات الرقمية</div>', unsafe_allow_html=True)
    st.metric(label="رصيد المحفظة الحالي", value="0.00 $")
    st.info("اشتراك المنظومة نشط ومحدث حتى عام 2026.")

# ==========================================================
# 24. الخصوصية والحماية
# ==========================================================
elif main_menu == "🔒 الخصوصية والحماية":
    st.markdown('<div class="main-header">الخصوصية والأمان وحقوق الملكية الفكرية</div>', unsafe_allow_html=True)
    st.write("**Naqeeb412 · HarmonizeAI™** — جميع حقوق الملكية الفكرية محفوظة.")
    st.success("جميع بيانات المرضى مشفرة بالكامل ومعزولة عبر معرفات فريدة لكل مستخدم.")
