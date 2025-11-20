from io import BytesIO
from datetime import datetime

from flask import send_file
from flask_login import login_required

from openpyxl import Workbook

from ...models import Task
from . import exports_bp as bp


@bp.route("/export/xlsx", methods=["GET"])
@login_required
def export_tasks_xlsx():
    wb = Workbook()
    ws = wb.active
    ws.title = "Задачи"

    headers = [
        "ID", "Название", "Описание", "Статус", "Приоритет",
        "Отдел", "Исполнитель", "Постановщик", "Создана", "Срок"
    ]
    ws.append(headers)

    for task in Task.query.order_by(Task.created_at.desc()).all():
        ws.append([
            task.id,
            task.title,
            task.description or "",
            task.status,
            task.priority,
            task.department or "",
            task.assigned_to.full_name or task.assigned_to.username,
            task.assigned_by.full_name or task.assigned_by.username,
            task.created_at.strftime("%Y-%m-%d %H:%M"),
            task.due_date.strftime("%Y-%m-%d") if task.due_date else "",
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return send_file(
        stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
