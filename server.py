import http.server
import socketserver
import os

# تحديد المنفذ المحلي
PORT = 8000

# التأكد من تشغيل السيرفر من نفس مجلد HarmonizeAI
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"==================================================")
    print(f"  Naqeeb412 · HarmonizeAI™ Local Server Active")
    print(f"  URL: http://localhost:{PORT}/index.html")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nتم إيقاف الخادم بنجاح.")
