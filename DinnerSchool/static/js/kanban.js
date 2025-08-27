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

document.addEventListener("DOMContentLoaded", function () {
  // Configurar drag and drop para todas las tarjetas
  const cards = document.querySelectorAll("[draggable='true']");
  cards.forEach((card) => {
    card.addEventListener("dragstart", dragStart);
    card.addEventListener("dragend", dragEnd);
  });

  // Configurar drop zones para las columnas
  const columns = document.querySelectorAll(".kanban-column");
  columns.forEach((column) => {
    column.addEventListener("dragover", allowDrop);
    column.addEventListener("drop", drop);
    column.addEventListener("dragleave", dragLeave);
  });

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
});
