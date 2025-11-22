from datetime import date, datetime

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ...extensions import db
from ...models import Task, Comment, Log, User
from ...core.constants import PRIORITIES, TASK_STATUSES
from ...core.permissions import can_create_task, can_edit_task, can_change_status, can_change_priority, can_change_deadline
from ...sockets import notify_task_changed
from . import views_bp as bp




@bp.route("/", methods=["GET"])
@login_required
def list_tasks():
    status_filter = request.args.get("status")
    priority_filter = request.args.get("priority")

    query = Task.query

    if status_filter and status_filter != "all":
        query = query.filter(Task.status == status_filter)
    if priority_filter and priority_filter != "all":
        query = query.filter(Task.priority == priority_filter)

    tasks = query.order_by(Task.created_at.desc()).all()

    users = User.query.order_by(User.full_name.asc()).all()

    return render_template(
        "tasks/list.html",
        page_title="Все задачи",
        breadcrumb="Список задач",
        tasks=tasks,
        users=users,
        PRIORITIES=PRIORITIES,
        TASK_STATUSES=TASK_STATUSES,
        status_filter=status_filter or "all",
        priority_filter=priority_filter or "all",
        can_create=can_create_task(current_user),
        current_date=date.today(),
        today=date.today(),
        
    )


@bp.route("/create", methods=["POST"])
@login_required
def create_task():
    if not can_create_task(current_user):
        flash("У вас нет прав для создания задач", "danger")
        return redirect(url_for("tasks_views.list_tasks"))

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    department = request.form.get("department") or None
    assigned_to_id = request.form.get("assigned_to")

    if not title or not assigned_to_id:
        flash("Название и исполнитель обязательны", "danger")
        return redirect(url_for("tasks_views.list_tasks"))

    task = Task(
        title=title,
        description=description,
        department=department,
        assigned_to_id=int(assigned_to_id),
        assigned_by_id=current_user.id,
    )
    db.session.add(task)
    db.session.commit()

    log = Log(task_id=task.id, user_id=current_user.id, action="create", details=f"Создана задача '{title}'")
    db.session.add(log)
    db.session.commit()

    notify_task_changed(task, "created")

    flash("Задача создана", "success")
    return redirect(url_for("tasks_views.list_tasks"))


@bp.route("/<int:task_id>/update", methods=["POST"])
@login_required
def update_task(task_id: int):
    task = Task.query.get_or_404(task_id)

    old_status = task.status
    old_priority = task.priority
    old_assigned_to = task.assigned_to_id
    old_due_date = task.due_date

    # --- Основные поля (если есть права на редактирование) ---
    if can_edit_task(current_user, task):
        task.title = request.form.get("title", "").strip() or task.title
        task.description = request.form.get("description", "").strip()
        task.department = request.form.get("department") or None

    # --- Новые значения из формы ---
    new_status = request.form.get("status") or task.status
    new_priority = request.form.get("priority") or task.priority
    new_assigned_to = request.form.get("assigned_to") or task.assigned_to_id
    new_due_date_raw = request.form.get("due_date") or ""

    # Парсим дату, если указана
    new_due_date = old_due_date
    if new_due_date_raw:
        try:
            new_due_date = datetime.strptime(new_due_date_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Некорректная дата", "danger")
            return redirect(url_for("tasks_views.list_tasks"))

    logs_to_add = []

    # --- Статус ---
    if new_status != old_status:
        # Проверяем права + допустимость перехода
        if not can_change_status(current_user, task, new_status):
            flash("Недопустимый переход статуса", "danger")
            return redirect(url_for("tasks_views.list_tasks"))

        # Доп. правило для "Отложена": дата обязательна
        if new_status == "Отложена" and not new_due_date_raw:
            flash("При выборе статуса 'Отложена' необходимо указать дату", "danger")
            return redirect(url_for("tasks_views.list_tasks"))

        task.status = new_status
        logs_to_add.append(
            Log(
                task_id=task.id,
                user_id=current_user.id,
                action="status",
                details=f"{old_status} → {new_status}",
            )
        )

    # --- Приоритет ---
    if new_priority != old_priority and can_change_priority(current_user, task):
        task.priority = new_priority
        logs_to_add.append(
            Log(
                task_id=task.id,
                user_id=current_user.id,
                action="priority",
                details=f"{old_priority} → {new_priority}",
            )
        )

    # --- Исполнитель ---
    new_assigned_to_id = int(new_assigned_to)
    if new_assigned_to_id != old_assigned_to:
        task.assigned_to_id = new_assigned_to_id
        logs_to_add.append(
            Log(
                task_id=task.id,
                user_id=current_user.id,
                action="delegate",
                details=f"Передано пользователю ID={new_assigned_to_id}",
            )
        )

   # --- Дата (срок) ---
    if new_due_date != old_due_date and can_change_deadline(current_user, task, new_status):
        task.due_date = new_due_date
        logs_to_add.append(
            Log(
                task_id=task.id,
                user_id=current_user.id,
                action="deadline",
                details=f"{old_due_date} → {new_due_date}",
            )
        )

    if logs_to_add:
        db.session.add_all(logs_to_add)
    db.session.commit()

    notify_task_changed(task, "updated")

    flash("Задача обновлена", "success")
    return redirect(url_for("tasks_views.list_tasks"))




@bp.route("/<int:task_id>/comment", methods=["POST"])
@login_required
def add_comment(task_id: int):
    task = Task.query.get_or_404(task_id)

    text = request.form.get("comment", "").strip()
    if not text:
        flash("Комментарий не может быть пустым", "danger")
        return redirect(url_for("tasks_views.list_tasks"))

    comment = Comment(task_id=task.id, author_id=current_user.id, text=text)
    db.session.add(comment)
    db.session.add(Log(task_id=task.id, user_id=current_user.id,
                       action="comment", details=text[:200]))
    db.session.commit()

    flash("Комментарий добавлен", "success")
    return redirect(url_for("tasks_views.list_tasks"))

