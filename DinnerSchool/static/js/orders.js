document.addEventListener("DOMContentLoaded", function () {
  const platilloSelect = document.getElementById("platillo");
  const precioInput = document.getElementById("precio");

  const ingredientesDisplay = document.getElementById("ingredientes-display");
  const ingredientesHiddenInput = document.getElementById(
    "ingredientes-hidden"
  );
  // ----------------------

  platilloSelect.addEventListener("change", function () {
    const selectedOption = platilloSelect.options[platilloSelect.selectedIndex];
    const ingredientesTexto = selectedOption.getAttribute("data-ingredientes");
    let ingredientesArray = JSON.parse(ingredientesTexto);
    var ingredientes = ingredientesArray.join(", ").toLowerCase();

    if (ingredientes) {
      ingredientesDisplay.value = ingredientes;
      ingredientesHiddenInput.value = ingredientes;
    } else {
      ingredientesDisplay.value = "";
      ingredientesHiddenInput.value = "";
    }
    const precio = parseFloat(selectedOption.dataset.precio || 0);
    precioInput.value = precio ? precio.toFixed(2) : "";
  });
});
