document.addEventListener("DOMContentLoaded", function() {
    const platilloSelect = document.getElementById("platillo");
    const ingredientesSelect = document.getElementById("ingredientes");
    const precioInput = document.getElementById("precio");

    platilloSelect.addEventListener("change", function() {
        ingredientesSelect.innerHTML = "";

        const selectedOption = platilloSelect.options[platilloSelect.selectedIndex];
        let ingredientes = [];

        try {
            ingredientes = JSON.parse(selectedOption.dataset.ingredientes || "[]");
        } catch (e) {
            console.error("Error al parsear ingredientes:", e);
        }

        const precio = parseFloat(selectedOption.dataset.precio || 0);

        if (ingredientes.length > 0) {
            ingredientes.forEach(ing => {
                const opt = document.createElement("option");
                opt.value = ing;
                opt.textContent = ing;
                ingredientesSelect.appendChild(opt);
            });
        } else {
            const opt = document.createElement("option");
            opt.textContent = "No hay ingredientes disponibles";
            ingredientesSelect.appendChild(opt);
        }

        precioInput.value = precio ? precio.toFixed(2) : "";
    });
});
