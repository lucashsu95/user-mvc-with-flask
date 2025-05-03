from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from models import User
from services.user_service import get_all_users, get_user_by_id, create_user, update_user, delete_user
from services.auth_service import authenticate_user
from werkzeug.security import check_password_hash

def index():
    users = get_all_users()
    displayUsers = [user.to_dict() for user in users]
    return render_template('index.html', users=displayUsers)

def create_user_page():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # 檢查所有必要欄位
        if not name or not email or not password:
            error = "所有欄位都是必填的"
            return render_template('create.html', error=error)
        
        # 檢查email是否已存在
        if User.query.filter_by(email=email).first():
            error = "此電子郵件已被註冊"
            return render_template('create.html', error=error)
        
        # 檢查密碼長度
        if len(password) < 8:
            error = "密碼長度必須至少8個字符"
            return render_template('create.html', error=error)
        
        # 建立新用戶
        create_user(name, email, password)
        return redirect(url_for('index'))
        
    return render_template('create.html')

@login_required
def edit_user_page(id):
    try:
        user = get_user_by_id(id)
        if not user:
            flash("用戶不存在")
            return redirect(url_for('index'))
        
        # 檢查當前用戶是否為要編輯的用戶
        if not current_user.is_authenticated or current_user.id != user.id:
            flash("您沒有權限編輯此用戶")
            return redirect(url_for('index'))
            
        # 檢查email是否已存在
        if User.query.filter_by(email=email).first():
            error = "此電子郵件已被註冊"
            return render_template('create.html', error=error)
            
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            
            if password and len(password) < 8:
                return render_template('edit.html', user=user, error="密碼長度必須至少8個字符")
            
            update_user(user, name, email, password if password else None)
            flash("用戶資料已更新")
            return redirect(url_for('index'))
            
        return render_template('edit.html', user=user)
    except Exception as e:
        flash(f"發生錯誤: {str(e)}")
        return redirect(url_for('index'))

@login_required
def delete_user_page(id):
    try:
        user = get_user_by_id(id)
        if not user:
            flash("用戶不存在")
            return redirect(url_for('index'))
        
        # 檢查當前用戶是否為要刪除的用戶
        if not current_user.is_authenticated or current_user.id != user.id:
            flash("您沒有權限刪除此用戶")
            return redirect(url_for('index'))
            
        delete_user(user)
        flash("用戶已刪除")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"發生錯誤: {str(e)}")
        return redirect(url_for('index'))

def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        # 檢查用戶是否存在
        if not user:
            return render_template('login.html', error="用戶不存在")
            
        # 檢查密碼是否正確
        is_correct = check_password_hash(user.passwordHash, password)
        
        if is_correct:
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error="帳號或密碼錯誤")
    return render_template('login.html')

@login_required
def logout_page():
    logout_user()
    return redirect(url_for('index'))