import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import Report


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot en marcha correctamente")


    def log_message(self, format, *args):
        return


def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Servidor HTTP iniciado en puerto {port}")
    server.serve_forever()


if __name__ == '__main__':
    # 1. Iniciar el servidor de salud para Render en un hilo secundario
    threading.Thread(target=run_http_server, daemon=True).start()


    # 2. Construir e iniciar el bot de Telegram
    print("Iniciando bot desde server.py...")
    app = Report.build_app()
    app.run_polling()
