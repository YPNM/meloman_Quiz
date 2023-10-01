document.addEventListener("DOMContentLoaded", function() {
  console.log("DOMContentLoaded event fired");
  var selectedCity = localStorage.getItem("selectedCity");

  if (!selectedCity) {
    var cityModal = new bootstrap.Modal(document.getElementById("cityModal"));
    cityModal.show();
  } else if (!window.location.search.includes("selectedCity=")) {
    var currentPage = document.getElementById("currentPage").value;
    var queryString = "?selectedCity=" + encodeURIComponent(selectedCity);
    window.location.href = currentPage + queryString;
  }
});

function selectCity(city) {
  var currentPage = document.getElementById("currentPage").value;
  localStorage.setItem("selectedCity", city);
  localStorage.removeItem("selectedGame")

  var cityModal = bootstrap.Modal.getInstance(document.getElementById("cityModal"));
  cityModal.hide();

  window.location.href = currentPage + "?selectedCity=" + encodeURIComponent(city);
}

document.addEventListener("DOMContentLoaded", function() {
  var selectedCity = localStorage.getItem("selectedCity");
  if (selectedCity) {
    document.getElementById("cityHeader").innerText = selectedCity;
  }
});
