import math

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


# --- اختبار المحرك الافتراضي (Simulation) ---
print("--- DentoFacial-HarmonizeAI Diagnostics ---")

# 1. حساب الزاوية وإعطاء التشخيص (الأسطر 52-54)
test_angle = calculate_nasolabial_angle((10, 50), (10, 10), (50, 10))
test_diag = get_nasolabial_diagnosis(test_angle) 

# 2. طباعة النتائج (الأسطر 56-58)
print(f"Computed Nasolabial Angle: {test_angle} degrees")
print(f"Clinical Diagnosis: {test_diag}")
print(f"Ricketts E-Line Analysis: {check_eline_status(45, 50)}")

