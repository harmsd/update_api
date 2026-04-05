document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("login").value.trim();
        const password = document.getElementById("password").value.trim();

        if (!username || !password) {
            alert("Введите логин и пароль");
            return;
        }

        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        try {
            const response = await fetch("http://127.0.0.1:8000/jwt/login", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData,
                credentials: "include"
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Ошибка авторизации");
            }

            window.location.href = "/licenses";

        } catch (error) {
            console.error("Ошибка:", error);
            alert(error.message);
        }
    });
});