import cv2
import mediapipe as mp
import numpy as np
import json
import os

class HarmonizeAnalyzer:
    def __init__(self, rules_path="Aesthetic_Clinical_Rules.json"):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def process_image(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            return None, None, "لم يتم العثور على الصورة."
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return None, image, "لم يتم التعرف على الوجه."
            
        landmarks = results.multi_face_landmarks[0]
        h, w, _ = image.shape
        
        points = {}
        for idx, lm in enumerate(landmarks.landmark):
            points[idx] = (int(lm.x * w), int(lm.y * h))
            
        return points, image, "تم تحليل المعالم السريرية بنجاح."

    def calculate_angle(self, p1, p2, p3):
        a, b, c = np.array(p1), np.array(p2), np.array(p3)
        ba, bc = a - b, c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

    def generate_full_clinical_report(self, points):
        report = {}
        diagnoses = []

        # 1. زاوية تحدب الوجه (Glabella 10, Subnasale 2, Pogonion 152)
        if 10 in points and 2 in points and 152 in points:
            prof_angle = self.calculate_angle(points[10], points[2], points[152])
            report["Facial Convexity Angle"] = f"{round(prof_angle, 1)}°"
            if prof_angle < 165.0:
                diagnoses.append("بروفايل محدب (Convex Profile - Class II Tendency)")
            elif prof_angle > 175.0:
                diagnoses.append("بروفايل مقعر (Concave Profile - Class III Tendency)")
            else:
                diagnoses.append("بروفايل مستقيم مثالي (Straight Profile)")

        # 2. الزاوية الأنفية الشفوية Nasolabial Angle (Pronasale 1, Subnasale 2, Labriale Superius 0)
        if 1 in points and 2 in points and 0 in points:
            naso_angle = self.calculate_angle(points[1], points[2], points[0])
            report["Nasolabial Angle"] = f"{round(naso_angle, 1)}°"
            if naso_angle < 90.0:
                diagnoses.append("زاوية أنفية شفوية حادة (Acute Nasolabial Angle - Upper Lip Protrusion)")
            elif naso_angle > 110.0:
                diagnoses.append("زاوية أنفية شفوية منفرجة (Obtuse Nasolabial Angle - Retruded Lip)")

        # 3. خط Ricketts E-Line (Nose Tip 1, Chin 152, Upper Lip 0, Lower Lip 17)
        if 1 in points and 152 in points and 0 in points and 17 in points:
            nose_tip, chin = np.array(points[1]), np.array(points[152])
            upper_lip, lower_lip = np.array(points[0]), np.array(points[17])

            def line_dist(p, l1, l2):
                return np.cross(l2 - l1, p - l1) / np.linalg.norm(l2 - l1)

            u_dist = line_dist(upper_lip, nose_tip, chin)
            l_dist = line_dist(lower_lip, nose_tip, chin)

            report["Upper Lip to E-Line"] = f"{round(float(u_dist), 1)} px"
            report["Lower Lip to E-Line"] = f"{round(float(l_dist), 1)} px"

        # 4. تحليل الأثلاث الوجهية Facial Thirds (Trichion 10, Subnasale 2, Menton 152)
        if 10 in points and 2 in points and 152 in points:
            # ارتفاع الثلث الأوسط والثلث السفلي
            mid_third = abs(points[2][1] - points[10][1])
            lower_third = abs(points[152][1] - points[2][1])
            total_h = mid_third + lower_third
            
            mid_pct = round((mid_third / total_h) * 100, 1) if total_h > 0 else 0
            low_pct = round((lower_third / total_h) * 100, 1) if total_h > 0 else 0

            report["Middle Third Ratio"] = f"{mid_pct}%"
            report["Lower Third Ratio"] = f"{low_pct}%"

        report["Diagnoses"] = diagnoses
        return report
