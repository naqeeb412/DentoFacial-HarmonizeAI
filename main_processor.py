import os

# Define the path to the patient data
PATIENT_ID = "patient_001"
DATA_PATH = f"data/cases/{PATIENT_ID}/"

def load_patient_images(path):
    """Function to scan the directory for clinical images."""
    if os.path.exists(path):
        files = os.listdir(path)
        images = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]
        return images
    return []

# Execute Loading
found_images = load_patient_images(DATA_PATH)

print(f"--- DentoFacial-HarmonizeAI ---")
print(f"Processing Data for: {PATIENT_ID}")
print(f"Found {len(found_images)} images for analysis: {found_images}")

if len(found_images) > 0:
    print("Status: Ready for Landmark Detection.")
else:
    print("Status: Waiting for clinical images...")
