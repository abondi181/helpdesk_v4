from .constants import ROLE_ADMIN, ROLE_HEAD_UD, ROLE_HEAD_DEPT, ROLE_EMPLOYEE


# МАШИНА СОСТОЯНИЙ ЗАДАЧИ
ALLOWED_TRANSITIONS = {
    "Новая": ["В работе"],
    "В работе": ["Выполнена", "Отложена"],
    "Отложена": ["В работе"],
    "Выполнена": ["Закрыта"],
    "Закрыта": [],
}



def is_admin(user):
    return user.role == ROLE_ADMIN


def is_head_ud(user):
    return user.role == ROLE_HEAD_UD


def is_head_dept(user):
    return user.role == ROLE_HEAD_DEPT


def is_employee(user):
    return user.role == ROLE_EMPLOYEE


# === 0. СОЗДАНИЕ ЗАДАЧ ===
def can_create_task(user) -> bool:
    """
    Кто может создавать задачи.
    Сейчас: любой авторизованный пользователь.
    Хочешь – потом ужесточим.
    """
    return True


# === 1. ПОЛНОЕ РЕДАКТИРОВАНИЕ ЗАДАЧИ (название, описание, исполнитель и т.п.) ===
def can_edit_task(user, task) -> bool:
    """Может ли пользователь редактировать основные поля задачи."""
    if is_admin(user):
        return True

    # Начальник УД — редактирует только свои созданные задачи
    if is_head_ud(user) and task.assigned_by == user.id:
        return True

    # Начальник отдела — задачи своего отдела
    if is_head_dept(user) and task.department == user.department:
        return True

    # Сотрудник — не редактирует основные поля
    return False


# === 2. СТАТУС ===
def can_change_status(user, task, new_status=None) -> bool:
    """
    Правила изменения статуса:

    Общие:
    - Запрещены переходы, не указанные в ALLOWED_TRANSITIONS (кроме админа).

    Роли:
    - Админ — любые переходы.
    - Сотрудник — только свои задачи, только вперёд (по ALLOWED_TRANSITIONS), до "Выполнена".
    - Начальник УД — может менять статус только выполненных задач.
    - Начальник отдела — только выполненные задачи своего отдела.
    """

    old_status = task.status

    # 1. Админ может всё
    if is_admin(user):
        return True

    # 2. Проверяем допустимость перехода по state-machine (если новый статус нам передали)
    if new_status is not None:
        allowed = ALLOWED_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            return False

    # 3. Сотрудник
    if is_employee(user):
        # Только свои задачи
        if task.assigned_to_id != user.id:
            return False
        # После "Выполнена" менять не может
        if old_status == "Выполнена":
            return False
        # Остальное уже проверено через ALLOWED_TRANSITIONS
        return True

    # 4. Начальник УД — только выполненные задачи
    if is_head_ud(user):
        return old_status == "Выполнена"

    # 5. Начальник отдела — выполненные задачи своего отдела
    if is_head_dept(user):
        return task.department == user.department and old_status == "Выполнена"

    return False




# === 3. ПРИОРИТЕТ ===
def can_change_priority(user, task) -> bool:
    """Изменение приоритета задачи."""
    if is_admin(user):
        return True

    # Начальник УД — любой приоритет
    if is_head_ud(user):
        return True

    # Начальник отдела — приоритет задач своего отдела
    if is_head_dept(user) and task.department == user.department:
        return True

    # Сотрудник — не меняет приоритет
    return False


# === 4. СРОКИ ===

def can_change_deadline(user, task, new_status=None) -> bool:
    """Изменение срока исполнения задачи."""
    # Админ — всегда может
    if is_admin(user):
        return True

    # Начальник УД — любые задачи
    if is_head_ud(user):
        return True

    # Начальник отдела — задачи своего отдела
    if is_head_dept(user) and task.department == user.department:
        return True

    # Сотрудник — только для своих задач И только при переходе в 'Отложена'
    if is_employee(user):
        if task.assigned_to_id != user.id:
            return False
        # если явно указано, что новый статус = "Отложена" — разрешаем
        if new_status == "Отложена":
            return True
        # во всех остальных случаях менять срок нельзя
        return False

    return False

def can_view_task(user, task):
    if is_admin(user):
        return True
    if is_head_ud(user):
        return True

    # руководитель отдела видит задачи подчинённых
    if is_head_dept(user):
        if task.assigned_to.manager_id == user.id:
            return True
        if task.assigned_to_id == user.id:
            return True
        return False

    # сотрудник — только свои
    return task.assigned_to_id == user.id
