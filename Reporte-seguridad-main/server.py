import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import Report  # Importa tu archivo Report.py


# 1. Definir el servidor web ligero para responder pings de Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot de Telegram en marcha")


    # Silenciar logs del servidor HTTP en la consola para mantener limpia la pantalla
    def log_message(self, format, *args):
        return


def run_http_server():
    # Render asigna automáticamente un puerto dinámico en la variable de entorno PORT (por defecto 8080)
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Servidor HTTP iniciado en el puerto {port}")
    server.serve_forever()


if __name__ == '__main__':
    # 2. Iniciar el servidor web en un hilo secundario (background)
    threading.Thread(target=run_http_server, daemon=True).start()


    # 3. Iniciar tu chatbot de Telegram (ejecuta el bloque principal de Report.py)
    # Como Report.py ejecuta app.run_polling(), este hilo se mantendrá activo escuchando mensajes
