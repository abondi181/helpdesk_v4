document.addEventListener("DOMContentLoaded", () => {
    // Мигание вкладки при событиях SocketIO
    if (window.io) {
        const socket = io();
        let originalTitle = document.title;
        let blinkInterval = null;

        socket.on("task_updated", (payload) => {
            if (!document.hasFocus()) {
                let visible = false;
                if (blinkInterval) clearInterval(blinkInterval);
                blinkInterval = setInterval(() => {
                    visible = !visible;
                    document.title = visible ? "⚡ Новое изменение задачи" : originalTitle;
                }, 1000);
                window.addEventListener("focus", () => {
                    clearInterval(blinkInterval);
                    document.title = originalTitle;
                }, { once: true });
            }
        });
    }
});
