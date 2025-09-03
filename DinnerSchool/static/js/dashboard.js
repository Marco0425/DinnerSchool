// Funcionalidad para el botón de cerrar sesión en el dashboard

document.addEventListener("DOMContentLoaded", function () {
  var logoutButton = document.getElementById("logoutButton");
  if (logoutButton) {
    logoutButton.addEventListener("click", function () {
      // Redirige al endpoint de logout
      window.location.href = "/core/logout/";
    });
  }
  
  // Ocultar botones según estado inicial
  ocultarBotonesCancelarSegunEstado();
});

/**
 * Función para mostrar el modal de confirmación.
 * @param {string} pedidoId - El ID del pedido a cancelar.
 * @param {number} total - El total del pedido a reembolsar.
 */
function showCancelModal(pedidoId, total) {
    // Si el modal ya existe, solo lo mostramos
    let modal = document.getElementById('cancelModal');
    if (modal) {
        document.getElementById('modal-text').innerHTML = `¿Estás seguro de que deseas cancelar el pedido #${pedidoId}? <br><br>Se reembolsará $${total} a tu cuenta.`;
        // Almacenamos los datos en el modal para la confirmación
        modal.dataset.pedidoId = pedidoId;
        modal.dataset.total = total;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        return;
    }

    // Si el modal no existe, lo creamos
    modal = document.createElement('div');
    modal.id = 'cancelModal';
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 hidden';
    
    // Contenido HTML del modal
    modal.innerHTML = `
        <div class="fixed inset-0 bg-gray-900 bg-opacity-50 transition-opacity" onclick="closeModal()"></div>
        
        <div class="bg-white rounded-lg shadow-xl overflow-hidden transform transition-all sm:w-full sm:max-w-md z-50">
            <div class="px-6 py-5">
                <div class="flex items-start">
                    <div class="flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                        <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    </div>
                    <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                        <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                            Cancelar Pedido
                        </h3>
                        <div class="mt-2">
                            <p id="modal-text" class="text-sm text-gray-500">
                                </p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="bg-gray-50 px-6 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm" id="confirmCancelBtn">
                    Sí, cancelar pedido
                </button>
                <button type="button" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm" id="dismissCancelBtn">
                    Descartar
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Añadimos los event listeners a los botones del modal una sola vez
    document.getElementById('confirmCancelBtn').addEventListener('click', () => {
        const pId = modal.dataset.pedidoId;
        const pTotal = modal.dataset.total;
        cancelarPedido(pId, pTotal);
        closeModal();
    });

    document.getElementById('dismissCancelBtn').addEventListener('click', () => {
        closeModal();
    });

    // Actualizamos el texto y mostramos el modal
    document.getElementById('modal-text').innerHTML = `¿Estás seguro de que deseas cancelar el pedido #${pedidoId}? <br><br>Se reembolsará $${total} a tu cuenta.`;
    modal.dataset.pedidoId = pedidoId;
    modal.dataset.total = total;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

/**
 * Función para cerrar el modal.
 */
function closeModal() {
    const modal = document.getElementById('cancelModal');
    if (modal) {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }
}

/**
 * Función para cancelar un pedido.
 * Esta función es llamada desde el modal.
 * @param {string} pedidoId - El ID del pedido a cancelar.
 * @param {number} total - El total del pedido a reembolsar.
 */
function cancelarPedido(pedidoId, total) {
    button = document.getElementById('btnCancelOrder' + pedidoId);
    if (!button) {
        console.error('Botón de cancelar no encontrado');
        return;
    }
    // Realizar petición AJAX
    fetch(`/comedor/cancelOrder/${pedidoId}/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'pedido_id': pedidoId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensaje de éxito
            mostrarNotificacion(data.message, 'success');
            
            // Obtener la fila del pedido
            const pedidoRow = button.closest('.flex.items-center.justify-between');
            
            // Actualizar el badge de estado a "Cancelado"
            const statusBadge = pedidoRow.querySelector('.inline-flex.items-center');
            if (statusBadge) {
                statusBadge.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800';
                statusBadge.textContent = 'Cancelado';
            }
            
            // Ocultar el botón de cancelar con animación
            button.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            button.style.opacity = '0';
            button.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
                button.style.display = 'none';
            }, 300);
            
            // Actualizar el crédito en la pantalla si existe
            const creditAmount = document.getElementById('creditAmount');
            if (creditAmount && data.nuevo_credito) {
                creditAmount.textContent = `${data.nuevo_credito}`;
                
                // Efecto visual en el crédito
                creditAmount.parentElement.style.transform = 'scale(1.05)';
                creditAmount.parentElement.style.transition = 'transform 0.2s ease';
                setTimeout(() => {
                    creditAmount.parentElement.style.transform = 'scale(1)';
                }, 200);
            }
        } else {
            // Mostrar mensaje de error
            mostrarNotificacion(data.message || 'Error al cancelar el pedido', 'error');
            
            // Restaurar el botón
            button.disabled = false;
            button.innerHTML = originalContent;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error de conexión al cancelar el pedido', 'error');
        
        // Restaurar el botón
        button.disabled = false;
        button.innerHTML = originalContent;
    });
}

/**
 * Función para ocultar botones de cancelar según el estado del pedido
 */
function ocultarBotonesCancelarSegunEstado() {
    // Buscar todos los pedidos en la página
    const pedidoRows = document.querySelectorAll('.flex.items-center.justify-between');
    
    pedidoRows.forEach(row => {
        const statusBadge = row.querySelector('.inline-flex.items-center');
        const cancelButton = row.querySelector('button[onclick*="cancelarPedido"]');
        
        if (statusBadge && cancelButton) {
            const statusText = statusBadge.textContent.trim().toLowerCase();
            
            // Ocultar botón si el estado no es "pendiente" o "en preparación"
            if (!['pendiente', 'en preparación'].includes(statusText)) {
                cancelButton.style.display = 'none';
            }
        }
    });
}

/**
 * Función para obtener el token CSRF
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Función para mostrar notificaciones
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Remover notificaciones existentes
    const existingNotifications = document.querySelectorAll('.notification-toast');
    existingNotifications.forEach(notification => notification.remove());
    
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification-toast fixed top-4 right-4 z-50 p-4 rounded-md shadow-lg transition-all duration-300 transform translate-x-full`;
    
    // Estilos según el tipo
    const estilos = {
        success: 'bg-green-100 border border-green-200 text-green-800',
        error: 'bg-red-100 border border-red-200 text-red-800',
        info: 'bg-blue-100 border border-blue-200 text-blue-800',
        warning: 'bg-yellow-100 border border-yellow-200 text-yellow-800'
    };
    
    notification.className += ` ${estilos[tipo] || estilos.info}`;
    
    // Icono según el tipo
    const iconos = {
        success: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>`,
        error: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>`,
        info: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
               </svg>`,
        warning: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>`
    };
    
    notification.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0 mr-3">
                ${iconos[tipo] || iconos.info}
            </div>
            <div class="flex-1">
                <span class="font-medium text-sm">${mensaje}</span>
            </div>
            <button class="ml-4 text-xl leading-none cursor-pointer hover:opacity-75" onclick="this.parentElement.parentElement.remove()">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    `;
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

/**
 * Función auxiliar para formatear moneda
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 2
    }).format(amount);
}

/**
 * Función para actualizar el estado visual de un pedido
 */
function updateOrderStatus(orderId, newStatus) {
    const orderElement = document.querySelector(`[data-order-id="${orderId}"]`);
    if (orderElement) {
        const statusBadge = orderElement.querySelector('.inline-flex.items-center');
        if (statusBadge) {
            // Actualizar clases según el nuevo estado
            statusBadge.className = `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusClasses(newStatus)}`;
            statusBadge.textContent = getStatusLabel(newStatus);
        }
    }
}

/**
 * Función para obtener las clases CSS según el estado
 */
function getStatusClasses(status) {
    const statusClasses = {
        0: 'bg-gray-100 text-gray-800',
        1: 'bg-yellow-100 text-yellow-800',
        2: 'bg-blue-100 text-blue-800',
        3: 'bg-green-100 text-green-800',
        4: 'bg-red-100 text-red-800'
    };
    return statusClasses[status] || 'bg-gray-100 text-gray-800';
}

/**
 * Función para obtener la etiqueta del estado
 */
function getStatusLabel(status) {
    const statusLabels = {
        0: 'Pendiente',
        1: 'En preparación',
        2: 'Finalizado',
        3: 'Entregado',
        4: 'Cancelado'
    };
    return statusLabels[status] || 'Desconocido';
}

// Inicializar funciones cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Ocultar botones según estado inicial
    ocultarBotonesCancelarSegunEstado();
    
    // Verificar estados cada 30 segundos (opcional)
    // setInterval(verificarEstadosPedidos, 30000);
});
