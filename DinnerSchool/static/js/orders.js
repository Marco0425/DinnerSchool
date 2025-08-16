document.addEventListener("DOMContentLoaded", function () {
  updateIngredientesDisplay();
  getstudentsByTutor();
});

function updateIngredientesDisplay() {
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
}

function getstudentsByTutor() {
  const tutorSelect = document.getElementById("tutor");
  const alumnoSelect = document.getElementById("alumno");
  alumnoSelect.disabled = true;

  // Guardamos todas las opciones de alumnos para no perderlas
  const todasLasOpcionesDeAlumno = Array.from(alumnoSelect.options);

  tutorSelect.addEventListener("change", function () {
    // Obtenemos el ID del tutor seleccionado
    const selectedTutorId = this.value;

    // Limpiamos el select de alumnos
    alumnoSelect.innerHTML = "";

    if (selectedTutorId) {
      // Si se seleccionó un tutor, habilitamos el select de alumnos
      alumnoSelect.disabled = false;

      // Agregamos la opción por defecto
      const defaultOption = todasLasOpcionesDeAlumno.find(
        (opt) => opt.value === ""
      );
      if (defaultOption) {
        defaultOption.textContent = "Selecciona el Alumno";
        alumnoSelect.appendChild(defaultOption.cloneNode(true));
      }

      // Filtramos y añadimos solo los alumnos del tutor seleccionado
      todasLasOpcionesDeAlumno.forEach(function (option) {
        if (option.dataset.tutorId === selectedTutorId) {
          alumnoSelect.appendChild(option.cloneNode(true));
        }
      });
    } else {
      // Si no hay tutor seleccionado, lo deshabilitamos y ponemos un mensaje
      alumnoSelect.disabled = true;
      const defaultOption = todasLasOpcionesDeAlumno.find(
        (opt) => opt.value === ""
      );
      if (defaultOption) {
        defaultOption.textContent = "Selecciona un tutor primero";
        alumnoSelect.appendChild(defaultOption.cloneNode(true));
      }
    }
  });
}
