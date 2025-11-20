from flask import jsonify, request
from flask_login import login_required, current_user

from ...models import Task
from ...core.constants import TASK_STATUSES, PRIORITIES
from . import api_bp as bp


@bp.route("/", methods=["GET"])
@login_required
def list_tasks_api():
    status = request.args.get("status")
    priority = request.args.get("priority")

    query = Task.query
    if status and status != "all":
        query = query.filter(Task.status == status)
    if priority and priority != "all":
        query = query.filter(Task.priority == priority)

    tasks = query.order_by(Task.created_at.desc()).all()

    data = []
    for t in tasks:
        data.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "department": t.department,
            "assigned_to": t.assigned_to.full_name or t.assigned_to.username,
            "assigned_by": t.assigned_by.full_name or t.assigned_by.username,
            "created_at": t.created_at.isoformat(),
            "due_date": t.due_date.isoformat() if t.due_date else None,
        })

    return jsonify({
        "tasks": data,
        "filters": {
            "statuses": TASK_STATUSES,
            "priorities": PRIORITIES,
        },
        "current_user": {
            "id": current_user.id,
            "role": current_user.role,
        }
    })

@bp.route("/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    task = Task.query.get_or_404(task_id)

    comments = []
    for c in task.comments:
        comments.append({
            "id": c.id,
            "author": c.author.full_name or c.author.username,
            "text": c.text,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    logs = []
    for lg in task.logs:
        logs.append({
            "id": lg.id,
            "user": lg.user.full_name if lg.user else "—",
            "action": lg.action,
            "details": lg.details,
            "created_at": lg.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "department": task.department,
        "assigned_to": task.assigned_to_id,
        "assigned_by": task.assigned_by_id,
        "created_at": task.created_at.strftime("%Y-%m-%d %H:%M"),
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "comments": comments,
        "logs": logs,
    })
