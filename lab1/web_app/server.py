from http.server import HTTPServer

from lab1.web_app.controllers import MainController

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MainController)
    print("Сервер запущен на http://localhost:8000")
    httpd.serve_forever()