function openTaskModal(taskId = null) {
    const backdrop = document.getElementById("taskModalBackdrop");
    const form = document.getElementById("taskModalForm");
    const idInput = document.getElementById("taskModalId");
    const titleEl = document.getElementById("taskModalTitle");

    // Если открываем существующую задачу → подгружаем данные
    if (taskId) {
        form.action = `/tasks/${taskId}/update`;
        idInput.value = taskId;
        titleEl.textContent = `Задача #${taskId}`;

        // Загружаем данные
        fetch(`/api/tasks/${taskId}`)
            .then(r => r.json())
            .then(task => {
                // Основные поля
                document.getElementById("taskTitle").value = task.title;
                document.getElementById("taskDescription").value = task.description || "";
                document.getElementById("taskDepartment").value = task.department || "";
                document.getElementById("taskAssignedTo").value = task.assigned_to;
                document.getElementById("taskStatus").value = task.status;
                document.getElementById("taskPriority").value = task.priority;

                // Комментарии
                const commentsBlock = document.getElementById("taskComments");
                commentsBlock.innerHTML = "";
                if (task.comments.length === 0) {
                    commentsBlock.innerHTML = `<div class="text-slate-400 text-xs">Комментариев пока нет</div>`;
                } else {
                    task.comments.forEach(c => {
                        commentsBlock.innerHTML += `
                            <div class="border p-2 rounded-lg bg-slate-50">
                                <div class="text-xs text-slate-600">
                                    <b>${c.author}</b> — ${c.created_at}
                                </div>
                                <div class="text-sm mt-1">${c.text}</div>
                            </div>`;
                    });
                }

                // История изменений
                const logBlock = document.getElementById("taskLog");
                logBlock.innerHTML = "";
                if (task.logs.length === 0) {
                    logBlock.innerHTML = `<div class="text-slate-400 text-xs">История пока пуста</div>`;
                } else {
                    task.logs.forEach(l => {
                        logBlock.innerHTML += `
                            <div class="border p-2 rounded bg-white">
                                <div class="text-xs text-slate-500">${l.created_at}</div>
                                <div class="text-sm">
                                    <b>${l.user}:</b> ${l.action} — ${l.details}
                                </div>
                            </div>`;
                    });
                }
            });
    } else {
        // Создание новой задачи
        form.action = "/tasks/create";
        idInput.value = "";
        titleEl.textContent = "Новая задача";
        form.reset();

        // Чистим вкладки
        document.getElementById("taskComments").innerHTML =
            `<div class="text-slate-400 text-xs">Комментариев пока нет</div>`;
        document.getElementById("taskLog").innerHTML =
            `<div class="text-slate-400 text-xs">История появится после сохранения задачи</div>`;
    }

    // Переключение вкладок
    document.querySelectorAll(".tab-button").forEach((btn, idx) => {
        btn.classList.toggle("active", idx === 0);
    });
    document.querySelectorAll(".tab-panel").forEach((panel, idx) => {
        panel.classList.toggle("hidden", idx !== 0);
    });

    backdrop.classList.remove("hidden");
}


function closeTaskModal() {
    const backdrop = document.getElementById("taskModalBackdrop");
    backdrop.classList.add("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
    // Логика переключения вкладок в модалке
    document.querySelectorAll(".tab-button").forEach((btn) => {
        btn.addEventListener("click", () => {
            const tab = btn.dataset.tab;
            document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            document.querySelectorAll(".tab-panel").forEach(panel => {
                panel.classList.toggle("hidden", panel.dataset.tabPanel !== tab);
            });
        });
    });
});


// ДОБАВЛЕНИЕ КОММЕНТАРИЯ В МОДАЛЬНОМ ОКНЕ
function submitComment() {
    const taskId = document.getElementById("taskModalId").value;
    const text = document.getElementById("taskNewComment").value.trim();
    if (!taskId || !text) return;

    fetch(`/tasks/${taskId}/comment`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        },
        body: `comment=${encodeURIComponent(text)}`
    })
    .then(() => {

        // 1. Очищаем поле ввода
        document.getElementById("taskNewComment").value = "";

        // 2. Дозагружаем ТОЛЬКО комментарии
        return fetch(`/api/tasks/${taskId}`);
    })
    .then(r => r.json())
    .then(task => {
        const commentsBlock = document.getElementById("taskComments");

        // Перестраиваем комментарии заново
        commentsBlock.innerHTML = "";
        task.comments.forEach(c => {
            commentsBlock.innerHTML += `
                <div class="border p-2 rounded-lg bg-slate-50">
                    <div class="text-xs text-slate-600">
                        <b>${c.author}</b> — ${c.created_at}
                    </div>
                    <div class="text-sm mt-1">${c.text}</div>
                </div>`;
        });
    });
}

