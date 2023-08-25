document.addEventListener("DOMContentLoaded", function() {
    if (!localStorage.getItem("selectedCity")) {
      var cityModal = new bootstrap.Modal(document.getElementById("cityModal"));
      cityModal.show();
    }
  });
  
  function selectCity(city) {
    localStorage.setItem("selectedCity", city);
    var cityModal = bootstrap.Modal.getInstance(document.getElementById("cityModal"));
    cityModal.hide();
    location.reload();
  }

  function getCity() {
    if (localStorage.getItem("selectedCity")) {
        var cityShow = n
    }
  }
  
  document.addEventListener("DOMContentLoaded", function() {
    var selectedCity = localStorage.getItem("selectedCity");
    if (selectedCity) {
      // Используйте значение selectedCity на странице, например, для заголовка
      document.getElementById("cityHeader").innerText = selectedCity;
    }
  });
  