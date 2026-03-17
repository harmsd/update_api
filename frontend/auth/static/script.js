form.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        const response = await fetch("http://127.0.0.1:8000/login", {
            method: "GET",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });


        if (!response.ok) {
            "Ошибка входа";
            return;
        }

        localStorage.setItem("access_token", data.access_token);
        message.textContent = "Вход выполнен успешно";

    } catch (error) {
        message.textContent = "Ошибка соединения с сервером";
    }
});