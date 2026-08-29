/**
 * Lógica de carrito compartida entre orders.js (pedidos de alumno/profesor)
 * y directSale.js (venta directa). Ambas páginas usan los mismos ids de DOM
 * (platillo, cantidad, turno, addToCart, cart-items, total-amount, clearCart,
 * submitOrder, message), así que el manejo del carrito vive en un solo lugar.
 */
window.CartCommon = (function () {
  function create() {
    let cart = [];
    let cartItemCounter = 0;

    const platilloSelect = document.getElementById("platillo");
    const notasInput = document.getElementById("notas");
    const cantidadInput = document.getElementById("cantidad");
    const turnoSelect = document.getElementById("turno");
    const addToCartBtn = document.getElementById("addToCart");
    const cartItemsContainer = document.getElementById("cart-items");
    const totalAmountSpan = document.getElementById("total-amount");
    const clearCartBtn = document.getElementById("clearCart");
    const submitOrderBtn = document.getElementById("submitOrder");

    function showMessage(text, type) {
      const messageDiv = document.getElementById("message");
      if (!messageDiv) return;
      messageDiv.textContent = text;
      messageDiv.className = `mt-6 p-3 text-sm text-center rounded-md ${getMessageClasses(type)}`;
      messageDiv.classList.remove("hidden");
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 3000);
    }

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

    function calculateTotal() {
      return cart.reduce((total, item) => total + item.subtotal, 0);
    }

    function updateCartDisplay() {
      if (cart.length === 0) {
        cartItemsContainer.innerHTML =
          '<p class="text-gray-500 text-center py-8">El carrito está vacío</p>';
        submitOrderBtn.disabled = true;
        submitOrderBtn.classList.add("opacity-50");
      } else {
        cartItemsContainer.innerHTML = "";
        cart.forEach((item) => {
          const card = document.createElement("div");
          card.className = "bg-gray-50 p-3 rounded-lg border";
          card.dataset.itemId = item.id;

          const row = document.createElement("div");
          row.className = "flex justify-between items-start";

          const info = document.createElement("div");
          info.className = "flex-1";
          info.innerHTML = `
            <h4 class="font-medium text-gray-900"></h4>
            <p class="text-sm text-gray-600">Turno: </p>
            <p class="text-sm text-gray-600">Cantidad: </p>
            ${item.notas ? '<p class="text-sm text-gray-600">Notas: </p>' : ''}
            <p class="text-sm font-medium text-gray-900">Subtotal: $${item.subtotal.toFixed(2)}</p>
          `;
          // Los campos de texto libre (nombre de platillo, notas) se llenan con
          // textContent para no abrir una vía de inyección de HTML.
          const [h4, turnoP, cantidadP, notasP] = info.querySelectorAll("h4, p");
          h4.textContent = item.platillo_nombre;
          turnoP.textContent = `Turno: ${item.turno_text}`;
          cantidadP.textContent = `Cantidad: ${item.cantidad}`;
          if (item.notas && notasP) {
            notasP.textContent = `Notas: ${item.notas}`;
          }

          const removeBtn = document.createElement("button");
          removeBtn.className = "remove-item text-red-600 hover:text-red-800 ml-2";
          removeBtn.title = "Eliminar del carrito";
          removeBtn.innerHTML =
            '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>';
          removeBtn.addEventListener("click", () => removeFromCart(item.id));

          row.appendChild(info);
          row.appendChild(removeBtn);
          card.appendChild(row);
          cartItemsContainer.appendChild(card);
        });

        submitOrderBtn.disabled = false;
        submitOrderBtn.classList.remove("opacity-50");
      }

      totalAmountSpan.textContent = `$${calculateTotal().toFixed(2)}`;
    }

    function removeFromCart(itemId) {
      cart = cart.filter((item) => item.id !== itemId);
      updateCartDisplay();
      showMessage("Platillo eliminado del carrito", "info");
    }

    function clearAddForm() {
      platilloSelect.value = "";
      const ingredientesDisplay = document.getElementById("ingredientes-display");
      if (ingredientesDisplay) ingredientesDisplay.value = "";
      notasInput.value = "";
      cantidadInput.value = "1";
      turnoSelect.value = "";
      if (window.jQuery && $(platilloSelect).data('select2')) {
        $(platilloSelect).val(null).trigger('change.select2');
      }
    }

    addToCartBtn.addEventListener("click", function () {
      const platillo = platilloSelect.value;
      const selectedOption = platilloSelect.options[platilloSelect.selectedIndex];
      const platilloNombre = selectedOption.getAttribute("data-nombre");
      const precio = parseFloat(selectedOption.getAttribute("data-precio"));
      const ingredientes = selectedOption.getAttribute("data-ingredientes");
      const notas = notasInput.value.trim();
      const cantidad = parseInt(cantidadInput.value, 10);
      const turno = turnoSelect.value;
      const turnoText = turnoSelect.options[turnoSelect.selectedIndex].text;

      if (!platillo) {
        showMessage("Por favor selecciona un platillo", "error");
        return;
      }
      if (!turno) {
        showMessage("Por favor selecciona un turno", "error");
        return;
      }
      if (!Number.isInteger(cantidad) || cantidad < 1) {
        showMessage("La cantidad debe ser un número mayor a 0", "error");
        return;
      }

      cart.push({
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
      });

      updateCartDisplay();
      clearAddForm();
      showMessage("Platillo agregado al carrito", "success");
    });

    clearCartBtn.addEventListener("click", function () {
      if (cart.length > 0) {
        if (confirm("¿Estás seguro de que quieres limpiar el carrito?")) {
          cart = [];
          updateCartDisplay();
          showMessage("Carrito limpiado", "info");
        }
      }
    });

    return {
      getCart: () => cart,
      calculateTotal,
      showMessage,
    };
  }

  return { create };
})();
