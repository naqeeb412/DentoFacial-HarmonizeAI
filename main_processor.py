import json
import os

# 1. Load Aesthetic Rules from JSON
def load_rules():
    try:
        with open('Aesthetic_Rules.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: Aesthetic_Rules.json not found.")
        return None

# 2. Setup Patient Data
PATIENT_ID = "patient_001"
rules = load_rules()

if rules:
    print(f"--- DentoFacial-HarmonizeAI System ---")
    print(f"Target Patient: {PATIENT_ID}")
    
    # Example of using the rules (E-Line for Ricketts)
    ideal_lower_lip = rules['e_line_ricketts']['lower_lip_to_eline']
    print(f"Clinical Standard: Lower lip should be around {ideal_lower_lip} mm to E-Line.")

    # Simulated clinical measurement for Patient 001
    clinical_measure = -5 
    
    print(f"Current Measurement: {clinical_measure} mm")
    if clinical_measure < ideal_lower_lip:
        print("Diagnosis: Lower lip is retruded.")
    else:
        print("Diagnosis: Lower lip position is within normal range.")
