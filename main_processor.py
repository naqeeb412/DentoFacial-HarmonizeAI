import os
import glob
from scripts.vision_processor import FacialVisionEngine
from scripts.analysis_logic import DentoFacialEngine

# المسار المربوط من Google Drive الخاص ببيانات المرضى
# تأكد من تطابق هذا المسار مع المسار الفعلي في الـ Drive الخاص بك
DATA_PATH = '/content/drive/MyDrive/HarmonizeAI_Data/raw/'

def run_harmonize_ai_pipeline():
    print("🚀 Starting DentoFacial-HarmonizeAI Integrated Pipeline...")
    
    # تهيئة محرك الرؤية
    vision_unit = FacialVisionEngine()
    
    # الحصول على كافة صور المرضى من المجلد تلقائياً
    # يبحث الكود عن أي ملف يبدأ بحرف 'p' وينتهي بـ '.jpg'
    patient_files = glob.glob(os.path.join(DATA_PATH, 'p*.jpg'))
    
    if not patient_files:
        print("⚠️ No patient files found in the directory. Please check the path.")
        return

    # المعالجة التلقائية لكل مريض
    for image_path in patient_files:
        patient_id = os.path.basename(image_path).split('.')[0]
        print(f"\n--- Processing: {patient_id} ---")
        
        # تهيئة المحلل لكل مريض على حدة لضمان استقلالية التقارير
        analysis_unit = DentoFacialEngine(patient_id=patient_id)
        
        # استخراج النقاط التشريحية من الصورة آلياً
        print(f"📸 Analyzing image: {image_path}")
        medical_points = vision_unit.get_ortho_points(image_path)
        
        if medical_points:
            print("✅ Landmarks detected successfully.")
            
            # إرسال النقاط لمحرك الحسابات
            analysis_unit.analyze_profile(
                n_tip=medical_points['NOSE_TIP'],
                sn=medical_points['SUBNASALE'],
                ul=medical_points['UPPER_LIP'],
                ll=medical_points['LOWER_LIP'],
                pg=medical_points['CHIN']
            )
            
            # توليد التقرير النهائي
            analysis_unit.generate_report()
            print(f"✅ Report generated for {patient_id}")
        else:
            print(f"❌ Failed to detect landmarks for {patient_id}. Please check image quality.")

if __name__ == "__main__":
    run_harmonize_ai_pipeline()
