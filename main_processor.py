from scripts.vision_processor import FacialVisionEngine
from scripts.analysis_logic import DentoFacialEngine
import json

def run_harmonize_ai_pipeline():
    print("🚀 Starting DentoFacial-HarmonizeAI Integrated Pipeline...")
    
    # 1. تهيئة المحركات
    vision_unit = FacialVisionEngine()
    analysis_unit = DentoFacialEngine(patient_id="CASE_YEM_2026_01")
    
    # 2. استخراج النقاط التشريحية من الصورة آلياً
    image_path = 'images/patient_test.jpg'
    print(f"📸 Processing image: {image_path}")
    
    medical_points = vision_unit.get_ortho_points(image_path)
    
    if medical_points:
        print("✅ Landmarks detected successfully.")
        
        # 3. إرسال النقاط لمحرك الحسابات (الزاوية الأنفية الشفوية مثلاً)
        # ملاحظة: سنستخدم النقاط المستخرجة (Nose, Subnasale, Upper Lip)
        analysis_unit.analyze_profile(
            n_tip=medical_points['NOSE_TIP'],
            sn=medical_points['SUBNASALE'],
            ul=medical_points['UPPER_LIP'],
            ll=medical_points['LOWER_LIP'],
            pg=medical_points['CHIN']
        )
        
        # 4. توليد التقرير النهائي
        print("\n--- 📄 FINAL CLINICAL REPORT ---")
        analysis_unit.generate_report()
    else:
        print("❌ Failed to detect landmarks. Please check image quality.")

if __name__ == "__main__":
    run_harmonize_ai_pipeline()
