from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from ...models import User, Log
from ...extensions import db
from ...core.constants import ROLES, ROLE_ADMIN
from . import bp
import secrets

@bp.before_request
def check_admin():
    # Только admin может видеть /users
    if not current_user.is_authenticated or current_user.role != ROLE_ADMIN:
        return redirect(url_for("tasks_views.list_tasks"))


@bp.route("/")
@login_required
def list_users():
    users = User.query.order_by(User.id.asc()).all()
    return render_template(
        "users/list.html",
        users=users,
        ROLES=ROLES,
        page_title="Пользователи",
        breadcrumb="Управление пользователями",
    )



@bp.route("/<int:user_id>/deactivate", methods=["POST"])
@login_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active_flag = False
    db.session.commit()
    flash("Пользователь деактивирован", "warning")
    return redirect(url_for("users.list_users"))


@bp.route("/<int:user_id>/update-field", methods=["POST"])
@login_required
def update_field(user_id):
    if current_user.role != ROLE_ADMIN:
        return {"error": "forbidden"}, 403

    user = User.query.get_or_404(user_id)

    field = request.form.get("field")
    value = request.form.get("value", "").strip()

    if field not in ("full_name", "role", "department", "is_active_flag"):
        return {"error": "invalid field"}, 400

    if field == "is_active_flag":
        user.is_active_flag = value == "1"
    else:
        setattr(user, field, value or None)

    db.session.commit()
    return {"status": "ok"}



@bp.route("/<int:user_id>/reset-password", methods=["POST"])
@login_required
def reset_password(user_id):
    if current_user.role != ROLE_ADMIN:
        return {"error": "forbidden"}, 403

    user = User.query.get_or_404(user_id)
    new_pass = secrets.token_hex(4)  # краткий, 8 символов
    user.set_password(new_pass)
    db.session.commit()

    return {"status": "ok", "password": new_pass}



@bp.route("/<int:user_id>/logs", methods=["GET"])
@login_required
def user_logs(user_id):
    if current_user.role != ROLE_ADMIN:
        return redirect(url_for("tasks_views.list_tasks"))

    user = User.query.get_or_404(user_id)
    logs = user.logs  # relation писали в модели Log ?

    return render_template(
        "users/logs.html",
        user=user,
        logs=logs,
        page_title=f"Логи пользователя {user.username}",
        breadcrumb=f"Логи {user.username}",
    )


@bp.route("/<int:user_id>/logs-panel")
@login_required
def user_logs_panel(user_id):
    if current_user.role != ROLE_ADMIN:
        return "forbidden", 403

    user = User.query.get_or_404(user_id)

    logs = (Log.query
            .filter_by(user_id=user.id)
            .order_by(Log.created_at.desc())
            .all())

    return render_template("users/logs_panel.html", user=user, logs=logs)
