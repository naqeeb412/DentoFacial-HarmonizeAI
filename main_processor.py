import os
import glob
from scripts.vision_processor import FacialVisionEngine
from scripts.analysis_logic import DentoFacialEngine

# المسار المحدث ليطابق تنظيم ملفاتك في Google Drive
DATA_PATH = '/content/drive/MyDrive/data/raw/clinical-record/'

def run_harmonize_ai_pipeline():
    print("🚀 Starting DentoFacial-HarmonizeAI Integrated Pipeline...")
    
    vision_unit = FacialVisionEngine()
    
    # البحث عن الصور داخل المجلدات الفرعية (مثل p001/patient.jpg)
    # الرمز ** يعني البحث في أي مجلدات فرعية، و recursive=True ضرورية لذلك
    search_path = os.path.join(DATA_PATH, '**', 'p*.jpg')
    patient_files = glob.glob(search_path, recursive=True)
    
    if not patient_files:
        print(f"⚠️ No patient files found in {DATA_PATH}. Please check the path.")
        return

    for image_path in patient_files:
        # استخراج اسم المجلد الفرعي ليكون هو الـ ID للمريض
        patient_id = os.path.basename(os.path.dirname(image_path))
        print(f"\n--- Processing Patient: {patient_id} ---")
        
        analysis_unit = DentoFacialEngine(patient_id=patient_id)
        
        print(f"📸 Analyzing image: {image_path}")
        medical_points = vision_unit.get_ortho_points(image_path)
        
        if medical_points:
            print("✅ Landmarks detected successfully.")
            analysis_unit.analyze_profile(
                n_tip=medical_points['NOSE_TIP'],
                sn=medical_points['SUBNASALE'],
                ul=medical_points['UPPER_LIP'],
                ll=medical_points['LOWER_LIP'],
                pg=medical_points['CHIN']
            )
            analysis_unit.generate_report()
            print(f"✅ Report generated for {patient_id}")
        else:
            print(f"❌ Failed to detect landmarks for {patient_id}.")

if __name__ == "__main__":
    run_harmonize_ai_pipeline()
