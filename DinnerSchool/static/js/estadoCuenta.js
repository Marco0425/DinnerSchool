document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const userSearch = document.getElementById('user-search');
    const userSelect = document.getElementById('user-select');
    const userDropdown = document.getElementById('user-dropdown');
    const userOptions = document.getElementById('user-options');
    const noResults = document.getElementById('no-results');
    const fechaInicio = document.getElementById('fecha-inicio');
    const fechaFin = document.getElementById('fecha-fin');
    const btnFiltrar = document.getElementById('btn-filtrar');
    const loading = document.getElementById('loading');
    const movimientosTable = document.getElementById('movimientos-table');
    const movimientosBody = document.getElementById('movimientos-body');
    const noData = document.getElementById('no-data');
    const userInfo = document.getElementById('user-info');
    const userDetails = document.getElementById('user-details');
    const resumen = document.getElementById('resumen');

    // Verificar elementos críticos
    if (!userSearch || !userSelect || !fechaInicio || !fechaFin || !btnFiltrar) {
        console.error('Elementos críticos del DOM no encontrados');
        return;
    }

    // Establecer fecha de hoy como default
    const hoy = new Date().toISOString().split('T')[0];
    fechaInicio.value = hoy;
    fechaFin.value = hoy;

    // Funcionalidad del dropdown personalizado
    let allOptions = [];
    
    function initializeOptions() {
        if (!userOptions) return;
        
        const options = userOptions.querySelectorAll('.user-option');
        allOptions = Array.from(options).map(option => ({
            element: option,
            value: option.dataset.value || '',
            searchText: (option.dataset.search || '').toLowerCase(),
            tipo: option.dataset.tipo || '',
            visible: true
        }));
    }

    function filterOptions(searchTerm) {
        if (!allOptions.length) return [];
        
        const filtered = allOptions.filter(option => {
            const matches = option.searchText.includes(searchTerm.toLowerCase());
            option.visible = matches;
            if (option.element) {
                option.element.style.display = matches ? 'block' : 'none';
            }
            return matches;
        });

        if (noResults) {
            if (filtered.length === 0) {
                noResults.classList.remove('hidden');
            } else {
                noResults.classList.add('hidden');
            }
        }

        return filtered;
    }

    // Eventos del dropdown
    if (userSearch) {
        userSearch.addEventListener('input', function() {
            const searchTerm = this.value;
            if (userDropdown) {
                userDropdown.classList.remove('hidden');
            }
            
            if (searchTerm.length > 0) {
                filterOptions(searchTerm);
            } else {
                allOptions.forEach(option => {
                    if (option.element) {
                        option.element.style.display = 'block';
                        option.visible = true;
                    }
                });
                if (noResults) {
                    noResults.classList.add('hidden');
                }
            }
        });

        userSearch.addEventListener('focus', function() {
            if (userDropdown) {
                userDropdown.classList.remove('hidden');
            }
            initializeOptions();
        });
    }

    // Cerrar dropdown al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!e.target) return;
        
        const isInsideSearch = userSearch && userSearch.contains(e.target);
        const isInsideDropdown = userDropdown && userDropdown.contains(e.target);
        
        if (!isInsideSearch && !isInsideDropdown && userDropdown) {
            userDropdown.classList.add('hidden');
        }
    });

    // Seleccionar opción
    if (userOptions) {
        userOptions.addEventListener('click', function(e) {
            const option = e.target.closest('.user-option');
            if (option) {
                const value = option.dataset.value;
                const textElement = option.querySelector('.font-medium');
                const text = textElement ? textElement.textContent : '';
                
                userSearch.value = text;
                userSelect.value = value;
                if (userDropdown) {
                    userDropdown.classList.add('hidden');
                }
            }
        });
    }

    // Evento del botón filtrar
    if (btnFiltrar) {
        btnFiltrar.addEventListener('click', function() {
            const userId = userSelect.value;
            const inicio = fechaInicio.value;
            const fin = fechaFin.value;

            if (!userId) {
                alert('Por favor selecciona un usuario');
                return;
            }

            if (!inicio || !fin) {
                alert('Por favor selecciona un rango de fechas');
                return;
            }

            if (new Date(inicio) > new Date(fin)) {
                alert('La fecha de inicio no puede ser mayor a la fecha fin');
                return;
            }

            cargarMovimientos(userId, inicio, fin);
        });
    }

    function cargarMovimientos(userId, fechaInicio, fechaFin) {
        // Mostrar loading y ocultar otros elementos
        showElement(loading);
        hideElement(movimientosTable);
        hideElement(noData);
        hideElement(userInfo);
        hideElement(resumen);

        // Obtener token CSRF
        let csrfToken = '';
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfMeta = document.querySelector('meta[name=csrf-token]');
        const csrfCookie = document.cookie.split(';').find(cookie => cookie.trim().startsWith('csrftoken='));
        
        if (csrfInput && csrfInput.value) {
            csrfToken = csrfInput.value;
        } else if (csrfMeta && csrfMeta.content) {
            csrfToken = csrfMeta.content;
        } else if (csrfCookie) {
            csrfToken = csrfCookie.split('=')[1];
        }

        if (!csrfToken) {
            hideElement(loading);
            alert('Error: Token de seguridad no encontrado');
            return;
        }

        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('fecha_inicio', fechaInicio);
        formData.append('fecha_fin', fechaFin);
        formData.append('csrfmiddlewaretoken', csrfToken);

        fetch('/comedor/get-movimientos/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideElement(loading);
            
            if (data && data.success) {
                mostrarUserInfo(data.user_info);
                mostrarMovimientos(data.movimientos);
                mostrarResumen(data.resumen);
            } else {
                alert(data.message || 'Error al cargar los movimientos');
            }
        })
        .catch(error => {
            hideElement(loading);
            alert('Error al cargar los movimientos: ' + error.message);
        });
    }

    // Funciones helper
    function showElement(element) {
        if (element) {
            element.classList.remove('hidden');
        }
    }

    function hideElement(element) {
        if (element) {
            element.classList.add('hidden');
        }
    }

    function mostrarUserInfo(userInfoData) {
        if (!userInfoData || !userDetails) return;
        
        let html = `
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <strong>Nombre:</strong> ${userInfoData.nombre || 'N/A'}
                </div>
                <div>
                    <strong>Tipo:</strong> ${userInfoData.tipo || 'N/A'}
                </div>
        `;
        
        if (userInfoData.alumnos && Array.isArray(userInfoData.alumnos) && userInfoData.alumnos.length > 0) {
            html += `
                <div class="col-span-2">
                    <strong>Alumnos:</strong>
                    <ul class="list-disc list-inside ml-4">
            `;
            userInfoData.alumnos.forEach(alumno => {
                if (alumno && alumno.nombre) {
                    html += `<li>${alumno.nombre} - ${alumno.nivel || 'N/A'} ${alumno.grado || 'N/A'} "${alumno.grupo || 'N/A'}"</li>`;
                }
            });
            html += `</ul></div>`;
        }

        html += `</div>`;
        userDetails.innerHTML = html;
        showElement(userInfo);
    }

    function mostrarMovimientos(movimientos) {
        if (!Array.isArray(movimientos) || !movimientosBody) return;
        
        if (movimientos.length === 0) {
            showElement(noData);
            return;
        }

        let html = '';
        movimientos.forEach(mov => {
            if (!mov) return;
            
            const tipoClass = mov.tipo === 'credito' ? 'text-green-600' : 'text-red-600';
            const montoClass = (mov.monto || 0) >= 0 ? 'text-green-600' : 'text-red-600';
            
            html += `
                <tr class="hover:bg-gray-50">
                    <td class="py-3 px-4 whitespace-nowrap text-sm text-gray-900">
                        ${mov.fecha || 'N/A'}
                    </td>
                    <td class="py-3 px-4 whitespace-nowrap text-sm font-medium ${tipoClass}">
                        ${mov.tipo_display || 'N/A'}
                    </td>
                    <td class="py-3 px-4 text-sm text-gray-700">
                        ${mov.descripcion || 'Sin descripción'}
                    </td>
                    <td class="py-3 px-4 whitespace-nowrap text-sm font-medium ${montoClass}">
                        $${Math.abs(mov.monto || 0).toFixed(2)}
                    </td>
                    <td class="py-3 px-4 whitespace-nowrap text-sm text-gray-700">
                        $${(mov.saldo_anterior || 0).toFixed(2)}
                    </td>
                    <td class="py-3 px-4 whitespace-nowrap text-sm font-bold text-blue-600">
                        $${(mov.saldo_final || 0).toFixed(2)}
                    </td>
                </tr>
            `;
        });

        movimientosBody.innerHTML = html;
        showElement(movimientosTable);
    }

    function mostrarResumen(resumenData) {
        if (!resumenData) return;
        
        const totalCreditos = document.getElementById('total-creditos');
        const totalGastos = document.getElementById('total-gastos');
        const saldoActual = document.getElementById('saldo-actual');
        
        if (totalCreditos) {
            totalCreditos.textContent = `$${(resumenData.total_creditos || 0).toFixed(2)}`;
        }
        if (totalGastos) {
            totalGastos.textContent = `$${Math.abs(resumenData.total_gastos || 0).toFixed(2)}`;
        }
        if (saldoActual) {
            saldoActual.textContent = `$${(resumenData.saldo_actual || 0).toFixed(2)}`;
        }
        
        showElement(resumen);
    }

    // Inicializar opciones
    setTimeout(() => {
        initializeOptions();
    }, 100);
});