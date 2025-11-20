from flask import Blueprint

# HTML-views
views_bp = Blueprint("tasks_views", __name__, url_prefix="/tasks")
# JSON API
api_bp = Blueprint("tasks_api", __name__, url_prefix="/api/tasks")
# Экспорты
exports_bp = Blueprint("tasks_exports", __name__, url_prefix="/tasks")

from . import views, api, exports  # noqa
