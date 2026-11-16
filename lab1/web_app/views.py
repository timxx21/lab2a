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

