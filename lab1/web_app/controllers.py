from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Импортируем наши репозитории и сущности
from lab1.autopartsLab1 import (
    DBConnection, PartRepDB, PartRepDBAdapter, Part
)
from . import views

class AddController:
    """Контроллер для обработки операций добавления."""

    def __init__(self, db_rep):
        self._db_rep = db_rep

    def show_form(self, handler, error=""):
        # Передаем part=None, так как это добавление
        html = views.render_form(part=None, error=error)
        self._send_html(handler, html)

    def handle_post(self, handler):
        content_length = int(handler.headers['Content-Length'])
        post_data = handler.rfile.read(content_length).decode('utf-8')
        form = parse_qs(post_data)

        try:
            new_part = Part(
                article=form.get('article', [''])[0],
                name=form.get('name', [''])[0],
                price=float(form.get('price', [0])[0]),
                manufacturer=form.get('manufacturer', [''])[0],
                weight=float(form.get('weight', [0])[0]),
                warranty_months=int(form.get('warranty_months', [0])[0])
            )
            self._db_rep.add(new_part)
            html = views.render_redirect("/")
            self._send_html(handler, html)

        except Exception as e:
            # При ошибке возвращаем форму с введенными данными
            part_data = {k: form.get(k, [''])[0] for k in
                         ['article', 'name', 'price', 'manufacturer', 'weight', 'warranty_months']}
            html = views.render_form(error=str(e))
            self._send_html(handler, html)

    def _send_html(self, handler, html, status=200):
        handler.send_response(status)
        handler.send_header('Content-type', 'text/html; charset=utf-8')
        handler.end_headers()
        handler.wfile.write(html.encode('utf-8'))


class EditController:
    """Отдельный контроллер для операций редактирования (MVC)"""

    def __init__(self, db_rep):
        self._db_rep = db_rep

    def show_form(self, handler, query):
        """Показ формы редактирования с заполненными данными."""
        part_id = int(query.get('id', [0])[0])
        try:
            part = self._db_rep.get_by_id(part_id)
            part_dict = {
                'id': part_id,
                'article': part.article,
                'name': part.name,
                'price': part.price,
                'manufacturer': part.manufacturer,
                'weight': part.weight,
                'warranty_months': part.warranty_months
            }
            # Передаем данные, форма заполнится
            html = views.render_form(part=part_dict)
            self._send_html(handler, html)
        except KeyError:
            handler.send_error(404, "Part not found")

    def handle_post(self, handler):
        """Обработка POST-запроса (сохранение изменений)."""
        content_length = int(handler.headers['Content-Length'])
        post_data = handler.rfile.read(content_length).decode('utf-8')
        form = parse_qs(post_data)

        part_id = int(form.get('id', [0])[0])

        try:
            # Валидация через класс Part
            updated_part = Part(
                article=form.get('article', [''])[0],
                name=form.get('name', [''])[0],
                price=float(form.get('price', [0])[0]),
                manufacturer=form.get('manufacturer', [''])[0],
                weight=float(form.get('weight', [0])[0]),
                warranty_months=int(form.get('warranty_months', [0])[0])
            )

            # Сохранение изменений в БД
            self._db_rep.update(part_id, updated_part)

            # Успех! Редирект на главную
            html = views.render_redirect("/")
            self._send_html(handler, html)

        except Exception as e:
            # Если ошибка валидации, показываем форму снова с ошибкой
            # Нам нужно передать обратно данные, чтобы они не стерлись
            part_dict = {
                'id': part_id,
                'article': form.get('article', [''])[0],
                'name': form.get('name', [''])[0],
                'price': form.get('price', [0])[0],
                'manufacturer': form.get('manufacturer', [''])[0],
                'weight': form.get('weight', [0])[0],
                'warranty_months': form.get('warranty_months', [0])[0]
            }
            html = views.render_form(part_dict, error=str(e))
            self._send_html(handler, html)

    def _send_html(self, handler, html, status=200):
        handler.send_response(status)
        handler.send_header('Content-type', 'text/html; charset=utf-8')
        handler.end_headers()
        handler.wfile.write(html.encode('utf-8'))

class MainController(BaseHTTPRequestHandler):
    # Инициализируем репозиторий один раз при старте
    _conn = DBConnection(host="localhost", user="root", password="pass", database="autoparts")
    _db_rep = PartRepDBAdapter(PartRepDB(_conn))

    _add_ctrl = AddController(_db_rep)
    _edit_ctrl = EditController(_db_rep)

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

        elif path == '/add':
            # Делегируем показ формы AddController-у
            self._add_ctrl.show_form(self)

        elif path == '/edit':
            # Делегируем контроллеру редактирования
            self._edit_ctrl.show_form(self, query)

        else:
            self.send_error(404, "Page not found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/add':
            # Делегируем обработку POST-запроса AddController-у
            self._add_ctrl.handle_post(self)

        elif path == '/edit':
            # Делегируем обработку формы редактирования
            self._edit_ctrl.handle_post(self)

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