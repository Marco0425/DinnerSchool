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

// Función para alternar la visibilidad de la contraseña (fuera del DOMContentLoaded)
function togglePasswordVisibility(inputId, button) {
  const passwordInput = document.getElementById(inputId);
  const eyeIcon = button.querySelector('svg');
  
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    // Cambiar a icono de ojo cerrado
    eyeIcon.innerHTML = `
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
    `;
  } else {
    passwordInput.type = 'password';
    // Cambiar a icono de ojo abierto
    eyeIcon.innerHTML = `
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    `;
  }
}
