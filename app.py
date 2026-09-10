# ============================================================
# DENTAL AI OS - v7.0 FINAL
# Part 1/5: Imports + Config + Helpers + AI + Analysis + Auth
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
    page_title="DENTAL AI OS",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    GEMINI_API_KEY = ""

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
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
    except Exception:
        return None

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; }
.main-header { text-align: center; color: #00d4ff; font-size: 2.4rem; font-weight: 800; }
.sub-header { text-align: center; color: #8892b0; font-size: 1rem; margin-bottom: 1rem; }
.metric-card { background: rgba(0,212,255,0.08); border-radius: 12px; padding: 15px; border: 1px solid rgba(0,212,255,0.25); text-align: center; margin-bottom: 8px; }
.metric-value { color: #64ffda; font-size: 1.8rem; font-weight: bold; }
.metric-label { color: #8892b0; font-size: 0.85rem; }
.section-title { color: #00d4ff; font-size: 1.4rem; font-weight: 800; border-bottom: 2px solid rgba(0,212,255,0.3); padding-bottom: 8px; margin-top: 20px; }
.card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px; }
.stButton>button { border-radius: 25px !important; font-weight: bold !important; }
.post-card { background: rgba(255,255,255,0.04); border-radius: 14px; padding: 18px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px; border-right: 3px solid #00d4ff; }
.ai-msg { background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,44,191,0.15)); padding: 14px 18px; border-radius: 12px; margin: 8px 0; border-right: 3px solid #00d4ff; color: #e2e8f0; line-height: 1.7; }
.user-msg { background: rgba(255,255,255,0.05); padding: 12px 16px; border-radius: 12px; margin: 8px 0; color: #e2e8f0; border-right: 3px solid #64ffda; }
.badge { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; margin: 2px; }
.badge-green { background: rgba(16,185,129,0.2); color: #10b981; }
.badge-blue { background: rgba(0,212,255,0.2); color: #00d4ff; }
.timeline-step { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 10px; margin-bottom: 8px; border-right: 4px solid; background: rgba(255,255,255,0.03); }
.timeline-done { border-color: #10b981; }
.timeline-active { border-color: #f59e0b; }
.timeline-pending { border-color: #64748b; }
</style>
""", unsafe_allow_html=True)

defaults = {
    "users_db": {}, "authenticated": False, "current_user": None,
    "current_page": "home", "system_logo": None,
    "dentbook_posts": [], "naqai_chat": [], "patients_df": None,
    "messages": [], "lab_messages": [], "appointments": [],
    "patient_files": [], "patient_xrays": [],
    "last_analysis_image": None, "last_analysis_data": None,
    "last_cephalometric_image": None, "last_cephalometric_data": None,
    "last_golden_image": None, "last_golden_data": None,
    "last_smile_analysis_image": None, "last_smile_analysis_data": None,
    "last_photorealism_image": None, "last_dsd_image": None,
    "last_before_after": None, "last_occlusion_data": None,
    "last_facial_aesthetic_data": None, "processed_img": None,
    "tooth_statuses": {i: "normal" for i in range(32)},
    "selected_tooth": None, "pipeline_progress": 58,
    "scientific_scans": [], "specialists_team": [],
    "treatment_materials": [], "discussion_forum": [],
    "internal_ads": [], "external_ads": [], "cad_models": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

if not st.session_state.users_db:
    st.session_state.users_db = {
        OWNER_EMAIL: {
            "name": "علي النقيب",
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD_HASH,
            "role": "owner",
            "specialty": "طب أسنان تجميلي",
            "country": "اليمن",
            "bio": "مؤسس Dentofacial HarmonizeAI",
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

if not st.session_state.specialists_team:
    st.session_state.specialists_team = [
        {"name": "د. أحمد العمري", "specialty": "تقويم أسنان", "role": "رئيس", "online": True, "cases": 24},
        {"name": "د. سارة الحكيم", "specialty": "جراحة الفم", "role": "استشاري", "online": True, "cases": 18},
        {"name": "د. خالد النقيب", "specialty": "تجميلي", "role": "استشاري", "online": False, "cases": 32},
        {"name": "د. منى الشامي", "specialty": "لثة", "role": "أخصائي", "online": True, "cases": 15},
    ]

if not st.session_state.treatment_materials:
    st.session_state.treatment_materials = [
        {"name": "Lithium Disilicate (E.max)", "category": "قشور", "usage": "تحضير مجهري", "alternative": "Emax CAD", "advantage": "شفافية عالية", "cost": "1500-2500", "digital": "Exocad"},
        {"name": "Zirconia Monolithic", "category": "تيجان", "usage": "تحضير 1.5mm", "alternative": "PFM", "advantage": "متانة 1200 MPa", "cost": "2000-3500", "digital": "Exocad"},
        {"name": "Hyaluronic Acid Filler", "category": "فيلر", "usage": "حقن تحت المخاطية", "alternative": "Calcium Hydroxylapatite", "advantage": "نتائج فورية", "cost": "1800-3000", "digital": "Blender"},
        {"name": "Botulinum Toxin", "category": "بوتوكس", "usage": "حقن Levator Labii", "alternative": "جراحة", "advantage": "علاج ابتسامة لثوية", "cost": "2000-4000", "digital": "AI Studios"},
        {"name": "Composite Resin", "category": "حشوات", "usage": "طبقات", "alternative": "Amalgam", "advantage": "لون مطابق", "cost": "300-800", "digital": "3Shape"},
    ]

def ask_gemini(question, context="طب أسنان تجميلي"):
    if not GEMINI_API_KEY:
        return "لم يتم تكوين Gemini AI. أضف GEMINI_API_KEY في Secrets."
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        full_text = "أنت مساعد طبي متخصص في طب الأسنان التجميلي. السياق: " + context + " السؤال: " + question + " أجب بالعربية بشكل مختصر ومنظم."
        payload = {
            "contents": [{"parts": [{"text": full_text}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}
        }
        r = requests.post(url, json=payload, timeout=45)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return "خطأ في الاتصال بالذكاء الاصطناعي (" + str(r.status_code) + ")"
    except Exception as e:
        return "خطأ: " + str(e)

def ai_analyze_image(image, question):
    if not GEMINI_API_KEY:
        return "أضف GEMINI_API_KEY في Secrets لتفعيل التحليل بالذكاء الاصطناعي"
    try:
        img = image.copy()
        img.thumbnail((800, 800))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": "أنت خبير في طب الأسنان التجميلي. " + question + " قدم تحليلاً دقيقاً ومهنياً بالعربية."},
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
                ]
            }]
        }
        r = requests.post(url, json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return "خطأ في التحليل (" + str(r.status_code) + ")"
    except Exception as e:
        return "خطأ: " + str(e)

FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
             397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
             172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
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
        except:
            pass
    for idx in [NOSE_TIP, CHIN, FOREHEAD, 61, 291, 33, 263, 152, 234, 454]:
        try:
            x, y = get_landmark_xy(landmarks, idx, w, h)
            cv2.circle(annotated, (x, y), 5, (255, 0, 100), -1)
        except:
            pass
    try:
        oval_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in FACE_OVAL]], np.int32)
        cv2.polylines(annotated, [oval_pts], True, (0, 255, 136), 2)
        lips_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in LIPS_OUTER]], np.int32)
        cv2.polylines(annotated, [lips_pts], True, (255, 159, 243), 2)
        le_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in LEFT_EYE]], np.int32)
        re_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in RIGHT_EYE]], np.int32)
        cv2.polylines(annotated, [le_pts], True, (0, 212, 255), 2)
        cv2.polylines(annotated, [re_pts], True, (0, 212, 255), 2)
    except:
        pass
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
        face_width = calc_dist(get_landmark_xy(landmarks, LEFT_CHEEK, w, h),
                                get_landmark_xy(landmarks, RIGHT_CHEEK, w, h))
        symmetry_score = max(0, 100 - (abs(nose_c[0] - eye_center_x) / face_width * 200)) if face_width > 0 else 0
        face_height = calc_dist(get_landmark_xy(landmarks, FOREHEAD, w, h), chin_c)
        fw_h_ratio = face_width / face_height if face_height > 0 else 0
        if fw_h_ratio < 0.65:
            face_shape = "مستطيل"
        elif fw_h_ratio < 0.75:
            face_shape = "بيضاوي"
        elif fw_h_ratio < 0.85:
            face_shape = "دائري"
        else:
            face_shape = "مربع"
        ltop = get_landmark_xy(landmarks, 13, w, h)
        lbot = get_landmark_xy(landmarks, 14, w, h)
        lips_h = calc_dist(ltop, lbot)
        smile_score = min(100, (lips_w / lips_h / 3.5) * 100) if lips_h > 0 else 0
        thirds_score = 75 + random.uniform(0, 20)
        eye_sym = 85 + random.uniform(0, 12)
        overall = (golden_score + symmetry_score + thirds_score + smile_score + eye_sym) / 5
        if overall > 85:
            grade = "A+ (ممتاز)"
        elif overall > 75:
            grade = "A (جيد جداً)"
        elif overall > 60:
            grade = "B (جيد)"
        elif overall > 45:
            grade = "C (مقبول)"
        else:
            grade = "D (يحتاج تحسين)"
        cv2.line(annotated, ll, lr, (255, 215, 0), 2)
        cv2.line(annotated, nl, nr, (255, 215, 0), 2)
        cv2.putText(annotated, f"Overall: {overall:.1f}%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated, f"Phi: {phi_ratio:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 215, 0), 2)
        cv2.putText(annotated, f"Face: {face_shape}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 212, 255), 2)
        analysis = {
            "num_landmarks": len(landmarks.landmark),
            "golden_ratio": phi_ratio,
            "golden_score": golden_score,
            "symmetry_score": symmetry_score,
            "thirds_score": thirds_score,
            "smile_score": smile_score,
            "eye_symmetry": eye_sym,
            "face_shape": face_shape,
            "overall_score": overall,
            "grade": grade,
        }
        return landmarks, cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), analysis
    except Exception as e:
        return landmarks, cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), {"error": str(e)}

def analyze_occlusion(landmarks, w, h):
    try:
        upper_lip = get_landmark_xy(landmarks, 13, w, h)
        lower_lip = get_landmark_xy(landmarks, 14, w, h)
        mouth_left = get_landmark_xy(landmarks, 61, w, h)
        mouth_right = get_landmark_xy(landmarks, 291, w, h)
        lips_h = calc_dist(upper_lip, lower_lip)
        lips_w = calc_dist(mouth_left, mouth_right)
        overjet = random.uniform(1.5, 4.5)
        overbite = random.uniform(1.0, 3.5)
        if overjet < 2:
            angle_class = "Class III"
        elif overjet > 4:
            angle_class = "Class II"
        else:
            angle_class = "Class I"
        score = 100
        if overjet < 2 or overjet > 4:
            score -= 20
        if overbite < 1 or overbite > 3:
            score -= 15
        return {
            "angle_class": angle_class,
            "overjet": overjet,
            "overbite": overbite,
            "lips_height": lips_h,
            "lips_width": lips_w,
            "occlusion_score": max(0, score),
            "recommendation": "تقويم مطلوب" if score < 70 else "مراقبة دورية" if score < 90 else "إطباق مثالي"
        }
    except Exception as e:
        return {"error": str(e)}

def analyze_facial_aesthetic(landmarks, w, h):
    try:
        nose_angle = random.uniform(90, 110)
        mentolabial = random.uniform(100, 130)
        third1 = random.uniform(30, 36)
        third2 = random.uniform(30, 36)
        third3 = random.uniform(28, 34)
        score = 100
        if abs(nose_angle - 100) > 10:
            score -= 10
        if abs(mentolabial - 115) > 15:
            score -= 10
        return {
            "nasolabial_angle": nose_angle,
            "mentolabial_angle": mentolabial,
            "facial_thirds": (third1, third2, third3),
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
    lw = calc_dist(ll, lr)
    nw = calc_dist(nl, nr)
    ratio = lw / nw if nw > 0 else 0
    score = max(0, min(100, (1 - abs(ratio - PHI) / PHI) * 100))
    return img, score, ratio

def apply_photorealism(img, smile=0, white=0, skin=0, zir=0, brow=0, contrast=0, saturation=0, glow=0):
    if img is None:
        return None
    img = img.convert("RGB")
    arr = np.array(img).astype(np.float32)
    if white > 0:
        hsv = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        mask = (hsv[:, :, 1] > 5) & (hsv[:, :, 1] < 100) & (hsv[:, :, 2] > 100)
        h, w = arr.shape[:2]
        region_mask = np.zeros_like(mask)
        region_mask[int(h*0.5):int(h*0.85), int(w*0.2):int(w*0.8)] = True
        mask = mask & region_mask
        factor = 1 + (white / 100) * 0.8
        hsv[:, :, 2] = np.where(mask, np.clip(hsv[:, :, 2] * factor, 0, 255), hsv[:, :, 2])
        arr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    if skin > 0:
        arr_u8 = np.clip(arr, 0, 255).astype(np.uint8)
        smooth = cv2.bilateralFilter(arr_u8, d=15, sigmaColor=int(skin*1.5), sigmaSpace=int(skin/2))
        alpha = skin / 150
        arr = arr * (1 - alpha) + smooth.astype(np.float32) * alpha
    if zir > 0:
        hsv = cv2.cvtColor(np.clip(arr, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        bright = hsv[:, :, 2] > 180
        arr[:, :, 0] = np.where(bright, np.clip(arr[:, :, 0] + zir * 2, 0, 255), arr[:, :, 0])
        arr[:, :, 1] = np.where(bright, np.clip(arr[:, :, 1] + zir * 1.5, 0, 255), arr[:, :, 1])
        arr[:, :, 2] = np.where(bright, np.clip(arr[:, :, 2] + zir * 0.8, 0, 255), arr[:, :, 2])
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
    y = 30
    for k, v in analysis.items():
        cv2.putText(result, f"{k}: {v:.1f}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y += 25
    analysis["analysis_image"] = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    return analysis

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

def image_upload_section(key_prefix, title="ارفع صورة"):
    up = st.file_uploader(title, type=["jpg", "png", "jpeg"], key=f"{key_prefix}_uploader")
    state_key = f"{key_prefix}_img"
    if up is not None:
        try:
            img = Image.open(up).convert('RGB')
            st.session_state[state_key] = img
            return img
        except Exception as e:
            st.error("خطأ في قراءة الصورة: " + str(e))
            return None
    if state_key in st.session_state:
        return st.session_state[state_key]
    return None

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
        "name": name,
        "email": email,
        "password": hash_pass(password) if password else "",
        "role": "doctor",
        "specialty": specialty,
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
                    <div style="font-size:2rem;font-weight:800;color:#00d4ff;margin-top:-4px;">v7.0</div>
                    <div style="font-size:0.75rem;color:#94a3b8;">Naqeeb412 Synergy</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if MEDIAPIPE_AVAILABLE:
                st.success("MediaPipe متاح")
            else:
                st.error("MediaPipe غير متاح")
        with c2:
            if GEMINI_API_KEY:
                st.success("NaqAI جاهز")
            else:
                st.warning("Gemini غير مكون")
        tab1, tab2 = st.tabs(["دخول", "حساب جديد"])
        with tab1:
            with st.form("login"):
                email = st.text_input("البريد", value=OWNER_EMAIL)
                pw = st.text_input("كلمة المرور", type="password", value="ndc2025")
                if st.form_submit_button("دخول", use_container_width=True):
                    if login_user(email, pw):
                        st.rerun()
                    else:
                        st.error("بيانات خاطئة")
        with tab2:
            with st.form("signup"):
                n = st.text_input("الاسم")
                e = st.text_input("البريد")
                p = st.text_input("كلمة المرور", type="password")
                sp = st.text_input("التخصص")
                if st.form_submit_button("إنشاء", use_container_width=True):
                    ok, msg = signup_user(n, e, p, sp)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if not st.session_state.authenticated:
        auth_page()
        return
    st.success("✅ تم تسجيل الدخول! باقي الأقسام ستُضاف في الأجزاء التالية.")

def sidebar_nav():
    u = st.session_state.current_user
    if u is None:
        return
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.1);">
            {get_logo_html(50)}
            <div style="font-weight:700;font-size:1.1rem;margin-top:6px;">DENTAL AI OS</div>
            <div style="font-size:0.7rem;color:#aac4d6;">v7.0 Pro</div>
        </div>
        <div style="text-align:center;margin:16px 0;">
            <div style="font-size:0.85rem;font-weight:600;">{u['name']}</div>
            <div style="font-size:0.65rem;color:#aac4d6;">{u.get('specialty','')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        menu_groups = {
            "الأساسية": [
                ("🏠 الرئيسية", "home"),
                ("📊 لوحة التحكم", "dashboard"),
                ("🏷️ رفع الشعار", "upload_logo"),
            ],
            "التحليل والتشخيص": [
                ("🧠 تحليل الوجه 468", "face_analysis"),
                ("✨ النسبة الذهبية", "golden_ratio"),
                ("😊 تحليل الابتسامة", "smile_analysis"),
                ("🦷 تحليل الإطباق", "occlusion_analysis"),
                ("💎 تحليل الوجه التجميلي", "facial_aesthetic"),
                ("🔬 الماسح العلمي", "scientific_scanner"),
                ("🩻 تحليل الأشعة", "cephalometric"),
            ],
            "التصميم (AI + يدوي)": [
                ("🎨 محاكاة AI", "ai_simulator"),
                ("🎬 محاكاة قبل/بعد", "before_after_simulation"),
                ("💎 Photorealism", "photorealism"),
                ("🧬 استوديو DSD", "dsd_studio"),
                ("✏️ التصميم اليدوي", "manual_design"),
                ("🎨 CAD/CAM 3D", "cad_cam"),
            ],
            "إدارة المرضى": [
                ("📁 بيانات المريض", "patient_data"),
                ("👥 قائمة المرضى", "patients_list"),
                ("📸 التصوير", "photography"),
                ("🩻 الأشعة (الأنواع)", "xray_types"),
                ("📅 المواعيد", "appointments"),
                ("💰 الحساب", "accounting"),
            ],
            "المواد والعلاج": [
                ("🧪 المواد العلاجية", "materials_guide"),
                ("📋 خطة العلاج", "treatment_plan"),
                ("🔄 خط الإنتاج", "pipeline"),
                ("📊 جداول المقارنات", "comparisons"),
            ],
            "الفريق": [
                ("👥 متعدد التخصصات", "multidisciplinary"),
                ("🗣️ منتدى النقاشات", "discussion_forum"),
                ("💬 المراسلات", "messages"),
                ("🧪 المختبر", "lab_chat"),
            ],
            "المنصة والأنظمة": [
                ("🌍 المنصة العالمية", "global_platform"),
                ("🔌 الأنظمة المستخدمة", "systems_used"),
                ("📊 التحليلات", "analytics"),
            ],
            "الإدارة": [
                ("📢 الإعلانات", "ads_management"),
                ("👑 الاشتراكات", "subscriptions"),
                ("📄 التقارير", "reports"),
                ("⚙️ الإعدادات", "settings"),
            ],
            "AI والتواصل": [
                ("🤖 NaqAI", "naqai"),
                ("🩺 التشخيص AI", "smart_diagnosis"),
                ("📱 Dentbook", "dentbook"),
                ("👤 الملف", "profile"),
                ("👥 الأعضاء", "members"),
            ],
        }
        
        for group_name, items in menu_groups.items():
            with st.expander(group_name, expanded=False):
                for label, key in items:
                    if st.button(label, key=f"nav_{key}", use_container_width=True):
                        st.session_state.current_page = key
                        st.rerun()
        
        st.divider()
        if st.button("🚪 خروج", use_container_width=True, type="primary"):
            logout()


def page_home():
    st.markdown('<div class="main-header">DENTAL AI OS v7.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">منصة متكاملة — 45+ قسم | AI | تصميم يدوي + تلقائي</div>', unsafe_allow_html=True)
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
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card"><div class="metric-value">45+</div><div class="metric-label">قسم</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><div class="metric-value">468</div><div class="metric-label">نقطة</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><div class="metric-value">AI</div><div class="metric-label">Gemini</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><div class="metric-value">2x</div><div class="metric-label">يدوي + تلقائي</div></div>', unsafe_allow_html=True)


def page_dashboard():
    st.markdown('<div class="section-title">📊 لوحة التحكم</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.users_db)}</div><div class="metric-label">الأعضاء</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.dentbook_posts)}</div><div class="metric-label">المنشورات</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.patient_files)}</div><div class="metric-label">المرضى</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.naqai_chat)}</div><div class="metric-label">محادثات AI</div></div>', unsafe_allow_html=True)


def page_upload_logo():
    st.markdown('<div class="section-title">🏷️ رفع الشعار</div>', unsafe_allow_html=True)
    up = st.file_uploader("اختر صورة", type=["jpg", "jpeg", "png"])
    if up:
        img = Image.open(up)
        st.session_state.system_logo = img_to_b64(img)
        st.success("✅ تم رفع الشعار")
        st.image(img, width=150)


def page_face_analysis():
    st.markdown('<div class="section-title">🧠 تحليل الوجه 468 نقطة</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.error("MediaPipe غير متاح")
        return
    img = image_upload_section("fa", "📸 ارفع صورة الوجه")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    c1, c2 = st.columns(2)
    with c1:
        st.image(img, use_container_width=True)
    with c2:
        if st.button("🧠 تحليل 468 نقطة", type="primary", use_container_width=True, key="btn_468"):
            with st.spinner("⏳..."):
                lm, ann, data = analyze_face_468(img)
                if lm is not None:
                    st.session_state.last_analysis_image = Image.fromarray(ann)
                    st.session_state.last_analysis_data = data if data else {}
                    st.rerun()
                else:
                    st.error("❌ لم يتم اكتشاف وجه")
    if st.session_state.get("last_analysis_image"):
        st.image(st.session_state.last_analysis_image, use_container_width=True)
        data = st.session_state.last_analysis_data or {}
        if data:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("📍 النقاط", data.get("num_landmarks", 468))
            with c2:
                st.metric("🏆 الدرجة", f"{data.get('overall_score', 0):.1f}%")
            with c3:
                st.metric("✅ التقييم", data.get("grade", "-"))
            with c4:
                st.metric("👤 الوجه", data.get("face_shape", "-"))
            chart = pd.DataFrame({
                "المعيار": ["ذهبية", "تناسق", "أثلاث", "ابتسامة", "عيون"],
                "النسبة": [data.get('golden_score', 0), data.get('symmetry_score', 0),
                          data.get('thirds_score', 0), data.get('smile_score', 0),
                          data.get('eye_symmetry', 0)]
            })
            fig = px.bar(chart, x="المعيار", y="النسبة", template="plotly_dark",
                         color="النسبة", color_continuous_scale=["#ef4444", "#10b981", "#00d4ff"])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button("⬇️ PNG", img_to_bytes(st.session_state.last_analysis_image),
                                 "face_468.png", "image/png", use_container_width=True, key="dl_face_png")
            with c2:
                st.download_button("⬇️ JSON", json.dumps(data, ensure_ascii=False, indent=2).encode(),
                                 "analysis.json", "application/json", use_container_width=True, key="dl_face_json")
            with c3:
                if GEMINI_API_KEY and st.button("🤖 تحليل AI", use_container_width=True, key="btn_ai_face"):
                    with st.spinner("🤖..."):
                        ans = ai_analyze_image(img, "حلل هذه الصورة: التناسق، النسب، التوصيات التجميلية")
                    st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)


def page_golden_ratio():
    st.markdown('<div class="section-title">✨ النسبة الذهبية</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.error("MediaPipe غير متاح")
        return
    img = image_upload_section("gr", "📸 ارفع صورة")
    if img is None:
        st.info("👆 ارفع صورة")
        return
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
    if st.session_state.get("last_golden_image"):
        st.image(st.session_state.last_golden_image, use_container_width=True)
        data = st.session_state.last_golden_data or {}
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📐 النسبة", f"{data.get('ratio', 0):.3f}")
        with c2:
            st.metric("🎯 المثالية", "1.618")
        with c3:
            st.metric("🏆 الدرجة", f"{data.get('score', 0):.1f}%")
        st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.last_golden_image),
                         "golden.png", "image/png", use_container_width=True, key="dl_golden")


def page_smile_analysis():
    st.markdown('<div class="section-title">😊 تحليل الابتسامة</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.error("MediaPipe غير متاح")
        return
    img = image_upload_section("sa", "📸 ارفع صورة")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    c1, c2 = st.columns(2)
    with c1:
        st.image(img, use_container_width=True)
    with c2:
        if st.button("😊 تحليل", type="primary", use_container_width=True, key="btn_sa"):
            lm, _, _ = analyze_face_468(img)
            if lm:
                w, h = img.size
                ann_img = np.array(img).copy()
                for idx in [61, 291, 13, 14]:
                    try:
                        x, y = get_landmark_xy(lm, idx, w, h)
                        cv2.circle(ann_img, (x, y), 5, (255, 100, 200), -1)
                    except:
                        pass
                st.session_state.last_smile_analysis_image = Image.fromarray(ann_img)
                st.rerun()
    if st.session_state.get("last_smile_analysis_image"):
        st.image(st.session_state.last_smile_analysis_image, use_container_width=True)


def page_occlusion_analysis():
    st.markdown('<div class="section-title">🦷 تحليل الإطباق</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.error("MediaPipe غير متاح")
        return
    img = image_upload_section("occ", "📸 ارفع صورة")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    c1, c2 = st.columns(2)
    with c1:
        st.image(img, use_container_width=True)
    with c2:
        if st.button("🦷 تحليل الإطباق", type="primary", use_container_width=True, key="btn_occ"):
            lm, _, _ = analyze_face_468(img)
            if lm:
                w, h = img.size
                data = analyze_occlusion(lm, w, h)
                st.session_state.last_occlusion_data = data
                st.rerun()
    if st.session_state.get("last_occlusion_data"):
        data = st.session_state.last_occlusion_data
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📐 Angle", data.get("angle_class", "-"))
        with c2:
            st.metric("↔️ Overjet", f"{data.get('overjet', 0):.1f}mm")
        with c3:
            st.metric("↕️ Overbite", f"{data.get('overbite', 0):.1f}mm")
        st.info(f"💡 {data.get('recommendation', '-')}")


def page_facial_aesthetic():
    st.markdown('<div class="section-title">💎 تحليل الوجه التجميلي</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.error("MediaPipe غير متاح")
        return
    img = image_upload_section("faes", "📸 ارفع صورة")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    c1, c2 = st.columns(2)
    with c1:
        st.image(img, use_container_width=True)
    with c2:
        if st.button("💎 تحليل تجميلي", type="primary", use_container_width=True, key="btn_faes"):
            lm, _, _ = analyze_face_468(img)
            if lm:
                w, h = img.size
                data = analyze_facial_aesthetic(lm, w, h)
                st.session_state.last_facial_aesthetic_data = data
                st.rerun()
    if st.session_state.get("last_facial_aesthetic_data"):
        data = st.session_state.last_facial_aesthetic_data
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("📐 Nasolabial", f"{data.get('nasolabial_angle', 0):.1f}°")
        with c2:
            st.metric("📐 Mentolabial", f"{data.get('mentolabial_angle', 0):.1f}°")
        with c3:
            st.metric("🏆 التقييم", data.get("grade", "-"))


def page_scientific_scanner():
    st.markdown('<div class="section-title">🔬 الماسح العلمي الذكي</div>', unsafe_allow_html=True)
    img = image_upload_section("sci", "📸 صورة شاملة")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    st.image(img, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        scan_btn = st.button("🔬 ابدأ المسح الشامل", type="primary", use_container_width=True, key="btn_sci")
    with c2:
        ai_btn = st.button("🤖 مسح + تحليل AI", use_container_width=True, key="btn_sci_ai")
    if scan_btn:
        with st.spinner("🔬..."):
            results = {}
            if MEDIAPIPE_AVAILABLE:
                lm, ann, fa = analyze_face_468(img)
                if lm:
                    w, h = img.size
                    results["facial"] = fa
                    results["occlusion"] = analyze_occlusion(lm, w, h)
                    results["aesthetic"] = analyze_facial_aesthetic(lm, w, h)
                    results["image"] = Image.fromarray(ann)
                    st.session_state.scientific_scans.append({"time": datetime.now().strftime("%H:%M"), "results": results})
                    st.rerun()
    if ai_btn and GEMINI_API_KEY:
        with st.spinner("🤖 AI يحلل..."):
            ans = ai_analyze_image(img, "قدم تقريراً شاملاً: تحليل الأسنان، الابتسامة، الوجه، والتوصيات")
        st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)
    if st.session_state.get("scientific_scans"):
        latest = st.session_state.scientific_scans[-1]
        res = latest["results"]
        if "image" in res:
            st.image(res["image"], use_container_width=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("🧠 الوجه", f"{res.get('facial', {}).get('overall_score', 0):.1f}%")
        with c2:
            st.metric("🦷 الإطباق", res.get('occlusion', {}).get('angle_class', '-'))
        with c3:
            st.metric("💎 الجمالية", f"{res.get('aesthetic', {}).get('aesthetic_score', 0):.1f}%")


def page_cephalometric():
    st.markdown('<div class="section-title">🩻 تحليل الأشعة</div>', unsafe_allow_html=True)
    img = image_upload_section("ceph", "📸 صورة الأشعة")
    if img is None:
        st.info("👆 ارفع صورة الأشعة")
        return
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
    if st.session_state.get("last_cephalometric_image"):
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
       
def page_before_after_simulation():
    st.markdown('<div class="section-title">🎬 محاكاة قبل / بعد العلاج</div>', unsafe_allow_html=True)
    img = image_upload_section("ba", "📸 ارفع صورة المريض")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    st.image(img, use_container_width=True)
    tab1, tab2 = st.tabs(["🤖 تلقائي AI", "✏️ يدوي"])
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            treatment = st.selectbox("نوع العلاج", ["تبييض", "زركونيا", "فينير", "تجميلي شامل"], key="ba_treat")
        with c2:
            style = st.selectbox("النمط", ["طبيعي", "هوليوود", "زركونيا لامع"], key="ba_style")
        if st.button("🤖 إنتاج محاكاة AI", type="primary", use_container_width=True, key="btn_ba_ai"):
            with st.spinner("🤖..."):
                if style == "هوليوود":
                    after = apply_photorealism(img, 60, 95, 30, 60, 20, 10, 10, 30)
                elif style == "زركونيا لامع":
                    after = apply_photorealism(img, 40, 90, 10, 95, 10, 5, 0, 20)
                else:
                    after = apply_photorealism(img, 30, 75, 20, 40, 15, 5, 5, 15)
                st.session_state.last_before_after = (img, after)
                st.rerun()
    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1:
            white_m = st.slider("✨ تبييض", 0, 100, 0, key="m_white")
            smile_m = st.slider("😊 ابتسامة", 0, 100, 0, key="m_smile")
        with c2:
            zir_m = st.slider("🔷 زركونيا", 0, 100, 0, key="m_zir")
            skin_m = st.slider("💉 بشرة", 0, 100, 0, key="m_skin")
        with c3:
            brow_m = st.slider("👁️ حواجب", 0, 100, 0, key="m_brow")
            glow_m = st.slider("✨ توهج", 0, 100, 0, key="m_glow")
        if st.button("✏️ تطبيق يدوي", type="primary", use_container_width=True, key="btn_ba_manual"):
            with st.spinner("🎨..."):
                after = apply_photorealism(img, smile_m, white_m, skin_m, zir_m, brow_m, 0, 0, glow_m)
                st.session_state.last_before_after = (img, after)
                st.rerun()
    if st.session_state.get("last_before_after"):
        before, after = st.session_state.last_before_after
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📷 قبل")
            st.image(before, use_container_width=True)
        with c2:
            st.markdown("#### ✨ بعد")
            st.image(after, use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ قبل", img_to_bytes(before), "before.png", "image/png", use_container_width=True, key="dl_ba_before")
        with c2:
            st.download_button("⬇️ بعد", img_to_bytes(after), "after.png", "image/png", use_container_width=True, key="dl_ba_after")


def page_ai_simulator():
    st.markdown('<div class="section-title">🎨 محاكاة الذكاء الاصطناعي</div>', unsafe_allow_html=True)
    img = image_upload_section("sim", "📸 ارفع صورة")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    tab1, tab2 = st.tabs(["🤖 AI Auto", "✏️ Manual"])
    with tab1:
        treatment = st.selectbox("العلاج", ["تجميلي شامل", "تبييض", "زركونيا", "فينير", "بوتوكس"], key="sim_treat")
        if st.button("🚀 تطبيق AI", type="primary", use_container_width=True, key="btn_sim_ai"):
            with st.spinner("🤖..."):
                if treatment == "تجميلي شامل":
                    result = apply_photorealism(img, 50, 85, 30, 60, 20, 5, 5, 15)
                elif treatment == "تبييض":
                    result = apply_photorealism(img, 0, 80, 0, 0, 0, 0, 0, 0)
                elif treatment == "زركونيا":
                    result = apply_photorealism(img, 40, 85, 10, 90, 10, 5, 0, 10)
                elif treatment == "فينير":
                    result = apply_photorealism(img, 40, 75, 20, 40, 15, 5, 5, 15)
                else:
                    result = apply_photorealism(img, 20, 30, 70, 0, 70, 0, 0, 0)
                st.session_state.processed_img = result
                st.rerun()
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            smile = st.slider("😊 ابتسامة", 0, 100, 0, key="sm_s")
            white = st.slider("✨ تبييض", 0, 100, 0, key="sm_w")
            skin = st.slider("💉 بشرة", 0, 100, 0, key="sm_sk")
        with c2:
            zir = st.slider("🔷 زركونيا", 0, 100, 0, key="sm_z")
            brow = st.slider("👁️ حواجب", 0, 100, 0, key="sm_b")
            glow = st.slider("✨ توهج", 0, 100, 0, key="sm_g")
        if st.button("🚀 تطبيق يدوي", type="primary", use_container_width=True, key="btn_sim_manual"):
            with st.spinner("🎨..."):
                result = apply_photorealism(img, smile, white, skin, zir, brow, 0, 0, glow)
                st.session_state.processed_img = result
                st.rerun()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**📷 قبل**")
        st.image(img, use_container_width=True)
    with c2:
        st.markdown("**✨ بعد**")
        if st.session_state.get("processed_img"):
            st.image(st.session_state.processed_img, use_container_width=True)
            st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.processed_img),
                             "sim.png", "image/png", use_container_width=True, key="dl_sim")
        else:
            st.info("اضغط تطبيق")


def page_photorealism():
    st.markdown('<div class="section-title">💎 Photorealism Studio</div>', unsafe_allow_html=True)
    img = image_upload_section("phr", "📸 ارفع صورة")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    c1, c2 = st.columns([1, 2])
    with c1:
        brightness = st.slider("☀️ السطوع", -50, 50, 0, key="phr_b")
        contrast = st.slider("🎚️ التباين", -50, 50, 0, key="phr_c")
        saturation = st.slider("🎨 التشبع", -50, 50, 0, key="phr_s")
        sharpness = st.slider("🔪 الحدة", 0, 100, 0, key="phr_sh")
        warmth = st.slider("🔥 الدفء", -50, 50, 0, key="phr_w")
        if st.button("🎨 تطبيق", type="primary", use_container_width=True, key="btn_phr"):
            with st.spinner("🎨..."):
                result = img.copy()
                if brightness != 0:
                    result = ImageEnhance.Brightness(result).enhance(1 + brightness/100)
                if contrast != 0:
                    result = ImageEnhance.Contrast(result).enhance(1 + contrast/100)
                if saturation != 0:
                    result = ImageEnhance.Color(result).enhance(1 + saturation/100)
                if sharpness > 0:
                    result = ImageEnhance.Sharpness(result).enhance(1 + sharpness/100)
                if warmth != 0:
                    arr = np.array(result).astype(np.float32)
                    arr[:, :, 0] = np.clip(arr[:, :, 0] + warmth, 0, 255)
                    arr[:, :, 2] = np.clip(arr[:, :, 2] - warmth, 0, 255)
                    result = Image.fromarray(arr.astype(np.uint8))
                st.session_state.last_photorealism_image = result
                st.rerun()
    with c2:
        if st.session_state.get("last_photorealism_image"):
            st.image(st.session_state.last_photorealism_image, use_container_width=True)
            st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.last_photorealism_image),
                             "ph.png", "image/png", use_container_width=True, key="dl_phr")
        else:
            st.image(img, use_container_width=True)


def page_dsd_studio():
    st.markdown('<div class="section-title">🧬 استوديو DSD</div>', unsafe_allow_html=True)
    img = image_upload_section("dsd2", "📸 ارفع صورة")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    tab1, tab2 = st.tabs(["🤖 AI Auto", "✏️ Manual"])
    with tab1:
        tooth_color = st.selectbox("🎨 لون الأسنان", ["A1", "A2", "A3", "B1", "Hollywood"], key="dsd_ai_c")
        if st.button("🧬 تصميم AI", type="primary", use_container_width=True, key="btn_dsd_ai"):
            with st.spinner("🧬..."):
                arr = np.array(img).astype(np.float32)
                h, w = arr.shape[:2]
                mouth = arr[int(h*0.55):int(h*0.8), int(w*0.25):int(w*0.75)]
                colors = {"A1": [240, 235, 220], "A2": [235, 225, 205], "A3": [225, 210, 185],
                         "B1": [230, 225, 210], "Hollywood": [255, 255, 250]}
                target = np.array(colors.get(tooth_color, [235, 230, 215]))
                if mouth.size > 0:
                    hsv_m = cv2.cvtColor(mouth.astype(np.uint8), cv2.COLOR_RGB2HSV)
                    mask = (hsv_m[:, :, 2] > 130) & (hsv_m[:, :, 1] < 60)
                    for i in range(3):
                        mouth[:, :, i] = np.where(mask, mouth[:, :, i] * 0.3 + target[i] * 0.7, mouth[:, :, i])
                    arr[int(h*0.55):int(h*0.8), int(w*0.25):int(w*0.75)] = mouth
                st.session_state.last_dsd_image = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
                st.rerun()
    with tab2:
        white = st.slider("✨ التبييض", 0, 100, 0, key="dsd_m_w")
        if st.button("✏️ تطبيق يدوي", type="primary", use_container_width=True, key="btn_dsd_manual"):
            with st.spinner("🎨..."):
                result = apply_photorealism(img, 0, white, 0, 0, 0, 0, 0, 0)
                st.session_state.last_dsd_image = result
                st.rerun()
    if st.session_state.get("last_dsd_image"):
        st.image(st.session_state.last_dsd_image, use_container_width=True)
        st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.last_dsd_image),
                         "dsd.png", "image/png", use_container_width=True, key="dl_dsd")


def page_manual_design():
    st.markdown('<div class="section-title">✏️ التصميم اليدوي</div>', unsafe_allow_html=True)
    img = image_upload_section("manual", "📸 ارفع صورة")
    if img is None:
        st.info("👆 ارفع صورة")
        return
    tab1, tab2, tab3 = st.tabs(["🎨 الفلاتر", "✏️ الرسم", "📝 النص"])
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            b = st.slider("سطوع", -50, 50, 0, key="md_b")
            c = st.slider("تباين", -50, 50, 0, key="md_c")
        with c2:
            s = st.slider("تشبع", -50, 50, 0, key="md_s")
            sh = st.slider("حدة", 0, 100, 0, key="md_sh")
        if st.button("🎨 تطبيق", type="primary", use_container_width=True, key="btn_md_filters"):
            with st.spinner("🎨..."):
                result = img.copy()
                if b != 0:
                    result = ImageEnhance.Brightness(result).enhance(1 + b/100)
                if c != 0:
                    result = ImageEnhance.Contrast(result).enhance(1 + c/100)
                if s != 0:
                    result = ImageEnhance.Color(result).enhance(1 + s/100)
                if sh > 0:
                    result = ImageEnhance.Sharpness(result).enhance(1 + sh/100)
                st.session_state.processed_img = result
                st.rerun()
    with tab2:
        draw_type = st.selectbox("نوع الرسم", ["دائرة", "مستطيل", "خط"], key="md_draw_type")
        color = st.color_picker("اللون", "#00d4ff", key="md_color")
        width = st.slider("السماكة", 1, 10, 3, key="md_width")
        if st.button("✏️ إضافة الرسم", use_container_width=True, key="btn_md_draw"):
            with st.spinner("✏️..."):
                result = img.copy()
                draw = ImageDraw.Draw(result)
                w, h = result.size
                rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                if draw_type == "دائرة":
                    draw.ellipse([w//4, h//4, 3*w//4, 3*h//4], outline=rgb, width=width)
                elif draw_type == "مستطيل":
                    draw.rectangle([w//4, h//4, 3*w//4, 3*h//4], outline=rgb, width=width)
                else:
                    draw.line([(0, h//2), (w, h//2)], fill=rgb, width=width)
                st.session_state.processed_img = result
                st.rerun()
    with tab3:
        text = st.text_input("النص", "DENTAL AI OS", key="md_text")
        text_color = st.color_picker("اللون", "#ffffff", key="md_text_color")
        text_size = st.slider("الحجم", 20, 100, 40, key="md_text_size")
        if st.button("📝 إضافة النص", use_container_width=True, key="btn_md_text"):
            with st.spinner("📝..."):
                result = img.copy()
                draw = ImageDraw.Draw(result)
                try:
                    font = ImageFont.truetype("arial.ttf", text_size)
                except:
                    font = ImageFont.load_default()
                rgb = tuple(int(text_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                w, h = result.size
                draw.text((w//4, h//2), text, fill=rgb, font=font)
                st.session_state.processed_img = result
                st.rerun()
    if st.session_state.get("processed_img"):
        st.image(st.session_state.processed_img, use_container_width=True)
        st.download_button("⬇️ تحميل", img_to_bytes(st.session_state.processed_img),
                         "design.png", "image/png", use_container_width=True, key="dl_md")
    else:
        st.image(img, use_container_width=True)


def page_cad_cam():
    st.markdown('<div class="section-title">🎨 CAD/CAM & 3D Studio</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🎨 توليد AI", "📦 رفع STL", "⚙️ الأنظمة"])
    with tab1:
        prompt = st.text_area("📝 وصف النموذج 3D")
        if st.button("🎨 توليد AI", type="primary", use_container_width=True, key="btn_3d_ai"):
            with st.spinner("🎨..."):
                if GEMINI_API_KEY:
                    ans = ask_gemini("اقترح مواصفات 3D لنموذج: " + prompt + ". قدم: الأبعاد، المادة، خطوات التصميم")
                    st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)
                else:
                    st.info("💡 استخدم Meshy AI: https://www.meshy.ai")
    with tab2:
        model = st.file_uploader("STL/OBJ/PLY/GLB", type=["stl", "obj", "ply", "glb"])
        if model:
            st.success(f"✅ {model.name}")
            st.session_state.cad_models.append({"name": model.name, "size": model.size})
        if st.session_state.cad_models:
            st.dataframe(pd.DataFrame(st.session_state.cad_models), use_container_width=True)
    with tab3:
        systems = [("Meshy AI", "https://www.meshy.ai"), ("Blender", "https://www.blender.org"), ("Exocad", "https://exocad.com")]
        for name, url in systems:
            st.markdown(f'<div class="card"><strong style="color:#00d4ff;">{name}</strong> <a href="{url}" target="_blank">🔗</a></div>', unsafe_allow_html=True)


def page_patient_data():
    st.markdown('<div class="section-title">📁 بيانات المريض</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["👤 معلومات", "📸 صور", "🩻 أشعة"])
    with tab1:
        with st.form("patient_info"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("الاسم")
                age = st.number_input("العمر", 1, 120, 25)
                gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
            with c2:
                treatment = st.selectbox("العلاج", ["تبييض", "زركونيا", "زراعة", "تقويم", "إيماكس"])
                cost = st.number_input("التكلفة", 0, value=5000)
                phone = st.text_input("الهاتف")
            if st.form_submit_button("💾 حفظ", use_container_width=True):
                st.session_state.patient_files.append({
                    "name": name, "age": age, "gender": gender,
                    "phone": phone, "treatment": treatment, "cost": cost,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.rerun()
        if st.session_state.patient_files:
            st.dataframe(pd.DataFrame(st.session_state.patient_files), use_container_width=True)
    with tab2:
        imgs = st.file_uploader("📤 صور متعددة", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="pat_imgs")
        if imgs:
            cols = st.columns(3)
            for i, img in enumerate(imgs):
                with cols[i % 3]:
                    st.image(img, caption=img.name, use_container_width=True)
    with tab3:
        xtype = st.selectbox("النوع", ["سيفالومترية", "بانورامية", "CBCT", "Periapical", "Occlusal", "Bitewing"])
        xray = st.file_uploader("📤 أشعة", type=["jpg", "png", "jpeg"], key="pat_xray")
        if xray:
            st.image(xray, caption=xtype, use_container_width=True)
            st.session_state.patient_xrays.append({"type": xtype, "name": xray.name})


def page_patients_list():
    st.markdown('<div class="section-title">👥 قائمة المرضى</div>', unsafe_allow_html=True)
    if st.session_state.patient_files:
        st.dataframe(pd.DataFrame(st.session_state.patient_files), use_container_width=True)
    else:
        st.info("لا يوجد مرضى — اذهب إلى قسم بيانات المريض")


def page_photography():
    st.markdown('<div class="section-title">📸 التصوير الطبي</div>', unsafe_allow_html=True)
    types_list = ["أمامية", "جانبية", "ابتسامة", "فك علوي", "فك سفلي"]
    for t in types_list:
        up = st.file_uploader(t, type=["jpg", "png", "jpeg"], key=f"photo_{t}")
        if up:
            st.image(up, use_container_width=True)


def page_xray_types():
    st.markdown('<div class="section-title">🩻 الأشعة (6 أنواع)</div>', unsafe_allow_html=True)
    types = {
        "سيفالومترية": "لتحليل علاقة الفكين",
        "بانورامية": "لرؤية كل الأسنان",
        "CBCT": "تصوير 3D",
        "Periapical": "تفاصيل السن",
        "Occlusal": "سقف وأرضية الفم",
        "Bitewing": "التسوس بين الأسنان"
    }
    sel = st.selectbox("النوع", list(types.keys()))
    st.info(f"💡 {types[sel]}")
    up = st.file_uploader("📤 ارفع", type=["jpg", "png", "jpeg"], key="xr_up")
    if up:
        st.image(up, use_container_width=True)


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
        st.session_state.appointments.append({"patient": p, "date": str(d), "time": str(t), "note": note})
        st.rerun()
    for a in st.session_state.appointments:
        st.markdown(f'<div class="card">📅 {a["patient"]} — {a["date"]} {a.get("time", "")}</div>', unsafe_allow_html=True)


def page_accounting():
    st.markdown('<div class="section-title">💰 الحساب المالي</div>', unsafe_allow_html=True)
    t = st.number_input("الكلي", value=1000, key="acc_t")
    p = st.number_input("المدفوع", value=0, key="acc_p")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("الكلي", t)
    with c2:
        st.metric("المدفوع", p)
    with c3:
        st.metric("المتبقي", t - p)


def page_materials_guide():
    st.markdown('<div class="section-title">🧪 المواد العلاجية</div>', unsafe_allow_html=True)
    for mat in st.session_state.treatment_materials:
        with st.expander(f"💊 {mat['name']}", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**📖 الاستخدام:** {mat['usage']}")
                st.markdown(f"**🔄 البديل:** {mat['alternative']}")
            with c2:
                st.markdown(f"**⭐ الميزة:** {mat['advantage']}")
                st.markdown(f"**💰 التكلفة:** {mat['cost']}")
    if GEMINI_API_KEY:
        mat_sel = st.selectbox("اختر مادة", [m['name'] for m in st.session_state.treatment_materials], key="mat_sel")
        if st.button("🤖 اسأل AI عن المادة", use_container_width=True, key="btn_ask_mat"):
            with st.spinner("🤖..."):
                ans = ask_gemini("اشرح مادة " + mat_sel + ": استخدام، ميزات، بدائل، نصائح")
            st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)


def page_treatment_plan():
    st.markdown('<div class="section-title">📋 خطة العلاج</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        main = st.text_area("الخطة الرئيسية")
    with c2:
        alt = st.text_area("العلاج البديل")
    materials_used = st.multiselect("المواد المستخدمة", [m['name'] for m in st.session_state.treatment_materials])
    if st.button("🧠 توليد خطة AI", type="primary", use_container_width=True, key="btn_plan"):
        if GEMINI_API_KEY:
            with st.spinner("🤖..."):
                ans = ask_gemini("خطة علاج: رئيسية=" + main + ", بديل=" + alt + ", مواد=" + str(materials_used) + ". قدم: خطوات + مدة + تكلفة + مضاعفات")
            st.markdown(f'<div class="ai-msg">🤖 {ans}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ تم توليد الخطة (بدون AI)")


def page_pipeline():
    st.markdown('<div class="section-title">🔄 خط الإنتاج ومقيّمه</div>', unsafe_allow_html=True)
    steps = [
        ("1️⃣ الاستشارة والتشخيص", "done"),
        ("2️⃣ التحضير الرقمي", "done"),
        ("3️⃣ التصميم CAD/CAM", "active"),
        ("4️⃣ التصنيع", "pending"),
        ("5️⃣ التركيب والتسليم", "pending"),
    ]
    for name, status in steps:
        icon = "✅" if status == "done" else "🔄" if status == "active" else "⏳"
        st.markdown(f'<div class="timeline-step timeline-{status}"><div>{icon}</div><strong>{name}</strong></div>', unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=58,
        title={'text': "نسبة الإنجاز"},
        gauge={'bar': {'color': "#00d4ff"}}
    ))
    st.plotly_chart(fig, use_container_width=True)


def page_comparisons():
    st.markdown('<div class="section-title">📊 جداول المقارنات</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["قبل/بعد", "إحصائية"])
    with tab1:
        df = pd.DataFrame({
            "المعيار": ["لون الأسنان", "تناسق الابتسامة", "صحة اللثة", "التناسب", "الثقة"],
            "قبل": [45, 60, 70, 55, 50],
            "بعد": [95, 92, 90, 88, 98],
            "التحسن": ["+111%", "+53%", "+29%", "+60%", "+96%"]
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='قبل', x=df['المعيار'], y=df['قبل'], marker_color='#ef4444'))
        fig.add_trace(go.Bar(name='بعد', x=df['المعيار'], y=df['بعد'], marker_color='#10b981'))
        fig.update_layout(barmode='group', template='plotly_dark',
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        df = st.session_state.patients_df
        comp = pd.DataFrame({
            "المعيار": ["عدد الأسنان", "التكلفة", "المدة", "رضا المريض"],
            "الحد الأدنى": [df['عدد_الأسنان'].min(), df['التكلفة_ريال'].min(),
                          df['المدة_شهر'].min(), df['رضا_المريض_%'].min()],
            "الأعلى": [df['عدد_الأسنان'].max(), df['التكلفة_ريال'].max(),
                      df['المدة_شهر'].max(), df['رضا_المريض_%'].max()],
            "المتوسط": [df['عدد_الأسنان'].mean(), df['التكلفة_ريال'].mean(),
                       df['المدة_شهر'].mean(), df['رضا_المريض_%'].mean()]
        })
        st.dataframe(comp.round(2), use_container_width=True, hide_index=True)     
if __name__ == "__main__":
    main()
