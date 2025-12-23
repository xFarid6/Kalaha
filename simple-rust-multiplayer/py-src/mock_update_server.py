from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import zipfile

PORT = 8000

class MockUpdateHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/version.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = {
                "version": "1.1.0",
                "url": f"http://127.0.0.1:{PORT}/update.zip"
            }
            self.wfile.write(json.dumps(data).encode())
        else:
            super().do_GET()

def create_mock_zip():
    # Crea un file zip con una versione fittizia "aggiornata" di constants.py
    with zipfile.ZipFile('update.zip', 'w') as z:
        # Nota: In un caso reale qui ci sarebbero tutti i file necessari
        z.writestr('constants.py', 'CURRENT_VERSION = "1.1.0"\nWINDOW_SIZE = (800, 600)\nTICK_RATE = 60\nUPDATE_URL = "http://127.0.0.1:8000/version.json"\n')

if __name__ == "__main__":
    create_mock_zip()
    print(f"Mock Update Server in ascolto su porta {PORT}")
    print("Servendo version.json e update.zip...")
    httpd = HTTPServer(('127.0.0.1', PORT), MockUpdateHandler)
    httpd.serve_forever()
