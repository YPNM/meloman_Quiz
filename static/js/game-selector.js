function selectGame(game) {
    localStorage.setItem("selectedGame", game);
    localStorage.setItem("selectedTableType", "game"); // Добавляем это для сохранения состояния
    const currentUrl = window.location.href;
    window.location.href = updateQueryStringParameter(currentUrl, "selectedGame", game);
}

document.addEventListener("DOMContentLoaded", function() {
    const selectedGame = localStorage.getItem("selectedGame");
    const selectedTableType = localStorage.getItem("selectedTableType");

    if (selectedTableType === "game") {
        gameRadio.checked = true;
        gameTable.style.display = 'block';
        seasonTable.style.display = 'none';
        gameButton.style.display = 'inline-block';
    } else {
        seasonRadio.checked = true;
        gameTable.style.display = 'none';
        seasonTable.style.display = 'block';
        gameButton.style.display = 'none';
    }
    if (selectedGame) {
        // Используйте значение selectedGame на странице, например, для заголовка
        document.getElementById("game-selector").innerText = selectedGame;
    }
});

function updateQueryStringParameter(uri, key, value) {
    const re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
    const separator = uri.indexOf("?") !== -1 ? "&" : "?";
    if (uri.match(re)) {
        return uri.replace(re, "$1" + key + "=" + encodeURIComponent(value) + "$2");
    } else {
        return uri + separator + key + "=" + encodeURIComponent(value);
    }
}

function updateQueryStringParameters(uri, parameters) {
    const separator = uri.includes("?") ? "&" : "?"; // Проверка наличия параметров
    for (const [key, value] of Object.entries(parameters)) {
        uri = updateQueryStringParameter(uri, key, value);
    }
    return uri + separator + Object.keys(parameters).map(key => key + "=" + parameters[key]).join("&");
}
