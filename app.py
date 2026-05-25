import os
import cv2
import numpy as np
import base64
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# إعداد مجلد لرفع الصور مؤقتاً إذا لزم الأمر
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def process_and_convert_b64(image_bytes):
    """دالة لقراءة الصورة، تحجيمها، وتحويلها إلى Base64 بأمان"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None, 0, 0
    
    # تحجيم موحد للعرض (عرض 600 بكسل)
    h, w = img.shape[:2]
    target_w = 600
    img_res = cv2.resize(img, (target_w, int(h * (target_w / w))), interpolation=cv2.INTER_AREA)
    h_res, w_res = img_res.shape[:2]
    
    # تحويل إلى جودة PNG وترميز Base64
    _, buffer = cv2.imencode('.png', img_res)
    img_b64 = base64.b64encode(buffer).decode('utf-8')
    return img_b64, w_res, h_res

@app.route('/')
def home():
    # لعرض ملف index.html الرئيسي عند فتح السيرفر
    return render_template('index.html')

@app.route('/analyze_patient', methods=['POST'])
def analyze_patient():
    try:
        # 1. استقبال الصور الثلاث من الواجهة الأمامية
        file_profile = request.files.get('image_profile')
        file_smile = request.files.get('image_smile')
        file_xray = request.files.get('image_xray')
        
        # 2. معالجة وتحويل كل صورة إلى Base64
        img_profile_b64, _, _ = process_and_convert_b64(file_profile.read()) if file_profile else (None, 0, 0)
        img_smile_b64, smile_w, smile_h = process_and_convert_b64(file_smile.read()) if file_smile else (None, 0, 0)
        img_xray_b64, _, _ = process_and_convert_b64(file_xray.read()) if file_xray else (None, 0, 0)
        
        # 3. محرك تشخيص AI الافتراضي وتوليد التقرير السريري
        diagnosis_report = {
            "xray_analysis": "تظهر صور الأشعة المرفوعة مستويات العظم السنخي المحيط بالقواطع والنهج الذروي. لا توجد ظلال لالتهابات نشطة، والكثافة تسمح بالتحميل الميكانيكي المباشر.",
            "aesthetic_analysis": "يظهر انحراف طفيف في خط المنتصف السني بمقدار 0.8 ملم نحو اليسار مقارنة بخط الوجه الساكن. القواطع الجانبية تتطلب تعديلاً بنسبة 12% للوصول للنسبة الذهبية للابتسامة.",
            "treatment_plan": [
                {"stage": "1. التحضيرية", "procedure": "تقليح وتنظيف اللثة لضمان قاعدة حيوية صحية.", "dept": "Periodontics"},
                {"stage": "2. التصحيحية", "procedure": "إعادة محاذاة الأسنان وتصحيح خط المنتصف تجميلياً.", "dept": "Orthodontics"},
                {"stage": "3. التجميلية", "procedure": "تطبيق عدسات الفينير للأسنان الستة الأمامية بناءً على أبعاد هندسة الابتسامة.", "dept": "Prosthodontics"}
            ]
        }
        
        # 4. إرسال البيانات والنتائج كاملة إلى المتصفح بصيغة JSON
        return jsonify({
            "status": "success",
            "img_profile": img_profile_b64,
            "img_smile": img_smile_b64,
            "smile_w": smile_w,
            "smile_h": smile_h,
            "img_xray": img_xray_b64,
            "report": diagnosis_report
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # تشغيل السيرفر المحلي على منفذ 5000
    app.run(debug=True, port=5000)
