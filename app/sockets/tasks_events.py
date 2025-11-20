from flask_socketio import emit

from ..extensions import socketio


def notify_task_changed(task, event_type: str):
    payload = {
        "event": event_type,
        "task_id": task.id,
        "title": task.title,
        "status": task.status,
        "priority": task.priority,
    }
    socketio.emit("task_updated", payload)

