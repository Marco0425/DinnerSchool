document.addEventListener("DOMContentLoaded", () => {
  const loginContainer = document.getElementById("loginContainer");
  const registerContainer = document.getElementById("registerContainer");

  const showRegisterFormLink = document.getElementById("showRegisterForm");
  const showLoginFormLink = document.getElementById("showLoginForm");

  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const messageDiv = document.getElementById("message");
  const formDescription = document.getElementById("form-description");

  /**
   * Oculta todos los contenedores de formularios.
   */
  function hideAllForms() {
    loginContainer.classList.add("hidden-form");
    registerContainer.classList.add("hidden-form");
    messageDiv.classList.add("hidden"); // Oculta mensajes al cambiar de formulario
  }

  /**
   * Muestra el formulario de inicio de sesión.
   */
  function showLoginForm() {
    hideAllForms();
    loginContainer.classList.remove("hidden-form");
    formDescription.textContent = "Inicia sesión para acceder a tu cuenta";
  }

  /**
   * Muestra el formulario de registro.
   */
  function showRegisterForm() {
    hideAllForms();
    registerForm.setAttribute("method", "post");
    registerForm.setAttribute("action", "/core/signInUp/");
    registerContainer.classList.remove("hidden-form");
    formDescription.textContent = "Crea tu cuenta para empezar";
  }

  // Inicialmente muestra el formulario de login
  showLoginForm();

  // Event listeners para cambiar entre formularios
  showRegisterFormLink.addEventListener("click", (event) => {
    event.preventDefault();
    showRegisterForm();
  });

  showLoginFormLink.addEventListener("click", (event) => {
    event.preventDefault();
    showLoginForm();
  });
});
