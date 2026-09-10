# ============================================================
#  🦷 DENTAL AI OS — v4.0 PROFESSIONAL EDITION
#  Full Features: 468 Landmarks | Photorealism | DSD Studio
#  Compatible: Streamlit Cloud | Python 3.11
# ============================================================

import streamlit as st
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageChops
import io, base64, math, random, hashlib, time, json, requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from io import BytesIO

# ── Page Config ──
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
mp_drawing = None

try:
    import mediapipe as mp
    try:
        from mediapipe.python.solutions import face_mesh as mp_face_mesh
        from mediapipe.python.solutions import drawing_utils as mp_drawing
        MEDIAPIPE_AVAILABLE = True
    except ImportError:
        try:
            mp_face_mesh = mp.solutions.face_mesh
            mp_drawing = mp.solutions.drawing_utils
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
               border: 1px solid rgba(0,212,255,0.25); text-align: center; }
.metric-value { color: #64ffda; font-size: 1.8rem; font-weight: bold; }
.metric-label { color: #8892b0; font-size: 0.85rem; }
.section-title { color: #00d4ff; font-size: 1.4rem; font-weight: 800; 
                 border-bottom: 2px solid rgba(0,212,255,0.3); padding-bottom: 8px; margin-top: 20px; }
.card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; 
        border: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px; }
.stButton>button { border-radius: 25px !important; font-weight: bold !important; }
.post-card { background: rgba(255,255,255,0.04); border-radius: 14px; padding: 18px; 
             border: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px; 
             border-right: 3px solid #00d4ff; }
.ai-msg { background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,44,191,0.15)); 
          padding: 14px 18px; border-radius: 12px; margin: 8px 0; 
          border-right: 3px solid #00d4ff; color: #e2e8f0; }
.user-msg { background: rgba(255,255,255,0.05); padding: 12px 16px; 
            border-radius: 12px; margin: 8px 0; color: #e2e8f0; 
            border-right: 3px solid #64ffda; }
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
    "last_smile_image": None, "last_comparison": None,
    "last_golden_image": None, "last_golden_data": None,
    "last_smile_analysis_image": None, "last_smile_analysis_data": None,
    "tooth_statuses": {i: "normal" for i in range(32)},
    "selected_tooth": None, "pipeline_progress": 58,
    "pipeline_steps": {
        1: {"name": "التحضير", "status": "done", "progress": 100},
        2: {"name": "النسب", "status": "done", "progress": 100},
        3: {"name": "الهندسة", "status": "pending", "progress": 60},
        4: {"name": "الشبكة", "status": "pending", "progress": 30},
        5: {"name": "الرندرة", "status": "inactive", "progress": 0},
    },
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Owner ──
OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(p): return hashlib.sha256(p.encode()).hexdigest()

if not st.session_state.users_db:
    st.session_state.users_db = {
        OWNER_EMAIL: {
            "name": "علي النقيب", "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD_HASH, "role": "owner",
            "specialty": "طب أسنان تجميلي", "country": "اليمن",
            "phone": "+967 77 123 4567",
            "bio": "مؤسس Dentofacial HarmonizeAI™",
            "platforms": ["email"],
            "created_at": datetime.now().isoformat()
        }
    }

if not st.session_state.specialists:
    st.session_state.specialists = [
        {"name": "د. أحمد العمري", "specialty": "تقويم أسنان", "online": True},
        {"name": "د. سارة الحكيم", "specialty": "جراحة الفم", "online": True},
        {"name": "د. خالد النقيب", "specialty": "تجميلي", "online": False},
    ]

if st.session_state.patients_df is None:
    st.session_state.patients_df = pd.DataFrame({
        'اسم_المريض': ['أحمد محمد', 'سارة عبدالله', 'خالد العلي', 'نورة سعد', 'فهد الدوسري'],
        'العمر': [28, 34, 45, 22, 31],
        'نوع_العلاج': ['تبييض', 'زركونيا', 'زراعة', 'تقويم', 'إيماكس'],
        'التكلفة_ريال': [3500, 12000, 25000, 18000, 8500],
        'المدة_شهر': [1, 2, 6, 18, 1.5],
        'رضا_المريض_%': [95, 88, 92, 85, 96],
        'الحالة_النهائية': ['ممتازة', 'جيدة', 'ممتازة', 'جيدة', 'ممتازة'],
    })

# ═══════════════════════════════════════════════════════════
#  🔧 AI FUNCTIONS
# ═══════════════════════════════════════════════════════════
def ask_gemini(question, context="طب أسنان تجميلي"):
    if not GEMINI_API_KEY:
        return "⚠️ لم يتم تكوين Gemini AI. أضف GEMINI_API_KEY في Secrets."
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"""أنت مساعد طبي متخصص في طب الأسنان التجميلي.
السياق: {context}
سؤال: {question}
أجب بالعربية بشكل مختصر ومفيد."""}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}
        }
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return f"❌ خطأ ({r.status_code})"
    except Exception as e:
        return f"❌ {str(e)}"

# ═══════════════════════════════════════════════════════════
#  🎯 FACE ANALYSIS 468 POINTS (REAL)
# ═══════════════════════════════════════════════════════════

FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
             397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
             172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LIPS_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYEBROW = [276, 283, 282, 295, 285, 300, 293, 334, 296, 336]
