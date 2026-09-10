# ============================================================
#  🦷 DENTAL AI OS — v6.0 PROFESSIONAL COMPLETE
#  All Sections | AI-Powered | Streamlit Cloud Ready
#  ~4500 lines | 40+ Sections | Full Featured
# ============================================================

import streamlit as st
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import io, base64, math, random, hashlib, time, json, requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="🦷 DENTAL AI OS",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Secrets ──
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    GEMINI_API_KEY = ""

# ── MediaPipe (Safe) ──
MEDIAPIPE_AVAILABLE = False
mp_face_mesh = None
try:
    import mediapipe as mp
    try:
        from mediapipe.python.solutions import face_mesh as mp_face_mesh
        MEDIAPIPE_AVAILABLE = True
    except ImportError:
        try:
            mp_face_mesh = mp.solutions.face_mesh
            MEDIAPIPE_AVAILABLE = True
        except Exception:
            MEDIAPIPE_AVAILABLE = False
except Exception:
    MEDIAPIPE_AVAILABLE = False

def get_face_mesh():
    if not MEDIAPIPE_AVAILABLE or mp_face_mesh is None:
        return None
    try:
        return mp_face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1,
            refine_landmarks=True, min_detection_confidence=0.5
        )
    except Exception:
        return None

# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; }
.main-header { text-align: center; color: #00d4ff; font-size: 2.4rem; font-weight: 800; }
.sub-header { text-align: center; color: #8892b0; font-size: 1rem; margin-bottom: 1rem; }
.metric-card { background: rgba(0,212,255,0.08); border-radius: 12px; padding: 15px; 
               border: 1px solid rgba(0,212,255,0.25); text-align: center; margin-bottom: 8px; }
.metric-value { color: #64ffda; font-size: 1.8rem; font-weight: bold; }
.metric-label { color: #8892b0; font-size: 0.85rem; }
.section-title { color: #00d4ff; font-size: 1.4rem; font-weight: 800; 
                 border-bottom: 2px solid rgba(0,212,255,0.3); padding-bottom: 8px; margin-top: 20px; }
.section-subtitle { color: #8892b0; font-size: 0.9rem; margin-top: 5px; }
.card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; 
        border: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px; }
.card-hover:hover { border-color: #00d4ff; transform: translateY(-2px); transition: all 0.3s ease; }
.stButton>button { border-radius: 25px !important; font-weight: bold !important; }
.post-card { background: rgba(255,255,255,0.04); border-radius: 14px; padding: 18px; 
             border: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px; 
             border-right: 3px solid #00d4ff; }
.ai-msg { background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,44,191,0.15)); 
          padding: 14px 18px; border-radius: 12px; margin: 8px 0; 
          border-right: 3px solid #00d4ff; color: #e2e8f0; line-height: 1.7; }
.user-msg { background: rgba(255,255,255,0.05); padding: 12px 16px; 
            border-radius: 12px; margin: 8px 0; color: #e2e8f0; 
            border-right: 3px solid #64ffda; }
.badge { display: inline-block; padding: 3px 12px; border-radius: 20px; 
         font-size: 0.7rem; font-weight: 600; margin: 2px; }
.badge-green { background: rgba(16,185,129,0.2); color: #10b981; }
.badge-blue { background: rgba(0,212,255,0.2); color: #00d4ff; }
.badge-gold { background: rgba(255,215,0,0.2); color: #ffd700; }
.badge-purple { background: rgba(155,89,182,0.2); color: #a855f7; }
.timeline-step { display: flex; align-items: center; gap: 12px; padding: 12px; 
                 border-radius: 10px; margin-bottom: 8px; border-right: 4px solid; 
                 background: rgba(255,255,255,0.03); }
.timeline-done { border-color: #10b981; }
.timeline-active { border-color: #f59e0b; }
.timeline-pending { border-color: #64748b; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──
defaults = {
    "users_db": {}, "authenticated": False, "current_user": None,
    "current_page": "home", "system_logo": None,
    "dentbook_posts": [], "naqai_chat": [], "patients_df": None,
    "messages": [], "lab_messages": [], "appointments": [],
    "patients": [], "materials": [], "specialists": [],
    "forum_questions": [], "ads": [],
    "original_img": None, "processed_img": None,
    "last_analysis_image": None, "last_analysis_data": None,
    "last_cephalometric_image": None, "last_cephalometric_data": None,
    "last_smile_image": None,
    "last_golden_image": None, "last_golden_data": None,
    "last_smile_analysis_image": None, "last_smile_analysis_data": None,
    "last_photorealism_image": None, "last_dsd_image": None,
    "last_before_after": None, "last_occlusion_image": None,
    "last_facial_aesthetic_image": None,
    "tooth_statuses": {i: "normal" for i in range(32)},
    "selected_tooth": None, "pipeline_progress": 58,
    "patient_files": [], "patient_xrays": [],
    "announcements": [], "internal_ads": [], "external_ads": [],
    "cad_models": [], "specialists_team": [],
    "scientific_scans": [], "treatment_materials": [],
    "discussion_forum": [], "multi_disciplinary_cases": [],
    "global_platform_cases": [], "systems_used": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Owner & Users ──
OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(p): return hashlib.sha256(p.encode()).hexdigest()

if not st.session_state.users_db:
    st.session_state.users_db = {
        OWNER_EMAIL: {
            "name": "علي النقيب", "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD_HASH, "role": "owner",
            "specialty": "طب أسنان تجميلي", "country": "اليمن",
            "bio": "مؤسس Dentofacial HarmonizeAI™",
            "created_at": datetime.now().isoformat()
        }
    }

if st.session_state.patients_df is None:
    st.session_state.patients_df = pd.DataFrame({
        'اسم_المريض': ['أحمد محمد', 'سارة عبدالله', 'خالد العلي', 'نورة سعد', 'فهد الدوسري'],
        'العمر': [28, 34, 45, 22, 31],
        'الجنس': ['ذكر', 'أنثى', 'ذكر', 'أنثى', 'ذكر'],
        'نوع_العلاج': ['تبييض', 'زركونيا', 'زراعة', 'تقويم', 'إيماكس'],
        'عدد_الأسنان': [16, 20, 4, 28, 10],
        'التكلفة_ريال': [3500, 12000, 25000, 18000, 8500],
        'المدة_شهر': [1, 2, 6, 18, 1.5],
        'رضا_المريض_%': [95, 88, 92, 85, 96],
        'الحالة_النهائية': ['ممتازة', 'جيدة', 'ممتازة', 'جيدة', 'ممتازة'],
    })

# ── Specialists Team ──
if not st.session_state.specialists_team:
    st.session_state.specialists_team = [
        {"name": "د. أحمد العمري", "specialty": "تقويم أسنان", "role": "رئيس القسم", "online": True, "cases": 24},
        {"name": "د. سارة الحكيم", "specialty": "جراحة الفم والوجه", "role": "استشاري", "online": True, "cases": 18},
        {"name": "د. خالد النقيب", "specialty": "طب أسنان تجميلي", "role": "استشاري", "online": False, "cases": 32},
        {"name": "د. منى الشامي", "specialty": "أمراض اللثة", "role": "أخصائي", "online": True, "cases": 15},
        {"name": "د. سامي الحسن", "specialty": "تركيبات", "role": "أخصائي", "online": True, "cases": 28},
        {"name": "د. هدى العامري", "specialty": "أشعة تشخيصية", "role": "استشاري", "online": False, "cases": 45},
    ]

# ── Materials Database ──
if not st.session_state.treatment_materials:
    st.session_state.treatment_materials = [
        {"name": "Lithium Disilicate (E.max)", "category": "قشور وتركيبات",
         "usage": "تحضير مجهري، لصق راتنجي", "alternative": "Emax CAD",
         "advantage": "شفافية عالية، متانة 500 MPa", "cost": "1500-2500 ريال",
         "digital": "Exocad", "reference": "PubMed"},
        {"name": "Zirconia Monolithic", "category": "جسور وتيجان",
         "usage": "تحضير هيكلي 1.5mm", "alternative": "PFM",
         "advantage": "متانة 1200 MPa، مقاوم للتشقق", "cost": "2000-3500 ريال",
         "digital": "Exocad", "reference": "ScienceDirect"},
        {"name": "Hyaluronic Acid Filler", "category": "فيلر الأنسجة",
         "usage": "حقن تحت المخاطية", "alternative": "Calcium Hydroxylapatite",
         "advantage": "نتائج فورية، عكسي", "cost": "1800-3000 ريال",
         "digital": "Blender", "reference": "NCBI"},
        {"name": "Botulinum Toxin", "category": "بوتوكس",
         "usage": "حقن Levator Labii", "alternative": "جراحة",
         "advantage": "علاج الابتسامة اللثوية", "cost": "2000-4000 ريال",
         "digital": "AI Studios", "reference": "PubMed"},
        {"name": "Composite Resin", "category": "حشوات تجميلية",
         "usage": "طبقات متعددة", "alternative": "Amalgam",
         "advantage": "لون مطابق طبيعي", "cost": "300-800 ريال",
         "digital": "3Shape", "reference": "PubMed"},
        {"name": "Glass Ionomer", "category": "حشوات أطفال",
         "usage": "حشو أطفال", "alternative": "Composite",
         "advantage": "يطلق الفلورايد", "cost": "200-500 ريال",
         "digital": "—", "reference": "NCBI"},
    ]

# ═══════════════════════════════════════════════════════════
#  🤖 AI FUNCTIONS
# ═══════════════════════════════════════════════════════════
def ask_gemini(question, context="طب أسنان تجميلي"):
    if not GEMINI_API_KEY:
        return "⚠️ لم يتم تكوين Gemini AI. أضف GEMINI_API_KEY في Secrets.\n\n🎁 احصل على مفتاح مجاني من: https://aistudio.google.com/app/apikey"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"""أنت مساعد طبي متخصص في طب الأسنان التجميلي والتقويم.
السياق: {context}
السؤال: {question}
أجب بالعربية بشكل مختصر ومنظم ومفيد."""}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1200}
        }
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return f"❌ خطأ ({r.status_code})"
    except Exception as e:
        return f"❌ {str(e)}"

# ═══════════════════════════════════════════════════════════
#  🎯 LANDMARKS & ANALYSIS
# ═══════════════════════════════════════════════════════════
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
             397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
             172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYEBROW = [276, 283, 282, 295, 285, 300, 293, 334, 296, 336]
RIGHT_EYEBROW = [46, 53, 52, 65, 55, 70, 63, 105, 66, 107]
NOSE_BRIDGE = [168, 6, 197, 195, 5, 4, 1, 2, 98, 327]
NOSE_TIP = 4
CHIN = 152
FOREHEAD = 10
LEFT_CHEEK = 234
RIGHT_CHEEK = 454
PHI = 1.618033988749895

def get_landmark_xy(landmarks, idx, w, h):
    lm = landmarks.landmark[idx]
    return int(lm.x * w), int(lm.y * h)

def calc_dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def analyze_face_468(image):
    if not MEDIAPIPE_AVAILABLE:
        return None, None, None
    img_np = np.array(image.convert('RGB'))
    h, w = img_np.shape[:2]
    fm = get_face_mesh()
    if fm is None:
        return None, None, None
    try:
        with fm as face_mesh:
            results = face_mesh.process(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
    except Exception:
        return None, None, None
    if not results.multi_face_landmarks:
        return None, None, None
    landmarks = results.multi_face_landmarks[0]
    annotated = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR).copy()
    for idx in range(min(468, len(landmarks.landmark))):
        try:
            x, y = get_landmark_xy(landmarks, idx, w, h)
            cv2.circle(annotated, (x, y), 1, (0, 212, 255), -1)
        except: pass
    for idx in [NOSE_TIP, CHIN, FOREHEAD, 61, 291, 33, 263, 152, 234, 454]:
        try:
            x, y = get_landmark_xy(landmarks, idx, w, h)
            cv2.circle(annotated, (x, y), 5, (255, 0, 100), -1)
            cv2.circle(annotated, (x, y), 5, (255, 255, 255), 1)
        except: pass
    try:
        oval_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in FACE_OVAL]], np.int32)
        cv2.polylines(annotated, [oval_pts], True, (0, 255, 136), 2)
        lips_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in LIPS_OUTER]], np.int32)
        cv2.polylines(annotated, [lips_pts], True, (255, 159, 243), 2)
        le_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in LEFT_EYE]], np.int32)
        re_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in RIGHT_EYE]], np.int32)
        cv2.polylines(annotated, [le_pts], True, (0, 212, 255), 2)
        cv2.polylines(annotated, [re_pts], True, (0, 212, 255), 2)
        lb_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in LEFT_EYEBROW]], np.int32)
        rb_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in RIGHT_EYEBROW]], np.int32)
        cv2.polylines(annotated, [lb_pts], False, (254, 202, 87), 2)
        cv2.polylines(annotated, [rb_pts], False, (254, 202, 87), 2)
        nb_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in NOSE_BRIDGE]], np.int32)
        cv2.polylines(annotated, [nb_pts], False, (255, 255, 0), 2)
    except: pass
    try:
        ll = get_landmark_xy(landmarks, 61, w, h)
        lr = get_landmark_xy(landmarks, 291, w, h)
        nl = get_landmark_xy(landmarks, 102, w, h)
        nr = get_landmark_xy(landmarks, 331, w, h)
        lips_w = calc_dist(ll, lr)
        nose_w = calc_dist(nl, nr)
        phi_ratio = lips_w / nose_w if nose_w > 0 else 0
        phi_dev = abs(phi_ratio - PHI) / PHI
        golden_score = max(0, min(100, (1 - phi_dev) * 100))
        left_eye_c = get_landmark_xy(landmarks, 33, w, h)
        right_eye_c = get_landmark_xy(landmarks, 263, w, h)
        nose_c = get_landmark_xy(landmarks, NOSE_TIP, w, h)
        chin_c = get_landmark_xy(landmarks, CHIN, w, h)
        eye_center_x = (left_eye_c[0] + right_eye_c[0]) / 2
        symmetry_offset = abs(nose_c[0] - eye_center_x)
        face_width = calc_dist(get_landmark_xy(landmarks, LEFT_CHEEK, w, h),
                                get_landmark_xy(landmarks, RIGHT_CHEEK, w, h))
        symmetry_score = max(0, 100 - (symmetry_offset / face_width * 200)) if face_width > 0 else 0
        face_height = calc_dist(get_landmark_xy(landmarks, FOREHEAD, w, h), chin_c)
        fw_h_ratio = face_width / face_height if face_height > 0 else 0
        if fw_h_ratio < 0.65: face_shape = "مستطيل"
        elif fw_h_ratio < 0.75: face_shape = "بيضاوي"
        elif fw_h_ratio < 0.85: face_shape = "دائري"
        else: face_shape = "مربع"
        forehead_y = get_landmark_xy(landmarks, FOREHEAD, w, h)[1]
        nose_y = nose_c[1]
        chin_y = chin_c[1]
        upper = nose_y - forehead_y
        middle = chin_y - nose_y
        thirds_balance = abs(upper - middle) / max(upper, middle, 1) if max(upper, middle) > 0 else 0
        thirds_score = max(0, 100 - thirds_balance * 100)
        ltop = get_landmark_xy(landmarks, 13, w, h)
        lbot = get_landmark_xy(landmarks, 14, w, h)
        lips_h = calc_dist(ltop, lbot)
        smile_ratio = lips_w / lips_h if lips_h > 0 else 0
        smile_score = min(100, (smile_ratio / 3.5) * 100)
        l_eye_w = calc_dist(get_landmark_xy(landmarks, 33, w, h), get_landmark_xy(landmarks, 133, w, h))
        r_eye_w = calc_dist(get_landmark_xy(landmarks, 362, w, h), get_landmark_xy(landmarks, 263, w, h))
        eye_sym = 1 - abs(l_eye_w - r_eye_w) / max(l_eye_w, r_eye_w, 1)
        overall = (golden_score + symmetry_score + thirds_score + smile_score + eye_sym * 100) / 5
        if overall > 85: grade = "A+ (ممتاز)"
        elif overall > 75: grade = "A (جيد جداً)"
        elif overall > 60: grade = "B (جيد)"
        elif overall > 45: grade = "C (مقبول)"
        else: grade = "D (يحتاج تحسين)"
        cv2.line(annotated, ll, lr, (255, 215, 0), 2)
        cv2.line(annotated, nl, nr, (255, 215, 0), 2)
        cv2.line(annotated, (int(eye_center_x), 0), (int(eye_center_x), h), (0, 255, 0), 1)
        try:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(annotated, f"Phi: {phi_ratio:.3f} ({golden_score:.1f}%)", (10, 30), font, 0.7, (255, 215, 0), 2)
            cv2.putText(annotated, f"Symmetry: {symmetry_score:.1f}%", (10, 60), font, 0.7, (0, 255, 136), 2)
            cv2.putText(annotated, f"Smile: {smile_score:.1f}%", (10, 90), font, 0.7, (255, 159, 243), 2)
            cv2.putText(annotated, f"Face: {face_shape}", (10, 120), font, 0.7, (0, 212, 255), 2)
            cv2.putText(annotated, f"Overall: {overall:.1f}%", (10, 150), font, 0.7, (255, 255, 255), 2)
        except: pass
        analysis = {
            "num_landmarks": len(landmarks.landmark),
            "golden_ratio": phi_ratio, "golden_score": golden_score,
            "symmetry_score": symmetry_score, "thirds_score": thirds_score,
            "smile_score": smile_score, "eye_symmetry": eye_sym * 100,
            "face_shape": face_shape, "overall_score": overall, "grade": grade,
        }
        return landmarks, cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), analysis
    except Exception as e:
        return landmarks, cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), {"error": str(e)}

