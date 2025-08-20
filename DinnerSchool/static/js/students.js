document.addEventListener("DOMContentLoaded", function () {
  updateGradosByNivel();
});

function updateGradosByNivel() {
  const nivelEducativoSelect = document.getElementById("nivelEducativo");
  const gradoSelect = document.getElementById("grado");
  
  if (!nivelEducativoSelect || !gradoSelect) {
    return; // Si no existen los elementos, salir de la función
  }

  // Opciones de grado según nivel educativo
  const gradosPorNivel = {
    '1': [ // Preescolar
      {value: '1', text: '1°'},
      {value: '2', text: '2°'},
      {value: '3', text: '3°'}
    ],
    '2': [ // Primaria
      {value: '1', text: '1°'},
      {value: '2', text: '2°'},
      {value: '3', text: '3°'},
      {value: '4', text: '4°'},
      {value: '5', text: '5°'},
      {value: '6', text: '6°'}
    ],
    '3': [ // Secundaria
      {value: '1', text: '1°'},
      {value: '2', text: '2°'},
      {value: '3', text: '3°'}
    ],
    '4': [ // Preparatoria
      {value: '1', text: '1°'},
      {value: '2', text: '2°'},
      {value: '3', text: '3°'}
    ]
  };

  // Guardar el grado actual para mantener la selección al editar
  const gradoActual = gradoSelect.dataset.currentValue || null;

  function actualizarGrados() {
    const nivelSeleccionado = nivelEducativoSelect.value;
    
    // Limpiar opciones de grado
    gradoSelect.innerHTML = '';
    
    if (nivelSeleccionado && gradosPorNivel[nivelSeleccionado]) {
      // Habilitar el select
      gradoSelect.disabled = false;
      
      // Agregar opción por defecto
      const optionDefault = document.createElement('option');
      optionDefault.value = '';
      optionDefault.textContent = 'Selecciona el Grado';
      gradoSelect.appendChild(optionDefault);
      
      // Agregar opciones según el nivel
      gradosPorNivel[nivelSeleccionado].forEach(grado => {
        const option = document.createElement('option');
        option.value = grado.value;
        option.textContent = grado.text;
        
        // Mantener selección si estamos editando
        if (gradoActual && gradoActual === grado.value) {
          option.selected = true;
        }
        
        gradoSelect.appendChild(option);
      });
    } else {
      // Deshabilitar y mostrar mensaje
      gradoSelect.disabled = true;
      const optionDisabled = document.createElement('option');
      optionDisabled.value = '';
      optionDisabled.textContent = 'Primero selecciona el Nivel Educativo';
      gradoSelect.appendChild(optionDisabled);
    }
  }

  // Escuchar cambios en nivel educativo
  nivelEducativoSelect.addEventListener('change', actualizarGrados);
  
  // Inicializar al cargar la página
  actualizarGrados();
}