import cv2
import mediapipe as mp

class FacialVisionEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            refine_landmarks=True
        )
        # تعريف أرقام النقاط التشريحية حسب معايير MediaPipe
        self.LANDMARKS = {
            'NOSE_TIP': 1,        # Pronasale
            'SUBNASALE': 164,     # Subnasale
            'UPPER_LIP': 0,       # Labrale Superius
            'LOWER_LIP': 17,      # Labrale Inferius
            'CHIN': 152           # Pogonion
        }

    def get_ortho_points(self, image_path):
        """استخراج الإحداثيات الدقيقة للنقاط الطبية"""
        image = cv2.imread(image_path)
        results = self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        points = {}
        if results.multi_face_landmarks:
            mesh = results.multi_face_landmarks[0]
            h, w, _ = image.shape
            
            for name, idx in self.LANDMARKS.items():
                landmark = mesh.landmark[idx]
                # تحويل الإحداثيات من نسبية إلى بكسل حقيقي
                points[name] = (int(landmark.x * w), int(landmark.y * h))
        
        return points
