async function fetchWithRefresh(url, options = {}) {
    let res = await fetch(url, { ...options, credentials: "include" });

    if (res.status === 401) {
        const refresh = await fetch("/jwt/refresh", {
            method: "POST",
            credentials: "include",
        });

        if (refresh.ok) {
            res = await fetch(url, { ...options, credentials: "include" });
        } else {
            window.location.href = "/login/";
            return;
        }
    }

    return res;
}