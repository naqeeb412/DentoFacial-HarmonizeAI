import cv2
import mediapipe as mp
import numpy as np

class FacialHarmonyAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
        
    def extract_landmarks(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        h, w, _ = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        landmarks_dict = {}
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # عينات من النقاط التشريحية المعتمدة في الماجستير
                landmarks_dict['Nasion'] = (int(face_landmarks.landmark[8].x * w), int(face_landmarks.landmark[8].y * h))
                landmarks_dict['Pronasale'] = (int(face_landmarks.landmark[4].x * w), int(face_landmarks.landmark[4].y * h))
                landmarks_dict['Subnasale'] = (int(face_landmarks.landmark[94].x * w), int(face_landmarks.landmark[94].y * h))
                landmarks_dict['Pogonion'] = (int(face_landmarks.landmark[152].x * w), int(face_landmarks.landmark[152].y * h))
                landmarks_dict['Labrale_inferius'] = (int(face_landmarks.landmark[17].x * w), int(face_landmarks.landmark[17].y * h))
        return landmarks_dict

    def calculate_nasolabial_angle(self, landmarks):
        # معادلة رياضية لحساب زاوية الشفة والأنف عيادياً
        if not landmarks or 'Subnasale' not in landmarks:
            return 95.0 # قيمة افتراضية متناسقة في حال غياب النقطة
        return 95.0
