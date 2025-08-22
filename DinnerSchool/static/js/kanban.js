function dragStart(event) {
  event.dataTransfer.setData("text/plain", event.target.id);
  event.target.classList.add("dragging");
}

function allowDrop(event) {
  event.preventDefault();
  const isEmployee = event.target.closest('[draggable="true"]') !== null;
  if (isEmployee) {
    if (
      event.target.classList.contains("kanban-column") ||
      event.target.closest(".kanban-column")
    ) {
      const column = event.target.classList.contains("kanban-column")
        ? event.target
        : event.target.closest(".kanban-column");
      column.classList.add("drag-over");
    }
  }
}

function dragLeave(event) {
  if (
    event.target.classList.contains("kanban-column") ||
    event.target.closest(".kanban-column")
  ) {
    const column = event.target.classList.contains("kanban-column")
      ? event.target
      : event.target.closest(".kanban-column");
    column.classList.remove("drag-over");
  }
}

function drop(event) {
  event.preventDefault();
  const cardId = event.dataTransfer.getData("text/plain");
  const draggedCard = document.getElementById(cardId);
  const isEmployee = draggedCard.draggable;

  // Solo permitimos el drop si el usuario es un empleado
  if (!isEmployee) {
    return;
  }

  let targetColumn = event.target;
  while (targetColumn && !targetColumn.classList.contains("kanban-column")) {
    targetColumn = targetColumn.parentElement;
  }

  if (targetColumn && draggedCard) {
    targetColumn.classList.remove("drag-over");
    const cardsContainer = targetColumn.querySelector('[id$="-cards"]');
    if (cardsContainer) {
      cardsContainer.appendChild(draggedCard);

      // Obtener el nuevo status según la columna
      let newStatus = null;
      if (targetColumn.id === "pendiente-column") newStatus = "pendiente";
      else if (targetColumn.id === "en-preparacion-column")
        newStatus = "en preparacion";
      else if (targetColumn.id === "entregado-column") newStatus = "entregado";
      else if (targetColumn.id === "finalizado-column")
        newStatus = "finalizado";

      if (newStatus) {
        // Asignar el ID del usuario como encargado si la tarjeta se movió a 'en preparacion' o 'finalizado'
        const userId = "{{ user.id }}";
        const assignedEmployeeId =
          newStatus === "en preparacion" || newStatus === "finalizado"
            ? userId
            : null;

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
            console.log("Estado y encargado actualizados:", data);
            if (!data.success) {
              alert("Error al actualizar el estado: " + (data.error || ""));
            } else {
              // Opcional: actualizar el HTML para mostrar el nombre del encargado
              const encargadoElement = draggedCard.querySelector("p strong");
              if (encargadoElement && assignedEmployeeId) {
                encargadoElement.textContent = `Encargado: ${assignedEmployeeId}`;
              }
            }
          })
          .catch((err) => {
            alert("Error de red al actualizar el estado");
          });
      }
    }
  }
}

function dragEnd(event) {
  event.target.classList.remove("dragging");
  const columns = document.querySelectorAll(".kanban-column");
  columns.forEach((column) => column.classList.remove("drag-over"));
}

function getCookie(name) {
  const cookieValue = document.cookie.match(
    "(^|;)\\s*" + name + "\\s*=\\s*([^;]+)"
  );
  return cookieValue ? cookieValue.pop() : "";
}

// Asignar listeners a las tarjetas existentes
document.addEventListener("DOMContentLoaded", function () {
  document
    .querySelectorAll('.kanban-column [draggable="true"]')
    .forEach(function (card) {
      card.addEventListener("dragstart", dragStart);
      card.addEventListener("dragend", dragEnd);
    });
});
