import cv2
import os

def check_setup():
    print("🛠️ Starting System Integrity Check...")
    
    # 1. التأكد من وجود الصورة
    img_path = 'images/patient_test.jpg'
    if os.path.exists(img_path):
        print(f"✅ Image Found: {img_path}")
        img = cv2.imread(img_path)
        h, w, _ = img.shape
        print(f"📏 Image Dimensions: {w}x{h} pixels")
    else:
        print("❌ Error: Patient image missing in /images folder.")

    # 2. التأكد من وصول الكود للمحركات
    try:
        from scripts.vision_processor import FacialVisionEngine
        test_engine = FacialVisionEngine()
        print("✅ Vision Engine: Loaded and Ready.")
    except Exception as e:
        print(f"❌ Vision Engine Error: {e}")

if __name__ == "__main__":
    check_setup()
