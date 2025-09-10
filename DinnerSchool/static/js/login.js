document.addEventListener("DOMContentLoaded", () => {
  const loginContainer = document.getElementById("loginContainer");
  const registerContainer = document.getElementById("registerContainer");
  const resetContainer = document.getElementById("resetContainer");
  const showRegisterFormLink = document.getElementById("showRegisterForm");
  const showLoginFormLink = document.getElementById("showLoginForm");
  const showResetFormLink = document.getElementById("showResetForm");
  const showLoginFromResetLink = document.getElementById("showLoginFromReset");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const resetForm = document.getElementById("resetForm");
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
    if (resetContainer) resetContainer.classList.add("hidden-form");
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

  function showResetForm() {
    hideAllForms();
    if (resetContainer) resetContainer.classList.remove("hidden-form");
    if (formDescription)
      formDescription.textContent = "Resetea tu contraseña";
  }

  if (onlyRegister) {
    // Solo mostrar el registro, ocultar login si existe
    if (loginContainer) loginContainer.classList.add("hidden-form");
    if (resetContainer) resetContainer.classList.add("hidden-form");
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

  if (showResetFormLink) {
    showResetFormLink.addEventListener("click", (event) => {
      event.preventDefault();
      showResetForm();
    });
  }

  if (showLoginFromResetLink) {
    showLoginFromResetLink.addEventListener("click", (event) => {
      event.preventDefault();
      showLoginForm();
    });
  }

  // Manejar el envío del formulario de login
  if (loginForm) {
    loginForm.addEventListener("submit", (event) => {
      event.preventDefault();
      
      const formData = new FormData(loginForm);
      
      // Crear un formulario temporal para enviar por POST
      const tempForm = document.createElement('form');
      tempForm.method = 'POST';
      tempForm.action = '/core/signInUp/';
      
      // Agregar CSRF token
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = csrfToken;
      tempForm.appendChild(csrfInput);
      
      // Agregar campos del login
      const usernameInput = document.createElement('input');
      usernameInput.type = 'hidden';
      usernameInput.name = 'username';
      usernameInput.value = document.getElementById('loginUsername').value;
      tempForm.appendChild(usernameInput);
      
      const passwordInput = document.createElement('input');
      passwordInput.type = 'hidden';
      passwordInput.name = 'password';
      passwordInput.value = document.getElementById('loginPassword').value;
      tempForm.appendChild(passwordInput);
      
      document.body.appendChild(tempForm);
      tempForm.submit();
    });
  }

  // Manejar el envío del formulario de reset de contraseña
  if (resetForm) {
    resetForm.addEventListener("submit", (event) => {
      event.preventDefault();
      
      const formData = new FormData(resetForm);
      
      // Mostrar mensaje de carga
      if (messageDiv) {
        messageDiv.classList.remove("hidden");
        messageDiv.className = "mt-6 p-3 text-sm text-center rounded-md bg-blue-100 text-blue-800 border border-blue-200";
        messageDiv.textContent = "Procesando solicitud...";
      }

      fetch('/core/reset-password/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
      })
      .then(response => response.json())
      .then(data => {
        if (messageDiv) {
          messageDiv.classList.remove("hidden");
          if (data.success) {
            messageDiv.className = "mt-6 p-3 text-sm text-center rounded-md bg-green-100 text-green-800 border border-green-200";
            messageDiv.innerHTML = `
              <div class="font-medium mb-2">¡Contraseña reseteada exitosamente!</div>
              <div class="text-xs">Tu nueva contraseña temporal es:</div>
              <div class="font-mono bg-white p-2 mt-2 rounded border text-lg">${data.temp_password}</div>
              <div class="text-xs mt-2">Por favor, copia esta contraseña y cámbiala en tus ajustes de cuenta después de iniciar sesión.</div>
            `;
            resetForm.reset();
            
            // Volver al login después de 8 segundos
            setTimeout(() => {
              showLoginForm();
            }, 8000);
          } else {
            messageDiv.className = "mt-6 p-3 text-sm text-center rounded-md bg-red-100 text-red-800 border border-red-200";
            messageDiv.textContent = data.message || "Error al procesar la solicitud.";
          }
        }
      })
      .catch(error => {
        console.error('Error:', error);
        if (messageDiv) {
          messageDiv.classList.remove("hidden");
          messageDiv.className = "mt-6 p-3 text-sm text-center rounded-md bg-red-100 text-red-800 border border-red-200";
          messageDiv.textContent = "Error de conexión. Inténtalo de nuevo.";
        }
      });
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
