(function () {
  function playBeep() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = ctx.createOscillator();
      const gain = ctx.createGain();
      oscillator.connect(gain);
      gain.connect(ctx.destination);
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(880, ctx.currentTime);
      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
      oscillator.start();
      oscillator.stop(ctx.currentTime + 0.5);
    } catch (e) {
      // Autoplay bloqueado hasta que el usuario interactúe con la página; no es crítico.
    }
  }

  function ensureToastContainer() {
    let container = document.getElementById('kanban-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'kanban-toast-container';
      container.style.cssText =
        'position:fixed; top:1rem; right:1rem; z-index:9999; display:flex; flex-direction:column; gap:0.5rem;';
      document.body.appendChild(container);
    }
    return container;
  }

  function showToast(data) {
    // Todo el contenido dinámico (titulo/turno/total pueden venir de texto libre
    // como el nombre de cliente de una venta directa) se inserta con textContent,
    // nunca con innerHTML, para no abrir una vía de XSS almacenado hacia otros admins.
    const container = ensureToastContainer();
    const toast = document.createElement('div');
    toast.style.cssText =
      'background:#fff; border-left:4px solid #dc2626; box-shadow:0 4px 12px rgba(0,0,0,0.15); border-radius:8px; padding:12px 16px; min-width:260px; font-family:inherit;';

    const header = document.createElement('div');
    header.style.cssText = 'display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;';

    const strong = document.createElement('strong');
    strong.style.color = '#111827';
    strong.textContent = 'Nuevo pedido';

    const badge = document.createElement('span');
    if (data.es_venta_directa) {
      badge.style.cssText = 'background:#dcfce7;color:#166534;padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:600;';
      badge.textContent = 'Venta Directa';
    } else {
      badge.style.cssText = 'background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:9999px;font-size:11px;font-weight:600;';
      badge.textContent = data.subtitulo || 'Pedido';
    }
    header.appendChild(strong);
    header.appendChild(badge);

    const titulo = document.createElement('div');
    titulo.style.cssText = 'color:#374151; font-size:14px;';
    titulo.textContent = data.titulo;

    const detalle = document.createElement('div');
    detalle.style.cssText = 'color:#6b7280; font-size:12px; margin-top:2px;';
    detalle.textContent = `Turno: ${data.turno} — Total: $${data.total}`;

    toast.appendChild(header);
    toast.appendChild(titulo);
    toast.appendChild(detalle);
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.transition = 'opacity 0.4s';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 400);
    }, 6000);
  }

  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/kanban/`);

    socket.onmessage = function (event) {
      const data = JSON.parse(event.data);
      playBeep();
      showToast(data);
      if (typeof window.checkForNewOrders === 'function') {
        window.checkForNewOrders();
      }
    };

    socket.onclose = function () {
      // Reintenta la conexión si se cae (red, redeploy, etc.)
      setTimeout(connect, 3000);
    };

    socket.onerror = function () {
      socket.close();
    };
  }

  document.addEventListener('DOMContentLoaded', connect);
})();
