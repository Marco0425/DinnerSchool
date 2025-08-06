// Funcionalidad para el botón de cerrar sesión en el dashboard

document.addEventListener("DOMContentLoaded", function () {
  var logoutButton = document.getElementById("logoutButton");
  if (logoutButton) {
    logoutButton.addEventListener("click", function () {
      // Redirige al endpoint de logout
      window.location.href = "/core/logout/";
    });
  }
});
