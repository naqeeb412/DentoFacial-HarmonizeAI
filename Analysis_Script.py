# التسميات الجديدة المعتمدة في HarmonizeAI
LATERAL_FILE = "1.jpg" 
PROFILE_FILE = "patient_profile1.jpg"

def get_image_path(filename):
    # الكود سيبحث الآن عن الصورة 1 داخل مجلد المشروع
    import os
    # تأكد من تعريف PROJECT_DATA_DIR أو استبداله بالمسار المباشر
    PROJECT_DATA_DIR = "/content/drive/MyDrive/HarmonizeAI/" 
    potential_path = os.path.join(PROJECT_DATA_DIR, filename)
    return potential_path

import math
import cv2
import mediapipe as mp

# DentoFacial-HarmonizeAI: Core Analysis Engine
# Focus: Interdisciplinary Synergy (Orthodontics & Aesthetics)

def calculate_nasolabial_angle(nose_tip, subnasale, upper_lip):
    """
    حساب الزاوية الأنفية الشفوية بدقة رياضية.
    المدخلات: إحداثيات (x, y) لثلاث نقاط تشريحية.
    """
    try:
        # حساب المتجهات بين النقاط
        ang1 = math.atan2(nose_tip[1] - subnasale[1], nose_tip[0] - subnasale[0])
        ang2 = math.atan2(upper_lip[1] - subnasale[1], upper_lip[0] - subnasale[0])
        
        angle = abs(math.degrees(ang1 - ang2))
        
        # لضمان الحصول على الزاوية الداخلية الصحيحة
        if angle > 180:
            angle = 360 - angle
            
        return round(angle, 2)
    except Exception as e:
        return f"Error in calculation: {e}"

def check_eline_status(lower_lip_x, e_line_x):
    """
    تحليل وضع الشفة السفلية بالنسبة لخط E-Line (Ricketts).
    """
    diff = lower_lip_x - e_line_x
    if diff < -2:
        return "Retruded (Needs orthodontic/surgical consultation)"
    elif -2 <= diff <= 0:
        return "Ideal Aesthetic Harmony"
    else:
        return "Protruded (Potential Orthodontic case)"
def get_nasolabial_diagnosis(angle):
    """
    تصنيف الزاوية بناءً على المعايير الجمالية المعتمدة (90-110 درجة).
    """
    if angle < 90:
        return "Acute (Possible Maxillary Protrusion)"
    elif 90 <= angle <= 110:
        return "Ideal Aesthetic Harmony"
    else:
        return "Obtuse (Possible Maxillary Retrusion)"
def calculate_skeletal_analysis(s, n, a, b):
    """
    تحليل علاقة الفكين عظمياً (SNA, SNB, ANB).
    """
    def get_angle(p1, p2, p3):
        # حساب الزاوية بين ثلاث نقاط باستخدام المتجهات
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        angle = math.degrees(math.atan2(v1[1], v1[0]) - math.atan2(v2[1], v2[0]))
        return abs(round(angle, 2))

    sna = get_angle(s, n, a)
    snb = get_angle(s, n, b)
    anb = round(sna - snb, 2)
    
    # تصنيف الحالة العظمية (Skeletal Class)
    if 2 <= anb <= 4:
        s_class = "Class I (Normal)"
    elif anb > 4:
        s_class = "Class II (Maxillary Protrusion)"
    else:
        s_class = "Class III (Mandibular Protrusion)"
        
    return sna, snb, anb, s_class

def extract_face_landmarks(image_path):
    """
    استخراج نقاط الوجه التشريحية باستخدام MediaPipe Face Mesh.
    """
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh:
        image = cv2.imread(image_path)
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            return None
        
        # استخراج النقاط (هنا نحدد أرقام النقاط الخاصة بالأنف والشفاه)
        landmarks = results.multi_face_landmarks[0].landmark
        return landmarks

# --- اختبار المحرك الافتراضي (Simulation) ---
print("--- DentoFacial-HarmonizeAI Diagnostics ---")

# 1. حساب الزاوية وإعطاء التشخيص (الأسطر 52-54)
test_angle = calculate_nasolabial_angle((10, 50), (10, 10), (50, 10))
test_diag = get_nasolabial_diagnosis(test_angle) 

# 2. طباعة النتائج (الأسطر 56-58)
print(f"Computed Nasolabial Angle: {test_angle} degrees")
print(f"Clinical Diagnosis: {test_diag}")
print(f"Ricketts E-Line Analysis: {check_eline_status(45, 50)}")

# 3. التحليل العظمي (Skeletal Analysis Simulation)
# نقاط افتراضية للمحاكاة: S(10,10), N(50,10), A(45,30), B(40,50)
sna, snb, anb, s_class = calculate_skeletal_analysis((10, 10), (50, 10), (45, 30), (40, 50))

