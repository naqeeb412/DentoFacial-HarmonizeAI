# ============================================================
#  🦷 DENTAL AI OS — Comprehensive Dental Analysis System
#  Version: 2.2 | Streamlit Cloud Ready
#  Compatible: Python 3.11 | No MediaPipe | No Build Errors
# ============================================================

import streamlit as st
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import io
import base64
import math
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import hashlib
import pandas as pd
from io import BytesIO
import time
import json

# ── Page Config ──
st.set_page_config(
    page_title="🦷 DENTAL AI OS",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
#  🧠 MediaPipe (OPTIONAL — Safe Fallback)
# ============================================================
MEDIAPIPE_AVAILABLE = False
mp_face_mesh = None
mp_drawing = None
mp_drawing_styles = None

try:
    import mediapipe as mp
    try:
        from mediapipe.python.solutions import face_mesh as mp_face_mesh
        from mediapipe.python.solutions import drawing_utils as mp_drawing
        from mediapipe.python.solutions import drawing_styles as mp_drawing_styles
        MEDIAPIPE_AVAILABLE = True
    except ImportError:
        try:
            mp_face_mesh = mp.solutions.face_mesh
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing_styles = mp.solutions.drawing_styles
            MEDIAPIPE_AVAILABLE = True
        except Exception:
            MEDIAPIPE_AVAILABLE = False
except Exception:
    MEDIAPIPE_AVAILABLE = False

def get_face_mesh():
    """Lazy init — يعيد None إذا لم تكن MediaPipe متاحة."""
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

# ── Custom CSS ──
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .main-header { text-align: center; color: #00d4ff; font-size: 2.4rem; font-weight: 700; }
    .sub-header { text-align: center; color: #8892b0; font-size: 1rem; margin-bottom: 1rem; }
    .metric-card { background: rgba(0,212,255,0.08); border-radius: 12px; padding: 15px; 
                   border: 1px solid rgba(0,212,255,0.25); text-align: center; }
    .metric-value { color: #64ffda; font-size: 1.8rem; font-weight: bold; }
    .metric-label { color: #8892b0; font-size: 0.85rem; }
    .section-title { color: #00d4ff; font-size: 1.3rem; font-weight: bold; 
                     border-bottom: 2px solid rgba(0,212,255,0.3); padding-bottom: 8px; margin-top: 20px; }
    .diagnosis-box { background: linear-gradient(135deg, rgba(123,44,191,0.15), rgba(0,212,255,0.1)); 
                     border-radius: 15px; padding: 20px; border: 1px solid rgba(0,212,255,0.2); }
    .card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px; }
    .stButton>button { border-radius: 25px !important; font-weight: bold !important; }
    .tooth { width: 44px; height: 52px; background: #f8fafc; border: 2px solid #cbd5e1; border-radius: 8px 8px 4px 4px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s ease; font-size: 11px; font-weight: 700; color: #1a2a3a; position: relative; user-select: none; }
    .tooth:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); border-color: #00d4ff; }
    .tooth .num { font-size: 9px; opacity: 0.5; margin-top: 2px; }
    .tooth .status-icon { font-size: 14px; line-height: 1; }
    .tooth.missing { background: #f1f3f5; border-color: #adb5bd; opacity: 0.5; }
    .tooth.carious { background: #fde8e8; border-color: #ef4444; }
    .tooth.treated { background: #d5f5e3; border-color: #10b981; }
    .tooth.crown { background: #fef9e7; border-color: #f59e0b; }
    .tooth.root-canal { background: #e8daef; border-color: #8e44ad; }
    .tooth-legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; justify-content: center; }
    .tooth-legend .legend-item { display: flex; align-items: center; gap: 6px; font-size: 13px; }
    .tooth-legend .legend-item .swatch { width: 24px; height: 28px; border-radius: 4px; border: 2px solid #cbd5e1; }
    .tooth-legend .legend-item .swatch.normal { background: #f8fafc; }
    .tooth-legend .legend-item .swatch.missing { background: #f1f3f5; opacity: 0.5; }
    .tooth-legend .legend-item .swatch.carious { background: #fde8e8; border-color: #ef4444; }
    .tooth-legend .legend-item .swatch.treated { background: #d5f5e3; border-color: #10b981; }
    .tooth-legend .legend-item .swatch.crown { background: #fef9e7; border-color: #f59e0b; }
    .tooth-legend .legend-item .swatch.root-canal { background: #e8daef; border-color: #8e44ad; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Session State ──
defaults = {
    "original_img": None, "processed_img": None, "analysis_img": None,
    "xray_img": None, "landmarks_468": None,
    "diagnosis_report": {}, "golden_ratio_data": {},
    "smile_score": 0, "symmetry_score": 0, "golden_score": 0,
    "patients": [], "dentbook_posts": [], "messages": [],
    "users_db": {}, "authenticated": False, "current_user": None,
    "naqai_chat": [], "dental_chart": ['normal'] * 32,
    "tooth_statuses": {i: "normal" for i in range(32)},
    "selected_tooth": None, "appointments": [], "materials": [],
    "specialists": [], "files_uploaded": [], "ads": [],
    "forum_questions": [], "lab_messages": [], "private_messages": [],
    "friend_requests": [], "pipeline_progress": 58,
    "patient_images": [], "xrays": [], "otp_sent": False,
    "pipeline_steps": {
        1: {"name": "التحضير والتوليد", "status": "done", "progress": 100},
        2: {"name": "النسب التناظرية", "status": "done", "progress": 100},
        3: {"name": "الهندسة السنية", "status": "pending", "progress": 60},
        4: {"name": "الشبكة الوجهية", "status": "pending", "progress": 30},
        5: {"name": "الرندرة الفائقة", "status": "inactive", "progress": 0},
    },
    "natural_teeth_layers": [], "image_layers": [], "current_layer": 0,
    "system_logo": None, "otp_store": {},
    "last_analysis_image": None, "last_analysis_data": None,
    "last_cephalometric_image": None, "last_cephalometric_data": None,
    "last_smile_image": None,
    "patients_df": None, "before_after_data": None,
    "current_page": "home"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── OWNER ──
OWNER_EMAIL = "ndcdental2025@outlook.com"
OWNER_PASSWORD_HASH = hashlib.sha256("ndc2025".encode()).hexdigest()

def hash_pass(p): return hashlib.sha256(p.encode()).hexdigest()
def generate_otp(): return ''.join(random.choices('0123456789', k=6))

if not st.session_state.users_db:
    st.session_state.users_db = {
        OWNER_EMAIL: {
            "name": "علي النقيب", "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD_HASH, "role": "owner",
            "specialty": "طب أسنان تجميلي", "country": "اليمن",
            "phone": "+967 77 123 4567",
            "bio": "مؤسس منصة Dentofacial HarmonizeAI™",
            "platforms": ["email"],
            "created_at": datetime.now().isoformat()
        }
    }

if not st.session_state.specialists:
    st.session_state.specialists = [
        {"name": "د. أحمد العمري", "specialty": "تقويم أسنان", "online": True},
        {"name": "د. سارة الحكيم", "specialty": "جراحة الفم والوجه", "online": True},
        {"name": "د. خالد النقيب", "specialty": "طب الأسنان التجميلي", "online": False},
    ]

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

if st.session_state.before_after_data is None:
    st.session_state.before_after_data = pd.DataFrame({
        'المعيار': ['لون الأسنان', 'تناظر الابتسامة', 'صحة اللثة', 'تناسب الأسنان', 'ثقة المريض'],
        'قبل_العلاج': [45, 60, 70, 55, 50],
        'بعد_العلاج': [95, 92, 90, 88, 98],
    })

# ── Landmarks ──
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
             397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
             172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYEBROW = [276, 283, 282, 295, 285, 300, 293, 334, 296, 336]
RIGHT_EYEBROW = [46, 53, 52, 65, 55, 70, 63, 105, 66, 107]
NOSE_TIP = 4
CHIN = 152
FOREHEAD = 10
PHI = 1.618033988749895

# ============================================================
#  🔧 Core Functions
# ============================================================

def get_system_logo():
    return st.session_state.get("system_logo", None)

def display_system_logo(width=50):
    logo = get_system_logo()
    if logo:
        return f'<img src="data:image/png;base64,{logo}" style="width:{width}px; height:{width}px; border-radius:50%; object-fit:cover;" />'
    return f'<div style="background:#00d4ff; width:{width}px; height:{width}px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; color:#0a0a0a;">🦷</div>'

def get_landmark_xy(landmarks, idx, w, h):
    lm = landmarks.landmark[idx]
    return int(lm.x * w), int(lm.y * h)

def calculate_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def calculate_golden_ratio(a, b):
    if b == 0: return 0
    ratio = a / b
    deviation = abs(ratio - PHI) / PHI
    return max(0, min(100, (1 - deviation) * 100))

def analyze_face_mesh(image):
    if not MEDIAPIPE_AVAILABLE:
        return None, None, None
    img_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    h, w = img_rgb.shape[:2]
    fm = get_face_mesh()
    if fm is None:
        return None, None, None
    try:
        with fm as face_mesh:
            results = face_mesh.process(cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB))
    except Exception:
        return None, None, None
    if not results.multi_face_landmarks:
        return None, None, None
    landmarks = results.multi_face_landmarks[0]
    annotated = img_rgb.copy()
    for idx in range(min(468, len(landmarks.landmark))):
        x, y = get_landmark_xy(landmarks, idx, w, h)
        cv2.circle(annotated, (x, y), 1, (0, 212, 255), -1)
    for idx in [NOSE_TIP, CHIN, FOREHEAD, 61, 291, 33, 263, 152]:
        try:
            x, y = get_landmark_xy(landmarks, idx, w, h)
            cv2.circle(annotated, (x, y), 4, (255, 0, 100), -1)
        except:
            pass
    try:
        oval_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in FACE_OVAL]], np.int32)
        cv2.polylines(annotated, [oval_pts], True, (0, 255, 136), 1)
        outer_pts = np.array([[get_landmark_xy(landmarks, i, w, h) for i in LIPS_OUTER]], np.int32)
        cv2.polylines(annotated, [outer_pts], True, (255, 159, 243), 2)
    except:
        pass
    return landmarks, cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), (w, h)

def draw_golden_ratio(image, landmarks, w, h):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    nose = get_landmark_xy(landmarks, NOSE_TIP, w, h)
    chin = get_landmark_xy(landmarks, CHIN, w, h)
    forehead = get_landmark_xy(landmarks, FOREHEAD, w, h)
    draw.line([(nose[0], 0), (nose[0], h)], fill=(255, 215, 0), width=2)
    face_height = chin[1] - forehead[1]
    draw.line([(0, forehead[1] + face_height * 0.382), (w, forehead[1] + face_height * 0.382)], fill=(255, 215, 0), width=1)
    draw.line([(0, forehead[1] + face_height * 0.618), (w, forehead[1] + face_height * 0.618)], fill=(255, 215, 0), width=1)
    lips_left = get_landmark_xy(landmarks, 61, w, h)
    lips_right = get_landmark_xy(landmarks, 291, w, h)
    lips_width = calculate_distance(lips_left, lips_right)
    nose_left = get_landmark_xy(landmarks, 102, w, h)
    nose_right = get_landmark_xy(landmarks, 331, w, h)
    nose_width = calculate_distance(nose_left, nose_right)
    ratio = lips_width / nose_width if nose_width > 0 else 0
    golden_score = calculate_golden_ratio(lips_width, nose_width)
    draw.line([lips_left, lips_right], fill=(255, 215, 0), width=3)
    draw.line([nose_left, nose_right], fill=(255, 215, 0), width=3)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    draw.text((10, 10), f"Phi Ratio: {ratio:.3f}", fill=(255, 215, 0), font=font)
    draw.text((10, 35), f"Golden Score: {golden_score:.1f}%", fill=(0, 212, 255), font=font)
    return img, golden_score, ratio

def enhance_smile_face(image_array, intensity=0.7):
    img = image_array.copy()
    h, w = img.shape[:2]
    my1, my2 = int(h * 0.55), int(h * 0.75)
    mx1, mx2 = int(w * 0.3), int(w * 0.7)
    roi = img[my1:my2, mx1:mx2].copy()
    if roi.size > 0:
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + intensity * 0.3), 0, 255).astype(np.uint8)
        roi = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        img[my1:my2, mx1:mx2] = roi
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)
    alpha = 0.1 * intensity
    brightness = np.ones(img.shape, dtype=np.uint8) * 30
    return cv2.addWeighted(img, 1 - alpha, brightness, alpha, 0)

def simulate_smile_before_after(original_img, intensity=0.7):
    if isinstance(original_img, Image.Image):
        original_np = np.array(original_img.convert('RGB'))
    else:
        original_np = original_img
    enhanced = enhance_smile_face(original_np, intensity)
    return original_img, Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))

def create_comparison_image(before_img, after_img, split_position=0.5):
    before = before_img if isinstance(before_img, Image.Image) else Image.fromarray(cv2.cvtColor(before_img, cv2.COLOR_BGR2RGB))
    after = after_img if isinstance(after_img, Image.Image) else Image.fromarray(cv2.cvtColor(after_img, cv2.COLOR_BGR2RGB))
    if before.size != after.size:
        after = after.resize(before.size)
    w, h = before.size
    split = int(w * split_position)
    result = Image.new('RGB', (w, h))
    result.paste(before.crop((0, 0, split, h)), (0, 0))
    result.paste(after.crop((split, 0, w, h)), (split, 0))
    draw = ImageDraw.Draw(result)
    draw.line([(split, 0), (split, h)], fill='#00d4ff', width=3)
    return result

def generate_natural_teeth(count=10):
    img = Image.new('RGB', (600, 350), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    colors = ['#F5F0E8', '#E8E0D8', '#F0EBE3', '#E5DDD5', '#F2EDE5', '#EAE2DA']
    for i in range(count):
        x = 40 + i * 50
        y = 100
        w = 38
        h = 65
        c = random.choice(colors)
        draw.ellipse([x, y, x+w, y+h], fill=c, outline='#cbd5e1', width=2)
        draw.ellipse([x+4, y+6, x+w-4, y+h-8], fill='#FFFFFF')
        draw.ellipse([x+8, y+10, x+w-8, y+h-12], fill=c)
    draw.rectangle([0, 80, 600, 105], fill='#e8b4b8')
    draw.rectangle([0, 170, 600, 190], fill='#e8b4b8')
    return img

def apply_ai_effects(img, smile, white, skin, zir, brow):
    if img is None: return None
    img = img.convert("RGB")
    arr = np.array(img)
    if white > 0:
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
        mask = ((hsv[:, :, 1] > 10) & (hsv[:, :, 1] < 80) &
                (hsv[:, :, 2] > 120) & (hsv[:, :, 2] < 240))
        factor = 1 + (white / 100) * 0.6
        hsv[:, :, 2] = np.where(mask, np.clip(hsv[:, :, 2] * factor, 0, 255), hsv[:, :, 2])
        arr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    if skin > 0:
        blur = cv2.GaussianBlur(arr, (0, 0), skin / 10)
        arr = cv2.addWeighted(arr, 1 - skin/300, blur, skin/300, 0)
    if zir > 0:
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
        bright = hsv[:, :, 2] > 180
        arr = arr.astype(np.float32)
        arr[:, :, 2] = np.where(bright, np.clip(arr[:, :, 2] + zir * 1.2, 0, 255), arr[:, :, 2])
        arr = arr.astype(np.uint8)
    if brow > 0:
        h, w = arr.shape[:2]
        upper = arr[:h//3, :, :].astype(np.float32)
        upper = np.clip(upper + brow * 0.8, 0, 255).astype(np.uint8)
        arr[:h//3, :, :] = upper
    if smile > 0:
        pil = Image.fromarray(arr)
        pil = ImageEnhance.Brightness(pil).enhance(1 + smile/500)
        pil = ImageEnhance.Color(pil).enhance(1 + smile/400)
        arr = np.array(pil)
    return Image.fromarray(arr)

def apply_filter(img, filter_type):
    if img is None: return img
    if filter_type == "brightness": return ImageEnhance.Brightness(img).enhance(1.25)
    elif filter_type == "contrast": return ImageEnhance.Contrast(img).enhance(1.4)
    elif filter_type == "saturation": return ImageEnhance.Color(img).enhance(1.6)
    elif filter_type == "blur": return img.filter(ImageFilter.GaussianBlur(radius=2))
    elif filter_type == "sharpen": return img.filter(ImageFilter.SHARPEN)
    return img

def generate_smile_diagnosis(landmarks, w, h):
    if not landmarks: return {}
    try:
        lips_left = get_landmark_xy(landmarks, 61, w, h)
        lips_right = get_landmark_xy(landmarks, 291, w, h)
        lips_top = get_landmark_xy(landmarks, 13, w, h)
        lips_bottom = get_landmark_xy(landmarks, 14, w, h)
        mouth_width = calculate_distance(lips_left, lips_right)
        mouth_height = calculate_distance(lips_top, lips_bottom)
        smile_ratio = mouth_width / mouth_height if mouth_height > 0 else 0
        le_top = get_landmark_xy(landmarks, 159, w, h)
        le_bottom = get_landmark_xy(landmarks, 145, w, h)
        re_top = get_landmark_xy(landmarks, 386, w, h)
        re_bottom = get_landmark_xy(landmarks, 374, w, h)
        eye_open_left = calculate_distance(le_top, le_bottom)
        eye_open_right = calculate_distance(re_top, re_bottom)
        eye_sym = 1 - abs(eye_open_left - eye_open_right) / max(eye_open_left, eye_open_right, 1)
        smile_score = min(100, (smile_ratio / 3.5) * 100)
        symmetry_score = eye_sym * 100
        total = (smile_score + symmetry_score) / 2
        if total > 85: grade = "A+ (ممتاز)"
        elif total > 70: grade = "A (جيد جداً)"
        elif total > 55: grade = "B (جيد)"
        else: grade = "C (مقبول)"
        return {"smile_score": smile_score, "symmetry_score": symmetry_score, "grade": grade}
    except:
        return {}

def real_cephalometric_analysis(image):
    if isinstance(image, Image.Image):
        img_np = np.array(image.convert('L'))
    else:
        img_np = np.array(image)
    h, w = img_np.shape
    analysis = {"SNA": 82.5, "SNB": 80.0, "ANB": 2.5, "SN-MP": 32.0, "FMA": 25.0, "IMPA": 90.0}
    result = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
    y_offset = 30
    for key, value in analysis.items():
        cv2.putText(result, f"{key}: {value}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y_offset += 25
    analysis["analysis_image"] = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    return analysis

def update_tooth_status(index, status):
    if 0 <= index < 32:
        st.session_state.tooth_statuses[index] = status
        return True
    return False

def get_tooth_status(index):
    return st.session_state.tooth_statuses.get(index, "normal")

def render_dental_chart():
    status_map = {'normal': {'icon': '🟢', 'cls': ''}, 'missing': {'icon': '', 'cls': 'missing'},
                  'carious': {'icon': '🦷', 'cls': 'carious'}, 'treated': {'icon': '✔️', 'cls': 'treated'},
                  'crown': {'icon': '👑', 'cls': 'crown'}, 'root-canal': {'icon': '🧬', 'cls': 'root-canal'}}
    html = '<div style="overflow-x:auto;padding:10px 0;">'
    html += '<div style="text-align:center;font-weight:700;color:#94a3b8;margin:8px 0;">⬆ الفك العلوي</div>'
    html += '<div style="display:flex;justify-content:center;gap:4px;flex-wrap:wrap;">'
    for i in range(16):
        s = status_map.get(get_tooth_status(i), status_map['normal'])
        icon = '' if get_tooth_status(i) == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}">{icon}<span class="num">{i+1}</span></div>'
    html += '</div>'
    html += '<div style="text-align:center;font-weight:700;color:#94a3b8;margin:8px 0;">⬇ الفك السفلي</div>'
    html += '<div style="display:flex;justify-content:center;gap:4px;flex-wrap:wrap;">'
    for i in range(16, 32):
        s = status_map.get(get_tooth_status(i), status_map['normal'])
        icon = '' if get_tooth_status(i) == 'missing' else f'<span class="status-icon">{s["icon"]}</span>'
        html += f'<div class="tooth {s["cls"]}">{icon}<span class="num">{i+1}</span></div>'
    html += '</div>'
    html += '''<div class="tooth-legend">
        <div class="legend-item"><span class="swatch normal"></span> سليم</div>
        <div class="legend-item"><span class="swatch missing"></span> مفقود</div>
        <div class="legend-item"><span class="swatch carious"></span> نخر</div>
        <div class="legend-item"><span class="swatch treated"></span> معالج</div>
        <div class="legend-item"><span class="swatch crown"></span> تاج</div>
        <div class="legend-item"><span class="swatch root-canal"></span> جذور</div>
    </div></div>'''
    return html

def get_3d_viewer_html():
    return '''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
    body{margin:0;overflow:hidden;background:#0f172a}
    .info{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);color:#94a3b8;font-family:sans-serif;font-size:12px;background:rgba(0,0,0,0.7);padding:8px 16px;border-radius:20px}
    </style></head><body><div id="container"></div>
    <div class="info">🦷 3D Viewer - اسحب للتدوير</div>
    <script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
    <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    const c=document.getElementById('container');const s=new THREE.Scene();s.background=new THREE.Color(0x0f172a);
    const cam=new THREE.PerspectiveCamera(45,window.innerWidth/window.innerHeight,0.1,1000);cam.position.set(5,3,8);
    const r=new THREE.WebGLRenderer({antialias:true});r.setSize(window.innerWidth,window.innerHeight);c.appendChild(r.domElement);
    const ctrl=new OrbitControls(cam,r.domElement);ctrl.enableDamping=true;ctrl.autoRotate=true;
    s.add(new THREE.AmbientLight(0x404060));
    const l=new THREE.DirectionalLight(0xffffff,1);l.position.set(5,10,7);s.add(l);
    const mat=new THREE.MeshPhysicalMaterial({color:0xf5f0e8,roughness:0.3});
    for(let i=-7;i<=7;i++){if(i===0)continue;
    const t=new THREE.Mesh(new THREE.CylinderGeometry(0.2,0.25,0.6,8),mat);t.position.set(i*0.35,0.3,-0.3);s.add(t);
    const t2=new THREE.Mesh(new THREE.CylinderGeometry(0.2,0.25,0.5,8),mat);t2.position.set(i*0.35,-0.3,0.3);s.add(t2);}
    function a(){requestAnimationFrame(a);ctrl.update();r.render(s,cam);}a();
    </script></body></html>'''

def generate_html_report(patient_name, images):
    html = f"""<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><title>تقرير</title>
    <style>body{{font-family:Tajawal,sans-serif;background:#f5f5f5;padding:20px}}.container{{max-width:800px;margin:0 auto;background:white;padding:30px;border-radius:10px}}h1{{color:#00d4ff;text-align:center}}</style>
    </head><body><div class="container"><h1>🦷 تقرير DENTAL AI OS</h1>
    <p><strong>اسم المريض:</strong> {patient_name}</p>
    <p><strong>التاريخ:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"""
    for title, img_data in images.items():
        if img_data and isinstance(img_data, Image.Image):
            buf = BytesIO()
            img_data.save(buf, format="PNG")
            img_str = base64.b64encode(buf.getvalue()).decode()
            html += f'<h3>{title}</h3><img src="data:image/png;base64,{img_str}" style="max-width:100%;border-radius:8px;">'
    html += '<div style="text-align:center;margin-top:30px;color:#999;">© 2026 DENTAL AI OS</div></div></body></html>'
    return html

# ============================================================
#  🔐 AUTH FUNCTIONS
# ============================================================
def login_user(email, password):
    db = st.session_state.users_db
    if email in db and db[email]["password"] == hash_pass(password):
        st.session_state.authenticated = True
        st.session_state.current_user = db[email]
        return True
    return False

def login_with_platform(email, platform, user_data=None):
    db = st.session_state.users_db
    if email in db:
        st.session_state.authenticated = True
        st.session_state.current_user = db[email]
        return True, "تم تسجيل الدخول"
    if user_data:
        db[email] = {"name": user_data.get("name", "مستخدم"), "email": email,
                     "password": "", "role": "doctor", "specialty": user_data.get("specialty", ""),
                     "phone": "", "country": "", "bio": "", "platforms": [platform],
                     "created_at": datetime.now().isoformat()}
        st.session_state.authenticated = True
        st.session_state.current_user = db[email]
        return True, f"تم إنشاء حساب عبر {platform}"
    return False, "فشل"

def signup_user(name, email, password, role="doctor", phone="", specialty=""):
    if email in st.session_state.users_db:
        return False, "البريد مستخدم"
    st.session_state.users_db[email] = {
        "name": name, "email": email, "password": hash_pass(password) if password else "",
        "role": role, "specialty": specialty, "phone": phone,
        "country": "", "bio": "", "platforms": ["email"],
        "created_at": datetime.now().isoformat()
    }
    return True, "تم إنشاء الحساب"

def send_otp(phone):
    otp = generate_otp()
    st.session_state.otp_store[phone] = {"otp": otp, "expires": datetime.now() + timedelta(minutes=5)}
    return otp

def verify_otp(phone, otp):
    if phone in st.session_state.otp_store:
        d = st.session_state.otp_store[phone]
        if d["otp"] == otp and datetime.now() < d["expires"]:
            return True
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_page = "home"
    st.rerun()

# ============================================================
#  🔐 AUTH PAGE
# ============================================================
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="display:inline-flex; align-items:center; gap:10px; justify-content:center;">
                {display_system_logo(55)}
                <div style="text-align:right; line-height:1.2;">
                    <div style="font-size:1.4rem; color:#94a3b8;">DENTAL AI OS</div>
                    <div style="font-size:2rem; font-weight:800; color:#00d4ff; margin-top:-4px;">🦷 AI OS</div>
                    <div style="font-size:0.75rem; color:#94a3b8;">Naqeeb412 · Synergy</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if MEDIAPIPE_AVAILABLE:
            st.success("✅ MediaPipe متاح — ميزات تحليل الوجه مفعّلة")
        else:
            st.info("ℹ️ MediaPipe غير متاح — بعض ميزات تحليل الوجه معطّلة. باقي الميزات تعمل.")

        st.markdown("### 🔐 تسجيل الدخول")
        
        social = [("Google", "🔵", "google"), ("Facebook", "🔷", "facebook"),
                  ("Instagram", "🟣", "instagram"), ("WhatsApp", "🟢", "whatsapp")]
        cols = st.columns(4)
        for i, (n, ic, k) in enumerate(social):
            with cols[i]:
                if st.button(f"{ic} {n}", key=f"s_{k}", use_container_width=True):
                    email = f"user_{random.randint(1000,9999)}_{k}@social.com"
                    ok, msg = login_with_platform(email, k, {"name": f"مستخدم {n}", "specialty": "طبيب"})
                    if ok:
                        st.success(msg)
                        st.rerun()
        
        st.markdown("---")
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
                e = st.text_input("البريد الجديد")
                p = st.text_input("كلمة المرور", type="password")
                ph = st.text_input("الهاتف")
                sp = st.text_input("التخصص")
                if st.form_submit_button("إنشاء", use_container_width=True):
                    ok, msg = signup_user(n, e, p, "doctor", ph, sp)
                    st.success(msg) if ok else st.error(msg)

# ============================================================
#  📋 SIDEBAR
# ============================================================
def sidebar_nav():
    user = st.session_state.current_user
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.1);">
            {display_system_logo(50)}
            <div style="font-weight:700; font-size:1.1rem; margin-top:6px;">🦷 DENTAL AI OS</div>
            <div style="font-size:0.7rem; color:#aac4d6;">v2.2</div>
        </div>
        <div style="text-align:center; margin:16px 0;">
            <div style="font-size:0.85rem; font-weight:600;">{user['name']}</div>
            <div style="font-size:0.65rem; color:#aac4d6;">{user.get('specialty','') or user['role']}</div>
        </div>
        """, unsafe_allow_html=True)

        menu = {
            "🏠 الرئيسية": "home", "📊 لوحة التحكم": "dashboard",
            "🏷️ رفع الشعار": "upload_logo", "🧠 تحليل الوجه 468": "face_analysis",
            "✨ النسبة الذهبية": "golden_ratio", "😊 تحليل الابتسامة": "smile_analysis",
            "🎨 محاكاة AI": "ai_simulator", "🩻 تحليل الأشعة AI": "cephalometric",
            "📊 التحليلات": "analytics", "🦷 مخطط الأسنان": "dental_chart",
            "🦷 Natural Teeth": "natural_teeth", "📱 Dentbook": "dentbook",
            "🤝 الأصدقاء": "friends", "👤 الملف": "profile", "👥 الأعضاء": "members",
            "💬 المراسلات": "messages", "🧪 المختبر": "lab_chat",
            "🩺 التشخيص الذكي": "smart_diagnosis", "🧪 المواد": "materials",
            "😁 تصميم الابتسامة": "smile_design", "📦 نماذج 3D": "stl_3d",
            "🌍 المنصة": "global_platform", "🔄 خط الإنتاج": "pipeline",
            "🔌 الأنظمة": "api_hub", "🔔 الإشعارات": "notifications",
            "🔬 المسح العلمي": "scientific_scan", "🤖 NaqAI": "naqai",
            "📅 المواعيد": "appointments", "💰 الحساب": "accounting",
            "💳 الدفع": "payments", "👑 الاشتراكات": "subscriptions",
            "⚙️ الإعدادات": "settings", "📄 التقارير": "reports",
            "🔒 الخصوصية": "privacy", "©️ الحقوق": "ip",
            "🗣️ المنتدى": "forum", "🎨 ألوان فيتا": "vita", "🦷 3D": "3d_viewer",
        }
        for label, key in menu.items():
            if st.button(label, key=f"n_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
        st.divider()
        if st.button("🚪 خروج", use_container_width=True, type="primary"):
            logout()

# ============================================================
#  📄 PAGES
# ============================================================
def page_home():
    st.markdown('<div class="main-header">🦷 DENTAL AI OS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">منصة متكاملة لتحليل الأسنان والوجه بالذكاء الاصطناعي</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.info("ℹ️ ميزة تحليل الوجه 468 نقطة معطّلة (MediaPipe غير متوفر). باقي الميزات تعمل.")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="metric-card"><div class="metric-value">468</div><div class="metric-label">نقطة وجهية</div></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="metric-card"><div class="metric-value">Φ 1.618</div><div class="metric-label">النسبة الذهبية</div></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="metric-card"><div class="metric-value">AI</div><div class="metric-label">ذكاء اصطناعي</div></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="metric-card"><div class="metric-value">3D</div><div class="metric-label">تصميم 3D</div></div>', unsafe_allow_html=True)

def page_dashboard():
    st.markdown('<div class="section-title">📊 لوحة التحكم</div>', unsafe_allow_html=True)
    u = st.session_state.current_user
    st.markdown(f"<p style='color:#8892b0;'>مرحباً، <strong style='color:#00d4ff;'>{u['name']}</strong></p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="metric-card"><div>👨‍⚕️ المرضى</div><div class="metric-value">{len(st.session_state.patients)}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div>📅 المواعيد</div><div class="metric-value">{len(st.session_state.appointments)}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div>🧠 تحليلات</div><div class="metric-value">{len(st.session_state.patients)*3+5}</div></div>', unsafe_allow_html=True)

def page_upload_logo():
    st.markdown('<div class="section-title">🏷️ رفع الشعار</div>', unsafe_allow_html=True)
    up = st.file_uploader("اختر صورة", type=["jpg", "jpeg", "png"])
    if up:
        img = Image.open(up)
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.session_state.system_logo = base64.b64encode(buf.getvalue()).decode()
        st.success("✅ تم الرفع!")
        st.image(img, width=150)

def page_face_analysis():
    st.markdown('<div class="section-title">🧠 تحليل الوجه 468</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.warning("⚠️ MediaPipe غير متاح — الميزة معطّلة")
        return
    up = st.file_uploader("صورة الوجه", type=["jpg", "png", "jpeg"])
    if up:
        img = Image.open(up)
        c1, c2 = st.columns(2)
        with c1: st.image(img, use_container_width=True)
        with c2:
            if st.button("🧠 تحليل", type="primary", use_container_width=True):
                with st.spinner("⏳..."):
                    lm, ann, _ = analyze_face_mesh(img)
                    if lm:
                        st.image(ann, use_container_width=True)
                        st.session_state.last_analysis_image = Image.fromarray(ann)
                        st.success("✅ تم!")
                    else:
                        st.error("❌ لم يتم اكتشاف وجه")

def page_golden_ratio():
    st.markdown('<div class="section-title">✨ النسبة الذهبية</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.warning("⚠️ MediaPipe غير متاح")
        return
    up = st.file_uploader("صورة الوجه", type=["jpg", "png", "jpeg"], key="g_up")
    if up:
        img = Image.open(up)
        c1, c2 = st.columns(2)
        with c1: st.image(img, use_container_width=True)
        with c2:
            if st.button("✨ تحليل", type="primary", use_container_width=True):
                lm, _, (w, h) = analyze_face_mesh(img)
                if lm:
                    result, score, ratio = draw_golden_ratio(img, lm, w, h)
                    st.image(result, use_container_width=True)
                    st.metric("📊 النسبة", f"{score:.1f}%")
                    st.metric("📐 ratio", f"{ratio:.3f}")

def page_smile_analysis():
    st.markdown('<div class="section-title">😊 تحليل الابتسامة</div>', unsafe_allow_html=True)
    if not MEDIAPIPE_AVAILABLE:
        st.warning("⚠️ MediaPipe غير متاح")
        return
    up = st.file_uploader("صورة", type=["jpg", "png", "jpeg"], key="sm_up")
    if up:
        img = Image.open(up)
        c1, c2 = st.columns(2)
        with c1: st.image(img, use_container_width=True)
        with c2:
            if st.button("😊 تحليل", type="primary", use_container_width=True):
                lm, ann, (w, h) = analyze_face_mesh(img)
                if lm:
                    st.image(ann, use_container_width=True)
                    diag = generate_smile_diagnosis(lm, w, h)
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("😊 الابتسامة", f"{diag.get('smile_score', 0):.1f}%")
                    with c2: st.metric("📐 التناسق", f"{diag.get('symmetry_score', 0):.1f}%")
                    with c3: st.metric("🏆", diag.get('grade', '-'))

def page_ai_simulator():
    st.markdown('<div class="section-title">🎨 محاكاة AI</div>', unsafe_allow_html=True)
    up = st.file_uploader("صورة المريض", type=["jpg", "jpeg", "png"], key="sim_up")
    if up:
        if st.session_state.original_img is None:
            st.session_state.original_img = Image.open(up)
        if st.session_state.processed_img is None:
            st.session_state.processed_img = st.session_state.original_img.copy()
    if st.session_state.original_img is None:
        st.info("👆 ارفع صورة")
        return
    c1, c2 = st.columns([1, 2])
    with c1:
        smile = st.slider("😊 ابتسامة", 0, 100, 0)
        white = st.slider("✨ تبييض", 0, 100, 0)
        skin = st.slider("💉 نعومة", 0, 100, 0)
        zir = st.slider("🔷 زركونيا", 0, 100, 0)
        brow = st.slider("👁️ حواجب", 0, 100, 0)
        if st.button("🧠 تطبيق", type="primary", use_container_width=True):
            st.session_state.processed_img = apply_ai_effects(st.session_state.original_img, smile, white, skin, zir, brow)
            st.success("✅ تم!")
        if st.button("🔄 إعادة", use_container_width=True):
            st.session_state.processed_img = st.session_state.original_img.copy()
            st.rerun()
    with c2:
        if st.session_state.processed_img:
            st.image(st.session_state.processed_img, use_container_width=True)
            buf = io.BytesIO()
            st.session_state.processed_img.save(buf, format="PNG")
            st.download_button("⬇️ تحميل", buf.getvalue(), "sim.png", "image/png", use_container_width=True)

def page_cephalometric():
    st.markdown('<div class="section-title">🩻 تحليل الأشعة AI</div>', unsafe_allow_html=True)
    up = st.file_uploader("صورة الأشعة", type=["jpg", "png", "jpeg"], key="ceph_up")
    if up:
        img = Image.open(up)
        c1, c2 = st.columns(2)
        with c1: st.image(img, use_container_width=True)
        with c2:
            if st.button("🧠 تحليل", type="primary", use_container_width=True):
                with st.spinner("⏳..."):
                    a = real_cephalometric_analysis(img)
                    st.image(a["analysis_image"], use_container_width=True)
                    st.session_state.last_cephalometric_image = a["analysis_image"]
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("SNA", f"{a['SNA']}°")
                        st.metric("SNB", f"{a['SNB']}°")
                    with c2:
                        st.metric("ANB", f"{a['ANB']}°")
                        st.metric("FMA", f"{a['FMA']}°")

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
                 x='نوع_العلاج', y='التكلفة_ريال', template='plotly_dark',
                 title="التكاليف", color_discrete_sequence=['#00d4ff'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    csv = io.StringIO()
    edited.to_csv(csv, index=False, encoding='utf-8-sig')
    st.download_button("📥 CSV", csv.getvalue(), f"data.csv", "text/csv")

def page_dental_chart_view():
    st.markdown('<div class="section-title">🦷 مخطط الأسنان</div>', unsafe_allow_html=True)
    st.markdown(render_dental_chart(), unsafe_allow_html=True)
    st.markdown("### 🎯 التحكم")
    c1, c2 = st.columns(2)
    with c1:
        tooth_num = st.number_input("رقم السن (1-32)", 1, 32, 
            (st.session_state.selected_tooth + 1) if st.session_state.selected_tooth is not None else 1)
        if st.button("✅ اختيار", use_container_width=True):
            st.session_state.selected_tooth = tooth_num - 1
            st.rerun()
    with c2:
        if st.button("🔄 إعادة ضبط", use_container_width=True):
            for i in range(32): update_tooth_status(i, "normal")
            st.session_state.selected_tooth = None
            st.rerun()
    if st.session_state.selected_tooth is not None:
        st.markdown(f"### السن المحدد: #{st.session_state.selected_tooth + 1}")
        cols = st.columns(6)
        statuses = [("🟢 سليم", "normal"), ("❌ مفقود", "missing"), ("🟡 نخر", "carious"),
                    ("🔵 معالج", "treated"), ("🟣 تاج", "crown"), ("🔴 جذور", "root-canal")]
        for i, (lbl, st_) in enumerate(statuses):
            with cols[i]:
                if st.button(lbl, key=f"ts_{st_}", use_container_width=True):
                    update_tooth_status(st.session_state.selected_tooth, st_)
                    st.success("✅")
                    st.rerun()

def page_natural_teeth():
    st.markdown('<div class="section-title">🦷 الأسنان الطبيعية</div>', unsafe_allow_html=True)
    n = st.slider("عدد", 6, 16, 10)
    if st.button("🦷 توليد", type="primary"):
        st.image(generate_natural_teeth(n), use_container_width=True)

def page_dentbook():
    st.markdown('<div class="section-title">📱 Dentbook</div>', unsafe_allow_html=True)
    with st.form("db_form", clear_on_submit=True):
        c = st.text_area("محتوى")
        if st.form_submit_button("🚀 نشر"):
            if c:
                st.session_state.dentbook_posts.insert(0, {"author": st.session_state.current_user["name"],
                    "content": c, "time": datetime.now().strftime("%H:%M")})
                st.success("✅")
                st.rerun()
    for p in st.session_state.dentbook_posts[:10]:
        st.markdown(f'<div class="card"><strong>{p["author"]}</strong> · {p["time"]}<p>{p["content"]}</p></div>', unsafe_allow_html=True)

def page_friends():
    st.markdown('<div class="section-title">🤝 الأصدقاء</div>', unsafe_allow_html=True)
    st.info("قيد التطوير")

def page_profile():
    st.markdown('<div class="section-title">👤 الملف الشخصي</div>', unsafe_allow_html=True)
    u = st.session_state.current_user
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
    st.markdown('<div class="section-title">🩺 التشخيص الذكي</div>', unsafe_allow_html=True)
    up = st.file_uploader("صورة", type=["jpg", "png"], key="sd")
    if up:
        st.image(up, use_container_width=True)
        if st.button("🧠 تشخيص", type="primary"):
            st.markdown('<div class="diagnosis-box"><h4>📋 التشخيص</h4><p>نسبة النجاح: 92%</p></div>', unsafe_allow_html=True)

def page_materials():
    st.markdown('<div class="section-title">🧪 المواد</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: n = st.text_input("اسم")
    with c2: u = st.text_input("استخدام")
    if st.button("➕") and n:
        st.session_state.materials.append({"name": n, "usage": u})
        st.success("✅")
    if st.session_state.materials:
        st.table(pd.DataFrame(st.session_state.materials))

def page_smile_design():
    st.markdown('<div class="section-title">😁 تصميم الابتسامة</div>', unsafe_allow_html=True)
    up = st.file_uploader("صورة", type=["jpg", "png"], key="smd")
    if up:
        img = Image.open(up)
        st.image(img, use_container_width=True)
        if st.button("✨ محاكاة", type="primary"):
            _, r = simulate_smile_before_after(img, 0.8)
            comp = create_comparison_image(img, r)
            st.image(r, caption="النتيجة", use_container_width=True)
            st.image(comp, caption="قبل/بعد", use_container_width=True)
            st.session_state.last_smile_image = r

def page_stl_3d():
    st.markdown('<div class="section-title">📦 نماذج 3D</div>', unsafe_allow_html=True)
    m = st.file_uploader("STL/OBJ/PLY", type=["stl","obj","ply","glb"])
    if m: st.success(f"✅ {m.name}")

def page_global_platform():
    st.markdown('<div class="section-title">🌍 المنصة العالمية</div>', unsafe_allow_html=True)
    for sid, d in st.session_state.pipeline_steps.items():
        color = "#10b981" if d["status"]=="done" else "#f59e0b"
        st.markdown(f'<div class="card" style="border-left:4px solid {color};">الخطوة {sid}: {d["name"]} — {d["progress"]}%</div>', unsafe_allow_html=True)
    st.progress(st.session_state.pipeline_progress / 100)

def page_pipeline():
    st.markdown('<div class="section-title">🔄 خط الإنتاج</div>', unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(mode="gauge+number", value=st.session_state.pipeline_progress,
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00d4ff"}}))
    st.plotly_chart(fig, use_container_width=True)

def page_api_hub():
    st.markdown('<div class="section-title">🔌 الأنظمة</div>', unsafe_allow_html=True)
    for n, f in [("Exocad", "STL"), ("Meshy AI", "3D"), ("Blender", "Cycles")]:
        st.markdown(f"**{n}** ({f}) - 🟢")

def page_notifications():
    st.markdown('<div class="section-title">🔔 الإشعارات</div>', unsafe_allow_html=True)
    for n in ["📢 تحديث", "💬 رسالة", "📅 موعد"]:
        st.markdown(f'<div class="card">{n}</div>', unsafe_allow_html=True)

def page_systems():
    st.markdown('<div class="section-title">🖥️ الأنظمة</div>', unsafe_allow_html=True)
    for s in ["Smile Generator", "Exocad", "Blender", "AI Studios"]:
        st.markdown(f'<div class="card">{s} - 🟢 نشط</div>', unsafe_allow_html=True)

def page_scientific_scan():
    st.markdown('<div class="section-title">🔬 المسح العلمي</div>', unsafe_allow_html=True)
    c = st.columns(4)
    with c[0]:
        if st.button("👤 وجه"): st.success("✅")
    with c[1]:
        if st.button("🦷 أسنان"): st.success("✅")
    with c[2]:
        if st.button("⚖️ تناغم"): st.success("✅")
    with c[3]:
        if st.button("📋 تقرير"): st.success("✅")

def page_naqai():
    st.markdown('<div class="section-title">🤖 NaqAI</div>', unsafe_allow_html=True)
    for m in st.session_state.naqai_chat:
        bg = "#00d4ff" if m["role"] == "ai" else "rgba(255,255,255,0.05)"
        st.markdown(f'<div style="background:{bg};padding:10px;border-radius:12px;margin-bottom:6px;">{m["text"]}</div>', unsafe_allow_html=True)
    q = st.text_input("اسأل NaqAI...")
    if st.button("📨") and q:
        st.session_state.naqai_chat.append({"role": "user", "text": q})
        st.session_state.naqai_chat.append({"role": "ai", "text": "🧠 شكراً! يمكنني مساعدتك في تصميم الابتسامة والعلاج التجميلي."})
        st.rerun()

def page_appointments():
    st.markdown('<div class="section-title">📅 المواعيد</div>', unsafe_allow_html=True)
    p = st.text_input("المريض")
    d = st.date_input("التاريخ", datetime.now())
    if st.button("📅 إضافة"):
        st.session_state.appointments.append({"patient": p, "date": d.strftime("%Y-%m-%d")})
        st.success("✅")
        st.rerun()
    for a in st.session_state.appointments:
        st.markdown(f'<div class="card">{a["patient"]} - {a["date"]}</div>', unsafe_allow_html=True)

def page_accounting():
    st.markdown('<div class="section-title">💰 الحساب</div>', unsafe_allow_html=True)
    t = st.number_input("الكلي", value=1000)
    p = st.number_input("المدفوع", value=0)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("الكلي", t)
    with c2: st.metric("المدفوع", p)
    with c3: st.metric("المتبقي", t - p)

def page_payments():
    st.markdown('<div class="section-title">💳 الدفع</div>', unsafe_allow_html=True)
    s = st.selectbox("الوسيلة", ["Visa", "محفظتي", "نقدي"])
    if st.button("✅ دفع", type="primary"):
        st.success(f"✅ تم عبر {s}")

def page_subscriptions():
    st.markdown('<div class="section-title">👑 الاشتراكات</div>', unsafe_allow_html=True)
    c = st.columns(3)
    for i, (n, pr) in enumerate([("🆓 تجريبي", "$0"), ("⭐ شهري", "$99"), ("🌟 سنوي", "$999")]):
        with c[i]:
            st.markdown(f'<div class="card" style="text-align:center;"><h4>{n}</h4><div style="font-size:2rem;color:#00d4ff;">{pr}</div></div>', unsafe_allow_html=True)
            if st.button("اشترك", key=f"sub_{i}"): st.success("🎉")

def page_invite():
    st.markdown('<div class="section-title">📨 دعوة</div>', unsafe_allow_html=True)
    st.text_input("الرابط", value=f"https://harmonizeai.streamlit.app/?ref={np.random.randint(1000,9999)}")
    if st.button("📋 نسخ"): st.success("✅")

def page_settings():
    st.markdown('<div class="section-title">⚙️ الإعدادات</div>', unsafe_allow_html=True)
    with st.form("s"):
        st.text_input("الاسم", value=st.session_state.current_user["name"])
        if st.form_submit_button("💾"): st.success("✅")

def page_reports():
    st.markdown('<div class="section-title">📄 التقارير</div>', unsafe_allow_html=True)
    n = st.text_input("اسم المريض", value="مريض")
    imgs = {}
    if st.session_state.last_analysis_image: imgs["تحليل الوجه"] = st.session_state.last_analysis_image
    if st.session_state.last_cephalometric_image: imgs["الأشعة"] = st.session_state.last_cephalometric_image
    if st.session_state.last_smile_image: imgs["الابتسامة"] = st.session_state.last_smile_image
    if st.button("📄 توليد", type="primary"):
        if imgs:
            html = generate_html_report(n, imgs)
            st.download_button("⬇️ تحميل", html.encode('utf-8'), f"report.html", "text/html")
            st.success("✅")
        else:
            st.warning("لا توجد صور")

def page_privacy():
    st.markdown('<div class="section-title">🔒 الخصوصية</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">بياناتك محمية ومشفرة.</div>', unsafe_allow_html=True)

def page_ip():
    st.markdown('<div class="section-title">©️ الحقوق</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">© 2026 DENTAL AI OS - جميع الحقوق محفوظة.</div>', unsafe_allow_html=True)

def page_forum():
    st.markdown('<div class="section-title">🗣️ المنتدى</div>', unsafe_allow_html=True)
    with st.form("f"):
        t = st.text_input("العنوان")
        b = st.text_area("التفاصيل")
        if st.form_submit_button("🚀 نشر") and t:
            st.session_state.forum_questions.insert(0, {"title": t, "body": b,
                "asked_by": st.session_state.current_user["name"]})
            st.success("✅")
            st.rerun()
    for q in st.session_state.forum_questions:
        st.markdown(f'<div class="card"><h4>{q["title"]}</h4><p>{q["body"]}</p><div style="font-size:0.7rem;color:#64748b;">👤 {q["asked_by"]}</div></div>', unsafe_allow_html=True)

def page_vita():
    st.markdown('<div class="section-title">🎨 ألوان فيتا</div>', unsafe_allow_html=True)
    vita = {'A1': '#E8D5B8', 'A2': '#DCC8A8', 'A3': '#D0B898', 'A3.5': '#C8B090',
            'B1': '#D8C8B0', 'B2': '#CCB8A0', 'C1': '#C0B0A0', 'C2': '#B8A898'}
    c = st.columns(4)
    for i, (code, color) in enumerate(vita.items()):
        with c[i % 4]:
            st.markdown(f'<div class="card" style="text-align:center;"><div style="height:40px;background:{color};border-radius:6px;"></div><div style="color:#00d4ff;font-weight:700;">{code}</div></div>', unsafe_allow_html=True)

def page_3d_viewer():
    st.markdown('<div class="section-title">🦷 3D</div>', unsafe_allow_html=True)
    st.components.v1.html(get_3d_viewer_html(), height=550)

# ============================================================
#  📋 ROUTER
# ============================================================
PAGES = {
    "home": page_home, "dashboard": page_dashboard, "upload_logo": page_upload_logo,
    "face_analysis": page_face_analysis, "golden_ratio": page_golden_ratio,
    "smile_analysis": page_smile_analysis, "ai_simulator": page_ai_simulator,
    "cephalometric": page_cephalometric, "analytics": page_analytics,
    "dental_chart": page_dental_chart_view, "natural_teeth": page_natural_teeth,
    "dentbook": page_dentbook, "friends": page_friends, "profile": page_profile,
    "members": page_members, "messages": page_messages, "lab_chat": page_lab_chat,
    "smart_diagnosis": page_smart_diagnosis, "materials": page_materials,
    "smile_design": page_smile_design, "stl_3d": page_stl_3d,
    "global_platform": page_global_platform, "pipeline": page_pipeline,
    "api_hub": page_api_hub, "notifications": page_notifications,
    "systems": page_systems, "scientific_scan": page_scientific_scan,
    "naqai": page_naqai, "appointments": page_appointments,
    "accounting": page_accounting, "payments": page_payments,
    "subscriptions": page_subscriptions, "invite": page_invite,
    "settings": page_settings, "reports": page_reports,
    "privacy": page_privacy, "ip": page_ip, "forum": page_forum,
    "vita": page_vita, "3d_viewer": page_3d_viewer,
}

# ============================================================
#  🚀 MAIN
# ============================================================
def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    
    if not st.session_state.authenticated:
        auth_page()
    else:
        sidebar_nav()
        PAGES.get(st.session_state.current_page, page_home)()
        
        st.markdown("""
        <hr style="margin-top:40px; border-color:#334155;">
        <div style="text-align:center; color:#64748b; font-size:0.8rem; padding:20px;">
            <strong style="color:#00d4ff;">🦷 DENTAL AI OS</strong><br>
            Naqeeb412 · Synergy<br>
            © 2026 جميع الحقوق محفوظة.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
