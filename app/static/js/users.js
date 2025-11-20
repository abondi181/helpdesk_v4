document.addEventListener("DOMContentLoaded", () => {

    // TEXT INPUT + SELECT FIELDS
    document.querySelectorAll(".inline-input").forEach(el => {
        el.addEventListener("change", () => {
            const tr = el.closest("tr");
            const userId = tr.dataset.userId;
            const field = el.dataset.field;
            const value = el.value.trim();

            fetch(`/users/${userId}/update-field`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `field=${field}&value=${encodeURIComponent(value)}`
            }).then(r => r.json()).then(j => {
                if (j.status === "ok") flashInline(el);
            });
        });
    });

    // CHECKBOX (active)
    document.querySelectorAll(".inline-input-checkbox").forEach(ch => {
        ch.addEventListener("change", () => {
            const tr = ch.closest("tr");
            const userId = tr.dataset.userId;
            const field = ch.dataset.field;
            const value = ch.checked ? "1" : "0";

            fetch(`/users/${userId}/update-field`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `field=${field}&value=${value}`
            }).then(r => r.json()).then(j => {
                if (j.status === "ok") flashInline(ch);
            });
        });
    });

});

// Visual indicator “Saved ✓”
function flashInline(el) {
    el.style.outline = "2px solid #22c55e"; /* green */
    setTimeout(() => {
        el.style.outline = "none";
    }, 500);
}


function resetPassword(id) {
    if (!confirm("Сгенерировать новый пароль для пользователя?")) return;

    fetch(`/users/${id}/reset-password`, { method: "POST" })
        .then(r => r.json())
        .then(j => {
            alert("Новый пароль: " + j.password);
        });
}

function openUserLog(id) {
    window.location.href = `/users/${id}/logs`; // В следующем шаге — drawer
}


function openUserDrawer(id) {
    // открываем панель
    const drawer = document.getElementById("userDrawer");
    drawer.classList.remove("translate-x-full");

    // Загружаем контент AJAXом
    fetch(`/users/${id}/logs-panel`)
        .then(r => r.text())
        .then(html => {
            document.getElementById("userDrawerContent").innerHTML = html;
        });
}

function closeUserDrawer() {
    const drawer = document.getElementById("userDrawer");
    drawer.classList.add("translate-x-full");
}