print(f"--- Skeletal Analysis (HarmonizeAI) ---")
print(f"SNA Angle: {sna} degrees | SNB Angle: {snb} degrees")
print(f"ANB Angle: {anb} degrees")
print(f"Skeletal Classification: {s_class}")
def generate_aesthetic_report(patient_name, naso_angle, e_line, skeletal_class):
    """
    إنشاء تقرير نهائي احترافي للمريض.
    """
    report = f"""
    ==========================================
    DentoFacial-HarmonizeAI: Clinical Report
    ==========================================
    Patient Name: {patient_name}
    Date: 2026-05-11
    
    1. Soft Tissue Analysis:
       - Nasolabial Angle: {naso_angle} degrees
       - Ricketts E-Line: {e_line}
       
    2. Skeletal Classification:
       - Result: {skeletal_class}
    
    Recommendation: Please consult with your orthodontist 
    for the final treatment plan.
    ==========================================
    """
    return report
# تجربة إنشاء التقرير النهائي
final_report = generate_aesthetic_report("Test Patient", test_angle, "Ideal", s_class)
print(final_report)
def run_automatic_analysis(image_path):
    # 1. استخراج النقاط من الصورة
    landmarks = extract_face_landmarks(image_path)
    if landmarks:
        # تحويل إحداثيات MediaPipe لنقاط يمكن حسابها
        # ملاحظة: نستخدم z للعمق في البروفايل الجانبي
        n_tip = (landmarks[4].x, landmarks[4].y)
        sn = (landmarks[164].x, landmarks[164].y)
        u_lip = (landmarks[0].x, landmarks[0].y)
        
        # 2. حساب زاوية الأنف والشفاه تلقائياً
        angle = calculate_nasolabial_angle(n_tip, sn, u_lip)
        diagnosis = get_nasolabial_diagnosis(angle)
        
        # 3. طباعة التقرير النهائي
        report = generate_aesthetic_report("Patient_001", angle, "Analyzed", "Pending Skeletal")
        print(report)
    else:
        print("Error: Could not detect face in image.")

# لتشغيل البرنامج على صورة حقيقية (قم بتغيير اسم الصورة لصورتك)
 run_automatic_analysis("patient_profile.jpg")
def def analyze_real_patient():
    """
    دالة التحليل السريري الموحدة لمشروع HarmonizeAI.
    تقوم بجلب الصورة '1.jpg' تلقائياً وإجراء الفحص السيفالومتري.
    """
    try:
        # 1. جلب المسار الصحيح باستخدام الثوابت والدالة التي أضفتها
        lateral_path = get_image_path(LATERAL_FILE)
        
        # 2. استخراج النقاط التشريحية من الصورة الجانبية رقم 1
        landmarks = extract_face_landmarks(lateral_path)
        
        if landmarks:
            # 3. حساب الزاوية الأنفية الشفوية (Nasolabial Angle)
            # نمرر النقاط المستخرجة من MediaPipe
            angle = calculate_nasolabial_angle(
                landmarks['nose_tip'], 
                landmarks['subnasale'], 
                landmarks['upper_lip']
            )
            
            # 4. استخراج التشخيص السريري بناءً على القيمة الرقمية
            diagnosis = get_nasolabial_diagnosis(angle)
            
            print(f"✅ Analysis Complete for Image: {LATERAL_FILE}")
            print(f"📊 Measured Angle: {angle}°")
            print(f"🩺 Clinical Diagnosis: {diagnosis}")
            
            return angle, diagnosis
        else:
            return "Error: Could not detect landmarks on image '1.jpg'"
            
    except Exception as e:
        return f"An error occurred during clinical analysis: {str(e)}"
(image_path):
    # 1. التعرف على الوجه ونقاطه
    landmarks = extract_face_landmarks(image_path)
    if landmarks:
        # 2. تحديد النقاط التشريحية (MediaPipe Indices)
        # 4: Nose Tip, 164: Subnasale, 0: Upper Lip
        nose = (landmarks[4].x * 100, landmarks[4].y * 100)
        sn = (landmarks[164].x * 100, landmarks[164].y * 100)
        ul = (landmarks[0].x * 100, landmarks[0].y * 100)
        
        # 3. تشغيل المحرك الحسابي
        angle = calculate_nasolabial_angle(nose, sn, ul)
        diag = get_nasolabial_diagnosis(angle)
        
        # 4. طباعة التقرير
        print(generate_aesthetic_report("Patient Ali", angle, "Analyzed", "Pending"))
    else:
        print("Could not find face landmarks in image.")
