from http.server import ThreadingHTTPServer

from lab1.autopartsLab1.observer import start_db_watcher
from lab1.web_app.controllers import MainController

def run_server():
    # Запускаем слушателя БД
    start_db_watcher()

    server_address = ('', 8000)
    httpd = ThreadingHTTPServer(server_address, MainController)
    print("Сервер запущен на http://localhost:8000")
    httpd.serve_forever()