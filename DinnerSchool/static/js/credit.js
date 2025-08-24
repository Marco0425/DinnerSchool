document.addEventListener('DOMContentLoaded', function() {
    // Obtener el botón de generar reporte
    const reportButton = document.getElementById('generateReportBtn');
    
    if (reportButton) {
        reportButton.addEventListener('click', generarReporte);
    }
});

/**
 * Función para generar y descargar el reporte
 */
function generarReporte() {
    const button = document.getElementById('generateReportBtn');
    
    // Deshabilitar el botón y mostrar estado de carga
    if (button) {
        button.disabled = true;
        button.className = "px-4 py-2 text-sm font-medium text-white bg-gray-500 rounded-md cursor-not-allowed transition duration-300 ease-in-out";
        button.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generando...
        `;
    }
    
    // Mostrar notificación de inicio
    mostrarNotificacion('Generando reporte, por favor espera...', 'info');
    
    // Realizar la petición al servidor
    fetch('/comedor/credit/report/generate/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (response.ok) {
            // Verificar si es un archivo (Excel/XLSX)
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
                return response.blob();
            } else {
                // Si no es un archivo, intentar leer como texto para ver el error
                return response.text().then(text => {
                    console.log('Response text:', text);
                    throw new Error(`Respuesta inesperada del servidor: ${text}`);
                });
            }
        } else {
            // Intentar obtener el mensaje de error del servidor
            return response.text().then(text => {
                console.log('Error response:', text);
                throw new Error(`Error ${response.status}: ${text}`);
            });
        }
    })
    .then(blob => {
        // Crear URL del blob y descargar el archivo
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // Nombre del archivo con fecha actual
        const fileName = `reporte_gastos_${new Date().toISOString().split('T')[0]}.xlsx`;
        link.download = fileName;
        
        // Simular click para descargar
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Limpiar URL del blob
        window.URL.revokeObjectURL(url);
        
        // Mostrar mensaje de éxito
        mostrarNotificacion('Reporte generado y descargado exitosamente', 'success');
    })
    .catch(error => {
        console.error('Error completo:', error);
        mostrarNotificacion(`Error al generar el reporte: ${error.message}`, 'error');
    })
    .finally(() => {
        // Restaurar el botón con los estilos originales
        if (button) {
            button.disabled = false;
            button.className = "px-4 py-2 text-sm font-medium text-white bg-primary-red rounded-md hover:bg-red-700 transition duration-300 ease-in-out";
            button.innerHTML = "Reporte";
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
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-md shadow-lg transition-all duration-300 transform translate-x-full`;
    
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
        success: '✓',
        error: '✗',
        info: 'ℹ',
        warning: '⚠'
    };
    
    notification.innerHTML = `
        <div class="flex items-center">
            <span class="text-lg mr-2">${iconos[tipo] || iconos.info}</span>
            <span class="font-medium">${mensaje}</span>
            <button class="ml-4 text-xl leading-none cursor-pointer" onclick="this.parentElement.parentElement.remove()">×</button>
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
 * Función alternativa para generar reporte con parámetros personalizados
 */
function generarReportePersonalizado(fechaInicio = null, fechaFin = null) {
    let url = '/comedor/credit/report/generate/';
    
    // Agregar parámetros de fecha si se proporcionan
    if (fechaInicio || fechaFin) {
        const params = new URLSearchParams();
        if (fechaInicio) params.append('fecha_inicio', fechaInicio);
        if (fechaFin) params.append('fecha_fin', fechaFin);
        url += '?' + params.toString();
    }
    
    // Usar la misma lógica que generarReporte pero con URL personalizada
    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('Error al generar el reporte personalizado');
        }
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `reporte_personalizado_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(url);
        mostrarNotificacion('Reporte personalizado generado exitosamente', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error al generar el reporte personalizado', 'error');
    });
}