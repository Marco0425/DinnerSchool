function dragStart(event) {
  event.dataTransfer.setData("text/plain", event.target.id);
  event.target.classList.add("dragging");
  
  // Si es una orden agrupada, también pasar los IDs de pedidos individuales
  if (event.target.dataset.pedidoIds) {
    event.dataTransfer.setData("text/pedido-ids", event.target.dataset.pedidoIds);
  }
}

function allowDrop(event) {
  event.preventDefault();
  event.target.closest('.kanban-column').classList.add("drag-over");
}

function dragLeave(event) {
  if (
    event.target.classList.contains("kanban-column") ||
    event.target.closest(".kanban-column")
  ) {
    event.target.closest('.kanban-column').classList.remove("drag-over");
  }
}

function drop(event) {
  event.preventDefault();
  const cardId = event.dataTransfer.getData("text/plain");
  const pedidoIds = event.dataTransfer.getData("text/pedido-ids");
  const draggedCard = document.getElementById(cardId);
  const targetColumn = event.currentTarget;
  
  // Remover indicador visual
  targetColumn.classList.remove("drag-over");

  // Solo permitir drag and drop para empleados
  if (!draggedCard.draggable) {
    return;
  }

  if (targetColumn && draggedCard) {
    // Encontrar el contenedor de cartas dentro de la columna
    const cardsContainer = targetColumn.querySelector('[id$="-cards"]');
    
    if (cardsContainer) {
      cardsContainer.appendChild(draggedCard);

      // Determinar nuevo status basado en el ID de la columna
      let newStatus = getStatusFromColumn(targetColumn);
      
      if (newStatus) {
        // Si es una orden agrupada, actualizar todos los pedidos
        if (pedidoIds) {
          updateGroupedOrder(pedidoIds.split(','), newStatus, draggedCard);
        } else {
          // Orden individual (lógica original)
          updateSingleOrder(cardId, newStatus, draggedCard);
        }
      }
    }
  }
}

function dragEnd(event) {
  event.target.classList.remove("dragging");
  // Limpiar todos los indicadores de drag-over
  document.querySelectorAll('.kanban-column').forEach((column) => {
    column.classList.remove("drag-over");
  });
}

// Variables globales para touch events
let draggedElement = null;
let touchStartX = 0;
let touchStartY = 0;
let isDragging = false;

// FUNCIONES PARA TOUCH EVENTS
function handleTouchStart(e) {
  e.preventDefault();
  draggedElement = this;
  const touch = e.touches[0];
  touchStartX = touch.clientX;
  touchStartY = touch.clientY;
  isDragging = false;
  
  // Agregar clase visual para indicar que se está arrastrando
  this.classList.add('opacity-50');
}

function handleTouchMove(e) {
  if (!draggedElement) return;
  
  e.preventDefault();
  const touch = e.touches[0];
  const deltaX = Math.abs(touch.clientX - touchStartX);
  const deltaY = Math.abs(touch.clientY - touchStartY);
  
  // Solo considerar como arrastre si se mueve más de 10px
  if (deltaX > 10 || deltaY > 10) {
    isDragging = true;
  }
  
  if (isDragging) {
    // Crear elemento visual que sigue el dedo
    let ghostElement = document.getElementById('touch-ghost');
    if (!ghostElement) {
      ghostElement = draggedElement.cloneNode(true);
      ghostElement.id = 'touch-ghost';
      ghostElement.style.position = 'fixed';
      ghostElement.style.pointerEvents = 'none';
      ghostElement.style.zIndex = '9999';
      ghostElement.style.opacity = '0.8';
      ghostElement.style.transform = 'scale(0.9)';
      ghostElement.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.3)';
      ghostElement.style.borderRadius = '8px';
      document.body.appendChild(ghostElement);
    }
    
    ghostElement.style.left = (touch.clientX - 50) + 'px';
    ghostElement.style.top = (touch.clientY - 50) + 'px';
    
    // Determinar sobre qué columna está el dedo
    const elementBelow = document.elementFromPoint(touch.clientX, touch.clientY);
    const column = elementBelow?.closest('.kanban-column');
    
    // Remover highlight de todas las columnas
    document.querySelectorAll('.kanban-column').forEach(col => {
      col.classList.remove('drag-over');
    });
    
    // Agregar highlight a la columna actual
    if (column) {
      column.classList.add('drag-over');
    }
  }
}

