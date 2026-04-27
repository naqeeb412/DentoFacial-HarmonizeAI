import json
import os

# 1. Load Aesthetic Rules from JSON
def load_rules():
    with open('Aesthetic_Rules.json', 'r') as f:
        return json.load(f)

# 2. Link with Patient Data
PATIENT_ID = "patient_001"
rules = load_rules()

print(f"--- DentoFacial-HarmonizeAI System ---")
print(f"Target Patient: {PATIENT_ID}")
print(f"Reference Standard: Ricketts E-Line is {rules['e_line_ricketts']['lower_lip_to_eline']} mm")

# Simulate a diagnostic check
clinical_measure = -5 # Example measurement from a photo
if clinical_measure < rules['e_line_ricketts']['lower_lip_to_eline']:
    print("Diagnosis: Lower lip is retruded relative to E-Line.")
else:
    print("Diagnosis: Lower lip position is within normal/protruded limits.")
