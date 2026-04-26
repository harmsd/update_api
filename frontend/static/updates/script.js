document.getElementById("logout-btn").addEventListener("click", async () => {
    const response = await fetch("/login/logout", {
        method: "POST",
        credentials: "include"
    });

    if (response.redirected) {
        window.location.href = response.url;
    } else {
        window.location.href = "/login/";
    }
});