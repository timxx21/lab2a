from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Импортируем наши репозитории и сущности
from lab1.autopartsLab1 import (
    DBConnection, PartRepDB, PartRepDBAdapter, Part
)
from . import views


class MainController(BaseHTTPRequestHandler):
    # Инициализируем репозиторий один раз при старте
    _conn = DBConnection(host="localhost", user="root", password="pass", database="autoparts")
    _db_rep = PartRepDBAdapter(PartRepDB(_conn))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == '/':
            # Чтение списка (Read)
            count = self._db_rep.get_count()
            dtos = self._db_rep.get_k_n_short_list(count, 1)
            html = views.render_main_page(dtos)
            self._send_html(html)

        elif path == '/view':
            # Просмотр полной информации
            part_id = int(query.get('id', [0])[0])
            try:
                part = self._db_rep.get_by_id(part_id)
                # Собираем словарь из атрибутов объекта Part
                part_dict = {
                    'id': part_id,
                    'article': part.article,
                    'name': part.name,
                    'price': part.price,
                    'manufacturer': part.manufacturer,
                    'weight': part.weight,
                    'warranty_months': part.warranty_months
                }
                html = views.render_view_page(part_dict)
                self._send_html(html)
            except KeyError:
                self.send_error(404, "Part not found")
        else:
            self.send_error(404, "Page not found")

    def _send_html(self, html, status=200):
        """Вспомогательный метод для отправки HTML в браузер"""
        self.send_response(status)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MainController)
    print("Сервер запущен на http://localhost:8000")
    httpd.serve_forever()