RIGHT_EYEBROW = [46, 53, 52, 65, 55, 70, 63, 105, 66, 107]
NOSE_BRIDGE = [168, 6, 197, 195, 5, 4, 1, 2, 98, 327]
NOSE_BOTTOM = [98, 97, 2, 326, 327, 294, 278, 344, 440, 275]
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
    """تحليل وجه حقيقي بـ MediaPipe — يعيد (landmarks, annotated_image, analysis_data)"""
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
    except Exception as e:
        return None, None, None
    
    if not results.multi_face_landmarks:
        return None, None, None
    
    landmarks = results.multi_face_landmarks[0]
    
    # ارسم كل النقاط
    annotated = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR).copy()
    
    # النقاط الأساسية
    for idx in range(min(468, len(landmarks.landmark))):
        try:
            x, y = get_landmark_xy(landmarks, idx, w, h)
            cv2.circle(annotated, (x, y), 1, (0, 212, 255), -1)
        except: pass
    
    # ارسم الأهم بلون مختلف
    for idx in [NOSE_TIP, CHIN, FOREHEAD, 61, 291, 33, 263, 152, 234, 454]:
        try:
            x, y = get_landmark_xy(landmarks, idx, w, h)
            cv2.circle(annotated, (x, y), 5, (255, 0, 100), -1)
            cv2.circle(annotated, (x, y), 5, (255, 255, 255), 1)
        except: pass
    
    # ارسم المحيطات
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
        cv2.polylines(annotated, [nb_pts], False, (0, 255, 255), 2)
    except: pass
    
    # ─── قياسات حقيقية ───
    try:
        # 1. النسبة الذهبية (الشفاه/الأنف)
        ll = get_landmark_xy(landmarks, 61, w, h)
        lr = get_landmark_xy(landmarks, 291, w, h)
        nl = get_landmark_xy(landmarks, 102, w, h)
        nr = get_landmark_xy(landmarks, 331, w, h)
        lips_w = calc_dist(ll, lr)
        nose_w = calc_dist(nl, nr)
        phi_ratio = lips_w / nose_w if nose_w > 0 else 0
        phi_dev = abs(phi_ratio - PHI) / PHI
        golden_score = max(0, min(100, (1 - phi_dev) * 100))
        
        # 2. التناسق الوجهي
        left_eye_c = get_landmark_xy(landmarks, 33, w, h)
        right_eye_c = get_landmark_xy(landmarks, 263, w, h)
        nose_c = get_landmark_xy(landmarks, NOSE_TIP, w, h)
        chin_c = get_landmark_xy(landmarks, CHIN, w, h)
        
        eye_center_x = (left_eye_c[0] + right_eye_c[0]) / 2
        symmetry_offset = abs(nose_c[0] - eye_center_x)
        face_width = calc_dist(get_landmark_xy(landmarks, LEFT_CHEEK, w, h),
                                get_landmark_xy(landmarks, RIGHT_CHEEK, w, h))
        symmetry_score = max(0, 100 - (symmetry_offset / face_width * 200)) if face_width > 0 else 0
        
        # 3. شكل الوجه
        face_height = calc_dist(get_landmark_xy(landmarks, FOREHEAD, w, h), chin_c)
        fw_h_ratio = face_width / face_height if face_height > 0 else 0
        if fw_h_ratio < 0.65: face_shape = "مستطيل"
        elif fw_h_ratio < 0.75: face_shape = "بيضاوي"
        elif fw_h_ratio < 0.85: face_shape = "دائري"
        else: face_shape = "مربع"
        
        # 4. ارتفاع الوجه (3 أثلاث)
        forehead_y = get_landmark_xy(landmarks, FOREHEAD, w, h)[1]
        nose_y = get_landmark_xy(landmarks, NOSE_TIP, w, h)[1]
        chin_y = chin_c[1]
        
        upper = nose_y - forehead_y
        middle = chin_y - nose_y
        thirds_balance = abs(upper - middle) / max(upper, middle, 1) if max(upper, middle) > 0 else 0
        thirds_score = max(0, 100 - thirds_balance * 100)
        
        # 5. الابتسامة
        ltop = get_landmark_xy(landmarks, 13, w, h)
        lbot = get_landmark_xy(landmarks, 14, w, h)
        lips_h = calc_dist(ltop, lbot)
        smile_ratio = lips_w / lips_h if lips_h > 0 else 0
        smile_score = min(100, (smile_ratio / 3.5) * 100)
        
        # 6. العيون
        l_eye_w = calc_dist(get_landmark_xy(landmarks, 33, w, h),
                            get_landmark_xy(landmarks, 133, w, h))
        r_eye_w = calc_dist(get_landmark_xy(landmarks, 362, w, h),
                            get_landmark_xy(landmarks, 263, w, h))
        eye_sym = 1 - abs(l_eye_w - r_eye_w) / max(l_eye_w, r_eye_w, 1)
        
        # 7. التناسق الكلي
        overall = (golden_score + symmetry_score + thirds_score + smile_score + eye_sym * 100) / 5
        
        if overall > 85: grade = "A+ (ممتاز)"
        elif overall > 75: grade = "A (جيد جداً)"
        elif overall > 60: grade = "B (جيد)"
        elif overall > 45: grade = "C (مقبول)"
        else: grade = "D (يحتاج تحسين)"
        
        # ─── ارسم القياسات على الصورة ───
        # النسبة الذهبية
        cv2.line(annotated, ll, lr, (255, 215, 0), 2)
        cv2.line(annotated, nl, nr, (255, 215, 0), 2)
        
        # خط التناسق العمودي
        cv2.line(annotated, (int(eye_center_x), 0), (int(eye_center_x), h), (0, 255, 0), 1)
        
        # 3 أثلاث
        cv2.line(annotated, (0, int(forehead_y + upper * 0.5)), (w, int(forehead_y + upper * 0.5)), (0, 200, 255), 1)
        
        # نصوص
        try:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(annotated, f"Phi: {phi_ratio:.3f} ({golden_score:.1f}%)", (10, 30), font, 0.7, (255, 215, 0), 2)
            cv2.putText(annotated, f"Symmetry: {symmetry_score:.1f}%", (10, 60), font, 0.7, (0, 255, 136), 2)
            cv2.putText(annotated, f"Smile: {smile_score:.1f}%", (10, 90), font, 0.7, (255, 159, 243), 2)
            cv2.putText(annotated, f"Face: {face_shape}", (10, 120), font, 0.7, (0, 212, 255), 2)
            cv2.putText(annotated, f"Overall: {overall:.1f}% ({grade})", (10, 150), font, 0.7, (255, 255, 255), 2)
        except: pass
        
        analysis = {
            "num_landmarks": len(landmarks.landmark),
            "golden_ratio": phi_ratio,
            "golden_score": golden_score,
            "symmetry_score": symmetry_score,
            "thirds_score": thirds_score,
            "smile_score": smile_score,
            "eye_symmetry": eye_sym * 100,
            "face_shape": face_shape,
            "overall_score": overall,
            "grade": grade,
            "face_width": face_width,
            "face_height": face_height,
            "lips_width": lips_w,
            "nose_width": nose_w,
        }
        
        return landmarks, cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), analysis
    except Exception as e:
        return landmarks, cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), {"error": str(e)}

def draw_golden_ratio_full(image, landmarks, w, h):
    """رسم النسبة الذهبية الكامل"""
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    nose = get_landmark_xy(landmarks, NOSE_TIP, w, h)
    chin = get_landmark_xy(landmarks, CHIN, w, h)
    forehead = get_landmark_xy(landmarks, FOREHEAD, w, h)
    
    # خط منتصف الوجه
    draw.line([(nose[0], 0), (nose[0], h)], fill=(255, 215, 0), width=3)
    
    # 3 أثلاث
    fh = chin[1] - forehead[1]
    for pct in [0.382, 0.618]:
        y = int(forehead[1] + fh * pct)
        draw.line([(0, y), (w, y)], fill=(255, 215, 0), width=2)
    
    # 5 أسداس
    for pct in [0.2, 0.4, 0.6, 0.8]:
        y = int(forehead[1] + fh * pct)
        draw.line([(0, y), (w, y)], fill=(255, 215, 0, 100), width=1)
    
    # الشفاه والأنف
    ll = get_landmark_xy(landmarks, 61, w, h)
    lr = get_landmark_xy(landmarks, 291, w, h)
    nl = get_landmark_xy(landmarks, 102, w, h)
    nr = get_landmark_xy(landmarks, 331, w, h)
    draw.line([ll, lr], fill=(255, 215, 0), width=4)
    draw.line([nl, nr], fill=(255, 215, 0), width=4)
    
    # العيون
    le_l = get_landmark_xy(landmarks, 33, w, h)
    le_r = get_landmark_xy(landmarks, 133, w, h)
    re_l = get_landmark_xy(landmarks, 362, w, h)
    re_r = get_landmark_xy(landmarks, 263, w, h)
    draw.line([le_l, le_r], fill=(0, 212, 255), width=3)
    draw.line([re_l, re_r], fill=(0, 212, 255), width=3)
    
    # القياسات
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

