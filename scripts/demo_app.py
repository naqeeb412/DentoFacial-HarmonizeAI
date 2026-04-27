import json
import os

def load_standards():
    """تحميل المعايير الجمالية من ملف البيانات"""
    try:
        with open('data/standards.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return "Error: Standards file not found."

def run_quick_analysis(patient_name, measured_angle):
    """إجراء تحليل سريع ومقارنته بالمعايير"""
    standards = load_standards()
    min_ideal = standards['nasolabial_angle']['min_ideal']
    max_ideal = standards['nasolabial_angle']['max_ideal']
    
    print(f"\n--- Clinical Analysis for: {patient_name} ---")
    print(f"Measured Nasolabial Angle: {measured_angle}°")
    
    if min_ideal <= measured_angle <= max_ideal:
        status = "✅ Ideal Aesthetic Harmony"
    elif measured_angle < min_ideal:
        status = "⚠️ Acute Angle (Potential Protrusion)"
    else:
        status = "⚠️ Obtuse Angle (Potential Retrusion)"
        
    print(f"Result: {status}")
    print(f"Reference: {standards['nasolabial_angle']['reference']}")
    print("-" * 40)

# تجربة تشغيل المحاكي لعيادة إب
if __name__ == "__main__":
    run_quick_analysis("Yemeni Patient Case 01", 102.5)
