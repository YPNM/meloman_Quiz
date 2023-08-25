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
});
