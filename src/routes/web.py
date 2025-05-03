from controllers.web_controllers import (
    index, create_user_page, edit_user_page, 
    delete_user_page, login_page, logout_page
)

def register_web_routes(app):
    # 網頁路由註冊
    app.add_url_rule('/', 'index', index)
    app.add_url_rule('/create', 'create_user', create_user_page, methods=['GET', 'POST'])
    app.add_url_rule('/edit/<int:id>', 'edit_user', edit_user_page, methods=['GET', 'POST'])
    app.add_url_rule('/delete/<int:id>', 'delete_user', delete_user_page)
    app.add_url_rule('/login', 'login', login_page, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', logout_page)