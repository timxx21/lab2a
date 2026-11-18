def render_main_page(parts, message="", min_price="", sort_field=""):
    rows = ""
    for p in parts:
        rows += f"""
        <tr>
            <td>{p['id']}</td>
            <td>{p['article']}</td>
            <td>{p['name']}</td>
            <td>{p['price']} ₽</td>
            <td>
                <a href="/view?id={p['id']}">Подробнее</a>
                <a href="/edit?id={p['id']}">Редактировать</a>
                 <a href="/delete?id={p['id']}" onclick="return confirm('Вы уверены, что хотите удалить {p['name']}?')" style="color: red;">Удалить</a>
            </td>
        </tr>
        """

    return f"""
    <html>
    <head><meta charset="utf-8"><title>Автозапчасти</title></head>
    <body>
        <h1>Список запчастей</h1>
        
        <form method="GET" action="/" style="margin-bottom: 20px; padding: 10px; background: #f0f0f0;">
            <label>Цена от: <input type="number" step="0.01" name="min_price" value="{min_price}"></label>
            
            <label>Сортировать по: 
                <select name="sort">
                    <option value="">Без сортировки</option>
                    <option value="article" {"selected" if sort_field == "article" else ""}>Артикулу</option>
                    <option value="price" {"selected" if sort_field == "price" else ""}>Цене</option>
                    <option value="name" {"selected" if sort_field == "name" else ""}>Названию</option>
                </select>
            </label>
            
            <button type="submit">Применить</button>
            <a href="/" style="margin-left: 10px;">Сбросить</a>
        </form>

        <a href="/add" style="display:inline-block; margin-bottom: 10px; padding: 5px 10px; border: 1px solid #ccc; text-decoration: none;">Добавить запись</a>
        
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
            <tr><th>ID</th><th>Артикул</th><th>Название</th><th>Цена</th><th>Действие</th></tr>
            {rows}
        </table>
         <script>
            const evtSource = new EventSource("/events");
            
            evtSource.onmessage = function(e) {{
                const data = JSON.parse(e.data);
                if (data.type === "data_changed") {{
                    console.log("БД изменилась! Обновляем страницу...");
                    window.location.reload(); 
                }}
            }};
            
            evtSource.onerror = function() {{
                console.error("Ошибка SSE. Переподключение...");
            }};
        </script>
    </body>
    </html>
    """


def render_view_page(part):
    return f"""
    <html>
    <head><meta charset="utf-8"><title>Просмотр</title></head>
    <body>
        <h1>Деталь: {part['name']}</h1>
        <p><b>Артикул:</b> {part['article']}</p>
        <p><b>Производитель:</b> {part['manufacturer']}</p>
        <p><b>Цена:</b> {part['price']} ₽</p>
        <p><b>Вес:</b> {part['weight']} кг</p>
        <p><b>Гарантия:</b> {part['warranty_months']} мес.</p>
        <a href="/">Назад</a>
    </body>
    </html>
    """

def render_form(part=None, error="", is_edit=False):
    """
    Универсальная форма (один класс окна).
    Если part=None, поля пустые (режим добавления).
    Если part передан, поля заполнены (режим редактирования).
    """
    error_html = f"<p style='color:red; font-weight:bold;'>{error}</p>" if error else ""

    # Определяем режим и action для формы
    action = "/edit" if is_edit else "/add"
    title = "Редактировать деталь" if is_edit else "Добавить новую деталь"
    button_text = "Обновить" if is_edit else "Сохранить"

    # Безопасно достаем значения (если part нет, будут пустые строки)
    def val(key):
        return part.get(key, '') if part else ''

    # Если это редактирование, нам нужен скрытый input с ID
    id_input = f'<input type="hidden" name="id" value="{val("id")}">' if is_edit else ''

    return f"""
    <html>
    <head><meta charset="utf-8"><title>{title}</title></head>
    <body>
        <h1>{title}</h1>
        {error_html}
        <form method="POST" action="{action}">
            {id_input}
            <p><label>Артикул: <input type="text" name="article" value="{val('article')}"></label></p>
            <p><label>Название: <input type="text" name="name" value="{val('name')}"></label></p>
            <p><label>Цена: <input type="number" step="0.01" name="price" value="{val('price')}"></label></p>
            <p><label>Производитель: <input type="text" name="manufacturer" value="{val('manufacturer')}"></label></p>
            <p><label>Вес: <input type="number" step="0.01" name="weight" value="{val('weight')}"></label></p>
            <p><label>Гарантия (мес): <input type="number" name="warranty_months" value="{val('warranty_months')}"></label></p>
            <button type="submit">{button_text}</button>
        </form>
        <br>
        <a href="/">Отмена</a>
    </body>
    </html>
    """

def render_redirect(url="/"):
    """Простой HTML для перенаправления браузера."""
    return f"""
    <html>
    <head><meta http-equiv="refresh" content="0; url={url}"></head>
    <body>Перенаправление...</body>
    </html>
    """