function handleTouchEnd(e) {
  if (!draggedElement) return;
  
  e.preventDefault();
  
  // Remover elemento ghost
  const ghostElement = document.getElementById('touch-ghost');
  if (ghostElement) {
    ghostElement.remove();
  }
  
  // Remover clase visual
  draggedElement.classList.remove('opacity-50');
  
  // Remover highlight de todas las columnas
  document.querySelectorAll('.kanban-column').forEach(col => {
    col.classList.remove('drag-over');
  });
  
  if (isDragging) {
    const touch = e.changedTouches[0];
    const elementBelow = document.elementFromPoint(touch.clientX, touch.clientY);
    const targetColumn = elementBelow?.closest('.kanban-column');
    
    if (targetColumn && targetColumn !== draggedElement.closest('.kanban-column')) {
      // Solo permitir si la tarjeta es draggable
      if (draggedElement.draggable) {
        // Encontrar el contenedor de cartas dentro de la columna
        const cardsContainer = targetColumn.querySelector('[id$="-cards"]');
        
        if (cardsContainer) {
          cardsContainer.appendChild(draggedElement);

          // Determinar nuevo status basado en el ID de la columna
          let newStatus = getStatusFromColumn(targetColumn);
          
          if (newStatus) {
            const cardId = draggedElement.id;
            const pedidoIds = draggedElement.dataset.pedidoIds;
            
            // Si es una orden agrupada, actualizar todos los pedidos
            if (pedidoIds) {
              updateGroupedOrder(pedidoIds.split(','), newStatus, draggedElement);
            } else {
              // Orden individual (lógica original)
              updateSingleOrder(cardId, newStatus, draggedElement);
            }
          }
        }
      }
    }
  }
  
  draggedElement = null;
  isDragging = false;
}

function getStatusFromColumn(column) {
  const columnId = column.id;
  
  // Mapear IDs de columna a status
  const statusMap = {
    'pendiente-column': 'pendiente',
    'en-preparacion-column': 'en preparacion',
    'finalizado-column': 'finalizado',
    'entregado-column': 'entregado',
    'cancelado-column': 'cancelado'
  };

  return statusMap[columnId] || null;
}

async function updateGroupedOrder(pedidoIds, newStatus, cardElement) {
  try {
    const userIdElement = document.getElementById("user-id-data");
    const userId = userIdElement ? userIdElement.dataset.userId : null;
    
    const assignedEmployeeId = 
      (newStatus === "en preparacion" || newStatus === "finalizado") ? userId : null;

    // Actualizar cada pedido individualmente
    const promises = pedidoIds.map((pedidoId) =>
      fetch("/comedor/order/update-status/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
          order_id: `order-${pedidoId}`,
          new_status: newStatus,
          assigned_employee_id: assignedEmployeeId,
        }),
      }).then((response) => response.json())
    );

    const results = await Promise.all(promises);
    const allSuccess = results.every((result) => result.success);

    if (allSuccess) {
      // Actualizar información del encargado en la tarjeta
      if (results[0].encargado) {
        const assigneeElement = cardElement.querySelector('.encargado-field');
        if (assigneeElement) {
          assigneeElement.innerHTML = `<strong>Encargado:</strong> ${results[0].encargado}`;
        }
      }
    } else {
      location.reload();
    }
  } catch (error) {
    location.reload();
  }
}

