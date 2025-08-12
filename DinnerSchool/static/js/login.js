document.addEventListener("DOMContentLoaded", () => {
  const loginContainer = document.getElementById("loginContainer");
  const registerContainer = document.getElementById("registerContainer");
  const showRegisterFormLink = document.getElementById("showRegisterForm");
  const showLoginFormLink = document.getElementById("showLoginForm");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const messageDiv = document.getElementById("message");
  const formDescription = document.getElementById("form-description");

  // Detectar si solo se debe mostrar el registro (modo staff)
  const onlyRegister =
    typeof window.onlyRegister !== "undefined"
      ? window.onlyRegister
      : document.getElementById("registerContainer") &&
        !document.getElementById("loginContainer");

  function hideAllForms() {
    if (loginContainer) loginContainer.classList.add("hidden-form");
    if (registerContainer) registerContainer.classList.add("hidden-form");
    if (messageDiv) messageDiv.classList.add("hidden");
  }

  function showLoginForm() {
    hideAllForms();
    if (loginContainer) loginContainer.classList.remove("hidden-form");
    if (formDescription)
      formDescription.textContent = "Inicia sesión para acceder a tu cuenta";
  }

  function showRegisterForm() {
    hideAllForms();
    if (registerForm) {
      registerForm.setAttribute("method", "post");
      registerForm.setAttribute("action", "/core/signInUp/");
    }
    if (registerContainer) registerContainer.classList.remove("hidden-form");
    if (formDescription)
      formDescription.textContent = "Crea tu cuenta para empezar";
  }

  if (onlyRegister) {
    // Solo mostrar el registro, ocultar login si existe
    if (loginContainer) loginContainer.classList.add("hidden-form");
    if (registerContainer) registerContainer.classList.remove("hidden-form");
    if (formDescription)
      formDescription.textContent = "Crea tu cuenta para empezar";
    // No agregar listeners para cambiar de formulario
    return;
  }

  // Inicialmente muestra el formulario de login
  showLoginForm();

  // Event listeners para cambiar entre formularios
  if (showRegisterFormLink) {
    showRegisterFormLink.addEventListener("click", (event) => {
      event.preventDefault();
      showRegisterForm();
    });
  }
  if (showLoginFormLink) {
    showLoginFormLink.addEventListener("click", (event) => {
      event.preventDefault();
      showLoginForm();
    });
  }
});