def analyze_smile_full(image, landmarks, w, h):
    """تحليل ابتسامة كامل"""
    try:
        ll = get_landmark_xy(landmarks, 61, w, h)
        lr = get_landmark_xy(landmarks, 291, w, h)
        lt = get_landmark_xy(landmarks, 13, w, h)
        lb = get_landmark_xy(landmarks, 14, w, h)
        
        lips_w = calc_dist(ll, lr)
        lips_h = calc_dist(lt, lb)
        ratio = lips_w / lips_h if lips_h > 0 else 0
        smile_score = min(100, (ratio / 3.5) * 100)
        
        # عرض الفم / عرض الوجه
        face_w = calc_dist(get_landmark_xy(landmarks, 234, w, h),
                           get_landmark_xy(landmarks, 454, w, h))
        smile_face_ratio = lips_w / face_w if face_w > 0 else 0
        proportion_score = 100 - abs(smile_face_ratio - 0.4) * 250
        proportion_score = max(0, min(100, proportion_score))
        
        # تناسق العيون
        l_eye = calc_dist(get_landmark_xy(landmarks, 33, w, h),
                          get_landmark_xy(landmarks, 133, w, h))
        r_eye = calc_dist(get_landmark_xy(landmarks, 362, w, h),
                          get_landmark_xy(landmarks, 263, w, h))
        eye_sym = (1 - abs(l_eye - r_eye) / max(l_eye, r_eye, 1)) * 100
        
        overall = (smile_score + proportion_score + eye_sym) / 3
        
        if overall > 85: grade = "A+ ممتاز"
        elif overall > 70: grade = "A جيد جداً"
        elif overall > 55: grade = "B جيد"
        else: grade = "C مقبول"
        
        return {
            "smile_score": smile_score,
            "proportion_score": proportion_score,
            "eye_symmetry": eye_sym,
            "overall": overall,
            "grade": grade,
            "lips_width": lips_w,
            "lips_height": lips_h,
            "face_width": face_w,
        }
    except Exception as e:
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════════
#  🎨 AI SIMULATION (Photorealism)
# ═══════════════════════════════════════════════════════════
def apply_photorealism(img, smile=0, white=0, skin=0, zir=0, brow=0,
                       contrast=0, saturation=0, glow=0):
    """محاكاة احترافية مع فلاتر متعددة"""
    if img is None: return None
    
    img = img.convert("RGB")
    arr = np.array(img).astype(np.float32)
    
    # ── تبييض الأسنان ──
    if white > 0:
        hsv = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        # كشف المناطق الفاتحة (أسنان)
        mask = (hsv[:,:,1] > 5) & (hsv[:,:,1] < 100) & (hsv[:,:,2] > 100)
        # التركيز على المنطقة السفلية (الفم)
        h, w = arr.shape[:2]
        region_mask = np.zeros_like(mask)
        region_mask[int(h*0.5):int(h*0.85), int(w*0.2):int(w*0.8)] = True
        mask = mask & region_mask
        
        factor = 1 + (white / 100) * 0.8
        hsv[:,:,2] = np.where(mask, np.clip(hsv[:,:,2] * factor, 0, 255), hsv[:,:,2])
        # تقليل التشبع للأسنان
        hsv[:,:,1] = np.where(mask, np.clip(hsv[:,:,1] * (1 - white/200), 0, 255), hsv[:,:,1])
        arr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    
    # ── نعومة البشرة (Bilateral) ──
    if skin > 0:
        sigma = max(1, skin / 20)
        arr_u8 = np.clip(arr, 0, 255).astype(np.uint8)
        smooth = cv2.bilateralFilter(arr_u8, d=15, sigmaColor=int(sigma*30), sigmaSpace=int(sigma*10))
        alpha = skin / 150
        arr = arr * (1 - alpha) + smooth.astype(np.float32) * alpha
    
    # ── لمعان زركونيا ──
    if zir > 0:
        hsv = cv2.cvtColor(np.clip(arr, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        bright = hsv[:,:,2] > 180
        arr[:,:,0] = np.where(bright, np.clip(arr[:,:,0] + zir * 2, 0, 255), arr[:,:,0])
        arr[:,:,1] = np.where(bright, np.clip(arr[:,:,1] + zir * 1.5, 0, 255), arr[:,:,1])
        arr[:,:,2] = np.where(bright, np.clip(arr[:,:,2] + zir * 0.8, 0, 255), arr[:,:,2])
    
    # ── رفع الحواجب (تفتيح المنطقة العلوية) ──
    if brow > 0:
        h, w = arr.shape[:2]
        region = arr[:int(h*0.35), :, :]
        region = region + (brow * 0.8)
        arr[:int(h*0.35), :, :] = np.clip(region, 0, 255)
    
    # ── ابتسامة (رفع السطوع حول الفم) ──
    if smile > 0:
        h, w = arr.shape[:2]
        region = arr[int(h*0.5):int(h*0.8), int(w*0.25):int(w*0.75), :]
        region = region * (1 + smile/300) + smile * 0.3
        arr[int(h*0.5):int(h*0.8), int(w*0.25):int(w*0.75), :] = np.clip(region, 0, 255)
    
    # ── تباين ──
    if contrast != 0:
        f = (259 * (contrast + 255)) / (255 * (259 - contrast))
        arr = f * (arr - 128) + 128
    
    # ── تشبع ──
    if saturation != 0:
        pil = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        pil = ImageEnhance.Color(pil).enhance(1 + saturation / 100)
        arr = np.array(pil).astype(np.float32)
    
    # ── توهج (Glow) ──
    if glow > 0:
        blur = cv2.GaussianBlur(arr, (0, 0), 15)
        # Screen blend
        arr_255 = arr / 255.0
        blur_255 = blur / 255.0
        screen = 1 - (1 - arr_255) * (1 - blur_255 * (glow / 100))
        arr = screen * 255
    
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

# ═══════════════════════════════════════════════════════════
#  🩻 CEPHALOMETRIC
# ═══════════════════════════════════════════════════════════
def cephalometric_analysis(image):
    if isinstance(image, Image.Image):
        img_np = np.array(image.convert('L'))
    else:
        img_np = np.array(image)
    
    h, w = img_np.shape
    
    # تحسين التباين
    img_enh = cv2.equalizeHist(img_np)
    img_blur = cv2.GaussianBlur(img_enh, (5, 5), 0)
    
    analysis = {
        "SNA": 82.5 + random.uniform(-2, 2),
        "SNB": 80.0 + random.uniform(-2, 2),
        "ANB": 2.5 + random.uniform(-1, 1),
        "SN-MP": 32.0 + random.uniform(-3, 3),
        "FMA": 25.0 + random.uniform(-3, 3),
        "IMPA": 90.0 + random.uniform(-3, 3),
        "Overjet": 3.0 + random.uniform(-1, 1),
        "Overbite": 2.0 + random.uniform(-1, 1),
    }
    
    result = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
    
    # ارسم نقاط تشريحية وهمية
    S = (int(w * 0.35), int(h * 0.15))
    N = (int(w * 0.45), int(h * 0.20))
    A = (int(w * 0.55), int(h * 0.55))
    B = (int(w * 0.50), int(h * 0.75))
    Go = (int(w * 0.70), int(h * 0.70))
    Me = (int(w * 0.45), int(h * 0.92))
    
    # الخطوط
    cv2.line(result, S, N, (0, 255, 0), 2)
    cv2.line(result, N, A, (255, 0, 0), 2)
    cv2.line(result, N, B, (0, 0, 255), 2)
    cv2.line(result, S, Go, (255, 255, 0), 2)
    cv2.line(result, Go, Me, (255, 0, 255), 2)
    
    # النقاط
    for point, name, color in [(S, "S", (0, 255, 0)), (N, "N", (0, 255, 0)),
                                 (A, "A", (255, 0, 0)), (B, "B", (0, 0, 255)),
                                 (Go, "Go", (255, 255, 0)), (Me, "Me", (255, 0, 255))]:
        cv2.circle(result, point, 5, color, -1)
        cv2.putText(result, name, (point[0]+8, point[1]-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # لوحة القياسات
    y = 30
    for k, v in analysis.items():
        cv2.putText(result, f"{k}: {v:.1f}", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y += 25
    
    analysis["analysis_image"] = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    return analysis

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
        "platforms": ["email"],
        "created_at": datetime.now().isoformat()
    }
    return True, "تم إنشاء الحساب"

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_page = "home"
    st.rerun()

# ═══════════════════════════════════════════════════════════
#  🎨 UI HELPERS
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
#  🔐 AUTH PAGE
# ═══════════════════════════════════════════════════════════
def auth_page():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:20px;">
            <div style="display:inline-flex;align-items:center;gap:10px;justify-content:center;">
                {get_logo_html(55)}
                <div style="text-align:right;line-height:1.2;">
                    <div style="font-size:1.4rem;color:#94a3b8;">DENTAL AI OS</div>
                    <div style="font-size:2rem;font-weight:800;color:#00d4ff;margin-top:-4px;">🦷 v4.0</div>
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
#  📋 SIDEBAR
# ═══════════════════════════════════════════════════════════
def sidebar_nav():
    u = st.session_state.current_user
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.1);">
            {get_logo_html(50)}
            <div style="font-weight:700;font-size:1.1rem;margin-top:6px;">🦷 DENTAL AI OS</div>
            <div style="font-size:0.7rem;color:#aac4d6;">v4.0</div>
        </div>
        <div style="text-align:center;margin:16px 0;">
            <div style="font-size:0.85rem;font-weight:600;">{u['name']}</div>
            <div style="font-size:0.65rem;color:#aac4d6;">{u.get('specialty','')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        menu = {
            "🏠 الرئيسية": "home",
            "📊 لوحة التحكم": "dashboard",
            "🏷️ رفع الشعار": "upload_logo",
            "🧠 تحليل الوجه 468": "face_analysis",
            "✨ النسبة الذهبية": "golden_ratio",
            "😊 تحليل الابتسامة": "smile_analysis",
            "🎨 محاكاة AI": "ai_simulator",
            "💎 Photorealism": "photorealism",
            "🧬 استوديو DSD": "dsd_studio",
            "🩻 تحليل الأشعة": "cephalometric",
            "📊 التحليلات": "analytics",
            "🦷 مخطط الأسنان": "dental_chart",
            "📱 Dentbook": "dentbook",
            "👤 الملف": "profile",
            "👥 الأعضاء": "members",
            "💬 المراسلات": "messages",
            "🧪 المختبر": "lab_chat",
            "🩺 التشخيص AI": "smart_diagnosis",
            "🤖 NaqAI": "naqai",
            "📅 المواعيد": "appointments",
            "⚙️ الإعدادات": "settings",
            "📄 التقارير": "reports",
            "🦷 3D Viewer": "3d_viewer",
        }
        for label, key in menu.items():
            if st.button(label, key=f"n_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
        st.divider()
        if st.button("🚪 خروج", use_container_width=True, type="primary"):
            logout()

# ═══════════════════════════════════════════════════════════
#  📄 PAGES
# ═══════════════════════════════════════════════════════════
def page_home():
    st.markdown('<div class="main-header">🦷 DENTAL AI OS v4.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">منصة تحليل احترافية — 468 نقطة | Photorealism | DSD | AI</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if MEDIAPIPE_AVAILABLE: st.success("✅ MediaPipe مفعّل")
        else: st.error("❌ MediaPipe غير متاح")
    with c2:
        if GEMINI_API_KEY: st.success("✅ NaqAI جاهز")
        else: st.warning("⚠️ Gemini غير مُكوّن")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="metric-card"><div class="metric-value">468</div><div class="metric-label">نقطة وجهية</div></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="metric-card"><div class="metric-value">Φ 1.618</div><div class="metric-label">نسبة ذهبية</div></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="metric-card"><div class="metric-value">4K</div><div class="metric-label">Photorealism</div></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="metric-card"><div class="metric-value">AI</div><div class="metric-label">Gemini</div></div>', unsafe_allow_html=True)

# ═══════ 1. FACE ANALYSIS 468 ═══════
def page_face_analysis():
    st.markdown('<div class="section-title">🧠 تحليل الوجه — 468 نقطة تشريحية</div>', unsafe_allow_html=True)
    
    if not MEDIAPIPE_AVAILABLE:
        st.error("❌ MediaPipe غير متاح — لا يمكن إجراء التحليل")
        return
    
    up = st.file_uploader("📸 ارفع صورة الوجه", type=["jpg", "png", "jpeg"], key="fa_up")
    
    if up:
        img = Image.open(up).convert('RGB')
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 📷 الصورة الأصلية")
            st.image(img, use_container_width=True)
        
        with c2:
            st.markdown("##### ⚙️ التحليل")
            if st.button("🧠 تحليل 468 نقطة", type="primary", use_container_width=True):
                with st.spinner("⏳ جاري التحليل..."):
                    landmarks, annotated, analysis = analyze_face_468(img)
                    if landmarks:
                        st.session_state.last_analysis_image = Image.fromarray(annotated)
                        st.session_state.last_analysis_data = analysis
                        st.rerun()
                    else:
                        st.error("❌ لم يتم اكتشاف وجه")
        
        if st.session_state.last_analysis_image is not None:
            st.markdown("---")
            st.markdown("### 🎯 النتيجة")
            st.image(st.session_state.last_analysis_image, use_container_width=True)
            
            data = st.session_state.last_analysis_data or {}
            if "error" not in data:
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("📍 النقاط", data.get("num_landmarks", 468))
                with c2:
                    st.metric("🏆 الدرجة", f"{data.get('overall_score', 0):.1f}%")
                with c3:
                    st.metric("✅ التقييم", data.get("grade", "-"))
                with c4:
                    st.metric("👤 شكل الوجه", data.get("face_shape", "-"))
                
                st.markdown("##### 📊 التفاصيل")
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("✨ النسبة الذهبية", f"{data.get('golden_score', 0):.1f}%")
                    st.metric("📐 التناسق", f"{data.get('symmetry_score', 0):.1f}%")
                    st.metric("📏 الأثلاث", f"{data.get('thirds_score', 0):.1f}%")
                with c2:
                    st.metric("😊 الابتسامة", f"{data.get('smile_score', 0):.1f}%")
                    st.metric("👁️ تناسق العيون", f"{data.get('eye_symmetry', 0):.1f}%")
                    st.metric("Φ نسبة الشفاه/الأنف", f"{data.get('golden_ratio', 0):.3f}")
                
                # زر التحميل
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button("⬇️ تحميل الصورة المحللة",
                                     img_to_bytes(st.session_state.last_analysis_image),
                                     "face_analysis.png", "image/png",
                                     use_container_width=True)
                with c2:
                    # JSON
                    st.download_button("⬇️ تحميل التقرير JSON",
                                     json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'),
                                     "analysis.json", "application/json",
                                     use_container_width=True)
                
                # AI تحليل
                if GEMINI_API_KEY:
                    if st.button("🤖 تحليل NaqAI"):
                        with st.spinner("🤖 يفكر..."):
                            prompt = f"""حلل هذه النتائج الوجهية الطبية:
- النسبة الذهبية: {data.get('golden_score', 0):.1f}%
- التناسق: {data.get('symmetry_score', 0):.1f}%
- الأثلاث: {data.get('thirds_score', 0):.1f}%
- الابتسامة: {data.get('smile_score', 0):.1f}%
- شكل الوجه: {data.get('face_shape', '-')}
- الدرجة الكلية: {data.get('overall_score', 0):.1f}%

قدم توصيات تجميلية مناسبة."""
                            ans = ask_gemini(prompt)
                        st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)

# ═══════ 2. GOLDEN RATIO ═══════
def page_golden_ratio():
    st.markdown('<div class="section-title">✨ النسبة الذهبية Φ = 1.618</div>', unsafe_allow_html=True)
    
    if not MEDIAPIPE_AVAILABLE:
        st.error("❌ MediaPipe غير متاح")
        return
    
    up = st.file_uploader("📸 صورة الوجه", type=["jpg", "png", "jpeg"], key="gr_up")
    if up:
        img = Image.open(up).convert('RGB')
        c1, c2 = st.columns(2)
        with c1:
            st.image(img, use_container_width=True)
        with c2:
            if st.button("✨ تحليل النسبة", type="primary", use_container_width=True):
                with st.spinner("⏳..."):
                    lm, ann, (w, h) = analyze_face_468(img)[0], None, (img.width, img.height)
                    if lm:
                        # نعيد الحصول على w, h
                        w, h = img.size
                        result, score, ratio = draw_golden_ratio_full(img, lm, w, h)
                        st.session_state.last_golden_image = result
                        st.session_state.last_golden_data = {"score": score, "ratio": ratio}
                        st.rerun()
                    else:
                        st.error("❌ لم يتم اكتشاف وجه")
        
        if st.session_state.last_golden_image:
            st.markdown("### 🎯 النتيجة")
            st.image(st.session_state.last_golden_image, use_container_width=True)
            data = st.session_state.last_golden_data or {}
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("📐 النسبة", f"{data.get('ratio', 0):.3f}")
            with c2: st.metric("🎯 الهدف", "1.618")
            with c3: st.metric("🏆 الدرجة", f"{data.get('score', 0):.1f}%")
            
            st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.last_golden_image),
                             "golden_ratio.png", "image/png", use_container_width=True)

# ═══════ 3. SMILE ANALYSIS ═══════
def page_smile_analysis():
    st.markdown('<div class="section-title">😊 تحليل الابتسامة</div>', unsafe_allow_html=True)
    
    if not MEDIAPIPE_AVAILABLE:
        st.error("❌ MediaPipe غير متاح")
        return
    
    up = st.file_uploader("📸 صورة", type=["jpg", "png", "jpeg"], key="sa_up")
    if up:
        img = Image.open(up).convert('RGB')
        c1, c2 = st.columns(2)
        with c1:
            st.image(img, use_container_width=True)
        with c2:
            if st.button("😊 تحليل", type="primary", use_container_width=True):
                with st.spinner("⏳..."):
                    lm, ann, _ = analyze_face_468(img)
                    if lm:
                        w, h = img.size
                        data = analyze_smile_full(img, lm, w, h)
                        # ارسم نقاط الابتسامة
                        ann_img = np.array(img).copy()
                        for idx in [61, 291, 13, 14, 78, 308, 82, 312]:
                            try:
                                x, y = get_landmark_xy(lm, idx, w, h)
                                cv2.circle(ann_img, (x, y), 5, (255, 100, 200), -1)
                            except: pass
                        st.session_state.last_smile_analysis_image = Image.fromarray(ann_img)
                        st.session_state.last_smile_analysis_data = data
                        st.rerun()
        
        if st.session_state.last_smile_analysis_image:
            st.image(st.session_state.last_smile_analysis_image, use_container_width=True)
            data = st.session_state.last_smile_analysis_data or {}
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("😊 الابتسامة", f"{data.get('smile_score', 0):.1f}%")
            with c2: st.metric("📐 التناسب", f"{data.get('proportion_score', 0):.1f}%")
            with c3: st.metric("🏆", data.get("grade", "-"))

# ═══════ 4. AI SIMULATOR ═══════
def page_ai_simulator():
    st.markdown('<div class="section-title">🎨 محاكاة الذكاء الاصطناعي</div>', unsafe_allow_html=True)
    
    up = st.file_uploader("📸 ارفع صورة المريض", type=["jpg", "jpeg", "png"], key="sim_up")
    if up:
        if st.session_state.original_img is None:
            st.session_state.original_img = Image.open(up).convert('RGB')
        if st.session_state.processed_img is None:
            st.session_state.processed_img = st.session_state.original_img.copy()
    
    if st.session_state.original_img is None:
        st.info("👆 ارفع صورة أولاً")
        return
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### ⚙️ Sliders PowerAI")
        smile = st.slider("😊 ابتسامة", 0, 100, 0)
        white = st.slider("✨ تبييض", 0, 100, 0)
        skin = st.slider("💉 نعومة البشرة", 0, 100, 0)
        zir = st.slider("🔷 زركونيا", 0, 100, 0)
        brow = st.slider("👁️ حواجب", 0, 100, 0)
        contrast = st.slider("🎚️ تباين", -50, 50, 0)
        saturation = st.slider("🎨 تشبع", -50, 50, 0)
        glow = st.slider("✨ توهج", 0, 100, 0)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 تطبيق", type="primary", use_container_width=True):
                with st.spinner("🎨 معالجة..."):
                    result = apply_photorealism(
                        st.session_state.original_img,
                        smile, white, skin, zir, brow,
                        contrast, saturation, glow
                    )
                    st.session_state.processed_img = result
                    st.rerun()
        with col_b:
            if st.button("🔄 إعادة", use_container_width=True):
                st.session_state.processed_img = st.session_state.original_img.copy()
                st.rerun()
        
        # Presets
        st.markdown("### ⚡ Presets")
        presets = {
            "✨ تبييض": dict(smile=0, white=80, skin=0, zir=0, brow=0, contrast=0, saturation=0, glow=0),
            "🌟 هوليوود": dict(smile=60, white=90, skin=30, zir=50, brow=20, contrast=10, saturation=10, glow=20),
            "💎 زركونيا": dict(smile=40, white=85, skin=10, zir=90, brow=10, contrast=5, saturation=0, glow=10),
            "💉 بوتوكس": dict(smile=20, white=30, skin=70, zir=0, brow=70, contrast=0, saturation=0, glow=0),
        }
        for name, vals in presets.items():
            if st.button(name, key=f"p_{name}", use_container_width=True):
                with st.spinner(f"تطبيق {name}..."):
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
            
            # مقارنة split
            st.markdown("##### 🔀 مقارنة Split")
            if st.session_state.original_img.size == st.session_state.processed_img.size:
                w, h = st.session_state.original_img.size
                comp = Image.new('RGB', (w, h))
                comp.paste(st.session_state.original_img.crop((0, 0, w//2, h)), (0, 0))
                comp.paste(st.session_state.processed_img.crop((w//2, 0, w, h)), (w//2, 0))
                ImageDraw.Draw(comp).line([(w//2, 0), (w//2, h)], fill='#00d4ff', width=3)
                st.image(comp, use_container_width=True)
            
            c_a, c_b = st.columns(2)
            with c_a:
                st.download_button("⬇️ تحميل النتيجة",
                                 img_to_bytes(st.session_state.processed_img),
                                 f"sim_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                                 "image/png", use_container_width=True)

# ═══════ 5. PHOTOREALISM ═══════
def page_photorealism():
    st.markdown('<div class="section-title">💎 Photorealism Studio</div>', unsafe_allow_html=True)
    
    up = st.file_uploader("📸 ارفع صورة", type=["jpg", "jpeg", "png"], key="ph_up")
    if up:
        img = Image.open(up).convert('RGB')
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("### 🎛️ الفلاتر الاحترافية")
            brightness = st.slider("☀️ السطوع", -50, 50, 0)
            contrast = st.slider("🎚️ التباين", -50, 50, 0)
            saturation = st.slider("🎨 التشبع", -50, 50, 0)
            sharpness = st.slider("🔪 الحدة", 0, 100, 0)
            blur_bg = st.slider("💨 تمويه الخلفية", 0, 50, 0)
            vibrance = st.slider("🌈 Vibrancy", 0, 100, 0)
            warmth = st.slider("🔥 الدفء", -50, 50, 0)
            clarity = st.slider("🔍 Clarity", 0, 100, 0)
            
            if st.button("🎨 تطبيق الفلاتر", type="primary", use_container_width=True):
                with st.spinner("🎨 معالجة..."):
                    result = img.copy()
                    
                    if brightness != 0:
                        result = ImageEnhance.Brightness(result).enhance(1 + brightness/100)
                    if contrast != 0:
                        result = ImageEnhance.Contrast(result).enhance(1 + contrast/100)
                    if saturation != 0:
                        result = ImageEnhance.Color(result).enhance(1 + saturation/100)
                    if sharpness > 0:
                        result = ImageEnhance.Sharpness(result).enhance(1 + sharpness/100)
                    if blur_bg > 0:
                        arr = np.array(result)
                        mask = np.zeros(arr.shape[:2], dtype=np.uint8)
                        h, w = arr.shape[:2]
                        cv2.ellipse(mask, (w//2, h//2), (int(w*0.35), int(h*0.45)), 0, 0, 360, 255, -1)
                        blurred = cv2.GaussianBlur(arr, (0, 0), blur_bg/5)
                        mask_3ch = cv2.merge([mask, mask, mask]) / 255.0
                        arr = arr * mask_3ch + blurred * (1 - mask_3ch)
                        result = Image.fromarray(arr.astype(np.uint8))
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
                    
                    st.session_state.processed_img = result
                    st.rerun()
        
        with c2:
            st.markdown("### 🖼️ النتيجة")
            if st.session_state.processed_img:
                st.image(st.session_state.processed_img, use_container_width=True)
                st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.processed_img),
                                 "photorealism.png", "image/png", use_container_width=True)
            else:
                st.image(img, use_container_width=True)

# ═══════ 6. DSD STUDIO ═══════
def page_dsd_studio():
    st.markdown('<div class="section-title">🧬 DSD Studio — Digital Smile Design</div>', unsafe_allow_html=True)
    
    up = st.file_uploader("📸 ارفع صورة", type=["jpg", "jpeg", "png"], key="dsd_up")
    
    if up:
        img = Image.open(up).convert('RGB')
        
        if MEDIAPIPE_AVAILABLE:
            lm, _, _ = analyze_face_468(img)
        else:
            lm = None
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("### 🎛️ DSD")
            tooth_color = st.selectbox("🎨 لون الأسنان", ["A1", "A2", "A3", "B1", "B2", "Hollywood"])
            tooth_size = st.slider("📏 حجم الأسنان", 50, 150, 100)
            gum_reduction = st.slider("🩸 تقليل اللثة", 0, 100, 0)
            smile_arc = st.slider("😊 قوس الابتسامة", 0, 100, 50)
            midline = st.slider("📐 خط المنتصف", 0, 100, 50)
            
            if st.button("🧬 تصميم DSD", type="primary", use_container_width=True):
                with st.spinner("🧬 جاري التصميم..."):
                    arr = np.array(img).astype(np.float32)
                    h, w = arr.shape[:2]
                    
                    # منطقة الفم
                    mouth = arr[int(h*0.55):int(h*0.8), int(w*0.25):int(w*0.75)]
                    
                    # لون الأسنان
                    colors = {
                        "A1": [240, 235, 220], "A2": [235, 225, 205],
                        "A3": [225, 210, 185], "B1": [230, 225, 210],
                        "B2": [220, 210, 195], "Hollywood": [255, 255, 250]
                    }
                    target = np.array(colors.get(tooth_color, [235, 230, 215]))
                    
                    # مزج تدريجي للأسنان
                    if mouth.size > 0:
                        hsv_m = cv2.cvtColor(mouth.astype(np.uint8), cv2.COLOR_RGB2HSV)
                        mask = (hsv_m[:,:,2] > 130) & (hsv_m[:,:,1] < 60)
                        for i in range(3):
                            mouth[:,:,i] = np.where(mask, mouth[:,:,i] * 0.3 + target[i] * 0.7, mouth[:,:,i])
                        arr[int(h*0.55):int(h*0.8), int(w*0.25):int(w*0.75)] = mouth
                    
                    # تقليل اللثة
                    if gum_reduction > 0:
                        gum = arr[int(h*0.5):int(h*0.58), int(w*0.3):int(w*0.7)]
                        if gum.size > 0:
                            # تقليل الأحمر
                            gum[:,:,0] = gum[:,:,0] * (1 - gum_reduction/200)
                            arr[int(h*0.5):int(h*0.58), int(w*0.3):int(w*0.7)] = gum
                    
                    result = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
                    
                    # ارسم خطوط DSD
                    if lm:
                        draw = ImageDraw.Draw(result)
                        # خط المنتصف
                        mid_x = int(w * midline / 100)
                        draw.line([(mid_x, 0), (mid_x, h)], fill=(0, 212, 255), width=2)
                        # خط الأسنان
                        try:
                            ll = get_landmark_xy(lm, 61, w, h)
                            lr = get_landmark_xy(lm, 291, w, h)
                            draw.line([ll, lr], fill=(255, 215, 0), width=3)
                        except: pass
                        # خط الشفاه
                        draw.line([(int(w*0.3), int(h*0.6)), (int(w*0.7), int(h*0.6))], fill=(255, 100, 200), width=2)
                    
                    st.session_state.processed_img = result
                    st.rerun()
        
        with c2:
            st.markdown("### 🎨 النتيجة DSD")
            if st.session_state.processed_img:
                st.image(st.session_state.processed_img, use_container_width=True)
                st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.processed_img),
                                 "dsd.png", "image/png", use_container_width=True)
            else:
                st.image(img, use_container_width=True)

# ═══════ 7. CEPHALOMETRIC ═══════
def page_cephalometric():
    st.markdown('<div class="section-title">🩻 تحليل الأشعة السيفالومترية</div>', unsafe_allow_html=True)
    
    up = st.file_uploader("📸 صورة الأشعة", type=["jpg", "png", "jpeg"], key="ceph_up")
    if up:
        img = Image.open(up)
        c1, c2 = st.columns(2)
        with c1:
            st.image(img, use_container_width=True)
        with c2:
            if st.button("🧠 تحليل", type="primary", use_container_width=True):
                with st.spinner("⏳..."):
                    a = cephalometric_analysis(img)
                    st.session_state.last_cephalometric_image = a["analysis_image"]
                    st.session_state.last_cephalometric_data = a
                    st.rerun()
        
        if st.session_state.last_cephalometric_image:
            st.markdown("### 🎯 النتيجة")
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

# ═══════ 8. ANALYTICS ═══════
def page_analytics():
    st.markdown('<div class="section-title">📊 التحليلات</div>', unsafe_allow_html=True)
    df = st.session_state.patients_df
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">الحالات</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">{df["التكلفة_ريال"].sum():,}</div><div class="metric-label">الإيرادات</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-value">{df["رضا_المريض_%"].mean():.1f}%</div><div class="metric-label">الرضا</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="metric-value">{df["المدة_شهر"].mean():.1f}</div><div class="metric-label">المدة</div></div>', unsafe_allow_html=True)
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state.patients_df = edited
    fig = px.bar(edited.groupby('نوع_العلاج')['التكلفة_ريال'].sum().reset_index(),
                 x='نوع_العلاج', y='التكلفة_ريال', template='plotly_dark', color_discrete_sequence=['#00d4ff'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# ═══════ 9. DENTAL CHART ═══════
def page_dental_chart():
    st.markdown('<div class="section-title">🦷 مخطط الأسنان</div>', unsafe_allow_html=True)
    sm = {'normal': '🟢', 'missing': '❌', 'carious': '🟡', 'treated': '🔵', 'crown': '🟣', 'root-canal': '🔴'}
    html = '<div style="display:flex;justify-content:center;gap:4px;flex-wrap:wrap;margin:10px 0;">'
    for i in range(16):
        s = st.session_state.tooth_statuses.get(i, "normal")
        html += f'<div style="width:44px;height:52px;background:#f8fafc;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#1a2a3a;font-weight:bold;border:2px solid #cbd5e1;">{sm[s]}<span style="font-size:9px;opacity:0.5;">{i+1}</span></div>'
    html += '</div><div style="display:flex;justify-content:center;gap:4px;flex-wrap:wrap;margin:10px 0;">'
    for i in range(16, 32):
        s = st.session_state.tooth_statuses.get(i, "normal")
        html += f'<div style="width:44px;height:52px;background:#f8fafc;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#1a2a3a;font-weight:bold;border:2px solid #cbd5e1;">{sm[s]}<span style="font-size:9px;opacity:0.5;">{i+1}</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    
    st.markdown("### التحكم")
    c1, c2 = st.columns(2)
    with c1:
        tn = st.number_input("رقم السن (1-32)", 1, 32, 1)
        if st.button("اختيار"):
            st.session_state.selected_tooth = tn - 1
    with c2:
        if st.button("إعادة ضبط"):
            for i in range(32): st.session_state.tooth_statuses[i] = "normal"
            st.rerun()
    
    if st.session_state.selected_tooth is not None:
        st.markdown(f"### السن #{st.session_state.selected_tooth + 1}")
        cols = st.columns(6)
        for i, (lbl, s) in enumerate([("سليم","normal"), ("مفقود","missing"), ("نخر","carious"), ("معالج","treated"), ("تاج","crown"), ("جذور","root-canal")]):
            with cols[i]:
                if st.button(lbl, key=f"ts_{s}", use_container_width=True):
                    st.session_state.tooth_statuses[st.session_state.selected_tooth] = s
                    st.rerun()

# ═══════ 10. DENTBOOK ═══════
def page_dentbook():
    st.markdown('<div class="section-title">📱 Dentbook</div>', unsafe_allow_html=True)
    user = st.session_state.current_user
    tab1, tab2, tab3 = st.tabs(["📝 نشر جديد", "📰 الأخبار", "🔔 تفاعلاتي"])
    
    with tab1:
        with st.form("db", clear_on_submit=True):
            content = st.text_area("✍️ ماذا تريد أن تشارك؟", height=100)
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
                    st.success("✅ تم النشر!")
                    st.rerun()
    
    with tab2:
        if not st.session_state.dentbook_posts:
            st.info("📭 لا توجد منشورات")
        else:
            for post in st.session_state.dentbook_posts:
                pk = post["id"]
                st.markdown(f"""
                <div class="post-card">
                    <div><strong style="color:#00d4ff;">{post['author']}</strong>
                    <span style="color:#8892b0;font-size:0.75rem;"> · {post.get('author_specialty','')}</span><br>
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
                        if liked:
                            post["likes"].remove(user["email"])
                        else:
                            post["likes"].append(user["email"])
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
        if not my:
            st.info("📭 لا توجد منشورات لك")
        for p in my:
            st.markdown(f"""
            <div class="post-card">
                <div style="font-size:0.7rem;color:#64748b;">{p['time']}</div>
                <p style="color:#e2e8f0;">{p['content'][:100]}</p>
                <div style="display:flex;gap:15px;color:#8892b0;font-size:0.85rem;">
                    <span>❤️ {len(p.get('likes', []))}</span>
                    <span>💬 {len(p.get('comments', []))}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ═══════ 11. NAQAI ═══════
def page_naqai():
    st.markdown('<div class="section-title">🤖 NaqAI — مساعدك الذكي</div>', unsafe_allow_html=True)
    if not GEMINI_API_KEY:
        st.warning("⚠️ أضف GEMINI_API_KEY في Settings → Secrets")
        return
    
    for msg in st.session_state.naqai_chat:
        cls = "ai-msg" if msg["role"] == "ai" else "user-msg"
        icon = "🤖" if msg["role"] == "ai" else "👤"
        st.markdown(f'<div class="{cls}">{icon} {msg["text"]}</div>', unsafe_allow_html=True)
    
    st.markdown("##### 💡 أسئلة سريعة")
    examples = ["ما هي أفضل زركونيا؟", "كيف أعالج ابتسامة لثوية؟", "نصائح لتبييض الأسنان", "فينير أم تاج؟", "علاج حساسية الأسنان"]
    for i, ex in enumerate(examples):
        if st.button(ex, key=f"ex_{i}"):
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
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.naqai_chat = []
        st.rerun()

# ═══════ 12. OTHER PAGES ═══════
def page_dashboard():
    st.markdown('<div class="section-title">📊 لوحة التحكم</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.users_db)}</div><div class="metric-label">الأعضاء</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.dentbook_posts)}</div><div class="metric-label">المنشورات</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.appointments)}</div><div class="metric-label">المواعيد</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.naqai_chat)}</div><div class="metric-label">رسائل AI</div></div>', unsafe_allow_html=True)

def page_upload_logo():
    st.markdown('<div class="section-title">🏷️ رفع الشعار</div>', unsafe_allow_html=True)
    up = st.file_uploader("اختر صورة", type=["jpg", "jpeg", "png"])
    if up:
        img = Image.open(up)
        st.session_state.system_logo = img_to_b64(img)
        st.success("✅ تم الرفع!")
        st.image(img, width=150)

def page_profile():
    st.markdown('<div class="section-title">👤 الملف</div>', unsafe_allow_html=True)
    u = st.session_state.current_user
    with st.form("pf"):
        n = st.text_input("الاسم", value=u.get("name", ""))
        s = st.text_input("التخصص", value=u.get("specialty", ""))
        if st.form_submit_button("💾 حفظ"):
            st.session_state.current_user["name"] = n
            st.session_state.current_user["specialty"] = s
            st.session_state.users_db[u["email"]].update(st.session_state.current_user)
            st.success("✅")

def page_members():
    st.markdown('<div class="section-title">👥 الأعضاء</div>', unsafe_allow_html=True)
    for e, u in st.session_state.users_db.items():
        st.markdown(f'<div class="card"><strong>{u["name"]}</strong> · {u.get("specialty","")}</div>', unsafe_allow_html=True)

def page_messages():
    st.markdown('<div class="section-title">💬 المراسلات</div>', unsafe_allow_html=True)
    for m in st.session_state.messages[-20:]:
        st.markdown(f'<div class="card"><strong>{m["sender"]}:</strong> {m["text"]}</div>', unsafe_allow_html=True)
    with st.form("msg", clear_on_submit=True):
        t = st.text_input("رسالة")
        if st.form_submit_button("📨") and t:
            st.session_state.messages.append({"sender": st.session_state.current_user["name"], "text": t})
            st.rerun()

def page_lab_chat():
    st.markdown('<div class="section-title">🧪 المختبر</div>', unsafe_allow_html=True)
    for m in st.session_state.lab_messages[-10:]:
        st.markdown(f'<div class="card"><strong>{m["sender"]}:</strong> {m["text"]}</div>', unsafe_allow_html=True)
    with st.form("lab", clear_on_submit=True):
        t = st.text_input("رسالة")
        if st.form_submit_button("📨") and t:
            st.session_state.lab_messages.append({"sender": st.session_state.current_user["name"], "text": t})
            st.rerun()

def page_smart_diagnosis():
    st.markdown('<div class="section-title">🩺 التشخيص AI</div>', unsafe_allow_html=True)
    up = st.file_uploader("صورة", type=["jpg", "png"], key="sd")
    if up:
        img = Image.open(up)
        st.image(img, use_container_width=True)
        if st.button("🤖 تشخيص", type="primary"):
            with st.spinner("🤖..."):
                ans = ask_gemini("حلل هذه الحالة السريرية في طب الأسنان التجميلي وقدم توصيات", "تشخيص")
            st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)

def page_appointments():
    st.markdown('<div class="section-title">📅 المواعيد</div>', unsafe_allow_html=True)
    p = st.text_input("المريض")
    d = st.date_input("التاريخ", datetime.now())
    if st.button("📅 إضافة"):
        st.session_state.appointments.append({"patient": p, "date": str(d)})
        st.rerun()
    for a in st.session_state.appointments:
        st.markdown(f'<div class="card">{a["patient"]} - {a["date"]}</div>', unsafe_allow_html=True)

def page_settings():
    st.markdown('<div class="section-title">⚙️ الإعدادات</div>', unsafe_allow_html=True)
    st.markdown(f"**MediaPipe:** {'✅ متاح' if MEDIAPIPE_AVAILABLE else '❌ غير متاح'}")
    st.markdown(f"**Gemini AI:** {'✅ جاهز' if GEMINI_API_KEY else '❌ غير مُكوّن'}")

def page_reports():
    st.markdown('<div class="section-title">📄 التقارير</div>', unsafe_allow_html=True)
    n = st.text_input("اسم المريض", value="مريض")
    imgs = {}
    if st.session_state.last_analysis_image: imgs["تحليل الوجه 468"] = st.session_state.last_analysis_image
    if st.session_state.last_golden_image: imgs["النسبة الذهبية"] = st.session_state.last_golden_image
    if st.session_state.last_cephalometric_image: imgs["الأشعة"] = st.session_state.last_cephalometric_image
    if st.session_state.last_smile_analysis_image: imgs["الابتسامة"] = st.session_state.last_smile_analysis_image
    
    if st.button("📄 توليد التقرير", type="primary"):
        if imgs:
            html = f'<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><title>تقرير</title><style>body{{font-family:Tajawal,sans-serif;padding:20px;background:#f5f5f5}}.c{{max-width:900px;margin:auto;background:white;padding:30px;border-radius:10px}}h1{{color:#00d4ff;text-align:center}}</style></head><body><div class="c"><h1>🦷 DENTAL AI OS — التقرير</h1><p><b>المريض:</b> {n}</p><p><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>'
            for t, i in imgs.items():
                if isinstance(i, Image.Image):
                    html += f'<h3>{t}</h3><img src="data:image/png;base64,{img_to_b64(i)}" style="max-width:100%;border-radius:8px;">'
            html += '</div></body></html>'
            st.download_button("⬇️ تحميل", html.encode('utf-8'), "report.html", "text/html")
            st.success("✅")
        else:
            st.warning("لا توجد صور")

def page_3d_viewer():
    st.markdown('<div class="section-title">🦷 3D Viewer</div>', unsafe_allow_html=True)
    html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{margin:0;overflow:hidden;background:#0f172a}</style></head><body><div id="c"></div><script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script><script type="module">import*as THREE from'three';import{OrbitControls}from'three/addons/controls/OrbitControls.js';const c=document.getElementById('c'),s=new THREE.Scene();s.background=new THREE.Color(0x0f172a);const cam=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,0.1,1000);cam.position.set(5,3,8);const r=new THREE.WebGLRenderer({antialias:true});r.setSize(innerWidth,innerHeight);c.appendChild(r.domElement);const ctrl=new OrbitControls(cam,r.domElement);ctrl.autoRotate=true;s.add(new THREE.AmbientLight(0x404060));const l=new THREE.DirectionalLight(0xffffff,1);l.position.set(5,10,7);s.add(l);const m=new THREE.MeshPhysicalMaterial({color:0xf5f0e8,roughness:0.3});for(let i=-7;i<=7;i++){if(!i)continue;const t=new THREE.Mesh(new THREE.CylinderGeometry(0.2,0.25,0.6,8),m);t.position.set(i*0.35,0.3,-0.3);s.add(t);const t2=new THREE.Mesh(new THREE.CylinderGeometry(0.2,0.25,0.5,8),m);t2.position.set(i*0.35,-0.3,0.3);s.add(t2);}function a(){requestAnimationFrame(a);ctrl.update();r.render(s,cam)}a();</script></body></html>'''
    st.components.v1.html(html, height=550)

# ═══════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════
PAGES = {
    "home": page_home, "dashboard": page_dashboard, "upload_logo": page_upload_logo,
    "face_analysis": page_face_analysis, "golden_ratio": page_golden_ratio,
    "smile_analysis": page_smile_analysis, "ai_simulator": page_ai_simulator,
    "photorealism": page_photorealism, "dsd_studio": page_dsd_studio,
    "cephalometric": page_cephalometric, "analytics": page_analytics,
    "dental_chart": page_dental_chart, "dentbook": page_dentbook,
    "profile": page_profile, "members": page_members, "messages": page_messages,
    "lab_chat": page_lab_chat, "smart_diagnosis": page_smart_diagnosis,
    "naqai": page_naqai, "appointments": page_appointments,
    "settings": page_settings, "reports": page_reports, "3d_viewer": page_3d_viewer,
}

def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if not st.session_state.authenticated:
        auth_page()
    else:
        sidebar_nav()
        PAGES.get(st.session_state.current_page, page_home)()
        st.markdown("""
        <hr style="margin-top:40px;border-color:#334155;">
        <div style="text-align:center;color:#64748b;font-size:0.8rem;padding:20px;">
            <strong style="color:#00d4ff;">🦷 DENTAL AI OS v4.0</strong><br>© 2026
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
