from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from ...core.constants import ROLE_EMPLOYEE

from ...extensions import db
from ...models import User
from . import bp

############# LOGIN ###################
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("tasks_views.list_tasks"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Успешный вход", "success")
            return redirect(url_for("tasks_views.list_tasks"))
        else:
            flash("Неверное имя пользователя или пароль", "danger")

    return render_template("auth/login.html")

############# LOGOUT ######################
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

############# РЕГИСТРАЦИЯ НОВЫХ СОТРУДНИКОВ ###############
@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("tasks_views.list_tasks"))

    if request.method == "POST":
        username = request.form.get("email").strip().lower()
        full_name = request.form.get("full_name").strip()
        password = request.form.get("password").strip()
        password2 = request.form.get("password2").strip()

        if not username or not password:
            flash("Email и пароль обязательны", "danger")
            return redirect(url_for("auth.register"))

        if password != password2:
            flash("Пароли не совпадают", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("Пользователь с таким email уже существует", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            username=username,
            full_name=full_name,
            role=ROLE_EMPLOYEE,
            department=None,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Регистрация завершена. Теперь вы можете войти.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")