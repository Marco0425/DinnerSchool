document.addEventListener("DOMContentLoaded", function () {
  const platilloSelect = document.getElementById("platillo");
  const ingredientesDisplay = document.getElementById("ingredientes-display");
  const ordersForm = document.getElementById("ordersForm");

  // Mostrar ingredientes cuando se selecciona un platillo
  platilloSelect.addEventListener("change", function () {
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

  // Lógica de carrito (agregar/quitar/mostrar/limpiar) compartida con orders.js
  const cartCtl = CartCommon.create();
  const submitOrderBtn = document.getElementById("submitOrder");

  // Enviar venta
  submitOrderBtn.addEventListener("click", function () {
    // form.submit() no dispara 'submit', hay que evitar el doble clic a mano.
    if (submitOrderBtn.disabled) return;

    const cart = cartCtl.getCart();
    if (cart.length === 0) {
      cartCtl.showMessage("El carrito está vacío", "error");
      return;
    }

    document.getElementById("cart-data").value = JSON.stringify(cart);
    const clienteNombreInput = document.getElementById("cliente_nombre");
    document.getElementById("final-cliente-nombre").value = clienteNombreInput
      ? clienteNombreInput.value.trim()
      : "";

    submitOrderBtn.disabled = true;
    submitOrderBtn.classList.add("opacity-50");
    ordersForm.submit();
  });
});
