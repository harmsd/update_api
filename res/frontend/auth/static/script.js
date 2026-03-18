document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const login = document.getElementById("login").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("http://localhost:8000/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    login: login,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                alert("Успешный вход");
            } else {
                alert(data.detail || "Ошибка авторизации");
            }

        } catch (error) {
            console.error("Ошибка запроса:", error);
            alert("Сервер недоступен");
        }
    });
});