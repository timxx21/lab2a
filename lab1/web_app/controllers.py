from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import queue
from urllib.parse import urlparse, parse_qs
from lab1.autopartsLab1.observer import event_bus

import json

import socket
# Отключаем системные ошибки разрыва соединения в Windows
socket.setdefaulttimeout(10.0)

# Импортируем наши репозитории и сущности
from lab1.autopartsLab1 import (
    DBConnection, PartRepDB, PartRepDBAdapter, Part, FilterSortDecorator, Refresher,
)
from . import views

class EventController:
    """Контроллер для Server-Sent Events (SSE)"""

    def handle_sse(self, handler):
        # 1. Заголовки для SSE
        handler.send_response(200)
        handler.send_header('Content-Type', 'text/event-stream')
        handler.send_header('Cache-Control', 'no-cache')
        handler.send_header('Connection', 'keep-alive')
        handler.end_headers()

        # 2. Подписываемся на шину
        q = event_bus.subscribe()
        try:
            while True:
                try:
                    event = q.get(timeout=10.0)
                    msg = f"data: {json.dumps({'type': event})}\n\n"
                    handler.wfile.write(msg.encode('utf-8'))
                    handler.wfile.flush()
                except queue.Empty:
                    try:
                        # Безопасный пинг
                        handler.wfile.write(b": keep-alive\n\n")
                        handler.wfile.flush()
                    except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                        break  # Браузер ушел, выходим
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass
        finally:
            event_bus.unsubscribe(q)

class AddController:
    """Контроллер для обработки операций добавления."""

    def __init__(self, db_rep):
        self._db_rep = db_rep

    def show_form(self, handler, error=""):
        # Явно указываем is_edit=False
        html = views.render_form(part=None, error=error, is_edit=False)
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
            # При ошибке тоже явно передаем is_edit=False
            html = views.render_form(part_data, error=str(e), is_edit=False)
            self._send_html(handler, html)

    def _send_html(self, handler, html, status=200):
        try:
            handler.send_response(status)
            handler.send_header('Content-type', 'text/html; charset=utf-8')
            handler.end_headers()
            handler.wfile.write(html.encode('utf-8'))
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            # Если браузер закрыл соединение, мы просто игнорируем это
            pass


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
            # Явно указываем is_edit=True
            html = views.render_form(part=part_dict, is_edit=True)
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
            # При ошибке тоже явно передаем is_edit=True
            html = views.render_form(part_dict, error=str(e), is_edit=True)
            self._send_html(handler, html)

    def _send_html(self, handler, html, status=200):
        try:
            handler.send_response(status)
            handler.send_header('Content-type', 'text/html; charset=utf-8')
            handler.end_headers()
            handler.wfile.write(html.encode('utf-8'))
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            # Если браузер закрыл соединение, мы просто игнорируем это
            pass

class DeleteController:
        """Контроллер для удаления записи (Пункт 5)."""

        def __init__(self, db_rep):
            self._db_rep = db_rep

        def handle_delete(self, handler, query):
            part_id = int(query.get('id', [0])[0])
            try:
                # Пытаемся удалить запись
                self._db_rep.delete(part_id)

                # Если успешно — делаем редирект на главную
                html = views.render_redirect("/")
                self._send_html(handler, html)

            except KeyError:
                handler.send_error(404, "Part not found")
            except Exception as e:
                handler.send_error(500, f"Ошибка при удалении: {e}")

        def _send_html(self, handler, html, status=200):
            try:
                handler.send_response(status)
                handler.send_header('Content-type', 'text/html; charset=utf-8')
                handler.end_headers()
                handler.wfile.write(html.encode('utf-8'))
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                # Если браузер закрыл вкладку или нажал "Стоп", просто игнорируем
                pass

class MainController(BaseHTTPRequestHandler):
    # Инициализируем репозиторий один раз при старте
    _conn = DBConnection(host="localhost", user="root", password="pass", database="autoparts")
    _db_rep = PartRepDBAdapter(PartRepDB(_conn))

    _add_ctrl = AddController(_db_rep)
    _edit_ctrl = EditController(_db_rep)
    _del_ctrl = DeleteController(_db_rep)
    _event_ctrl = EventController()
    _refresher = Refresher()

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (ConnectionAbortedError, ConnectionResetError):
            pass  # Игнорируем системные ошибки Windows при отключении клиента

    def do_GET(self):
        # Принудительно обновляем соединение с БД, чтобы сбросить кэш транзакции
        try:
            self._conn.connect().commit()
        except Exception:
            pass
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == '/':
            # Читаем параметры фильтрации из URL (если есть)
            min_price = query.get('min_price', [''])[0]
            min_id = query.get('min_id', [''])[0]
            max_id = query.get('max_id', [''])[0]
            min_article = query.get('min_article', [''])[0]
            max_article = query.get('max_article', [''])[0]
            sort_field = query.get('sort', [''])[0]

            # Базовый репозиторий (БД)
            active_rep = self._db_rep

            # Контроллер не знает, как фильтровать: он лишь описывает
            # диапазоны, а применяет их декоратор.
            ranges = {}
            if min_price:
                ranges['price'] = (min_price, None)
            if min_id or max_id:
                ranges['id'] = (min_id, max_id)

            # Лексикографический диапазон по артикулу (больше X — меньше Y)
            text_ranges = {}
            if min_article or max_article:
                text_ranges['article'] = (min_article, max_article)

            # Если применены фильтры — оборачиваем в Декоратор из ЛР2!
            if ranges or text_ranges or sort_field:
                active_rep = FilterSortDecorator(
                    wrapped=active_rep,
                    sort_key=sort_field if sort_field else None,
                    ranges=ranges,
                    text_ranges=text_ranges,
                )

            # Получаем данные (либо из БД напрямую, либо из Декоратора)
            count = active_rep.get_count()
            # Если фильтр ничего не оставил — не запрашиваем k=0 (нарушает контракт
            # get_k_n_short_list), а просто показываем пустую таблицу.
            dtos = active_rep.get_k_n_short_list(count, 1) if count > 0 else []

            # Рендерим страницу, передавая текущие значения для формы
            html = views.render_main_page(
                dtos, min_price=min_price, sort_field=sort_field,
                min_id=min_id, max_id=max_id,
                min_article=min_article, max_article=max_article,
            )
            self._send_html(html)

        elif path == '/view':
            # 1. Принудительно обновляем соединение с БД, чтобы сбросить кэш транзакции
            try:
                self._conn.connect().commit()  # сбрасываем транзакцию
            except Exception:
                pass  # если соединение упало, оно переподключится ниже

            # 2. Создаем новый репозиторий (или используем старый, но с свежим соединением)
            current_rep = PartRepDBAdapter(PartRepDB(self._conn))

            # 3. Используем Refresher для сброса старых проекций (если они были)
            self._refresher.purge()
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

        elif path == '/delete':
            self._del_ctrl.handle_delete(self, query)

        elif path == '/events':
            self._event_ctrl = EventController()
            self._event_ctrl.handle_sse(self)

        else:
            self.send_error(404, "Page not found")

    def do_POST(self):
        # Принудительно обновляем соединение с БД, чтобы сбросить кэш транзакции
        try:
            self._conn.connect().commit()
        except Exception:
            pass

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
        try:
            self.send_response(status)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass # Игнорируем разрыв соединения