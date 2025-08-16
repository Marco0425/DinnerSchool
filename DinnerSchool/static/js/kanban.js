// Solo funcionalidad drag & drop, las tarjetas ya están en el HTML
function dragStart(event) {
  event.dataTransfer.setData("text/plain", event.target.id);
  event.target.classList.add("dragging");
}

function allowDrop(event) {
  event.preventDefault();
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
      console.log(`Nuevo estado: ${newStatus}`);
      if (newStatus) {
        fetch("/comedor/order/update-status/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ order_id: cardId, new_status: newStatus }),
        })
          .then((response) => response.json())
          .then((data) => {
            console.log("Estado actualizado:", data);
            if (!data.success) {
              alert("Error al actualizar el estado: " + (data.error || ""));
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

// Asignar listeners a las tarjetas existentes
document.addEventListener("DOMContentLoaded", function () {
  document
    .querySelectorAll('.kanban-column [draggable="true"]')
    .forEach(function (card) {
      card.addEventListener("dragstart", dragStart);
      card.addEventListener("dragend", dragEnd);
    });
});
