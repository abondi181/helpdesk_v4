from datetime import datetime, date

from ..extensions import db
from ..core.constants import STATUS_NEW, PRIORITY_MEDIUM


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    department = db.Column(db.String(80), nullable=True)

    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    assigned_to = db.relationship(
        "User",
        foreign_keys=[assigned_to_id],
        back_populates="tasks_assigned",
    )
    assigned_by = db.relationship(
        "User",
        foreign_keys=[assigned_by_id],
        back_populates="tasks_created",
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(32), default=STATUS_NEW, nullable=False)
    priority = db.Column(db.String(32), default=PRIORITY_MEDIUM, nullable=False)

    comments = db.relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    logs = db.relationship("Log", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Task {self.id}: {self.title[:30]}>"
