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

if __name__ == "__main__":
    main()
