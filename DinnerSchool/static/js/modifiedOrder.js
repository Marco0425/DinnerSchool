/**
 * Script para la funcionalidad de modificar pedidos
 * Maneja la selección de platillos, ingredientes y actualización del resumen
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const platilloSelect = document.getElementById('platillo_select');
    const ingredientesDisplay = document.getElementById('ingredientes-display');
    const cantidadInput = document.getElementById('cantidad');
    const turnoSelect = document.getElementById('turno');
    const notaInput = document.getElementById('nota');
    const ingredientesHidden = document.getElementById('ingredientes');
    const orderSummary = document.getElementById('order_summary');
    const summaryContent = document.getElementById('summary_content');
    const totalPrice = document.getElementById('total_price');
    const priceDifference = document.getElementById('price_difference');
    const submitBtn = document.getElementById('submit_btn');
    const modifyOrderForm = document.getElementById('modifyOrderForm');

    // Obtener datos del pedido actual desde el template
    const currentOrderElement = document.getElementById('current-order-data');
    let currentOrder = {
        platillo_id: 0,
        ingredientes: [],
        nota: "",
        cantidad: 1,
        turno: 0,
        total: 0
    };

    // Procesar datos del pedido actual
    if (currentOrderElement) {
        try {
            const rawData = JSON.parse(currentOrderElement.textContent);
            currentOrder = {
                platillo_id: rawData.platillo_id || 0,
                ingredientes: parseIngredientes(rawData.ingredientes_seleccionados),
                nota: rawData.nota || "",
                cantidad: rawData.cantidad || 1,
                turno: rawData.turno || 0,
                total: rawData.total_actual || 0
            };
            console.log('Datos del pedido cargados:', currentOrder);
        } catch (error) {
            console.error('Error al parsear datos del pedido:', error);
        }
    }

    let selectedIngredientes = [...currentOrder.ingredientes];

    /**
     * Función para parsear ingredientes de manera segura
     * @param {*} ingredientesData - Datos de ingredientes (puede ser array, string, null, etc.)
     * @returns {Array} Array de ingredientes válido
     */
    function parseIngredientes(ingredientesData) {
        // Si ya es un array, devolverlo
        if (Array.isArray(ingredientesData)) {
            return ingredientesData;
        }
        
        // Si es null o undefined, devolver array vacío
        if (!ingredientesData) {
            return [];
        }
        
        // Si es un string, intentar parsearlo como JSON
        if (typeof ingredientesData === 'string') {
            try {
                const parsed = JSON.parse(ingredientesData);
                return Array.isArray(parsed) ? parsed : [];
            } catch (error) {
                console.warn('No se pudo parsear ingredientes como JSON:', ingredientesData);
                // Si no es JSON válido, asumir que es una lista separada por comas
                return ingredientesData.split(',').map(item => item.trim()).filter(item => item.length > 0);
            }
        }
        
        // Cualquier otro tipo, devolver array vacío
        return [];
    }

    /**
     * Función para mostrar los ingredientes en el textarea
     * @param {Array} ingredientesArray - Array de ingredientes del platillo
     */
    function mostrarIngredientes(ingredientesArray) {
        // Validar que ingredientesArray sea un array
        const validIngredientes = Array.isArray(ingredientesArray) ? ingredientesArray : [];
        
        if (validIngredientes.length > 0) {
            // Mostrar todos los ingredientes del platillo
            selectedIngredientes = [...validIngredientes];
            ingredientesDisplay.value = validIngredientes.join(', ');
        } else {
            selectedIngredientes = [];
            ingredientesDisplay.value = 'Sin ingredientes';
        }
        
        // Actualizar el campo oculto
        ingredientesHidden.value = JSON.stringify(selectedIngredientes);
    }

    /**
     * Función para actualizar el resumen del pedido modificado
     */
    function actualizarResumen() {
        const platilloOption = platilloSelect.options[platilloSelect.selectedIndex];
        
        if (platilloSelect.value && platilloOption) {
            const precio = parseFloat(platilloOption.dataset.precio) || 0;
            const cantidad = parseInt(cantidadInput.value) || 1;
            const total = precio * cantidad;
            const diferencia = total - (currentOrder.total || 0);
            
            // Etiquetas de turno
            const turnoLabels = ['Receso 1', 'Receso 2', 'Comida'];
            const turnoLabel = turnoLabels[parseInt(turnoSelect.value)] || 'No seleccionado';
            
            // Generar HTML del resumen
            summaryContent.innerHTML = generateSummaryHTML(platilloOption, cantidad, turnoLabel);
            
            // Actualizar precio total
            totalPrice.textContent = `$${total.toFixed(2)}`;
            
            // Mostrar diferencia de precio
            updatePriceDifference(diferencia);
            
            // Mostrar resumen y habilitar botón
            orderSummary.style.display = 'block';
            submitBtn.disabled = false;
        } else {
            // Ocultar resumen y deshabilitar botón si no hay platillo seleccionado
            orderSummary.style.display = 'none';
            submitBtn.disabled = true;
        }
    }

    /**
     * Función para generar el HTML del resumen
     * @param {HTMLElement} platilloOption - Opción del platillo seleccionado
     * @param {number} cantidad - Cantidad del pedido
     * @param {string} turnoLabel - Etiqueta del turno
     * @returns {string} HTML del resumen
     */
    function generateSummaryHTML(platilloOption, cantidad, turnoLabel) {
        const platilloNombre = platilloOption.dataset.nombre || platilloOption.textContent.split(' - ')[0] || 'Sin nombre';
        
        return `
            <div class="space-y-2">
                <div class="flex justify-between">
                    <span>Platillo:</span>
                    <span class="font-medium">${escapeHtml(platilloNombre)}</span>
                </div>
                <div class="flex justify-between">
                    <span>Cantidad:</span>
                    <span class="font-medium">${cantidad}</span>
                </div>
                <div class="flex justify-between">
                    <span>Turno:</span>
                    <span class="font-medium">${turnoLabel}</span>
                </div>
                ${selectedIngredientes.length > 0 ? `
                <div class="flex justify-between">
                    <span>Ingredientes:</span>
                    <span class="font-medium text-right">${selectedIngredientes.map(ing => escapeHtml(ing)).join(', ')}</span>
                </div>
                ` : ''}
                ${notaInput.value ? `
                <div class="flex justify-between">
                    <span>Nota:</span>
                    <span class="font-medium text-right">${escapeHtml(notaInput.value)}</span>
                </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Función para actualizar la visualización de la diferencia de precio
     * @param {number} diferencia - Diferencia entre precio nuevo y actual
     */
    function updatePriceDifference(diferencia) {
        if (diferencia > 0) {
            priceDifference.innerHTML = `<span class="text-red-600 font-medium">Costo adicional: +$${diferencia.toFixed(2)}</span>`;
        } else if (diferencia < 0) {
            priceDifference.innerHTML = `<span class="text-green-600 font-medium">Ahorro: $${Math.abs(diferencia).toFixed(2)}</span>`;
        } else {
            priceDifference.innerHTML = `<span class="text-gray-600">Sin cambio en el precio</span>`;
        }
    }

    /**
     * Función para escapar HTML y prevenir XSS
     * @param {string} text - Texto a escapar
     * @returns {string} Texto escapado
     */
    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    /**
     * Función para manejar el cambio de platillo
     */
    function handlePlatilloChange() {
        if (platilloSelect.value) {
            const option = platilloSelect.options[platilloSelect.selectedIndex];
            try {
                const ingredientesString = option.dataset.ingredientes || '[]';
                const ingredientes = JSON.parse(ingredientesString);
                const validIngredientes = Array.isArray(ingredientes) ? ingredientes : [];
                
                mostrarIngredientes(validIngredientes);
            } catch (error) {
                console.error('Error al parsear ingredientes del platillo:', error);
                mostrarIngredientes([]);
            }
        } else {
            ingredientesDisplay.value = 'Los ingredientes aparecerán aquí...';
            orderSummary.style.display = 'none';
            submitBtn.disabled = true;
            selectedIngredientes = [];
            ingredientesHidden.value = '[]';
        }
        actualizarResumen();
    }

    /**
     * Función para cerrar el modal
     */
    function closeModal() {
        const modal = document.getElementById('confirmModal');
        if (modal) {
            modal.classList.remove('flex');
            modal.classList.add('hidden');
            
            // Eliminar el modal del DOM después de cerrar
            setTimeout(() => {
                if (modal.parentNode) {
                    modal.remove();
                }
            }, 300); // Esperar la transición de cierre
        }
    }

    /**
     * Función para mostrar el modal de confirmación
     */
    function showConfirmModal() {
        // Si el modal ya existe, actualizarlo y mostrarlo
        let modal = document.getElementById('confirmModal');
        if (modal) {
            // Actualizar el contenido del modal
            updateModalContent(modal);
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            return;
        }

        // Si el modal no existe, lo creamos
        modal = document.createElement('div');
        modal.id = 'confirmModal';
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 hidden';
        
        // Crear el contenido del modal
        createModalContent(modal);
        
        // Agregar el modal al body
        document.body.appendChild(modal);

        // Mostrar el modal
        modal.classList.remove('hidden');
        modal.classList.add('flex');

        // Enfocar el botón de confirmar
        const confirmBtn = document.getElementById('confirmModifyBtn');
        if (confirmBtn) {
            confirmBtn.focus();
        }
    }

    /**
     * Función para crear el contenido del modal
     * @param {HTMLElement} modal - Elemento modal
     */
    function createModalContent(modal) {
        // Obtener datos actuales para el mensaje
        const platilloOption = platilloSelect.options[platilloSelect.selectedIndex];
        const platilloNombre = platilloOption ? platilloOption.dataset.nombre : 'Sin seleccionar';
        const cantidad = cantidadInput.value || 1;
        const precio = platilloOption ? parseFloat(platilloOption.dataset.precio) : 0;
        const total = precio * cantidad;
        const diferencia = total - currentOrder.total;

        let diferenciaText = '';
        if (diferencia > 0) {
            diferenciaText = `<br><span class="text-red-600 font-medium">Costo adicional: +$${diferencia.toFixed(2)}</span>`;
        } else if (diferencia < 0) {
            diferenciaText = `<br><span class="text-green-600 font-medium">Ahorro: $${Math.abs(diferencia).toFixed(2)}</span>`;
        } else {
            diferenciaText = '<br><span class="text-gray-600">Sin cambio en el precio</span>';
        }
        
        // Contenido HTML del modal
        modal.innerHTML = `
            <div class="fixed inset-0 bg-gray-900 bg-opacity-50 transition-opacity" onclick="closeModal()"></div>
            
            <div class="bg-white rounded-lg shadow-xl overflow-hidden transform transition-all sm:w-full sm:max-w-md z-50">
                <div class="px-6 py-5">
                    <div class="flex items-start">
                        <div class="flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 sm:mx-0 sm:h-10 sm:w-10">
                            <svg class="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                        </div>
                        <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                            <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                                Confirmar Modificación
                            </h3>
                            <div class="mt-2">
                                <p id="modal-text" class="text-sm text-gray-500">
                                    ¿Estás seguro de que quieres modificar este pedido? <br><br>
                                    <strong>Nuevo platillo:</strong> ${escapeHtml(platilloNombre)} <br>
                                    <strong>Cantidad:</strong> ${cantidad} <br>
                                    <strong>Total:</strong> $${total.toFixed(2)}
                                    ${diferenciaText}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-gray-50 px-6 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                    <button type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-red text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm" id="confirmModifyBtn">
                        Sí, guardar cambios
                    </button>
                    <button type="button" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm" id="dismissModifyBtn">
                        Cancelar
                    </button>
                </div>
            </div>
        `;

        // Añadir event listeners a los botones del modal
        const confirmBtn = modal.querySelector('#confirmModifyBtn');
        const dismissBtn = modal.querySelector('#dismissModifyBtn');

        if (confirmBtn) {
            confirmBtn.addEventListener('click', function() {
                closeModal();
                // Enviar el formulario
                if (modifyOrderForm) {
                    modifyOrderForm.submit();
                }
            });
        }

        if (dismissBtn) {
            dismissBtn.addEventListener('click', function() {
                closeModal();
            });
        }
    }

    /**
     * Función para actualizar el contenido del modal existente
     * @param {HTMLElement} modal - Elemento modal existente
     */
    function updateModalContent(modal) {
        const modalText = modal.querySelector('#modal-text');
        if (modalText) {
            // Obtener datos actuales para el mensaje
            const platilloOption = platilloSelect.options[platilloSelect.selectedIndex];
            const platilloNombre = platilloOption ? platilloOption.dataset.nombre : 'Sin seleccionar';
            const cantidad = cantidadInput.value || 1;
            const precio = platilloOption ? parseFloat(platilloOption.dataset.precio) : 0;
            const total = precio * cantidad;
            const diferencia = total - currentOrder.total;

            let diferenciaText = '';
            if (diferencia > 0) {
                diferenciaText = `<br><span class="text-red-600 font-medium">Costo adicional: +$${diferencia.toFixed(2)}</span>`;
            } else if (diferencia < 0) {
                diferenciaText = `<br><span class="text-green-600 font-medium">Ahorro: $${Math.abs(diferencia).toFixed(2)}</span>`;
            } else {
                diferenciaText = '<br><span class="text-gray-600">Sin cambio en el precio</span>';
            }

            modalText.innerHTML = `
                ¿Estás seguro de que quieres modificar este pedido? <br><br>
                <strong>Nuevo platillo:</strong> ${escapeHtml(platilloNombre)} <br>
                <strong>Cantidad:</strong> ${cantidad} <br>
                <strong>Total:</strong> $${total.toFixed(2)}
                ${diferenciaText}
            `;
        }
    }

    /**
     * Función para validar y mostrar el modal de confirmación
     * @param {Event} e - Evento del botón
     */
    function validateAndShowModal(e) {
        e.preventDefault();
        
        // Validar platillo seleccionado
        if (!platilloSelect.value) {
            alert('Por favor selecciona un platillo');
            return false;
        }
        
        // Validar cantidad
        const cantidad = parseInt(cantidadInput.value);
        if (!cantidad || cantidad < 1) {
            alert('La cantidad debe ser al menos 1');
            return false;
        }
        
        // Validar turno seleccionado
        if (turnoSelect.value === '') {
            alert('Por favor selecciona un turno');
            return false;
        }
        
        // Si todas las validaciones pasan, mostrar el modal
        showConfirmModal();
        return true;
    }

    // Event Listeners
    if (platilloSelect) {
        platilloSelect.addEventListener('change', handlePlatilloChange);
    }

    if (cantidadInput) {
        cantidadInput.addEventListener('input', actualizarResumen);
    }

    if (turnoSelect) {
        turnoSelect.addEventListener('change', actualizarResumen);
    }

    if (notaInput) {
        notaInput.addEventListener('input', actualizarResumen);
    }

    // Event listener para el botón de submit (ahora usa type="button")
    if (submitBtn) {
        submitBtn.addEventListener('click', validateAndShowModal);
    }

    // Función global para cerrar modal (para el onclick del backdrop)
    window.closeModal = closeModal;

    // Inicialización: si hay un platillo seleccionado al cargar la página
    if (platilloSelect && platilloSelect.value) {
        handlePlatilloChange();
    }

    // Función para debugging (solo en desarrollo)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.modifiedOrderDebug = {
            currentOrder,
            selectedIngredientes,
            actualizarResumen,
            mostrarIngredientes,
            parseIngredientes,
            showConfirmModal
        };
    }
});