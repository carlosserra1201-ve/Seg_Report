import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import Report  # Carga todo el código y handlers de Report.py


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot en marcha")


    def log_message(self, format, *args):
        return


def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Servidor HTTP iniciado en el puerto {port}")
    server.serve_forever()


if __name__ == '__main__':
    # 1. Iniciar el servidor web de salud en segundo plano
    threading.Thread(target=run_http_server, daemon=True).start()
    
    # 2. Iniciar el bot y mantener la aplicación en ejecución constante
    print("Bot @ReporteAChBot en marcha desde server.py...")
    Report.app.run_polling()
