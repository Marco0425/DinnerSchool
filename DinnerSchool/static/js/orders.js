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

  // Inicializar Select2 para el select de tutor
  if (window.jQuery && $('#tutor').length) {
    $('#tutor').select2({
      width: '100%',
      placeholder: 'Selecciona el tutor/profesor',
      allowClear: true,
      language: {
        noResults: function() {
          return 'No hay resultados';
        }
      }
    });
  }
  let cart = [];
  let cartItemCounter = 0;

  // Elementos del DOM
  const platilloSelect = document.getElementById("platillo");
  const ingredientesDisplay = document.getElementById("ingredientes-display");
  const notasInput = document.getElementById("notas");
  const cantidadInput = document.getElementById("cantidad");
  const turnoSelect = document.getElementById("turno");
  const addToCartBtn = document.getElementById("addToCart");
  const cartItemsContainer = document.getElementById("cart-items");
  const totalAmountSpan = document.getElementById("total-amount");
  const clearCartBtn = document.getElementById("clearCart");
  const submitOrderBtn = document.getElementById("submitOrder");
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

  // Agregar platillo al carrito
  addToCartBtn.addEventListener("click", function () {
    const platillo = platilloSelect.value;
    const platilloText = platilloSelect.options[platilloSelect.selectedIndex]
      .text;
    const platilloNombre = platilloSelect.options[platilloSelect.selectedIndex].getAttribute(
      "data-nombre"
    );
    const precio = parseFloat(
      platilloSelect.options[platilloSelect.selectedIndex].getAttribute("data-precio")
    );
    const ingredientes = platilloSelect.options[platilloSelect.selectedIndex].getAttribute(
      "data-ingredientes"
    );
    const notas = notasInput.value.trim();
    const cantidad = parseInt(cantidadInput.value);
    const turno = turnoSelect.value;
    const turnoText = turnoSelect.options[turnoSelect.selectedIndex].text;

    // Validaciones
    if (!platillo) {
      showMessage("Por favor selecciona un platillo", "error");
      return;
    }
    if (!turno) {
      showMessage("Por favor selecciona un turno", "error");
      return;
    }
    if (cantidad < 1) {
      showMessage("La cantidad debe ser mayor a 0", "error");
      return;
    }

    // Crear item del carrito
    const cartItem = {
      id: ++cartItemCounter,
      platillo_id: platillo,
      platillo_nombre: platilloNombre,
      precio: precio,
      cantidad: cantidad,
      subtotal: precio * cantidad,
      ingredientes: ingredientes,
      notas: notas,
      turno: turno,
      turno_text: turnoText,
    };

    // Agregar al carrito
    cart.push(cartItem);

    // Actualizar vista del carrito
    updateCartDisplay();

    // Limpiar formulario
    clearAddForm();

    showMessage("Platillo agregado al carrito", "success");
  });

  // Limpiar carrito
  clearCartBtn.addEventListener("click", function () {
    if (cart.length > 0) {
      if (confirm("¿Estás seguro de que quieres limpiar el carrito?")) {
        cart = [];
        updateCartDisplay();
        showMessage("Carrito limpiado", "info");
      }
    }
  });

  // Enviar orden
  submitOrderBtn.addEventListener("click", function () {
    if (cart.length === 0) {
      showMessage("El carrito está vacío", "error");
      return;
    }

    // Validar información del pedido
    const alumnoSelect =
      document.getElementById("alumno_tutor") ||
      document.getElementById("alumno");
    const tutorSelect = document.getElementById("tutor");

    if (alumnoSelect && !alumnoSelect.value && !tutorSelect.value.includes("Profesor_")) {
      showMessage("Por favor selecciona un alumno", "error");
      return;
    }

    if (
      tutorSelect &&
      tutorSelect.value &&
      alumnoSelect &&
      !alumnoSelect.value &&
      !tutorSelect.value.includes("Profesor_")
    ) {
      showMessage("Si seleccionas un tutor, debes seleccionar un alumno", "error");
      return;
    }

    // Preparar datos para envío
    document.getElementById("cart-data").value = JSON.stringify(cart);
    document.getElementById("final-total").value = calculateTotal();

    if (alumnoSelect) {
      document.getElementById("final-alumno").value = alumnoSelect.value;
    }
    if (tutorSelect) {
      document.getElementById("final-tutor").value = tutorSelect.value;
    }

    // Enviar formulario
    ordersForm.submit();
  });

  // Función para actualizar la vista del carrito
  function updateCartDisplay() {
    if (cart.length === 0) {
      cartItemsContainer.innerHTML =
        '<p class="text-gray-500 text-center py-8">El carrito está vacío</p>';
      submitOrderBtn.disabled = true;
      submitOrderBtn.classList.add("opacity-50");
    } else {
      let cartHTML = "";
      cart.forEach((item) => {
        cartHTML += `
                    <div class="bg-gray-50 p-3 rounded-lg border" data-item-id="${item.id}">
                        <div class="flex justify-between items-start">
                            <div class="flex-1">
                                <h4 class="font-medium text-gray-900">${item.platillo_nombre}</h4>
                                <p class="text-sm text-gray-600">Turno: ${item.turno_text}</p>
                                <p class="text-sm text-gray-600">Cantidad: ${item.cantidad}</p>
                                ${item.notas ? `<p class="text-sm text-gray-600">Notas: ${item.notas}</p>` : ''}
                                <p class="text-sm font-medium text-gray-900">Subtotal: $${item.subtotal.toFixed(2)}</p>
                            </div>
                            <button 
                                class="remove-item text-red-600 hover:text-red-800 ml-2"
                                data-item-id="${item.id}"
                                title="Eliminar del carrito"
                            >
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                `;
      });
      cartItemsContainer.innerHTML = cartHTML;

      // Agregar event listeners a botones de eliminar
      document.querySelectorAll(".remove-item").forEach((btn) => {
        btn.addEventListener("click", function () {
          const itemId = parseInt(this.getAttribute("data-item-id"));
          removeFromCart(itemId);
        });
      });

      submitOrderBtn.disabled = false;
      submitOrderBtn.classList.remove("opacity-50");
    }

    // Actualizar total
    totalAmountSpan.textContent = `$${calculateTotal().toFixed(2)}`;
  }

  // Función para eliminar item del carrito
  function removeFromCart(itemId) {
    cart = cart.filter((item) => item.id !== itemId);
    updateCartDisplay();
    showMessage("Platillo eliminado del carrito", "info");
  }

  // Función para calcular total
  function calculateTotal() {
    return cart.reduce((total, item) => total + item.subtotal, 0);
  }

  // Función para limpiar formulario de agregar
  function clearAddForm() {
    platilloSelect.value = "";
    ingredientesDisplay.value = "";
    notasInput.value = "";
    cantidadInput.value = "1";
    turnoSelect.value = "";
  }

  // Función para mostrar mensajes
  function showMessage(text, type) {
    const messageDiv = document.getElementById("message");
    messageDiv.textContent = text;
    messageDiv.className = `mt-6 p-3 text-sm text-center rounded-md ${getMessageClasses(
      type
    )}`;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 3000);
  }

  // Función para obtener clases de mensaje
  function getMessageClasses(type) {
    switch (type) {
      case "success":
        return "bg-green-100 text-green-800 border border-green-200";
      case "error":
        return "bg-red-100 text-red-800 border border-red-200";
      case "warning":
        return "bg-yellow-100 text-yellow-800 border border-yellow-200";
      case "info":
        return "bg-blue-100 text-blue-800 border border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border border-gray-200";
    }
  }

  // Funcionalidad existente para tutores/alumnos (si existe)
  const tutorSelect = document.getElementById("tutor");
  const alumnoSelect = document.getElementById("alumno");

  if (tutorSelect && alumnoSelect) {
    console.log("Tutor and alumno selects found");
    $(tutorSelect).on('change', function () {
      console.log("Tutor select changed");
      const tutorId = this.value;
      const alumnoOptions = alumnoSelect.querySelectorAll('option[data-tutor-id]');

      // Resetear opciones de alumno
      alumnoSelect.value = "";
      alumnoOptions.forEach((option) => {
        option.style.display = "none";
      });

      if (tutorId) {
        alumnoOptions.forEach((option) => {
          if (option.getAttribute('data-tutor-id') === tutorId) {
            option.style.display = "block";
          }
        });
        alumnoSelect.disabled = false;
      } else {
        alumnoSelect.disabled = true;
      }

      // Refrescar Select2 para mostrar solo las opciones visibles
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
    });
  }
});