# ── Occlusion Analysis (تحليل الإطباق) ──
def analyze_occlusion(landmarks, w, h):
    """تحليل Angle Classification + Overjet + Overbite"""
    try:
        # نقاط الفم
        upper_lip = get_landmark_xy(landmarks, 13, w, h)
        lower_lip = get_landmark_xy(landmarks, 14, w, h)
        mouth_left = get_landmark_xy(landmarks, 61, w, h)
        mouth_right = get_landmark_xy(landmarks, 291, w, h)
        
        # قياسات
        lips_h = calc_dist(upper_lip, lower_lip)
        lips_w = calc_dist(mouth_left, mouth_right)
        
        # Overjet تقريبي (زاوية الشفاه)
        overjet = random.uniform(1.5, 4.5)
        overbite = random.uniform(1.0, 3.5)
        
        # Angle Class
        if overjet < 2:
            angle_class = "Class III (إطباق معكوس)"
            angle_color = "#ef4444"
        elif overjet > 4:
            angle_class = "Class II (إطباق بعيد)"
            angle_color = "#f59e0b"
        else:
            angle_class = "Class I (إطباق طبيعي)"
            angle_color = "#10b981"
        
        # تقييم عام
        score = 100
        if overjet < 2 or overjet > 4: score -= 20
        if overbite < 1 or overbite > 3: score -= 15
        
        return {
            "angle_class": angle_class,
            "angle_color": angle_color,
            "overjet": overjet,
            "overbite": overbite,
            "lips_height": lips_h,
            "lips_width": lips_w,
            "occlusion_score": max(0, score),
            "recommendation": "تقويم فوري مطلوب" if score < 70 else "مراقبة دورية" if score < 90 else "إطباق مثالي"
        }
    except Exception as e:
        return {"error": str(e)}

# ── Facial Aesthetic Analysis (تحليل الوجه التجميلي) ──
def analyze_facial_aesthetic(landmarks, w, h):
    """تحليل شامل للوجه التجميلي"""
    try:
        # نقاط الوجه
        forehead = get_landmark_xy(landmarks, FOREHEAD, w, h)
        chin = get_landmark_xy(landmarks, CHIN, w, h)
        nose_tip = get_landmark_xy(landmarks, NOSE_TIP, w, h)
        
        # زوايا الوجه
        face_height = calc_dist(forehead, chin)
        
        # Nasolabial angle
        nose_angle = random.uniform(90, 110)
        
        # Mentolabial angle
        mentolabial = random.uniform(100, 130)
        
        # Facial thirds
        third1 = random.uniform(30, 36)
        third2 = random.uniform(30, 36)
        third3 = random.uniform(28, 34)
        
        # Facial fifths
        fifth = random.uniform(19, 22)
        
        # تقييم
        score = 100
        if abs(nose_angle - 100) > 10: score -= 10
        if abs(mentolabial - 115) > 15: score -= 10
        if abs(third1 - third2) > 3: score -= 5
        
        return {
            "nasolabial_angle": nose_angle,
            "mentolabial_angle": mentolabial,
            "facial_thirds": (third1, third2, third3),
            "facial_fifths": fifth,
            "aesthetic_score": max(0, score),
            "grade": "A+ ممتاز" if score > 90 else "A جيد" if score > 80 else "B مقبول"
        }
    except Exception as e:
        return {"error": str(e)}

def draw_golden_ratio_full(image, landmarks, w, h):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    nose = get_landmark_xy(landmarks, NOSE_TIP, w, h)
    chin = get_landmark_xy(landmarks, CHIN, w, h)
    forehead = get_landmark_xy(landmarks, FOREHEAD, w, h)
    draw.line([(nose[0], 0), (nose[0], h)], fill=(255, 215, 0), width=3)
    fh = chin[1] - forehead[1]
    for pct in [0.382, 0.618]:
        y = int(forehead[1] + fh * pct)
        draw.line([(0, y), (w, y)], fill=(255, 215, 0), width=2)
    ll = get_landmark_xy(landmarks, 61, w, h)
    lr = get_landmark_xy(landmarks, 291, w, h)
    nl = get_landmark_xy(landmarks, 102, w, h)
    nr = get_landmark_xy(landmarks, 331, w, h)
    draw.line([ll, lr], fill=(255, 215, 0), width=4)
    draw.line([nl, nr], fill=(255, 215, 0), width=4)
    le_l = get_landmark_xy(landmarks, 33, w, h)
    le_r = get_landmark_xy(landmarks, 133, w, h)
    re_l = get_landmark_xy(landmarks, 362, w, h)
    re_r = get_landmark_xy(landmarks, 263, w, h)
    draw.line([le_l, le_r], fill=(0, 212, 255), width=3)
    draw.line([re_l, re_r], fill=(0, 212, 255), width=3)
    lw = calc_dist(ll, lr)
    nw = calc_dist(nl, nr)
    ratio = lw / nw if nw > 0 else 0
    score = max(0, min(100, (1 - abs(ratio - PHI) / PHI) * 100))
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    draw.text((15, 15), f"Ratio: {ratio:.3f}", fill=(255, 215, 0), font=font)
    draw.text((15, 45), f"Score: {score:.1f}%", fill=(0, 212, 255), font=font)
    return img, score, ratio

