import cv2
import mediapipe as mp
import numpy as np
import math

class HarmonizeAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

    def process_image(self, image_path):
        """تحميل الصورة واستخراج نقاط الوجه (Landmarks)"""
        image = cv2.imread(image_path)
        if image is None:
            return None, None, "لم يتم العثور على الصورة، تحقق من المسار."
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return None, image, "لم يتم التعرف على الوجه في الصورة."
            
        landmarks = results.multi_face_landmarks[0]
        h, w, _ = image.shape
        
        # تحويل إحداثيات النقاط إلى بكسل (Pixel Coordinates)
        points = {}
        for idx, lm in enumerate(landmarks.landmark):
            points[idx] = (int(lm.x * w), int(lm.y * h))
            
        return points, image, "تم استخراج النقاط بنجاح."

    def analyze_e_line(self, points):
        """حساب خط Ricketts E-Line للبروفايل (من قمة الأنف إلى الذقن)"""
        # أهم النقاط في MediaPipe:
        # Pronasale (قمة الأنف) = 1
        # Soft Tissue Pogonion (قمة الذقن) = 152
        # Labriale Superius (الشفة العليا) = 0
        # Labriale Inferius (الشفة السفلى) = 17
        
        if 1 not in points or 152 not in points or 0 not in points or 17 not in points:
            return "تعذر حساب E-Line، بعض النقاط غير واضحة."

        nose_tip = np.array(points[1])
        chin = np.array(points[152])
        upper_lip = np.array(points[0])
        lower_lip = np.array(points[17])

        # حساب المسافة العمودية من الشفاه إلى الخط الواصل بين الأنف والذقن
        def point_to_line_dist(p, line_p1, line_p2):
            return np.cross(line_p2 - line_p1, p - line_p1) / np.linalg.norm(line_p2 - line_p1)

        dist_upper = point_to_line_dist(upper_lip, nose_tip, chin)
        dist_lower = point_to_line_dist(lower_lip, nose_tip, chin)

        return {
            "Upper Lip to E-Line (px)": round(float(dist_upper), 2),
            "Lower Lip to E-Line (px)": round(float(dist_lower), 2)
        }

# مثال بسيط للتشغيل والتجربة
if __name__ == "__main__":
    analyzer = HarmonizeAnalyzer()
    print("HarmonizeAI Analyzer Ready!")
