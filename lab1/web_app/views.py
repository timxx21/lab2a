def render_main_page(parts, message=""):
    rows = ""
    for p in parts:
        rows += f"""
        <tr>
            <td>{p['id']}</td>
            <td>{p['article']}</td>
            <td>{p['name']}</td>
            <td>{p['price']} ₽</td>
            <td><a href="/view?id={p['id']}">Подробнее</a></td>
        </tr>
        """

    return f"""
    <html>
    <head><meta charset="utf-8"><title>Автозапчасти</title></head>
    <body>
        <h1>Список запчастей</h1>
        <p>{message}</p>
        <a href="/add" style="display:inline-block; margin-bottom: 10px; padding: 5px 10px; border: 1px solid #ccc; text-decoration: none;">Добавить запись</a>
        <table border="1">
            <tr><th>ID</th><th>Артикул</th><th>Название</th><th>Цена</th><th>Действие</th></tr>
            {rows}
        </table>
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

def render_add_form(error=""):
    """Форма добавления новой детали с выводом ошибок валидации."""
    error_html = f"<p style='color:red; font-weight:bold;'>{error}</p>" if error else ""
    return f"""
    <html>
    <head><meta charset="utf-8"><title>Добавление детали</title></head>
    <body>
        <h1>Добавить новую деталь</h1>
        {error_html}
        <form method="POST" action="/add">
            <p><label>Артикул: <input type="text" name="article"></label></p>
            <p><label>Название: <input type="text" name="name"></label></p>
            <p><label>Цена: <input type="number" step="0.01" name="price"></label></p>
            <p><label>Производитель: <input type="text" name="manufacturer"></label></p>
            <p><label>Вес: <input type="number" step="0.01" name="weight"></label></p>
            <p><label>Гарантия (мес): <input type="number" name="warranty_months"></label></p>
            <button type="submit">Сохранить</button>
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
