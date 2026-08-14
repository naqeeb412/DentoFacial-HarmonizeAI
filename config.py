import os

# المسارات الأساسية للنظام
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

# ملفات القواعد الإكلينيكية
AESTHETIC_RULES_PATH = os.path.join(BASE_DIR, "Aesthetic_Clinical_Rules.json")
STANDARDS_PATH = os.path.join(DATA_DIR, "standards.json")

# إعدادات واجهة Streamlit
PAGE_CONFIG = {
    "page_title": "DentoFacial-HarmonizeAI",
    "page_icon": "🦷",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}
