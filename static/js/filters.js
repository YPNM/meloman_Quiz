document.addEventListener("DOMContentLoaded", function() {
    const menuButton = document.querySelector(".menu-button");
    const filtersContainer = document.querySelector(".filters");

    menuButton.addEventListener("click", function() {
        filtersContainer.classList.toggle("show-menu");
    });

    // Закрываем меню при клике вне меню
    document.addEventListener("click", function(event) {
        if (!filtersContainer.contains(event.target) && !menuButton.contains(event.target)) {
            filtersContainer.classList.remove("show-menu");
        }
    });

    var radioButtons = document.querySelectorAll("input[name='game-types']");

    radioButtons.forEach(function(radioButton) {
        radioButton.addEventListener("click", function() {
            var selectedGameType = this.value;
            var currentUrl = window.location.href;
            var updatedUrl = updateQueryStringParameter(currentUrl, "game-type", selectedGameType);
            window.location.href = updatedUrl;
            localStorage.setItem("selectedGameType", selectedGameType); // Сохраняем выбранное значение
        });
    });

    var selectedGameType = localStorage.getItem("selectedGameType");
    if (selectedGameType) {
        var radio = document.querySelector("input[name='game-types'][value='" + selectedGameType + "']");
        if (radio) {
            radio.checked = true;
        }
    }

    function updateQueryStringParameter(uri, key, value) {
        var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
        var separator = uri.indexOf("?") !== -1 ? "&" : "?";
        if (uri.match(re)) {
            return uri.replace(re, "$1" + key + "=" + value + "$2");
        }
        else {
            return uri + separator + key + "=" + value;
        }
    }
});