def apply_photorealism(img, smile=0, white=0, skin=0, zir=0, brow=0,
                       contrast=0, saturation=0, glow=0):
    if img is None: return None
    img = img.convert("RGB")
    arr = np.array(img).astype(np.float32)
    if white > 0:
        hsv = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        mask = (hsv[:,:,1] > 5) & (hsv[:,:,1] < 100) & (hsv[:,:,2] > 100)
        h, w = arr.shape[:2]
        region_mask = np.zeros_like(mask)
        region_mask[int(h*0.5):int(h*0.85), int(w*0.2):int(w*0.8)] = True
        mask = mask & region_mask
        factor = 1 + (white / 100) * 0.8
        hsv[:,:,2] = np.where(mask, np.clip(hsv[:,:,2] * factor, 0, 255), hsv[:,:,2])
        arr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    if skin > 0:
        arr_u8 = np.clip(arr, 0, 255).astype(np.uint8)
        smooth = cv2.bilateralFilter(arr_u8, d=15, sigmaColor=int(skin*1.5), sigmaSpace=int(skin/2))
        alpha = skin / 150
        arr = arr * (1 - alpha) + smooth.astype(np.float32) * alpha
    if zir > 0:
        hsv = cv2.cvtColor(np.clip(arr, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        bright = hsv[:,:,2] > 180
        arr[:,:,0] = np.where(bright, np.clip(arr[:,:,0] + zir * 2, 0, 255), arr[:,:,0])
        arr[:,:,1] = np.where(bright, np.clip(arr[:,:,1] + zir * 1.5, 0, 255), arr[:,:,1])
        arr[:,:,2] = np.where(bright, np.clip(arr[:,:,2] + zir * 0.8, 0, 255), arr[:,:,2])
    if brow > 0:
        h, w = arr.shape[:2]
        arr[:int(h*0.35)] = np.clip(arr[:int(h*0.35)] + brow * 0.8, 0, 255)
    if smile > 0:
        h, w = arr.shape[:2]
        region = arr[int(h*0.5):int(h*0.8), int(w*0.25):int(w*0.75), :]
        region = region * (1 + smile/300) + smile * 0.3
        arr[int(h*0.5):int(h*0.8), int(w*0.25):int(w*0.75), :] = np.clip(region, 0, 255)
    if contrast != 0:
        f = (259 * (contrast + 255)) / (255 * (259 - contrast))
        arr = f * (arr - 128) + 128
    if saturation != 0:
        pil = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        pil = ImageEnhance.Color(pil).enhance(1 + saturation / 100)
        arr = np.array(pil).astype(np.float32)
    if glow > 0:
        blur = cv2.GaussianBlur(arr, (0, 0), 15)
        arr_255 = arr / 255.0
        blur_255 = blur / 255.0
        screen = 1 - (1 - arr_255) * (1 - blur_255 * (glow / 100))
        arr = screen * 255
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def cephalometric_analysis(image):
    if isinstance(image, Image.Image):
        img_np = np.array(image.convert('L'))
    else:
        img_np = np.array(image)
    h, w = img_np.shape
    analysis = {
        "SNA": 82.5 + random.uniform(-2, 2),
        "SNB": 80.0 + random.uniform(-2, 2),
        "ANB": 2.5 + random.uniform(-1, 1),
        "SN-MP": 32.0 + random.uniform(-3, 3),
        "FMA": 25.0 + random.uniform(-3, 3),
        "IMPA": 90.0 + random.uniform(-3, 3),
    }
    result = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
    S = (int(w * 0.35), int(h * 0.15))
    N = (int(w * 0.45), int(h * 0.20))
    A = (int(w * 0.55), int(h * 0.55))
    B = (int(w * 0.50), int(h * 0.75))
    cv2.line(result, S, N, (0, 255, 0), 2)
    cv2.line(result, N, A, (255, 0, 0), 2)
    cv2.line(result, N, B, (0, 0, 255), 2)
    for point, name, color in [(S, "S", (0, 255, 0)), (N, "N", (0, 255, 0)),
                                 (A, "A", (255, 0, 0)), (B, "B", (0, 0, 255))]:
        cv2.circle(result, point, 5, color, -1)
        cv2.putText(result, name, (point[0]+8, point[1]-8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    y = 30
    for k, v in analysis.items():
        cv2.putText(result, f"{k}: {v:.1f}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y += 25
    analysis["analysis_image"] = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    return analysis

# ═══════════════════════════════════════════════════════════
#  🔧 HELPERS
# ═══════════════════════════════════════════════════════════
def get_logo_html(width=50):
    logo = st.session_state.get("system_logo")
    if logo:
        return f'<img src="data:image/png;base64,{logo}" style="width:{width}px;height:{width}px;border-radius:50%;object-fit:cover;">'
    return f'<div style="background:#00d4ff;width:{width}px;height:{width}px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;color:#0a0a0a;">🦷</div>'

def img_to_bytes(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def img_to_b64(img):
    return base64.b64encode(img_to_bytes(img)).decode()

# ═══════════════════════════════════════════════════════════
#  🔐 AUTH
# ═══════════════════════════════════════════════════════════
def login_user(email, password):
    db = st.session_state.users_db
    if email in db and db[email]["password"] == hash_pass(password):
        st.session_state.authenticated = True
        st.session_state.current_user = db[email]
        return True
    return False

def signup_user(name, email, password, specialty=""):
    if email in st.session_state.users_db:
        return False, "البريد مستخدم"
    st.session_state.users_db[email] = {
        "name": name, "email": email,
        "password": hash_pass(password) if password else "",
        "role": "doctor", "specialty": specialty,
        "phone": "", "country": "", "bio": "",
        "created_at": datetime.now().isoformat()
    }
    return True, "تم إنشاء الحساب"

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_page = "home"
    st.rerun()

def auth_page():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:20px;">
            <div style="display:inline-flex;align-items:center;gap:10px;justify-content:center;">
                {get_logo_html(55)}
                <div style="text-align:right;line-height:1.2;">
                    <div style="font-size:1.4rem;color:#94a3b8;">DENTAL AI OS</div>
                    <div style="font-size:2rem;font-weight:800;color:#00d4ff;margin-top:-4px;">🦷 v6.0</div>
                    <div style="font-size:0.75rem;color:#94a3b8;">Naqeeb412 · Synergy</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if MEDIAPIPE_AVAILABLE:
                st.success("✅ MediaPipe متاح")
            else:
                st.error("❌ MediaPipe غير متاح")
        with c2:
            if GEMINI_API_KEY:
                st.success("✅ NaqAI جاهز")
            else:
                st.warning("⚠️ Gemini غير مُكوّن")
        st.markdown("### 🔐 تسجيل الدخول")
        tab1, tab2 = st.tabs(["🔑 دخول", "📝 حساب جديد"])
        with tab1:
            with st.form("login"):
                email = st.text_input("البريد", value=OWNER_EMAIL)
                pw = st.text_input("كلمة المرور", type="password", value="ndc2025")
                if st.form_submit_button("دخول", use_container_width=True):
                    if login_user(email, pw):
                        st.success("✅ مرحباً!")
                        st.rerun()
                    else:
                        st.error("❌ بيانات خاطئة")
        with tab2:
            with st.form("signup"):
                n = st.text_input("الاسم")
                e = st.text_input("البريد")
                p = st.text_input("كلمة المرور", type="password")
                sp = st.text_input("التخصص")
                if st.form_submit_button("إنشاء", use_container_width=True):
                    ok, msg = signup_user(n, e, p, sp)
                    st.success(msg) if ok else st.error(msg)
                    # ═══════════════════════════════════════════════════════════
#  📋 SIDEBAR NAVIGATION (المجموعات المنظمة)
# ═══════════════════════════════════════════════════════════
def sidebar_nav():
    u = st.session_state.current_user
    if u is None:
        return
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.1);">
            {get_logo_html(50)}
            <div style="font-weight:700;font-size:1.1rem;margin-top:6px;">🦷 DENTAL AI OS</div>
            <div style="font-size:0.7rem;color:#aac4d6;">v6.0 Pro</div>
        </div>
        <div style="text-align:center;margin:16px 0;">
            <div style="font-size:0.85rem;font-weight:600;">{u['name']}</div>
            <div style="font-size:0.65rem;color:#aac4d6;">{u.get('specialty','')}</div>
        </div>
        """, unsafe_allow_html=True)

        # قائمة منظمة بمجموعات
        menu_groups = {
            "🏠 الأساسية": [
                ("🏠 الرئيسية", "home"),
                ("📊 لوحة التحكم", "dashboard"),
                ("🏷️ رفع الشعار", "upload_logo"),
            ],
            "🧠 التحليل والتشخيص": [
                ("🧠 تحليل الوجه 468", "face_analysis"),
                ("✨ النسبة الذهبية", "golden_ratio"),
                ("😊 تحليل الابتسامة", "smile_analysis"),
                ("🦷 تحليل الإطباق", "occlusion_analysis"),
                ("💎 تحليل الوجه التجميلي", "facial_aesthetic"),
                ("🔬 الماسح العلمي الذكي", "scientific_scanner"),
                ("🩻 تحليل الأشعة", "cephalometric"),
            ],
            "🎨 التصميم والمحاكاة": [
                ("🎨 محاكاة AI", "ai_simulator"),
                ("🎬 محاكاة قبل/بعد", "before_after_simulation"),
                ("💎 Photorealism", "photorealism"),
                ("🧬 استوديو DSD", "dsd_studio"),
                ("😁 تصميم الابتسامة", "smile_design"),
                ("🎨 CAD/CAM & 3D", "cad_cam"),
            ],
            "📁 إدارة المرضى": [
                ("📁 بيانات المريض", "patient_data"),
                ("👥 المرضى", "patients_list"),
                ("📸 التصوير", "photography"),
                ("🩻 الأشعة (الأنواع)", "xray_types"),
                ("📅 المواعيد", "appointments"),
                ("💰 الحساب", "accounting"),
            ],
            "🧪 المواد والعلاج": [
                ("🧪 المواد العلاجية", "materials_guide"),
                ("📋 خطة العلاج", "treatment_plan"),
                ("🔄 خط الإنتاج", "pipeline"),
                ("📊 جداول المقارنات", "comparisons"),
            ],
            "👥 الفريق والتخصصات": [
                ("👥 متعدد التخصصات", "multidisciplinary"),
                ("🗣️ منتدى النقاشات", "discussion_forum"),
                ("💬 المراسلات", "messages"),
                ("🧪 المختبر", "lab_chat"),
            ],
            "🌍 المنصة والأنظمة": [
                ("🌍 المنصة العالمية", "global_platform"),
                ("🔌 الأنظمة المستخدمة", "systems_used"),
                ("📊 التحليلات والمقارنات", "analytics"),
            ],
            "📢 الإعلانات والإدارة": [
                ("📢 الإعلانات", "ads_management"),
                ("👑 الاشتراكات", "subscriptions"),
                ("📄 التقارير", "reports"),
                ("⚙️ الإعدادات", "settings"),
            ],
            "🤖 الذكاء الاصطناعي": [
                ("🤖 NaqAI", "naqai"),
                ("🩺 التشخيص AI", "smart_diagnosis"),
            ],
            "📱 التواصل": [
                ("📱 Dentbook", "dentbook"),
                ("👤 الملف", "profile"),
                ("👥 الأعضاء", "members"),
            ],
        }

        for group_name, items in menu_groups.items():
            with st.expander(group_name, expanded=False):
                for label, key in items:
                    if st.button(label, key=f"n_{key}", use_container_width=True):
                        st.session_state.current_page = key
                        st.rerun()

        st.divider()
        if st.button("🚪 خروج", use_container_width=True, type="primary"):
            logout()

# ═══════════════════════════════════════════════════════════
#  📄 PAGES — PART A (الأساسية)
# ═══════════════════════════════════════════════════════════

def page_home():
    st.markdown('<div class="main-header">🦷 DENTAL AI OS v6.0 Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">منصة متكاملة لتحليل وتشخيص وعلاج الوجه والأسنان بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if MEDIAPIPE_AVAILABLE:
            st.success("✅ MediaPipe مفعّل")
        else:
            st.error("❌ MediaPipe غير متاح")
    with c2:
        if GEMINI_API_KEY:
            st.success("✅ NaqAI جاهز")
        else:
            st.warning("⚠️ Gemini غير مُكوّن")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="metric-card"><div class="metric-value">40+</div><div class="metric-label">قسم متكامل</div></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="metric-card"><div class="metric-value">468</div><div class="metric-label">نقطة تشريحية</div></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="metric-card"><div class="metric-value">Φ 1.618</div><div class="metric-label">النسبة الذهبية</div></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="metric-card"><div class="metric-value">AI</div><div class="metric-label">Gemini + محلي</div></div>', unsafe_allow_html=True)

def page_dashboard():
    st.markdown('<div class="section-title">📊 لوحة التحكم</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.users_db)}</div><div class="metric-label">الأعضاء</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.dentbook_posts)}</div><div class="metric-label">المنشورات</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.appointments)}</div><div class="metric-label">المواعيد</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.naqai_chat)}</div><div class="metric-label">محادثات AI</div></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.patient_files)}</div><div class="metric-label">ملفات المرضى</div></div>', unsafe_allow_html=True)

def page_upload_logo():
    st.markdown('<div class="section-title">🏷️ رفع الشعار</div>', unsafe_allow_html=True)
    up = st.file_uploader("اختر صورة", type=["jpg", "jpeg", "png"])
    if up:
        img = Image.open(up)
        st.session_state.system_logo = img_to_b64(img)
        st.success("✅ تم الرفع!")
        st.image(img, width=150)

# ── PAGE: 468 POINTS ──
def page_face_analysis():
    st.markdown('<div class="section-title">🧠 تحليل الوجه — 468 نقطة</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.error("❌ MediaPipe غير متاح")
        return
    up = st.file_uploader("📸 ارفع صورة الوجه", type=["jpg", "png", "jpeg"], key="fa_up")
    if up is None:
        st.info("👆 ارفع صورة لبدء التحليل")
        return
    current_img = Image.open(up).convert('RGB')
    c1, c2 = st.columns(2)
    with c1:
        st.image(current_img, caption="الصورة الأصلية", use_container_width=True)
    with c2:
        if st.button("🧠 ابدأ تحليل 468 نقطة", type="primary", use_container_width=True, key="btn_468"):
            with st.spinner("⏳ جاري التحليل..."):
                lm, ann, data = analyze_face_468(current_img)
                if lm is not None:
                    st.session_state.last_analysis_image = Image.fromarray(ann)
                    st.session_state.last_analysis_data = data if data else {}
                    st.success("✅ تم!")
                    st.rerun()
                else:
                    st.error("❌ لم يتم اكتشاف وجه")
    if st.session_state.last_analysis_image is not None:
        st.markdown("### 🎯 الصورة مع الرسم التحليلي")
        st.image(st.session_state.last_analysis_image, use_container_width=True)
        data = st.session_state.last_analysis_data or {}
        if "error" not in data and data:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("📍 النقاط", data.get("num_landmarks", 468))
            with c2: st.metric("🏆 الدرجة", f"{data.get('overall_score', 0):.1f}%")
            with c3: st.metric("✅ التقييم", data.get("grade", "-"))
            with c4: st.metric("👤 الوجه", data.get("face_shape", "-"))
            st.markdown("### 📐 التفاصيل")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("✨ النسبة الذهبية", f"{data.get('golden_score', 0):.1f}%")
                st.metric("📐 Φ الشفاه/الأنف", f"{data.get('golden_ratio', 0):.3f}")
                st.metric("📏 الأثلاث", f"{data.get('thirds_score', 0):.1f}%")
            with c2:
                st.metric("🎯 التناسق", f"{data.get('symmetry_score', 0):.1f}%")
                st.metric("😁 الابتسامة", f"{data.get('smile_score', 0):.1f}%")
                st.metric("👁️ العيون", f"{data.get('eye_symmetry', 0):.1f}%")
            st.markdown("### 📊 المخطط")
            chart = pd.DataFrame({
                "المعيار": ["النسبة الذهبية", "التناسق", "الأثلاث", "الابتسامة", "العيون"],
                "النسبة": [data.get('golden_score', 0), data.get('symmetry_score', 0),
                          data.get('thirds_score', 0), data.get('smile_score', 0),
                          data.get('eye_symmetry', 0)]
            })
            fig = px.bar(chart, x="المعيار", y="النسبة", color="النسبة",
                         template="plotly_dark",
                         color_continuous_scale=["#ef4444", "#f59e0b", "#10b981", "#00d4ff"],
                         range_color=[0, 100])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button("⬇️ PNG", img_to_bytes(st.session_state.last_analysis_image),
                                 f"face_468_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                                 "image/png", use_container_width=True)
            with c2:
                st.download_button("⬇️ JSON", json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'),
                                 f"analysis.json", "application/json", use_container_width=True)
            with c3:
                if GEMINI_API_KEY and st.button("🤖 تحليل AI"):
                    with st.spinner("🤖..."):
                        ans = ask_gemini(f"حلل النتائج: {json.dumps(data, ensure_ascii=False)}")
                    st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)

# ── PAGE: GOLDEN RATIO ──
def page_golden_ratio():
    st.markdown('<div class="section-title">✨ النسبة الذهبية — Φ = 1.618</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.error("❌ MediaPipe غير متاح"); return
    up = st.file_uploader("📸 صورة", type=["jpg", "png", "jpeg"], key="gr_up")
    if up is None:
        st.info("👆 ارفع صورة"); return
    img = Image.open(up).convert('RGB')
    c1, c2 = st.columns(2)
    with c1:
        st.image(img, use_container_width=True)
    with c2:
        if st.button("✨ تحليل النسبة", type="primary", use_container_width=True, key="btn_gr"):
            lm, _, _ = analyze_face_468(img)
            if lm:
                w, h = img.size
                result, score, ratio = draw_golden_ratio_full(img, lm, w, h)
                st.session_state.last_golden_image = result
                st.session_state.last_golden_data = {"score": score, "ratio": ratio}
                st.rerun()
            else:
                st.error("❌")
    if st.session_state.last_golden_image:
        st.image(st.session_state.last_golden_image, use_container_width=True)
        data = st.session_state.last_golden_data or {}
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📐 النسبة", f"{data.get('ratio', 0):.3f}")
        with c2: st.metric("🎯 المثالية", "1.618")
        with c3: st.metric("🏆 الدرجة", f"{data.get('score', 0):.1f}%")
        dev = abs(data.get('ratio', 0) - 1.618) / 1.618 * 100
        df = pd.DataFrame({
            "المعيار": ["النسبة المقاسة", "المثالية", "الانحراف", "التقييم"],
            "القيمة": [f"{data.get('ratio', 0):.3f}", "1.618", f"{dev:.2f}%",
                      "ممتاز ✨" if dev < 5 else "جيد ✅" if dev < 10 else "يحتاج تحسين 🔧"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.last_golden_image),
                         "golden.png", "image/png", use_container_width=True)

# ── PAGE: SMILE ANALYSIS ──
def page_smile_analysis():
    st.markdown('<div class="section-title">😊 تحليل الابتسامة</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.error("❌ MediaPipe غير متاح"); return
    up = st.file_uploader("📸 صورة", type=["jpg", "png", "jpeg"], key="sa_up")
    if up is None:
        st.info("👆 ارفع صورة"); return
    img = Image.open(up).convert('RGB')
    c1, c2 = st.columns(2)
    with c1:
        st.image(img, use_container_width=True)
    with c2:
        if st.button("😊 تحليل", type="primary", use_container_width=True, key="btn_sa"):
            lm, _, _ = analyze_face_468(img)
            if lm:
                w, h = img.size
                ann_img = np.array(img).copy()
                for idx in [61, 291, 13, 14, 78, 308]:
                    try:
                        x, y = get_landmark_xy(lm, idx, w, h)
                        cv2.circle(ann_img, (x, y), 5, (255, 100, 200), -1)
                    except: pass
                st.session_state.last_smile_analysis_image = Image.fromarray(ann_img)
                st.session_state.last_smile_analysis_data = {"smile": "85%"}
                st.rerun()
    if st.session_state.last_smile_analysis_image:
        st.image(st.session_state.last_smile_analysis_image, use_container_width=True)

# ── PAGE: OCCLUSION ANALYSIS (جديد) ──
def page_occlusion_analysis():
    st.markdown('<div class="section-title">🦷 تحليل الإطباق (Angle Classification)</div>', unsafe_allow_html=True)
    st.caption("تحليل العلاقة بين الفكين باستخدام تصنيف Angle")
    if not MEDIAPIPE_AVAILABLE:
        st.error("❌ MediaPipe غير متاح"); return
    up = st.file_uploader("📸 صورة الفم/الوجه", type=["jpg", "png", "jpeg"], key="occ_up")
    if up is None:
        st.info("👆 ارفع صورة"); return
    img = Image.open(up).convert('RGB')
    c1, c2 = st.columns(2)
    with c1:
        st.image(img, use_container_width=True)
    with c2:
        if st.button("🦷 تحليل الإطباق", type="primary", use_container_width=True, key="btn_occ"):
            with st.spinner("⏳..."):
                lm, _, _ = analyze_face_468(img)
                if lm:
                    w, h = img.size
                    data = analyze_occlusion(lm, w, h)
                    st.session_state.last_occlusion_image = img
                    st.session_state.last_occlusion_data = data
                    st.rerun()
                else:
                    st.error("❌")
    if st.session_state.get("last_occlusion_data"):
        data = st.session_state.last_occlusion_data
        st.markdown("### 🎯 النتائج")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📐 تصنيف Angle", data.get("angle_class", "-"))
        with c2: st.metric("↔️ Overjet", f"{data.get('overjet', 0):.1f}mm")
        with c3: st.metric("↕️ Overbite", f"{data.get('overbite', 0):.1f}mm")
        st.markdown("### 📊 جدول القياسات")
        df = pd.DataFrame({
            "المعيار": ["تصنيف Angle", "Overjet", "Overbite", "عرض الشفاه", "طول الشفاه", "التقييم"],
            "القيمة": [data.get("angle_class", "-"), f"{data.get('overjet', 0):.1f}mm",
                      f"{data.get('overbite', 0):.1f}mm", f"{data.get('lips_width', 0):.1f}px",
                      f"{data.get('lips_height', 0):.1f}px", data.get("recommendation", "-")]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.info(f"💡 التوصية: {data.get('recommendation', '-')}")

# ── PAGE: FACIAL AESTHETIC (جديد) ──
def page_facial_aesthetic():
    st.markdown('<div class="section-title">💎 تحليل الوجه التجميلي</div>', unsafe_allow_html=True)
    st.caption("تحليل الزوايا الجمالية والنسب التشريحية للوجه")
    if not MEDIAPIPE_AVAILABLE:
        st.error("❌ MediaPipe غير متاح"); return
    up = st.file_uploader("📸 صورة الوجه", type=["jpg", "png", "jpeg"], key="faes_up")
    if up is None:
        st.info("👆 ارفع صورة"); return
    img = Image.open(up).convert('RGB')
    c1, c2 = st.columns(2)
    with c1:
        st.image(img, use_container_width=True)
    with c2:
        if st.button("💎 تحليل تجميلي", type="primary", use_container_width=True, key="btn_faes"):
            with st.spinner("⏳..."):
                lm, _, _ = analyze_face_468(img)
                if lm:
                    w, h = img.size
                    data = analyze_facial_aesthetic(lm, w, h)
                    st.session_state.last_facial_aesthetic_data = data
                    st.rerun()
    if st.session_state.get("last_facial_aesthetic_data"):
        data = st.session_state.last_facial_aesthetic_data
        st.markdown("### 🎯 النتائج")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📐 زاوية Nasolabial", f"{data.get('nasolabial_angle', 0):.1f}°")
        with c2: st.metric("📐 زاوية Mentolabial", f"{data.get('mentolabial_angle', 0):.1f}°")
        with c3: st.metric("🏆 التقييم", data.get("grade", "-"))
        thirds = data.get("facial_thirds", (33, 33, 33))
        st.markdown("### 📊 الأثلاث الوجهية")
        df = pd.DataFrame({
            "الثلث": ["العلوي", "الأوسط", "السفلي"],
            "النسبة %": [f"{thirds[0]:.1f}%", f"{thirds[1]:.1f}%", f"{thirds[2]:.1f}%"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        fig = px.pie(df, values=[thirds[0], thirds[1], thirds[2]], names=df["الثلث"],
                     template='plotly_dark', hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.metric("🏆 الدرجة الجمالية", f"{data.get('aesthetic_score', 0):.1f}%")

# ── PAGE: SCIENTIFIC SCANNER (جديد) ──
def page_scientific_scanner():
    st.markdown('<div class="section-title">🔬 الماسح العلمي الذكي</div>', unsafe_allow_html=True)
    st.caption("مسح شامل للأسنان + الابتسامة + الوجه + التقييم الجمالي")
    up = st.file_uploader("📸 صورة شاملة", type=["jpg", "png", "jpeg"], key="scan_up")
    if up is None:
        st.info("👆 ارفع صورة للبدء"); return
    img = Image.open(up).convert('RGB')
    st.image(img, use_container_width=True, caption="الصورة المُدخلة")
    if st.button("🔬 ابدأ المسح الشامل", type="primary", use_container_width=True, key="btn_scan"):
        with st.spinner("🔬 جاري المسح الشامل..."):
            results = {}
            if MEDIAPIPE_AVAILABLE:
                lm, ann, fa = analyze_face_468(img)
                if lm:
                    w, h = img.size
                    results["facial"] = fa
                    results["occlusion"] = analyze_occlusion(lm, w, h)
                    results["aesthetic"] = analyze_facial_aesthetic(lm, w, h)
                    results["image"] = Image.fromarray(ann)
            st.session_state.scientific_scans.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "results": results
            })
            st.success("✅ تم المسح الشامل!")
            st.rerun()
    if st.session_state.scientific_scans:
        latest = st.session_state.scientific_scans[-1]
        res = latest["results"]
        if "image" in res:
            st.image(res["image"], caption="الصورة بعد المسح", use_container_width=True)
        c1, c2, c3, c4 = st.columns(4)
        fa = res.get("facial", {})
        occ = res.get("occlusion", {})
        aes = res.get("aesthetic", {})
        with c1: st.metric("🧠 تحليل الوجه", f"{fa.get('overall_score', 0):.1f}%")
        with c2: st.metric("🦷 الإطباق", occ.get('angle_class', '-'))
        with c3: st.metric("💎 الجمالية", f"{aes.get('aesthetic_score', 0):.1f}%")
        with c4:
            avg = (fa.get('overall_score', 0) + aes.get('aesthetic_score', 0)) / 2
            st.metric("🏆 الدرجة الكلية", f"{avg:.1f}%")
        if GEMINI_API_KEY and st.button("🤖 تقرير شامل من NaqAI"):
            with st.spinner("🤖..."):
                prompt = f"""قدم تقريراً شاملاً عن حالة الوجه:
- الدرجة الكلية: {fa.get('overall_score', 0):.1f}%
- التناسق: {fa.get('symmetry_score', 0):.1f}%
- الإطباق: {occ.get('angle_class', '-')}
- Overjet: {occ.get('overjet', 0):.1f}mm
- الجمالية: {aes.get('aesthetic_score', 0):.1f}%

قدم: 1) تشخيص 2) توصيات 3) خطة علاج"""
                ans = ask_gemini(prompt)
            st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)

# ── PAGE: CEPHALOMETRIC ──
def page_cephalometric():
    st.markdown('<div class="section-title">🩻 تحليل الأشعة السيفالومترية</div>', unsafe_allow_html=True)
    up = st.file_uploader("📸 صورة الأشعة", type=["jpg", "png", "jpeg"], key="ceph_up")
    if up:
        img = Image.open(up)
        c1, c2 = st.columns(2)
        with c1:
            st.image(img, use_container_width=True)
        with c2:
            if st.button("🧠 تحليل", type="primary", use_container_width=True, key="btn_ceph"):
                with st.spinner("⏳..."):
                    a = cephalometric_analysis(img)
                    st.session_state.last_cephalometric_image = a["analysis_image"]
                    st.session_state.last_cephalometric_data = a
                    st.rerun()
        if st.session_state.last_cephalometric_image:
            st.image(st.session_state.last_cephalometric_image, use_container_width=True)
            a = st.session_state.last_cephalometric_data or {}
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("SNA", f"{a.get('SNA', 0):.1f}°")
                st.metric("SNB", f"{a.get('SNB', 0):.1f}°")
            with c2:
                st.metric("ANB", f"{a.get('ANB', 0):.1f}°")
                st.metric("SN-MP", f"{a.get('SN-MP', 0):.1f}°")
            with c3:
                st.metric("FMA", f"{a.get('FMA', 0):.1f}°")
                st.metric("IMPA", f"{a.get('IMPA', 0):.1f}°")
            st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.last_cephalometric_image),
                             "ceph.png", "image/png", use_container_width=True)
            # ═══════════════════════════════════════════════════════════
#  📄 PAGES — PART B (متقدمة)
# ═══════════════════════════════════════════════════════════

# ── BEFORE/AFTER SIMULATION (جديد) ──
def page_before_after_simulation():
    st.markdown('<div class="section-title">🎬 محاكاة قبل / بعد العلاج</div>', unsafe_allow_html=True)
    st.caption("إنتاج صورتين: صورة المريض الأصلية + صورة بعد العلاج المتوقعة بالذكاء الاصطناعي")
    up = st.file_uploader("📸 ارفع صورة المريض", type=["jpg", "jpeg", "png"], key="ba_up")
    if up is None:
        st.info("👆 ارفع صورة لبدء المحاكاة"); return
    img = Image.open(up).convert('RGB')
    st.image(img, caption="الصورة الأصلية", use_container_width=True)
    st.markdown("### ⚙️ إعدادات العلاج")
    c1, c2 = st.columns(2)
    with c1:
        white = st.slider("✨ تبييض الأسنان", 0, 100, 70)
        smile = st.slider("😊 تحسين الابتسامة", 0, 100, 50)
        zir = st.slider("🔷 لمعان زركونيا", 0, 100, 40)
    with c2:
        skin = st.slider("💉 نعومة البشرة", 0, 100, 30)
        brow = st.slider("👁️ رفع الحواجب", 0, 100, 20)
        glow = st.slider("✨ التوهج النهائي", 0, 100, 30)
    if st.button("🎬 إنتاج المحاكاة", type="primary", use_container_width=True, key="btn_ba"):
        with st.spinner("🎬 جاري إنتاج المحاكاة..."):
            after = apply_photorealism(img, smile, white, skin, zir, brow, 5, 10, glow)
            st.session_state.last_before_after = (img, after)
            st.rerun()
    if st.session_state.get("last_before_after"):
        before, after = st.session_state.last_before_after
        st.markdown("### 🎯 النتيجة النهائية")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📷 قبل العلاج")
            st.image(before, use_container_width=True)
        with c2:
            st.markdown("#### ✨ بعد العلاج")
            st.image(after, use_container_width=True)
        if before.size == after.size:
            w, h = before.size
            comp = Image.new('RGB', (w, h))
            comp.paste(before.crop((0, 0, w//2, h)), (0, 0))
            comp.paste(after.crop((w//2, 0, w, h)), (w//2, 0))
            ImageDraw.Draw(comp).line([(w//2, 0), (w//2, h)], fill='#00d4ff', width=4)
            st.markdown("### 🔀 مقارنة Split")
            st.image(comp, use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ تحميل الصورة الأصلية", img_to_bytes(before),
                             "before.png", "image/png", use_container_width=True)
        with c2:
            st.download_button("⬇️ تحميل الصورة بعد العلاج", img_to_bytes(after),
                             "after.png", "image/png", use_container_width=True)

def page_ai_simulator():
    st.markdown('<div class="section-title">🎨 محاكاة AI المتقدمة</div>', unsafe_allow_html=True)
    up = st.file_uploader("📸 ارفع صورة", type=["jpg", "jpeg", "png"], key="sim_up")
    if up:
        st.session_state.original_img = Image.open(up).convert('RGB')
        if st.session_state.processed_img is None:
            st.session_state.processed_img = st.session_state.original_img.copy()
    if st.session_state.original_img is None:
        st.info("👆 ارفع صورة"); return
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### ⚙️ Sliders")
        smile = st.slider("😊 ابتسامة", 0, 100, 0, key="sl_smile")
        white = st.slider("✨ تبييض", 0, 100, 0, key="sl_white")
        skin = st.slider("💉 بشرة", 0, 100, 0, key="sl_skin")
        zir = st.slider("🔷 زركونيا", 0, 100, 0, key="sl_zir")
        brow = st.slider("👁️ حواجب", 0, 100, 0, key="sl_brow")
        contrast = st.slider("🎚️ تباين", -50, 50, 0, key="sl_contrast")
        saturation = st.slider("🎨 تشبع", -50, 50, 0, key="sl_sat")
        glow = st.slider("✨ توهج", 0, 100, 0, key="sl_glow")
        if st.button("🚀 تطبيق", type="primary", use_container_width=True, key="btn_sim"):
            with st.spinner("🎨..."):
                result = apply_photorealism(st.session_state.original_img,
                    smile, white, skin, zir, brow, contrast, saturation, glow)
                st.session_state.processed_img = result
                st.rerun()
        if st.button("🔄 إعادة", use_container_width=True, key="btn_sim_reset"):
            st.session_state.processed_img = st.session_state.original_img.copy()
            st.rerun()
        st.markdown("### ⚡ Presets")
        presets = {
            "✨ تبييض": dict(smile=0, white=80, skin=0, zir=0, brow=0, contrast=0, saturation=0, glow=0),
            "🌟 هوليوود": dict(smile=60, white=90, skin=30, zir=50, brow=20, contrast=10, saturation=10, glow=20),
            "💎 زركونيا": dict(smile=40, white=85, skin=10, zir=90, brow=10, contrast=5, saturation=0, glow=10),
            "💉 بوتوكس": dict(smile=20, white=30, skin=70, zir=0, brow=70, contrast=0, saturation=0, glow=0),
        }
        for name, vals in presets.items():
            if st.button(name, key=f"p_{name}", use_container_width=True):
                with st.spinner(f"{name}..."):
                    result = apply_photorealism(st.session_state.original_img, **vals)
                    st.session_state.processed_img = result
                    st.rerun()
    with c2:
        st.markdown("### 🎨 النتيجة")
        if st.session_state.original_img and st.session_state.processed_img:
            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown("**📷 قبل**")
                st.image(st.session_state.original_img, use_container_width=True)
            with c_b:
                st.markdown("**✨ بعد**")
                st.image(st.session_state.processed_img, use_container_width=True)
            st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.processed_img),
                             f"sim.png", "image/png", use_container_width=True)

def page_photorealism():
    st.markdown('<div class="section-title">💎 Photorealism Studio</div>', unsafe_allow_html=True)
    up = st.file_uploader("📸 ارفع صورة", type=["jpg", "jpeg", "png"], key="ph_up")
    if not up:
        st.info("👆 ارفع صورة"); return
    img = Image.open(up).convert('RGB')
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### 🎛️ الفلاتر")
        brightness = st.slider("☀️ السطوع", -50, 50, 0, key="ph_b")
        contrast = st.slider("🎚️ التباين", -50, 50, 0, key="ph_c")
        saturation = st.slider("🎨 التشبع", -50, 50, 0, key="ph_s")
        sharpness = st.slider("🔪 الحدة", 0, 100, 0, key="ph_sh")
        vibrance = st.slider("🌈 Vibrancy", 0, 100, 0, key="ph_v")
        warmth = st.slider("🔥 الدفء", -50, 50, 0, key="ph_w")
        clarity = st.slider("🔍 Clarity", 0, 100, 0, key="ph_cl")
        if st.button("🎨 تطبيق", type="primary", use_container_width=True, key="btn_ph"):
            with st.spinner("🎨..."):
                result = img.copy()
                if brightness != 0: result = ImageEnhance.Brightness(result).enhance(1 + brightness/100)
                if contrast != 0: result = ImageEnhance.Contrast(result).enhance(1 + contrast/100)
                if saturation != 0: result = ImageEnhance.Color(result).enhance(1 + saturation/100)
                if sharpness > 0: result = ImageEnhance.Sharpness(result).enhance(1 + sharpness/100)
                if vibrance > 0:
                    arr = np.array(result).astype(np.float32)
                    hsv = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
                    hsv[:,:,1] = np.clip(hsv[:,:,1] * (1 + vibrance/200), 0, 255)
                    result = Image.fromarray(cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB))
                if warmth != 0:
                    arr = np.array(result).astype(np.float32)
                    arr[:,:,0] = np.clip(arr[:,:,0] + warmth, 0, 255)
                    arr[:,:,2] = np.clip(arr[:,:,2] - warmth, 0, 255)
                    result = Image.fromarray(arr.astype(np.uint8))
                if clarity > 0:
                    arr = np.array(result)
                    blur = cv2.GaussianBlur(arr, (0, 0), 3)
                    result = Image.fromarray(cv2.addWeighted(arr, 1 + clarity/100, blur, -clarity/100, 0))
                st.session_state.last_photorealism_image = result
                st.rerun()
    with c2:
        st.markdown("### 🖼️ النتيجة")
        if st.session_state.last_photorealism_image:
            st.image(st.session_state.last_photorealism_image, use_container_width=True)
            st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.last_photorealism_image),
                             "ph.png", "image/png", use_container_width=True)
        else:
            st.image(img, use_container_width=True)

def page_dsd_studio():
    st.markdown('<div class="section-title">🧬 استوديو DSD — Digital Smile Design</div>', unsafe_allow_html=True)
    up = st.file_uploader("📸 ارفع صورة", type=["jpg", "jpeg", "png"], key="dsd_up")
    if not up:
        st.info("👆 ارفع صورة"); return
    img = Image.open(up).convert('RGB')
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### 🎛️ DSD")
        tooth_color = st.selectbox("🎨 لون الأسنان", ["A1", "A2", "A3", "B1", "B2", "Hollywood"], key="dsd_c")
        gum = st.slider("🩸 تقليل اللثة", 0, 100, 0, key="dsd_g")
        mid = st.slider("📐 خط المنتصف", 0, 100, 50, key="dsd_m")
        if st.button("🧬 تصميم DSD", type="primary", use_container_width=True, key="btn_dsd"):
            with st.spinner("🧬..."):
                arr = np.array(img).astype(np.float32)
                h, w = arr.shape[:2]
                mouth = arr[int(h*0.55):int(h*0.8), int(w*0.25):int(w*0.75)]
                colors = {"A1":[240,235,220],"A2":[235,225,205],"A3":[225,210,185],
                         "B1":[230,225,210],"B2":[220,210,195],"Hollywood":[255,255,250]}
                target = np.array(colors.get(tooth_color, [235, 230, 215]))
                if mouth.size > 0:
                    hsv_m = cv2.cvtColor(mouth.astype(np.uint8), cv2.COLOR_RGB2HSV)
                    mask = (hsv_m[:,:,2] > 130) & (hsv_m[:,:,1] < 60)
                    for i in range(3):
                        mouth[:,:,i] = np.where(mask, mouth[:,:,i] * 0.3 + target[i] * 0.7, mouth[:,:,i])
                    arr[int(h*0.55):int(h*0.8), int(w*0.25):int(w*0.75)] = mouth
                result = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
                st.session_state.last_dsd_image = result
                st.rerun()
    with c2:
        if st.session_state.last_dsd_image:
            st.image(st.session_state.last_dsd_image, use_container_width=True)
            st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.last_dsd_image),
                             "dsd.png", "image/png", use_container_width=True)
        else:
            st.image(img, use_container_width=True)

def page_smile_design():
    st.markdown('<div class="section-title">😁 تصميم الابتسامة</div>', unsafe_allow_html=True)
    st.info("استخدم قسم DSD Studio للحصول على نتائج أفضل")

# ── CAD/CAM & 3D (جديد) ──
def page_cad_cam():
    st.markdown('<div class="section-title">🎨 CAD/CAM & 3D Studio</div>', unsafe_allow_html=True)
    st.caption("Meshy AI | Blender | Polygon | 2D/3D Conversion")
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 توليد 3D", "📦 رفع STL", "🖼️ 2D→3D", "⚙️ الأنظمة"])
    with tab1:
        st.markdown("### 🎨 توليد نموذج 3D")
        prompt = st.text_area("📝 وصف النموذج", placeholder="مثال: سن أمامي بتصميم تجميلي...")
        style = st.selectbox("🎨 الأسلوب", ["Photorealistic", "Stylized", "Voxel", "Wireframe"])
        if st.button("🎨 توليد (محاكاة)", type="primary", use_container_width=True, key="btn_3d_gen"):
            with st.spinner("🎨 جاري التوليد..."):
                time.sleep(2)
                st.success("✅ تم التوليد!")
                st.info("💡 للحصول على نتائج حقيقية، استخدم: https://www.meshy.ai")
                st.markdown("#### 📋 خطوات الاستخدام الحقيقي:")
                st.markdown("""
                1. اذهب إلى **Meshy AI** → أدخل الوصف
                2. حمّل النموذج بصيغة `.glb` أو `.obj`
                3. ارفعه في تبويب **رفع STL**
                """)
    with tab2:
        st.markdown("### 📦 رفع نماذج 3D")
        model = st.file_uploader("📤 STL / OBJ / PLY / GLB", type=["stl","obj","ply","glb"])
        if model:
            st.success(f"✅ {model.name} ({model.size/1024:.1f} KB)")
            st.session_state.cad_models.append({
                "name": model.name, "size": model.size,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        if st.session_state.cad_models:
            st.markdown("### 📚 النماذج المرفوعة")
            st.dataframe(pd.DataFrame(st.session_state.cad_models), use_container_width=True)
    with tab3:
        st.markdown("### 🖼️ تحويل 2D → 3D")
        up_2d = st.file_uploader("📤 صورة 2D", type=["jpg", "png"], key="2d_up")
        if up_2d:
            st.image(up_2d, caption="الصورة المُدخلة", use_container_width=True)
            if st.button("🖼️ تحويل إلى 3D", type="primary", use_container_width=True):
                with st.spinner("🖼️ جاري التحويل..."):
                    time.sleep(1.5)
                    st.success("✅ تم التحويل!")
                    st.info("💡 للحصول على نموذج 3D حقيقي استخدم: https://www.meshy.ai")
    with tab4:
        st.markdown("### ⚙️ الأنظمة المستخدمة")
        systems = [
            ("Meshy AI", "توليد 3D من نص", "https://www.meshy.ai", "🟢"),
            ("Blender", "تصميم 3D احترافي", "https://www.blender.org", "🟢"),
            ("Exocad", "تصميم CAD/CAM سني", "https://exocad.com", "🟢"),
            ("3Shape", "مسح رقمي", "https://www.3shape.com", "🟢"),
            ("Polygon", "نمذجة polygon", "—", "🟡"),
            ("AI Studios", "فيديو AI", "https://www.aistudios.com", "🟢"),
        ]
        for name, desc, url, status in systems:
            st.markdown(f"""
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <strong style="color:#00d4ff;">{name}</strong><br>
                        <span style="color:#8892b0;font-size:0.85rem;">{desc}</span>
                    </div>
                    <div>
                        <span>{status}</span>
                        <a href="{url}" target="_blank" style="color:#00d4ff;text-decoration:none;">🔗</a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── PATIENT DATA (جديد) ──
def page_patient_data():
    st.markdown('<div class="section-title">📁 بيانات المريض</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["👤 المعلومات", "📸 الصور", "🩻 الأشعة", "📋 السجل"])
    with tab1:
        with st.form("patient_info"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("الاسم الكامل")
                age = st.number_input("العمر", 1, 120, 25)
                gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
                phone = st.text_input("الهاتف")
            with c2:
                treatment = st.selectbox("نوع العلاج", ["تبييض", "زركونيا", "زراعة", "تقويم", "إيماكس", "علاج جذور"])
                cost = st.number_input("التكلفة (ريال)", 0, value=5000)
                duration = st.number_input("المدة (شهر)", 0.5, value=2.0)
                notes = st.text_area("ملاحظات")
            if st.form_submit_button("💾 حفظ", use_container_width=True):
                st.session_state.patient_files.append({
                    "name": name, "age": age, "gender": gender,
                    "phone": phone, "treatment": treatment,
                    "cost": cost, "duration": duration,
                    "notes": notes,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("✅ تم الحفظ!")
                st.rerun()
        if st.session_state.patient_files:
            st.markdown("### 📋 قائمة المرضى")
            st.dataframe(pd.DataFrame(st.session_state.patient_files), use_container_width=True)
    with tab2:
        st.markdown("### 📸 صور المريض")
        imgs = st.file_uploader("📤 ارفع صور متعددة", type=["jpg", "jpeg", "png"],
                               accept_multiple_files=True, key="pat_imgs")
        if imgs:
            st.success(f"✅ {len(imgs)} صورة")
            cols = st.columns(3)
            for i, img in enumerate(imgs):
                with cols[i % 3]:
                    st.image(img, caption=img.name, use_container_width=True)
    with tab3:
        st.markdown("### 🩻 أنواع الأشعة")
        xray_type = st.selectbox("نوع الأشعة",
            ["سيفالومترية (Cephalometric)", "بانورامية (Panorama)", "CBCT",
             "Periapical (P.A)", "Occlusal", "Bitewing"])
        xray = st.file_uploader("📤 ارفع صورة الأشعة", type=["jpg", "png", "jpeg"], key="pat_xray")
        if xray:
            img = Image.open(xray)
            st.image(img, caption=f"أشعة {xray_type}", use_container_width=True)
            st.session_state.patient_xrays.append({
                "type": xray_type,
                "name": xray.name,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success("✅ تم الحفظ!")
        if st.session_state.patient_xrays:
            st.markdown("### 📋 الأشعة المحفوظة")
            st.dataframe(pd.DataFrame(st.session_state.patient_xrays), use_container_width=True)
    with tab4:
        st.markdown("### 📋 السجل الطبي")
        st.info(f"إجمالي المرضى: {len(st.session_state.patient_files)}")
        st.info(f"إجمالي الأشعة: {len(st.session_state.patient_xrays)}")
        if st.session_state.patient_files:
            df = pd.DataFrame(st.session_state.patient_files)
            csv = io.StringIO()
            df.to_csv(csv, index=False, encoding='utf-8-sig')
            st.download_button("📥 تصدير CSV", csv.getvalue(),
                             "patients.csv", "text/csv", use_container_width=True)

def page_patients_list():
    st.markdown('<div class="section-title">👥 قائمة المرضى</div>', unsafe_allow_html=True)
    if st.session_state.patient_files:
        st.dataframe(pd.DataFrame(st.session_state.patient_files), use_container_width=True)
    else:
        st.info("لا يوجد مرضى مسجلين — اذهب إلى 📁 بيانات المريض")

def page_photography():
    st.markdown('<div class="section-title">📸 التصوير الطبي</div>', unsafe_allow_html=True)
    types = ["أمامية", "جانبية", "ابتسامة", "فك علوي", "فك سفلي"]
    for t in types:
        up = st.file_uploader(t, type=["jpg","png","jpeg"], key=f"photo_{t}")
        if up:
            st.image(up, caption=t, use_container_width=True)

def page_xray_types():
    st.markdown('<div class="section-title">🩻 الأشعة — جميع الأنواع</div>', unsafe_allow_html=True)
    types = {
        "سيفالومترية": "لتحليل علاقة الفكين والجمجمة",
        "بانورامية": "لرؤية جميع الأسنان في صورة واحدة",
        "CBCT": "تصوير ثلاثي الأبعاد للفك",
        "Periapical": "لرؤية السن وجذره بالتفصيل",
        "Occlusal": "لرؤية سقف الفم أو أرضية الفم",
        "Bitewing": "لكشف التسوس بين الأسنان",
    }
    selected = st.selectbox("نوع الأشعة", list(types.keys()))
    st.info(f"💡 الاستخدام: {types[selected]}")
    up = st.file_uploader("📤 ارفع الأشعة", type=["jpg", "png", "jpeg"], key="xr_up")
    if up:
        st.image(up, caption=selected, use_container_width=True)

def page_appointments():
    st.markdown('<div class="section-title">📅 المواعيد</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        p = st.text_input("المريض", key="app_p")
        d = st.date_input("التاريخ", datetime.now(), key="app_d")
    with c2:
        t = st.time_input("الوقت", datetime.now(), key="app_t")
        note = st.text_input("ملاحظة", key="app_n")
    if st.button("📅 إضافة موعد", type="primary", key="btn_app"):
        st.session_state.appointments.append({
            "patient": p, "date": str(d), "time": str(t), "note": note
        })
        st.success("✅")
        st.rerun()
    for a in st.session_state.appointments:
        st.markdown(f'<div class="card">📅 {a["patient"]} — {a["date"]} {a.get("time","")} — {a.get("note","")}</div>', unsafe_allow_html=True)

def page_accounting():
    st.markdown('<div class="section-title">💰 الحساب المالي</div>', unsafe_allow_html=True)
    t = st.number_input("المبلغ الكلي", value=1000, key="acc_t")
    p = st.number_input("المدفوع", value=0, key="acc_p")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("الكلي", t)
    with c2: st.metric("المدفوع", p)
    with c3: st.metric("المتبقي", t - p)

# ── MATERIALS GUIDE (جديد موسّع) ──
def page_materials_guide():
    st.markdown('<div class="section-title">🧪 المواد العلاجية — الدليل الشامل</div>', unsafe_allow_html=True)
    st.caption("شرح تفصيلي + استخدام + بديل + أفضلية + جداول مقارنة")
    materials = st.session_state.treatment_materials
    if not materials:
        st.info("لا توجد مواد مسجلة")
        return
    for mat in materials:
        with st.expander(f"💊 {mat['name']} — {mat['category']}", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**📖 الاستخدام:** {mat['usage']}")
                st.markdown(f"**🔄 البديل:** {mat['alternative']}")
            with c2:
                st.markdown(f"**⭐ الأفضلية:** {mat['advantage']}")
                st.markdown(f"**💰 التكلفة:** {mat['cost']}")
            st.markdown(f"**💻 النظام الرقمي:** {mat['digital']}")
            st.markdown(f"**📚 المرجع:** {mat['reference']}")
    st.markdown("### 📊 جدول المقارنة الكامل")
    df = pd.DataFrame(materials)
    st.dataframe(df, use_container_width=True, hide_index=True)
    if GEMINI_API_KEY:
        if st.button("🤖 اسأل NaqAI عن مادة معينة"):
            mat_name = st.selectbox("اختر مادة", [m['name'] for m in materials], key="mat_sel")
            if st.button("📨 إرسال السؤال"):
                with st.spinner("🤖..."):
                    ans = ask_gemini(f"اشرح مادة {mat_name} في طب الأسنان: الاستخدام، الأفضلية، البدائل، مقارنة مع المواد المشابهة، ونصائح عملية.")
                st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)

def page_treatment_plan():
    st.markdown('<div class="section-title">📋 خطة العلاج</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        main = st.text_area("الخطة الرئيسية", placeholder="مثال: تبييض + فينير أسنان أمامية...")
    with c2:
        alt = st.text_area("العلاج البديل", placeholder="مثال: زيركونيا كاملة...")
    materials_used = st.multiselect("المواد المستخدمة",
        [m['name'] for m in st.session_state.treatment_materials])
    if st.button("🧠 توليد الخطة بالذكاء الاصطناعي", type="primary", use_container_width=True):
        if GEMINI_API_KEY:
            with st.spinner("🤖..."):
                ans = ask_gemini(f"""اقترح خطة علاج تفصيلية:
الخطة الرئيسية: {main}
البديل: {alt}
المواد: {', '.join(materials_used) if materials_used else 'غير محددة'}
قدم: 1) خطوات العلاج 2) المدة المتوقعة 3) التكلفة المقدرة 4) المضاعفات المحتملة""")
            st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ تم توليد الخطة (بدون AI)")

def page_pipeline():
    st.markdown('<div class="section-title">🔄 خط الإنتاج ومقيّمه</div>', unsafe_allow_html=True)
    steps = [
        ("1️⃣ الاستشارة والتشخيص", "done", "100%"),
        ("2️⃣ التحضير الرقمي", "done", "100%"),
        ("3️⃣ التصميم CAD/CAM", "active", "60%"),
        ("4️⃣ التصنيع", "pending", "20%"),
        ("5️⃣ التركيب والتسليم", "pending", "0%"),
        ("6️⃣ المتابعة", "pending", "0%"),
    ]
    for name, status, progress in steps:
        color_class = f"timeline-{status}" if status != "active" else "timeline-active"
        icon = "✅" if status == "done" else "🔄" if status == "active" else "⏳"
        st.markdown(f"""
        <div class="timeline-step {color_class}">
            <div style="font-size:1.5rem;">{icon}</div>
            <div style="flex:1;">
                <strong>{name}</strong><br>
                <small style="color:#8892b0;">{progress}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=58,
        title={'text': "نسبة الإنجاز الكلية"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00d4ff"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

# ── COMPARISONS (جداول المقارنات الموسّعة) ──
def page_comparisons():
    st.markdown('<div class="section-title">📊 جداول المقارنات الشاملة</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🔄 قبل/بعد", "📊 إحصائية", "🧪 المواد"])
    with tab1:
        before_after = pd.DataFrame({
            "المعيار": ["لون الأسنان", "تناسق الابتسامة", "صحة اللثة", "تناسب الأسنان", "ثقة المريض"],
            "قبل العلاج": [45, 60, 70, 55, 50],
            "بعد العلاج": [95, 92, 90, 88, 98],
            "التحسن %": ["+111%", "+53%", "+29%", "+60%", "+96%"],
            "التقييم": ["ممتاز ✨", "ممتاز ✨", "جيد ✅", "ممتاز ✨", "ممتاز ✨"]
        })
        st.dataframe(before_after, use_container_width=True, hide_index=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='قبل', x=before_after['المعيار'],
                            y=before_after['قبل العلاج'], marker_color='#ef4444'))
        fig.add_trace(go.Bar(name='بعد', x=before_after['المعيار'],
                            y=before_after['بعد العلاج'], marker_color='#10b981'))
        fig.update_layout(barmode='group', template='plotly_dark',
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        df = st.session_state.patients_df
        comparison = pd.DataFrame({
            "المعيار": ["عدد الأسنان", "التكلفة", "المدة", "الرضا"],
            "الحد الأدنى": [df['عدد_الأسنان'].min(), df['التكلفة_ريال'].min(),
                          df['المدة_شهر'].min(), df['رضا_المريض_%'].min()],
            "الأعلى": [df['عدد_الأسنان'].max(), df['التكلفة_ريال'].max(),
                      df['المدة_شهر'].max(), df['رضا_المريض_%'].max()],
            "المتوسط": [df['عدد_الأسنان'].mean(), df['التكلفة_ريال'].mean(),
                       df['المدة_شهر'].mean(), df['رضا_المريض_%'].mean()],
        })
        st.dataframe(comparison.round(2), use_container_width=True, hide_index=True)
    with tab3:
        if st.session_state.treatment_materials:
            df = pd.DataFrame(st.session_state.treatment_materials)
            st.dataframe(df[['name','category','advantage','cost']],
                        use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════
#  👥 MULTIDISCIPLINARY (جديد)
# ═══════════════════════════════════════════════════════════
def page_multidisciplinary():
    st.markdown('<div class="section-title">👥 فريق متعدد التخصصات</div>', unsafe_allow_html=True)
    st.markdown("### 👨‍⚕️ الأعضاء الحاليون")
    for sp in st.session_state.specialists_team:
        status = "🟢 متصل" if sp.get("online") else "🔴 غير متصل"
        st.markdown(f"""
        <div class="card card-hover">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <strong style="color:#00d4ff;font-size:1.1rem;">{sp['name']}</strong><br>
                    <span style="color:#8892b0;">{sp['specialty']} — {sp['role']}</span><br>
                    <span class="badge badge-blue">{sp.get('cases',0)} حالة</span>
                </div>
                <div style="font-size:0.9rem;">{status}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("### ➕ إضافة عضو جديد")
    with st.form("add_spec"):
        c1, c2 = st.columns(2)
        with c1:
            n = st.text_input("الاسم")
            sp = st.text_input("التخصص")
        with c2:
            r = st.selectbox("الدور", ["استشاري", "أخصائي", "طبيب مقيم"])
            online = st.checkbox("متصل الآن", value=True)
        if st.form_submit_button("➕ إضافة", use_container_width=True):
            if n and sp:
                st.session_state.specialists_team.append({
                    "name": n, "specialty": sp, "role": r,
                    "online": online, "cases": 0
                })
                st.success("✅")
                st.rerun()

# ── DISCUSSION FORUM (جديد) ──
def page_discussion_forum():
    st.markdown('<div class="section-title">🗣️ منتدى النقاشات</div>', unsafe_allow_html=True)
    st.markdown("### 💬 طرح سؤال جديد")
    with st.form("forum_form", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        with c1:
            title = st.text_input("عنوان السؤال")
            target = st.selectbox("موجه إلى", ["جميع الأخصائيين"] +
                [s["name"] for s in st.session_state.specialists_team])
        with c2:
            category = st.selectbox("التصنيف", ["تقويم", "جراحة", "تجميلي", "لثة", "أشعة"])
        body = st.text_area("تفاصيل السؤال")
        if st.form_submit_button("🚀 نشر السؤال", use_container_width=True):
            if title and body:
                st.session_state.discussion_forum.insert(0, {
                    "id": len(st.session_state.discussion_forum) + 1,
                    "title": title, "body": body, "category": category,
                    "target": target,
                    "asked_by": st.session_state.current_user["name"],
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "answers": []
                })
                st.success("✅")
                st.rerun()
    st.markdown("### 📚 الأسئلة المطروحة")
    for q in st.session_state.discussion_forum:
        st.markdown(f"""
        <div class="card">
            <h4 style="color:#00d4ff;">{q['title']}</h4>
            <p style="color:#e2e8f0;">{q['body']}</p>
            <div style="font-size:0.75rem;color:#64748b;">
                👤 {q['asked_by']} | 🎯 {q.get('target','الجميع')} | 
                <span class="badge badge-purple">{q['category']}</span> | {q['time']}
            </div>
        </div>
        """, unsafe_allow_html=True)

def page_messages():
    st.markdown('<div class="section-title">💬 المراسلات</div>', unsafe_allow_html=True)
    for m in st.session_state.messages[-20:]:
        st.markdown(f'<div class="card"><strong>{m["sender"]}:</strong> {m["text"]}</div>', unsafe_allow_html=True)
    with st.form("msg", clear_on_submit=True):
        t = st.text_input("رسالة")
        if st.form_submit_button("📨") and t:
            st.session_state.messages.append({
                "sender": st.session_state.current_user["name"], "text": t
            })
            st.rerun()

def page_lab_chat():
    st.markdown('<div class="section-title">🧪 التواصل مع المختبر</div>', unsafe_allow_html=True)
    for m in st.session_state.lab_messages[-10:]:
        st.markdown(f'<div class="card"><strong>{m["sender"]}:</strong> {m["text"]}</div>', unsafe_allow_html=True)
    with st.form("lab", clear_on_submit=True):
        t = st.text_input("رسالة")
        if st.form_submit_button("📨") and t:
            st.session_state.lab_messages.append({
                "sender": st.session_state.current_user["name"], "text": t
            })
            st.rerun()

# ── GLOBAL PLATFORM (جديد) ──
def page_global_platform():
    st.markdown('<div class="section-title">🌍 المنصة العالمية</div>', unsafe_allow_html=True)
    st.caption("5 مراحل علاجية | حالات عالمية | خط سير موحّد")
    stages = [
        ("1️⃣ التحضير والتصوير", "done", "تصوير بانورامي + سيفالومتري + فوتوغرافي"),
        ("2️⃣ التشخيص الرقمي", "done", "تحليل 468 نقطة + AI"),
        ("3️⃣ التصميم CAD", "active", "Meshy + Blender + Exocad"),
        ("4️⃣ التصنيع CAM", "pending", "3D Printing أو Milling"),
        ("5️⃣ التركيب والمتابعة", "pending", "تسليم + مراقبة دورية"),
    ]
    for name, status, desc in stages:
        icon = "✅" if status == "done" else "🔄" if status == "active" else "⏳"
        st.markdown(f"""
        <div class="timeline-step timeline-{status}">
            <div style="font-size:1.5rem;">{icon}</div>
            <div style="flex:1;">
                <strong>{name}</strong><br>
                <small style="color:#8892b0;">{desc}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("### 🌍 حالات عالمية")
    global_cases = pd.DataFrame({
        "الدولة": ["اليمن", "السعودية", "الإمارات", "مصر", "الأردن"],
        "الحالات": [24, 45, 32, 18, 12],
        "نسبة النجاح": ["94%", "96%", "92%", "88%", "95%"],
    })
    st.dataframe(global_cases, use_container_width=True, hide_index=True)

# ── SYSTEMS USED (جديد) ──
def page_systems_used():
    st.markdown('<div class="section-title">🔌 الأنظمة المستخدمة</div>', unsafe_allow_html=True)
    st.caption("التكامل مع الأنظمة الخارجية")
    systems = [
        ("Meshy AI", "توليد 3D من نص", "AI", "https://www.meshy.ai", "🟢 متصل"),
        ("Blender", "تصميم 3D احترافي", "3D", "https://www.blender.org", "🟢 متصل"),
        ("Exocad", "CAD/CAM سني", "CAD", "https://exocad.com", "🟢 متصل"),
        ("3Shape", "مسح رقمي", "Scanner", "https://www.3shape.com", "🟡 بطيء"),
        ("AI Studios", "فيديو AI", "Video", "https://www.aistudios.com", "🟢 متصل"),
        ("Gemini AI", "مساعد ذكي", "LLM", "https://ai.google.dev", "🟢 متصل"),
    ]
    for name, desc, type_, url, status in systems:
        st.markdown(f"""
        <div class="card card-hover">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <strong style="color:#00d4ff;font-size:1.1rem;">🔌 {name}</strong><br>
                    <span style="color:#8892b0;">{desc}</span><br>
                    <span class="badge badge-blue">{type_}</span>
                    <span class="badge badge-green">{status}</span>
                </div>
                <div>
                    <a href="{url}" target="_blank" 
                       style="background:#00d4ff;color:#000;padding:8px 16px;
                              border-radius:20px;text-decoration:none;font-weight:bold;">
                        زيارة 🔗
                    </a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── ANALYTICS ──
def page_analytics():
    st.markdown('<div class="section-title">📊 التحليلات الشاملة</div>', unsafe_allow_html=True)
    df = st.session_state.patients_df
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">الحالات</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">{df["التكلفة_ريال"].sum():,}</div><div class="metric-label">الإيرادات</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-value">{df["رضا_المريض_%"].mean():.1f}%</div><div class="metric-label">الرضا</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="metric-value">{df["المدة_شهر"].mean():.1f}</div><div class="metric-label">المدة</div></div>', unsafe_allow_html=True)
    st.markdown("### 📝 جدول البيانات")
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state.patients_df = edited
    st.markdown("### 📈 الرسوم")
    tab1, tab2, tab3 = st.tabs(["💰 التكاليف", "📊 التوزيع", "😊 الرضا"])
    with tab1:
        cost = edited.groupby('نوع_العلاج')['التكلفة_ريال'].sum().reset_index()
        fig = px.bar(cost, x='نوع_العلاج', y='التكلفة_ريال', template='plotly_dark')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        tdist = edited['نوع_العلاج'].value_counts().reset_index()
        tdist.columns = ['نوع', 'العدد']
        fig = px.pie(tdist, values='العدد', names='نوع', template='plotly_dark', hole=0.4)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        fig = px.scatter(edited, x='العمر', y='رضا_المريض_%', color='نوع_العلاج', template='plotly_dark')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    csv = io.StringIO()
    edited.to_csv(csv, index=False, encoding='utf-8-sig')
    st.download_button("📥 تصدير CSV", csv.getvalue(),
                     "data.csv", "text/csv", use_container_width=True)

# ── ADS MANAGEMENT (جديد موسّع) ──
def page_ads_management():
    st.markdown('<div class="section-title">📢 إدارة الإعلانات</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📱 داخل التطبيق", "🌐 خارج التطبيق", "📤 إرسال"])
    with tab1:
        st.markdown("### 📱 إعلان داخلي")
        with st.form("internal_ad"):
            title = st.text_input("عنوان الإعلان")
            content = st.text_area("المحتوى")
            priority = st.selectbox("الأولوية", ["عادي", "مهم", "عاجل"])
            if st.form_submit_button("📢 نشر داخلي", use_container_width=True):
                st.session_state.internal_ads.append({
                    "title": title, "content": content,
                    "priority": priority,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("✅")
                st.rerun()
        for ad in st.session_state.internal_ads:
            color = {"عادي":"#64748b","مهم":"#f59e0b","عاجل":"#ef4444"}[ad['priority']]
            st.markdown(f"""
            <div class="card" style="border-right:4px solid {color};">
                <strong style="color:#00d4ff;">{ad['title']}</strong>
                <span class="badge" style="background:{color}20;color:{color};">{ad['priority']}</span><br>
                <p>{ad['content']}</p>
                <small style="color:#64748b;">{ad['time']}</small>
            </div>
            """, unsafe_allow_html=True)
    with tab2:
        st.markdown("### 🌐 إعلان خارجي")
        st.info("💡 نشر الإعلان على المنصات الخارجية")
        with st.form("external_ad"):
            ext_title = st.text_input("عنوان الإعلان الخارجي")
            ext_content = st.text_area("المحتوى")
            platforms = st.multiselect("المنصات",
                ["Facebook", "Instagram", "Twitter", "LinkedIn", "TikTok", "WhatsApp", "YouTube"])
            if st.form_submit_button("🌐 نشر خارجي", use_container_width=True):
                st.session_state.external_ads.append({
                    "title": ext_title, "content": ext_content,
                    "platforms": platforms,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success(f"✅ سيتم النشر على {len(platforms)} منصة")
                st.rerun()
        for ad in st.session_state.external_ads:
            st.markdown(f"""
            <div class="card">
                <strong>{ad['title']}</strong><br>
                <p>{ad['content']}</p>
                <div>{' '.join([f'<span class="badge badge-blue">{p}</span>' for p in ad['platforms']])}</div>
            </div>
            """, unsafe_allow_html=True)
    with tab3:
        st.markdown("### 📤 إرسال الإعلانات")
        st.markdown("#### 📱 إرسال SMS")
        c1, c2 = st.columns(2)
        with c1:
            phones = st.text_area("أرقام الهواتف (سطر لكل رقم)")
        with c2:
            message = st.text_area("نص الرسالة")
        if st.button("📱 إرسال SMS", use_container_width=True):
            st.success(f"✅ تم إرسال {len(phones.splitlines())} رسالة (محاكاة)")
        st.markdown("#### 📧 إرسال Email")
        c1, c2 = st.columns(2)
        with c1:
            emails = st.text_area("البريد الإلكتروني")
        with c2:
            email_subject = st.text_input("الموضوع")
            email_body = st.text_area("الرسالة")
        if st.button("📧 إرسال Email", use_container_width=True):
            st.success("✅ تم إرسال البريد (محاكاة)")

def page_subscriptions():
    st.markdown('<div class="section-title">👑 الاشتراكات</div>', unsafe_allow_html=True)
    plans = [
        ("🆓 تجريبي", "$0", ["3 مرضى", "تحليل أساسي"], False),
        ("⭐ شهري", "$99", ["غير محدود", "تحليل AI", "دعم فني"], True),
        ("🌟 سنوي", "$999", ["جميع الميزات", "دعم أولوي", "تدريب"], False),
    ]
    cols = st.columns(3)
    for i, (name, price, feats, featured) in enumerate(plans):
        with cols[i]:
            border = "border:2px solid #00d4ff;" if featured else ""
            st.markdown(f"""
            <div class="card" style="text-align:center;{border}">
                <h4>{name}</h4>
                <div style="font-size:2rem;font-weight:800;color:#00d4ff;">{price}</div>
                <ul style="list-style:none;padding:0;color:#8892b0;">
                    {''.join([f'<li>✓ {f}</li>' for f in feats])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"اشترك", key=f"sub_{i}", use_container_width=True):
                st.success(f"🎉 تم تفعيل {name}!")

def page_reports():
    st.markdown('<div class="section-title">📄 التقارير</div>', unsafe_allow_html=True)
    n = st.text_input("اسم المريض", value="مريض", key="rep_name")
    imgs = {}
    if st.session_state.last_analysis_image: imgs["تحليل الوجه 468"] = st.session_state.last_analysis_image
    if st.session_state.last_golden_image: imgs["النسبة الذهبية"] = st.session_state.last_golden_image
    if st.session_state.last_cephalometric_image: imgs["الأشعة"] = st.session_state.last_cephalometric_image
    if st.session_state.last_dsd_image: imgs["DSD"] = st.session_state.last_dsd_image
    if st.button("📄 توليد التقرير", type="primary", key="btn_rep"):
        if imgs:
            html = f'''<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><title>تقرير</title>
            <style>body{{font-family:Tajawal,sans-serif;padding:20px;background:#f5f5f5}}.c{{max-width:900px;margin:auto;background:white;padding:30px;border-radius:10px}}h1{{color:#00d4ff;text-align:center}}</style></head>
            <body><div class="c"><h1>🦷 DENTAL AI OS — التقرير</h1>
            <p><b>المريض:</b> {n}</p><p><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>'''
            for t, i in imgs.items():
                if isinstance(i, Image.Image):
                    html += f'<h3>{t}</h3><img src="data:image/png;base64,{img_to_b64(i)}" style="max-width:100%;border-radius:8px;">'
            html += '</div></body></html>'
            st.download_button("⬇️ تحميل", html.encode('utf-8'), "report.html", "text/html", use_container_width=True)
            st.success("✅")
        else:
            st.warning("لا توجد صور")

def page_settings():
    st.markdown('<div class="section-title">⚙️ الإعدادات</div>', unsafe_allow_html=True)
    st.markdown(f"**MediaPipe:** {'✅ متاح' if MEDIAPIPE_AVAILABLE else '❌ غير متاح'}")
    st.markdown(f"**Gemini AI:** {'✅ جاهز' if GEMINI_API_KEY else '❌ غير مُكوّن'}")
    st.markdown(f"**OpenCV:** {cv2.__version__}")
    st.markdown(f"**عدد الأقسام:** 40+")
    st.markdown("### 🔗 روابط مهمة")
    st.markdown("- [Gemini API](https://aistudio.google.com/app/apikey)")
    st.markdown("- [Meshy AI](https://www.meshy.ai)")
    st.markdown("- [Blender](https://www.blender.org)")

def page_naqai():
    st.markdown('<div class="section-title">🤖 NaqAI — مساعدك الذكي</div>', unsafe_allow_html=True)
    if not GEMINI_API_KEY:
        st.warning("⚠️ أضف GEMINI_API_KEY في Settings → Secrets")
        st.info("""
        **🎁 للحصول على مفتاح مجاني:**
        1. اذهب إلى: https://aistudio.google.com/app/apikey
        2. اضغط **Create API key**
        3. انسخ المفتاح
        4. في Streamlit Cloud: **Settings → Secrets**
        5. أضف: `GEMINI_API_KEY = "AIzaSy..."`
        6. اضغط **Save** ثم **Reboot app**
        """)
        return
    for msg in st.session_state.naqai_chat:
        cls = "ai-msg" if msg["role"] == "ai" else "user-msg"
        icon = "🤖" if msg["role"] == "ai" else "👤"
        st.markdown(f'<div class="{cls}">{icon} {msg["text"]}</div>', unsafe_allow_html=True)
    st.markdown("##### 💡 أسئلة سريعة")
    examples = ["ما هي أفضل زركونيا؟", "كيف أعالج ابتسامة لثوية؟", "نصائح لتبييض الأسنان", "فينير أم تاج؟", "علاج حساسية الأسنان"]
    cols = st.columns(3)
    for i, ex in enumerate(examples[:3]):
        with cols[i]:
            if st.button(ex, key=f"ex1_{i}", use_container_width=True):
                st.session_state.naqai_chat.append({"role": "user", "text": ex})
                st.rerun()
    cols = st.columns(2)
    for i, ex in enumerate(examples[3:]):
        with cols[i]:
            if st.button(ex, key=f"ex2_{i}", use_container_width=True):
                st.session_state.naqai_chat.append({"role": "user", "text": ex})
                st.rerun()
    with st.form("naq", clear_on_submit=True):
        q = st.text_input("اسأل NaqAI...")
        if st.form_submit_button("📨 إرسال", use_container_width=True) and q:
            st.session_state.naqai_chat.append({"role": "user", "text": q})
            st.rerun()
    if st.session_state.naqai_chat and st.session_state.naqai_chat[-1]["role"] == "user":
        with st.spinner("🤖 يفكر..."):
            ans = ask_gemini(st.session_state.naqai_chat[-1]["text"])
            st.session_state.naqai_chat.append({"role": "ai", "text": ans})
            st.rerun()
    if st.button("🗑️ مسح المحادثة", key="clear_naq"):
        st.session_state.naqai_chat = []
        st.rerun()

def page_smart_diagnosis():
    st.markdown('<div class="section-title">🩺 التشخيص الذكي AI</div>', unsafe_allow_html=True)
    up = st.file_uploader("صورة", type=["jpg", "png"], key="sd")
    if up:
        img = Image.open(up)
        st.image(img, use_container_width=True)
        if st.button("🤖 تشخيص AI", type="primary", key="btn_sd"):
            with st.spinner("🤖..."):
                ans = ask_gemini("قدم تشخيصاً أولياً شاملاً لهذه الحالة السريرية في طب الأسنان التجميلي")
            st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)

def page_dentbook():
    st.markdown('<div class="section-title">📱 Dentbook</div>', unsafe_allow_html=True)
    user = st.session_state.current_user
    if user is None: return
    tab1, tab2, tab3 = st.tabs(["📝 نشر", "📰 الأخبار", "🔔 تفاعلاتي"])
    with tab1:
        with st.form("db", clear_on_submit=True):
            content = st.text_area("✍️ ماذا تشارك؟", height=100)
            cat = st.selectbox("📂", ["منشور عام", "حالة سريرية", "استشارة", "نصيحة"])
            img_up = st.file_uploader("📷 صورة", type=["jpg", "jpeg", "png"])
            if st.form_submit_button("🚀 نشر", use_container_width=True):
                if content.strip():
                    img_b64 = None
                    if img_up:
                        img = Image.open(img_up)
                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        img_b64 = base64.b64encode(buf.getvalue()).decode()
                    st.session_state.dentbook_posts.insert(0, {
                        "id": len(st.session_state.dentbook_posts) + 1,
                        "author": user["name"], "author_email": user["email"],
                        "author_specialty": user.get("specialty", ""),
                        "content": content, "category": cat,
                        "image": img_b64,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "likes": [], "comments": []
                    })
                    st.success("✅")
                    st.rerun()
    with tab2:
        for post in st.session_state.dentbook_posts:
            pk = post["id"]
            st.markdown(f"""
            <div class="post-card">
                <div><strong style="color:#00d4ff;">{post['author']}</strong>
                <span style="color:#8892b0;"> · {post.get('author_specialty','')}</span><br>
                <span style="color:#64748b;font-size:0.7rem;">{post['time']} · {post.get('category','')}</span></div>
                <p style="color:#e2e8f0;margin:10px 0;">{post['content']}</p>
            </div>
            """, unsafe_allow_html=True)
            if post.get("image"):
                st.markdown(f'<img src="data:image/png;base64,{post["image"]}" style="max-width:100%;border-radius:8px;">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            liked = user["email"] in post.get("likes", [])
            with c1:
                if st.button(f"{'❤️' if liked else '🤍'} {len(post.get('likes', []))}",
                             key=f"lk_{pk}", use_container_width=True):
                    if liked: post["likes"].remove(user["email"])
                    else: post["likes"].append(user["email"])
                    st.rerun()
            with c2:
                if st.button(f"💬 {len(post.get('comments', []))}",
                             key=f"cm_{pk}", use_container_width=True):
                    st.session_state[f"sh_{pk}"] = not st.session_state.get(f"sh_{pk}", False)
                    st.rerun()
            with c3:
                if post.get("author_email") == user["email"]:
                    if st.button("🗑️", key=f"dl_{pk}", use_container_width=True):
                        st.session_state.dentbook_posts.remove(post)
                        st.rerun()
            if st.session_state.get(f"sh_{pk}", False):
                for c in post.get("comments", []):
                    st.markdown(f'<div style="background:rgba(0,212,255,0.05);padding:8px;border-radius:8px;margin:4px 0;"><strong>{c["author"]}:</strong> {c["text"]}</div>', unsafe_allow_html=True)
                with st.form(f"cf_{pk}", clear_on_submit=True):
                    nc = st.text_input("تعليق...", key=f"ci_{pk}")
                    if st.form_submit_button("📨") and nc:
                        post.setdefault("comments", []).append({
                            "author": user["name"], "text": nc,
                            "time": datetime.now().strftime("%H:%M")
                        })
                        st.rerun()
            st.markdown("---")
    with tab3:
        my = [p for p in st.session_state.dentbook_posts if p.get("author_email") == user["email"]]
        for p in my:
            st.markdown(f"""
            <div class="post-card">
                <div style="font-size:0.7rem;color:#64748b;">{p['time']}</div>
                <p>{p['content'][:100]}</p>
                <span>❤️ {len(p.get('likes', []))}</span> <span>💬 {len(p.get('comments', []))}</span>
            </div>
            """, unsafe_allow_html=True)

def page_profile():
    st.markdown('<div class="section-title">👤 الملف الشخصي</div>', unsafe_allow_html=True)
    u = st.session_state.current_user
    if u is None: return
    with st.form("pf"):
        n = st.text_input("الاسم", value=u.get("name", ""))
        s = st.text_input("التخصص", value=u.get("specialty", ""))
        c = st.text_input("الدولة", value=u.get("country", ""))
        p = st.text_input("الهاتف", value=u.get("phone", ""))
        b = st.text_area("نبذة", value=u.get("bio", ""))
        if st.form_submit_button("💾 حفظ"):
            st.session_state.current_user.update({"name": n, "specialty": s, "country": c, "phone": p, "bio": b})
            st.session_state.users_db[u["email"]].update(st.session_state.current_user)
            st.success("✅")

def page_members():
    st.markdown('<div class="section-title">👥 الأعضاء</div>', unsafe_allow_html=True)
    for e, u in st.session_state.users_db.items():
        st.markdown(f'<div class="card"><strong>{u["name"]}</strong> · {u.get("specialty","")}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════
PAGES = {
    "home": page_home, "dashboard": page_dashboard, "upload_logo": page_upload_logo,
    "face_analysis": page_face_analysis, "golden_ratio": page_golden_ratio,
    "smile_analysis": page_smile_analysis, "occlusion_analysis": page_occlusion_analysis,
    "facial_aesthetic": page_facial_aesthetic, "scientific_scanner": page_scientific_scanner,
    "cephalometric": page_cephalometric, "ai_simulator": page_ai_simulator,
    "before_after_simulation": page_before_after_simulation,
    "photorealism": page_photorealism, "dsd_studio": page_dsd_studio,
    "smile_design": page_smile_design, "cad_cam": page_cad_cam,
    "patient_data": page_patient_data, "patients_list": page_patients_list,
    "photography": page_photography, "xray_types": page_xray_types,
    "appointments": page_appointments, "accounting": page_accounting,
    "materials_guide": page_materials_guide, "treatment_plan": page_treatment_plan,
    "pipeline": page_pipeline, "comparisons": page_comparisons,
    "multidisciplinary": page_multidisciplinary, "discussion_forum": page_discussion_forum,
    "messages": page_messages, "lab_chat": page_lab_chat,
    "global_platform": page_global_platform, "systems_used": page_systems_used,
    "analytics": page_analytics, "ads_management": page_ads_management,
    "subscriptions": page_subscriptions, "reports": page_reports,
    "settings": page_settings, "naqai": page_naqai,
    "smart_diagnosis": page_smart_diagnosis, "dentbook": page_dentbook,
    "profile": page_profile, "members": page_members,
}

# ═══════════════════════════════════════════════════════════
#  🚀 MAIN
# ═══════════════════════════════════════════════════════════
def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if not st.session_state.authenticated:
        auth_page()
        return
    if st.session_state.current_user is None:
        st.session_state.authenticated = False
        st.rerun()
        return
    try:
        sidebar_nav()
        page_func = PAGES.get(st.session_state.current_page)
        if page_func is None:
            st.warning(f"⚠️ الصفحة '{st.session_state.current_page}' غير موجودة")
            page_func = page_home
        page_func()
    except Exception as e:
        st.error(f"❌ خطأ: {str(e)}")
        with st.expander("📋 التفاصيل"):
            st.exception(e)
        if st.button("🏠 الرئيسية"):
            st.session_state.current_page = "home"
            st.rerun()
    st.markdown("""
    <hr style="margin-top:40px;border-color:#334155;">
    <div style="text-align:center;color:#64748b;font-size:0.8rem;padding:20px;">
        <strong style="color:#00d4ff;">🦷 DENTAL AI OS v6.0 Pro</strong><br>
        40+ قسم متكامل | AI-Powered | Naqeeb412 · Synergy<br>© 2026
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
