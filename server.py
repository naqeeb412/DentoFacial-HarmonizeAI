import http.server
import socketserver
import os

# إعداد منفذ التشغيل وخادم الـ HTTP
PORT = 8000
DIRECTORY = "."

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run_server():
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"[*] خادم HarmonizeAI يعمل الآن بنجاح على المنفذ: http://localhost:{PORT}")
        print(f"[*] يتم خدمة الملفات من المجلد الحالي: {os.path.abspath(DIRECTORY)}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] يتم إيقاف الخادم بناءً على طلب المستخدم...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