function updateSingleOrder(cardId, newStatus, cardElement) {
  const userIdElement = document.getElementById("user-id-data");
  const userId = userIdElement ? userIdElement.dataset.userId : null;
  
  const assignedEmployeeId = 
    (newStatus === "en preparacion" || newStatus === "finalizado") ? userId : null;

  fetch("/comedor/order/update-status/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      order_id: cardId,
      new_status: newStatus,
      assigned_employee_id: assignedEmployeeId,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Actualizar información del encargado
        if (data.encargado) {
          const assigneeElement = cardElement.querySelector('.order-assignee, .encargado-field');
          if (assigneeElement) {
            assigneeElement.textContent = `Encargado: ${data.encargado}`;
          }
        }
      } else {
        alert("Error al actualizar el estado: " + (data.error || ""));
      }
    })
    .catch((error) => {
      alert("Error de red al actualizar el estado");
    });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


  // Configurar drag and drop para todas las tarjetas
  const cards = document.querySelectorAll("[draggable='true']");
  cards.forEach((card) => {
    // Mouse events
    card.addEventListener("dragstart", dragStart);
    card.addEventListener("dragend", dragEnd);
    
    // Touch events
    card.addEventListener('touchstart', handleTouchStart, { passive: false });
    card.addEventListener('touchmove', handleTouchMove, { passive: false });
    card.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    // Prevenir scroll en dispositivos táctiles durante el arrastre
    card.style.touchAction = 'none';
    card.style.userSelect = 'none';
  });

    // Polling para actualizar el kanban cada 5 segundos
    function fetchAndUpdateKanban() {
      fetch("/comedor/api/pedidos-del-dia/")
        .then(response => response.json())
        .then(data => {
          updateKanbanColumns(data.orders);
        });
    }

  // Llama a la función cada 5 segundos
  setInterval(fetchAndUpdateKanban, 1000);
  // También la llama al cargar la página
  fetchAndUpdateKanban();

  // Permite actualizar el kanban inmediatamente tras crear/cancelar pedido
  window.refreshKanban = fetchAndUpdateKanban;

    // Función para actualizar las columnas del kanban
    function updateKanbanColumns(orders) {
      // Solo elimina las tarjetas canceladas/entregadas y agrega nuevas
      const columns = {
        pendiente: document.getElementById("pendiente-cards"),
        en_preparacion: document.getElementById("en-preparacion-cards"),
        finalizado: document.getElementById("finalizado-cards"),
        entregado: document.getElementById("entregado-cards")
      };
      console.log(orders);
      console.log(columns);

      // Crear un set con los IDs actuales de las órdenes (id entero)
      const currentOrderIds = new Set();
      Object.values(columns).forEach(col => {
        if (col) {
          Array.from(col.children).forEach(card => {
            if (card.id && card.id.startsWith('order-')) {
              currentOrderIds.add(parseInt(card.id.substring(6)));
            }
          });
        }
      });

      // Crear un set con los IDs de las órdenes nuevas (id entero)
      const newOrderIds = new Set(orders.map(order => order.id));

      // Eliminar tarjetas que ya no están (canceladas/entregadas)
      Object.values(columns).forEach(col => {
        if (col) {
          Array.from(col.children).forEach(card => {
            const cardId = parseInt(card.id.substring(6));
            if (!newOrderIds.has(cardId)) {
              console.log("Removing card:", cardId);
              card.remove();
            }
          });
        }
      });

      // Agregar nuevas tarjetas que no están presentes
      orders.forEach(order => {
        const col = columns[order.status];
        if (col && !currentOrderIds.has(order.id)) {
          col.innerHTML += renderOrderCard(order);
          console.log("Adding card:", order.id);
        }
      });

      // Reasigna eventos drag & drop a las nuevas tarjetas
      const cards = document.querySelectorAll("[draggable='true']");
      cards.forEach((card) => {
        card.addEventListener("dragstart", dragStart);
        card.addEventListener("dragend", dragEnd);
        card.addEventListener('touchstart', handleTouchStart, { passive: false });
        card.addEventListener('touchmove', handleTouchMove, { passive: false });
        card.addEventListener('touchend', handleTouchEnd, { passive: false });
        card.style.touchAction = 'none';
        card.style.userSelect = 'none';
      });
    }

    // Renderiza el HTML de una tarjeta de orden agrupada (simplificado)
    function renderOrderCard(order) {
      let platillosHtml = order.platillos.map(p => `
        <div class="bg-gray-50 p-2 rounded border-l-2 border-primary-red">
          <div class="flex justify-between items-start">
            <div>
              <span class="font-medium text-gray-800">${p.nombre}</span>
              ${p.cantidad > 1 ? `<span class="text-primary-red font-semibold ml-1">x${p.cantidad}</span>` : ""}
            </div>
            <span class="text-sm text-gray-600">$${p.precio.toFixed(2)}</span>
          </div>
          ${p.ingredientes && p.ingredientes.length ? `<p class="text-xs text-gray-500 mt-1"><strong>Ingredientes:</strong> ${p.ingredientes.join(", ")}</p>` : ""}
          ${p.nota ? `<p class="text-xs text-blue-600 mt-1"><strong>Nota:</strong> ${p.nota}</p>` : ""}
        </div>
      `).join("");

      return `
        <div
          id="order-${order.id}"
          class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 cursor-grab active:cursor-grabbing ${order.status === 'finalizado' || order.status === 'entregado' ? 'opacity-80' : ''}"
          draggable="${order.is_employee ? 'true' : 'false'}"
          data-pedido-ids="${order.pedido_ids.join(',')}"
        >
          <div class="flex justify-between items-start mb-3">
            <div>
              <h3 class="font-bold text-gray-900 mb-1">${order.user_name}</h3>
              <p class="text-sm text-gray-600">
                ${order.is_profesor ? '<strong>Profesor</strong>' : `<strong>${order.user_level}</strong>`}
              </p>
            </div>
            <div class="text-right">
              <p class="text-xs text-gray-500"><strong>Turno:</strong> ${order.turno}</p>
              ${order.platillos.length > 1 ? `<span class="inline-block px-2 py-1 bg-primary-red text-white text-xs rounded-full mt-1">${order.platillos.length} platillos</span>` : ""}
            </div>
          </div>
          <div class="space-y-2 mb-3">${platillosHtml}</div>
          <div class="border-t pt-2 mb-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Total items:</span>
              <span class="font-semibold">${order.total_cantidad}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Total:</span>
              <span class="font-bold text-primary-red">$${order.total_precio.toFixed(2)}</span>
            </div>
          </div>
          ${order.is_employee ? `<p class="text-xs text-gray-500 encargado-field"><strong>Encargado:</strong> ${order.encargado}</p>` : ""}
        </div>
      `;
    }

  // Configurar drop zones para las columnas
  const columns = document.querySelectorAll(".kanban-column");
  columns.forEach((column) => {
    column.addEventListener("dragover", allowDrop);
    column.addEventListener("drop", drop);
    column.addEventListener("dragleave", dragLeave);
  });

