from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import base64
import os

app = Flask(__name__)

def process_and_encode(img_bytes, mode="smile"):
    # تحويل مصفوفة البايتات إلى صورة OpenCV
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # تحجيم الصورة للحفاظ على الأداء
    h, w, _ = img.shape
    target_w = 700
    img_res = cv2.resize(img, (target_w, int(h * (target_w / w))), interpolation=cv2.INTER_AREA)
    
    # إذا كانت صورة الابتسامة، نرسم خطوط التحليل الافتراضية هندسياً
    if mode == "smile":
        h_res, w_res, _ = img_res.shape
        # خط الابتسامة الأفقي (أزرق/ذهبي)
        cv2.line(img_res, (0, int(h_res*0.42)), (w_res, int(h_res*0.42)), (248, 189, 56), 2)
        # خط المنتصف العمودي (أصفر)
        cv2.line(img_res, (int(w_res*0.5), 0), (int(w_res*0.5), h_res), (0, 255, 255), 2)
        # قوس التناسب الذهبي للأسنان (أخضر)
        cv2.ellipse(img_res, (int(w_res*0.5), int(h_res*0.38)), (int(w_res*0.23), int(h_res*0.1
