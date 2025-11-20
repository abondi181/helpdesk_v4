from .constants import ROLE_ADMIN, ROLE_HEAD_UD, ROLE_HEAD_DEPT, ROLE_EMPLOYEE


def is_admin(user):
    return user.role == ROLE_ADMIN


def is_head_ud(user):
    return user.role == ROLE_HEAD_UD


def is_head_dept(user):
    return user.role == ROLE_HEAD_DEPT


def is_employee(user):
    return user.role == ROLE_EMPLOYEE


# === 1. ПОЛНОЕ РЕДАКТИРОВАНИЕ (название, описание, исполнитель) ===
def can_edit_task(user, task):
    """Может ли редактировать содержание задачи."""
    if is_admin(user):
        return True

    # Начальник УД — редактирует только свои созданные
    if is_head_ud(user) and task.assigned_by == user.id:
        return True

    # Начальник отдела — только задачи своего отдела
    if is_head_dept(user) and task.department == user.department:
        return True

    # Сотрудник — не может редактировать задачу
    return False


# === 2. СТАТУС ===
def can_change_status(user, task):
    """Правила изменения статуса."""

    # Админ — может всё
    if is_admin(user):
        return True

    # Сотрудник — может менять СВОИ задачи, пока НЕ выполнена
    if is_employee(user):
        return task.assigned_to == user.id and task.status != "Выполнена"

    # Начальник УД — может менять статус любой выполненной задачи
    if is_head_ud(user):
        return task.status == "Выполнена"

    # Начальник отдела — выполненные задачи своего отдела
    if is_head_dept(user):
        return task.department == user.department and task.status == "Выполнена"

    return False


# === 3. ПРИОРИТЕТ ===
def can_change_priority(user, task):
    if is_admin(user):
        return True

    if is_head_ud(user):
        return True

    if is_head_dept(user) and task.department == user.department:
        return True

    # Сотрудник не может менять приоритет
    return False


# === 4. СРОКИ ===
def can_change_deadline(user, task):
    if is_admin(user):
        return True

    if is_head_ud(user):
        return True

    if is_head_dept(user) and task.department == user.department:
        return True

    # Сотрудник — нет
    return False
