document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.querySelector(".search-input");
    const teams = document.querySelectorAll(".team-row"); // Добавьте класс "team-row" к строкам таблицы с командами

    searchInput.addEventListener("input", function() {
        const searchTerm = searchInput.value.toLowerCase().trim();

        teams.forEach(function(team) {
            const teamName = team.querySelector(".team-name").textContent.toLowerCase();
            if (teamName.includes(searchTerm)) {
                team.style.display = "table-row";
            } else {
                team.style.display = "none";
            }
        });
    });
});
