from analysis_logic import HarmonizeAnalyzer

# 1. تهيئة المحرك
analyzer = HarmonizeAnalyzer()

# 2. ضع مسار أي صورة بروفايل موجودة لديك
image_path = "patient_profile.jpg" 

# 3. تشغيل المعالجة والتحليل
points, img, msg = analyzer.process_image(image_path)
print("حالة المعالجة:", msg)

if points:
    report = analyzer.generate_clinical_report(points)
    print("\n--- تقرير التحليل السريري ---")
    for key, val in report.items():
        print(f"{key}: {val}")
