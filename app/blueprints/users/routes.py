from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from werkzeug.security import generate_password_hash

from ...extensions import db
from ...models.user import User
from ...core.constants import ROLES, DEPARTMENTS

bp = Blueprint("users", __name__, url_prefix="/users")


# === Список пользователей ===

@bp.route("/")
@login_required
def list_users():
    users = User.query.order_by(User.id).all()

    # Руководители — это пользователи с ролью head_dept или head_ud
    managers = User.query.filter(User.role.in_(["head_dept", "head_ud", "admin"])).all()

    return render_template(
        "users/list.html",
        users=users,
        managers=managers,
        ROLES=ROLES,
        DEPARTMENTS=DEPARTMENTS,
    )


# === Создание пользователя ===

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_user():
    if request.method == "POST":
        username = request.form.get("username")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        department = request.form.get("department")
        manager_id = request.form.get("manager_id") or None

        if not username or not password:
            flash("Логин и пароль обязательны!", "danger")
            return redirect(url_for("users.create_user"))

        new_user = User(
            username=username,
            full_name=full_name,
            email=email,
            role=role,
            department=department,
            manager_id=manager_id,
            is_active_flag=True,
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Пользователь создан", "success")
        return redirect(url_for("users.list_users"))

    managers = User.query.all()

    return render_template(
        "users/create.html",
        managers=managers,
        ROLES=ROLES,
        DEPARTMENTS=DEPARTMENTS,
    )


# === Универсальное обновление одного поля AJAX ===

@bp.route("/<int:user_id>/update-field", methods=["POST"])
@login_required
def update_field(user_id):
    user = User.query.get_or_404(user_id)

    field = request.form.get("field")
    value = request.form.get("value")

    if field not in ("username", "full_name", "email",
                     "role", "department", "manager_id",
                     "is_active_flag"):
        return jsonify({"error": "invalid field"}), 400

    # Special cases
    if field == "is_active_flag":
        user.is_active_flag = value == "true"
    elif field == "manager_id":
        user.manager_id = int(value) if value not in ("", "null", None) else None
    else:
        setattr(user, field, value)

    db.session.commit()

    return jsonify({"status": "ok"})


# === API: список руководителей ===

@bp.route("/managers")
@login_required
def get_managers():
    managers = User.query.filter(User.role.in_(["head_dept", "head_ud", "admin"])).all()

    return jsonify([
        {
            "id": u.id,
            "name": u.full_name or u.username
        }
        for u in managers
    ])


# === Сброс пароля ===

@bp.route("/<int:user_id>/reset-password", methods=["POST"])
@login_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)

    new_pass = request.form.get("password", "123456")  # дефолт

    user.password_hash = generate_password_hash(new_pass)
    db.session.commit()

    return jsonify({"status": "ok", "new_password": new_pass})


# === Удаление пользователя ===

@bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"status": "ok"})
