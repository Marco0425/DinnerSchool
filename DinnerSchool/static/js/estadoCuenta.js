document.addEventListener('DOMContentLoaded', function () {
    var userSearch = document.getElementById('user-search');
    var userSelect = document.getElementById('user-select');
    var userDropdown = document.getElementById('user-dropdown');
    var userOptions = document.getElementById('user-options');
    var noResults = document.getElementById('no-results');
    var fechaInicio = document.getElementById('fecha-inicio');
    var fechaFin = document.getElementById('fecha-fin');
    var btnFiltrar = document.getElementById('btn-filtrar');
    var loading = document.getElementById('loading');
    var movimientosTable = document.getElementById('movimientos-table');
    var movimientosBody = document.getElementById('movimientos-body');
    var noData = document.getElementById('no-data');
    var userInfo = document.getElementById('user-info');
    var userDetails = document.getElementById('user-details');
    var resumen = document.getElementById('resumen');
    var alumnoFilterWrap = document.getElementById('alumno-filter-wrap');
    var alumnoSelect = document.getElementById('alumno-select');

    // Fecha de hoy por defecto
    var hoy = new Date().toISOString().split('T')[0];
    fechaInicio.value = hoy;
    fechaFin.value = hoy;

    // --- Filtros rápidos de período ---
    function isoWeekStart(d) {
        var day = d.getDay() || 7;
        var mon = new Date(d);
        mon.setDate(d.getDate() - day + 1);
        return mon.toISOString().split('T')[0];
    }

    document.querySelectorAll('.quick-filter').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var now = new Date();
            var start, end = now.toISOString().split('T')[0];
            switch (this.dataset.period) {
                case 'today':
                    start = end;
                    break;
                case 'week':
                    start = isoWeekStart(now);
                    break;
                case 'month':
                    start = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
                    break;
                case 'year':
                    start = new Date(now.getFullYear(), 0, 1).toISOString().split('T')[0];
                    break;
            }
            fechaInicio.value = start;
            fechaFin.value = end;

            // Resaltar botón activo
            document.querySelectorAll('.quick-filter').forEach(function (b) {
                b.classList.remove('bg-primary-red', 'text-white', 'border-primary-red');
                b.classList.add('border-gray-300', 'text-gray-600');
            });
            this.classList.add('bg-primary-red', 'text-white', 'border-primary-red');
            this.classList.remove('border-gray-300', 'text-gray-600');
        });
    });

    // --- Dropdown de usuario ---
    var allOptions = [];

    function initializeOptions() {
        if (!userOptions) return;
        var options = userOptions.querySelectorAll('.user-option');
        allOptions = Array.from(options).map(function (opt) {
            return {
                element: opt,
                value: opt.dataset.value || '',
                searchText: (opt.dataset.search || '').toLowerCase(),
                tipo: opt.dataset.tipo || '',
                alumnos: JSON.parse(opt.dataset.alumnos || '[]'),
                visible: true
            };
        });
    }

    function filterOptions(searchTerm) {
        var filtered = allOptions.filter(function (opt) {
            var matches = opt.searchText.includes(searchTerm.toLowerCase());
            opt.visible = matches;
            opt.element.style.display = matches ? 'block' : 'none';
            return matches;
        });
        noResults.classList.toggle('hidden', filtered.length > 0);
        return filtered;
    }

    function populateAlumnoDropdown(alumnos) {
        alumnoSelect.innerHTML = '<option value="">Todos los alumnos</option>';
        if (alumnos && alumnos.length > 0) {
            alumnos.forEach(function (a) {
                var opt = document.createElement('option');
                opt.value = a.id;
                opt.textContent = a.nombre;
                alumnoSelect.appendChild(opt);
            });
            alumnoFilterWrap.classList.remove('hidden');
        } else {
            alumnoFilterWrap.classList.add('hidden');
        }
    }

    userSearch.addEventListener('input', function () {
        userDropdown.classList.remove('hidden');
        if (this.value.length > 0) {
            filterOptions(this.value);
        } else {
            allOptions.forEach(function (opt) {
                opt.element.style.display = 'block';
                opt.visible = true;
            });
            noResults.classList.add('hidden');
        }
    });

    userSearch.addEventListener('focus', function () {
        userDropdown.classList.remove('hidden');
        initializeOptions();
    });

    document.addEventListener('click', function (e) {
        if (!userSearch.contains(e.target) && !userDropdown.contains(e.target)) {
            userDropdown.classList.add('hidden');
        }
    });

    userOptions.addEventListener('click', function (e) {
        var option = e.target.closest('.user-option');
        if (!option) return;
        var value = option.dataset.value;
        var text = option.querySelector('.font-medium').textContent;
        userSearch.value = text;
        userSelect.value = value;
        userDropdown.classList.add('hidden');

        // Mostrar/ocultar dropdown de alumnos
        var alumnos = JSON.parse(option.dataset.alumnos || '[]');
        populateAlumnoDropdown(alumnos);
    });

    // --- Botón Filtrar ---
    btnFiltrar.addEventListener('click', function () {
        var userId = userSelect.value;
        var inicio = fechaInicio.value;
        var fin = fechaFin.value;

        if (!userId) { alert('Por favor selecciona un usuario'); return; }
        if (!inicio || !fin) { alert('Por favor selecciona un rango de fechas'); return; }
        if (new Date(inicio) > new Date(fin)) { alert('La fecha de inicio no puede ser mayor a la fecha fin'); return; }

        cargarMovimientos(userId, inicio, fin, alumnoSelect.value || '');
    });

    function cargarMovimientos(userId, inicio, fin, alumnoId) {
        showEl(loading);
        hideEl(movimientosTable);
        hideEl(noData);
        hideEl(userInfo);
        hideEl(resumen);

        var csrfToken = '';
        var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) csrfToken = csrfInput.value;
        if (!csrfToken) {
            var cookie = document.cookie.split(';').find(function (c) { return c.trim().startsWith('csrftoken='); });
            if (cookie) csrfToken = cookie.split('=')[1];
        }
        if (!csrfToken) { hideEl(loading); alert('Error: Token de seguridad no encontrado'); return; }

        var formData = new FormData();
        formData.append('user_id', userId);
        formData.append('fecha_inicio', inicio);
        formData.append('fecha_fin', fin);
        formData.append('csrfmiddlewaretoken', csrfToken);
        if (alumnoId) formData.append('alumno_id', alumnoId);

        fetch('/comedor/get-movimientos/', {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(function (data) {
            hideEl(loading);
            if (data && data.success) {
                mostrarUserInfo(data.user_info);
                mostrarMovimientos(data.movimientos);
                mostrarResumen(data.resumen);
            } else {
                alert(data.message || 'Error al cargar los movimientos');
            }
        })
        .catch(function (err) {
            hideEl(loading);
            alert('Error al cargar los movimientos: ' + err.message);
        });
    }

    // --- Helpers ---
    function showEl(el) { if (el) el.classList.remove('hidden'); }
    function hideEl(el) { if (el) el.classList.add('hidden'); }

    function mostrarUserInfo(info) {
        if (!info || !userDetails) return;
        var html = '<div class="grid grid-cols-2 gap-4"><div><strong>Nombre:</strong> ' + (info.nombre || 'N/A') + '</div><div><strong>Tipo:</strong> ' + (info.tipo || 'N/A') + '</div>';
        if (info.alumnos && info.alumnos.length > 0) {
            html += '<div class="col-span-2"><strong>Alumnos:</strong><ul class="list-disc list-inside ml-4">';
            info.alumnos.forEach(function (a) {
                if (a && a.nombre) html += '<li>' + a.nombre + ' - ' + (a.nivel || 'N/A') + ' ' + (a.grado || 'N/A') + ' "' + (a.grupo || 'N/A') + '"</li>';
            });
            html += '</ul></div>';
        }
        html += '</div>';
        userDetails.innerHTML = html;
        showEl(userInfo);
    }

    function mostrarMovimientos(movimientos) {
        if (!Array.isArray(movimientos) || !movimientosBody) return;
        if (movimientos.length === 0) { showEl(noData); return; }
        var html = '';
        movimientos.forEach(function (mov) {
            if (!mov) return;
            var montoClass = (mov.monto || 0) >= 0 ? 'text-green-600' : 'text-red-600';
            var tipoClass = montoClass;
            html += '<tr class="hover:bg-gray-50">' +
                '<td class="py-3 px-4 whitespace-nowrap text-sm text-gray-900">' + (mov.fecha || 'N/A') + '</td>' +
                '<td class="py-3 px-4 whitespace-nowrap text-sm font-medium ' + tipoClass + '">' + (mov.tipo_display || 'N/A') + '</td>' +
                '<td class="py-3 px-4 text-sm text-gray-700">' + (mov.descripcion || 'Sin descripción') + '</td>' +
                '<td class="py-3 px-4 whitespace-nowrap text-sm font-medium ' + montoClass + '">$' + Math.abs(mov.monto || 0).toFixed(2) + '</td>' +
                '<td class="py-3 px-4 whitespace-nowrap text-sm text-gray-700">$' + (mov.saldo_anterior || 0).toFixed(2) + '</td>' +
                '<td class="py-3 px-4 whitespace-nowrap text-sm font-bold text-blue-600">$' + (mov.saldo_final || 0).toFixed(2) + '</td>' +
                '</tr>';
        });
        movimientosBody.innerHTML = html;
        showEl(movimientosTable);
    }

    function mostrarResumen(resumenData) {
        if (!resumenData) return;
        var tc = document.getElementById('total-creditos');
        var tg = document.getElementById('total-gastos');
        var sa = document.getElementById('saldo-actual');
        if (tc) tc.textContent = '$' + (resumenData.total_creditos || 0).toFixed(2);
        if (tg) tg.textContent = '$' + Math.abs(resumenData.total_gastos || 0).toFixed(2);
        if (sa) sa.textContent = '$' + (resumenData.saldo_actual || 0).toFixed(2);
        showEl(resumen);
    }

    setTimeout(initializeOptions, 100);
});
