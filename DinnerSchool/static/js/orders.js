document.addEventListener("DOMContentLoaded", function () {
  // Inicializar Select2 para el select de platillos
  if (window.jQuery && $('#platillo').length) {
    $('#platillo').select2({
      width: '100%',
      placeholder: 'Selecciona el Platillo',
      allowClear: true,
      language: {
        noResults: function() {
          return 'No hay resultados';
        }
      }
    });
  }

  // Inicializar Select2 para el select de alumno
  if (window.jQuery && $('#alumno').length) {
    $('#alumno').select2({
      width: '100%',
      placeholder: 'Selecciona un alumno',
      allowClear: true,
      language: {
        noResults: function() {
          return 'No hay resultados';
        }
      }
    });
  }

  // Inicializar Select2 para el select de alumno_tutor
  if (window.jQuery && $('#alumno_tutor').length) {
    $('#alumno_tutor').select2({
      width: '100%',
      placeholder: 'Selecciona un alumno',
      allowClear: true,
      language: {
        noResults: function() {
          return 'No hay resultados';
        }
      }
    });
  }

  // Inicializar búsqueda personalizada para tutores (adaptada de credit.js)
  initializeTutorSearch();

  const ingredientesDisplay = document.getElementById("ingredientes-display");
  const ordersForm = document.getElementById("ordersForm");

  // Mostrar ingredientes cuando se selecciona un platillo
  if (window.jQuery && $('#platillo').length) {
    $('#platillo').on('select2:select select2:clear change', function () {
      const selectedOption = this.options[this.selectedIndex];
      if (selectedOption && selectedOption.value) {
        const ingredientesTexto = selectedOption.getAttribute("data-ingredientes");
        let ingredientesArray = JSON.parse(ingredientesTexto);
        var ingredientes = ingredientesArray.join(", ").toLowerCase();
        ingredientesDisplay.value = ingredientes || "No hay ingredientes especificados";
      } else {
        ingredientesDisplay.value = "";
      }
    });
  }

  // Lógica de carrito (agregar/quitar/mostrar/limpiar) compartida con directSale.js
  const cartCtl = CartCommon.create();
  const submitOrderBtn = document.getElementById("submitOrder");

  // Enviar orden
  submitOrderBtn.addEventListener("click", function () {
    // form.submit() no dispara 'submit', hay que evitar el doble clic a mano.
    if (submitOrderBtn.disabled) return;

    const cart = cartCtl.getCart();
    if (cart.length === 0) {
      cartCtl.showMessage("El carrito está vacío", "error");
      return;
    }

    // Validar información del pedido
    const alumnoSelect =
      document.getElementById("alumno_tutor") ||
      document.getElementById("alumno");
    const tutorSelect = document.getElementById("tutor");

    if (alumnoSelect && !alumnoSelect.value && !tutorSelect.value.includes("Profesor_")) {
      cartCtl.showMessage("Por favor selecciona un alumno", "error");
      return;
    }

    if (
      tutorSelect &&
      tutorSelect.value &&
      alumnoSelect &&
      !alumnoSelect.value &&
      !tutorSelect.value.includes("Profesor_")
    ) {
      cartCtl.showMessage("Si seleccionas un tutor, debes seleccionar un alumno", "error");
      return;
    }

    // Preparar datos para envío
    document.getElementById("cart-data").value = JSON.stringify(cart);
    document.getElementById("final-total").value = cartCtl.calculateTotal();

    if (alumnoSelect) {
      document.getElementById("final-alumno").value = alumnoSelect.value;
    }
    if (tutorSelect) {
      document.getElementById("final-tutor").value = tutorSelect.value;
    }

    // Capturar y enviar la fecha
    const fechaInput = document.getElementById("fecha");
    if (fechaInput && fechaInput.value.trim() !== '') {
      // Si el admin seleccionó una fecha, usarla
      document.getElementById("final-fecha").value = fechaInput.value;
    } else {
      // Si no hay fecha seleccionada o el campo no existe, usar fecha actual
      const today = new Date().toISOString().split('T')[0];
      document.getElementById("final-fecha").value = today;
    }

    // Enviar formulario
    submitOrderBtn.disabled = true;
    submitOrderBtn.classList.add("opacity-50");
    ordersForm.submit();
    // Actualizar el kanban inmediatamente si está disponible
    if (window.refreshKanban) {
      setTimeout(window.refreshKanban, 1000); // Espera 1s para que el pedido se procese
    }
  });

  /**
   * Función para inicializar el select con búsqueda del tutor (igual a credit.js)
   */
  function initializeTutorSearch() {
    const searchInput = document.getElementById('tutor-search');
    const hiddenSelect = document.getElementById('tutor');
    const dropdown = document.getElementById('tutor-dropdown');
    const optionsContainer = document.getElementById('tutor-options');
    const noResults = document.getElementById('no-results');

    // Verificar que los elementos existan antes de continuar
    if (!searchInput || !hiddenSelect || !dropdown) {
      return; // No hacer nada si no estamos en la página de órdenes
    }

    const allOptions = document.querySelectorAll('.tutor-option');

    // Mostrar/ocultar dropdown
    searchInput.addEventListener('focus', function() {
      dropdown.classList.remove('hidden');
      filterOptions('');
    });

    // Ocultar dropdown al hacer click fuera
    document.addEventListener('click', function(e) {
      if (!e.target.closest('#tutor-search') && !e.target.closest('#tutor-dropdown')) {
        dropdown.classList.add('hidden');
      }
    });

    // Filtrar opciones mientras se escribe
    searchInput.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase();
      filterOptions(searchTerm);

      // Limpiar selección si se modifica el texto
      if (hiddenSelect.value && !this.value) {
        hiddenSelect.value = '';
        updateAlumnoSelect(''); // Actualizar select de alumnos
      }
    });

    // Manejar selección de opción
    allOptions.forEach(option => {
      option.addEventListener('click', function() {
        const value = this.dataset.value;
        const text = this.querySelector('div').textContent;

        searchInput.value = text;
        hiddenSelect.value = value;
        dropdown.classList.add('hidden');

        // Actualizar select de alumnos basado en la selección
        updateAlumnoSelect(value);

        // Remover highlight de todas las opciones
        allOptions.forEach(opt => opt.classList.remove('bg-blue-100'));
      });
    });

    // Función para filtrar opciones
    function filterOptions(searchTerm) {
      let hasVisibleOptions = false;

      allOptions.forEach(option => {
        const searchText = option.dataset.search;
        const isVisible = searchText.includes(searchTerm);

        option.style.display = isVisible ? 'block' : 'none';
        if (isVisible) hasVisibleOptions = true;

        // Remover highlight al filtrar
        option.classList.remove('bg-blue-100');
      });

      // Mostrar/ocultar mensaje de "no resultados"
      if (hasVisibleOptions) {
        if (noResults) noResults.classList.add('hidden');
        if (optionsContainer) optionsContainer.classList.remove('hidden');
      } else {
        if (noResults) noResults.classList.remove('hidden');
        if (optionsContainer) optionsContainer.classList.add('hidden');
      }
    }

    // Navegación con teclado
    searchInput.addEventListener('keydown', function(e) {
      const visibleOptions = Array.from(allOptions).filter(opt => opt.style.display !== 'none');
      let currentIndex = visibleOptions.findIndex(opt => opt.classList.contains('bg-blue-100'));

      switch(e.key) {
        case 'ArrowDown':
          e.preventDefault();
          if (visibleOptions.length === 0) return;

          // Remover highlight actual
          if (currentIndex >= 0) {
            visibleOptions[currentIndex].classList.remove('bg-blue-100');
          }

          // Mover al siguiente o al primero
          const nextIndex = currentIndex < visibleOptions.length - 1 ? currentIndex + 1 : 0;
          visibleOptions[nextIndex].classList.add('bg-blue-100');

          // Scroll para mantener visible
          visibleOptions[nextIndex].scrollIntoView({ block: 'nearest' });
          break;

        case 'ArrowUp':
          e.preventDefault();
          if (visibleOptions.length === 0) return;

          // Remover highlight actual
          if (currentIndex >= 0) {
            visibleOptions[currentIndex].classList.remove('bg-blue-100');
          }

          // Mover al anterior o al último
          const prevIndex = currentIndex > 0 ? currentIndex - 1 : visibleOptions.length - 1;
          visibleOptions[prevIndex].classList.add('bg-blue-100');

          // Scroll para mantener visible
          visibleOptions[prevIndex].scrollIntoView({ block: 'nearest' });
          break;

        case 'Enter':
          e.preventDefault();
          if (currentIndex >= 0 && visibleOptions[currentIndex]) {
            visibleOptions[currentIndex].click();
          }
          break;

        case 'Escape':
          dropdown.classList.add('hidden');
          searchInput.blur();
          // Limpiar highlights
          allOptions.forEach(opt => opt.classList.remove('bg-blue-100'));
          break;

        case 'Tab':
          dropdown.classList.add('hidden');
          // Limpiar highlights
          allOptions.forEach(opt => opt.classList.remove('bg-blue-100'));
          break;
      }
    });

    // Limpiar highlights cuando se pierde el foco
    searchInput.addEventListener('blur', function() {
      setTimeout(() => {
        allOptions.forEach(opt => opt.classList.remove('bg-blue-100'));
      }, 200); // Delay para permitir clicks en opciones
    });
  }

  // Función para actualizar el select de alumnos basado en el tutor seleccionado
  function updateAlumnoSelect(tutorId) {
    const alumnoSelect = document.getElementById("alumno");

    if (!alumnoSelect) return;

    // Guardar todas las opciones originales si no están guardadas
    if (!window.originalAlumnoOptions) {
      window.originalAlumnoOptions = Array.from(alumnoSelect.options).map(opt => ({
        value: opt.value,
        text: opt.text,
        tutorId: opt.getAttribute('data-tutor-id')
      }));
    }

    // Limpiar opciones actuales
    alumnoSelect.innerHTML = '';

    // Agregar opción por defecto
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    alumnoSelect.appendChild(defaultOption);

    // Si es profesor, ocultar el select de alumno
    if (tutorId.startsWith('Profesor_')) {
      alumnoSelect.style.display = 'none';
      alumnoSelect.disabled = true;
      defaultOption.text = 'No requerido para profesores';
    } else if (tutorId.startsWith('Tutor_')) {
      // Mostrar solo alumnos del tutor seleccionado
      window.originalAlumnoOptions.forEach(opt => {
        if (opt.tutorId === tutorId) {
          const option = document.createElement('option');
          option.value = opt.value;
          option.text = opt.text;
          option.setAttribute('data-tutor-id', opt.tutorId);
          alumnoSelect.appendChild(option);
        }
      });
      alumnoSelect.disabled = false;
      alumnoSelect.style.display = '';
      defaultOption.text = 'Selecciona el Alumno';
    } else {
      alumnoSelect.disabled = true;
      alumnoSelect.style.display = '';
      defaultOption.text = 'Selecciona un tutor primero';
    }

    // Reinicializar Select2 si está disponible
    if (window.jQuery && $(alumnoSelect).data('select2')) {
      $(alumnoSelect).val(null).trigger('change.select2');
      $(alumnoSelect).select2('destroy');
      $(alumnoSelect).select2({
        width: '100%',
        placeholder: 'Selecciona un alumno',
        allowClear: true,
        language: {
          noResults: function() {
            return 'No hay resultados';
          }
        }
      });
    }
  }
});
