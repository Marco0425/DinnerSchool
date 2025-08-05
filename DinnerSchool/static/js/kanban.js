// Datos de prueba para los pedidos
let orders = [
  {
    id: "order-1",
    platillo: "Hamburguesa Clásica",
    ingredientes: "Sin cebolla, extra queso",
    nota: "Para llevar",
    alumno: "Ana García",
    nivel: "Primaria",
    turno: "Comida",
    status: "pendiente",
  },
  {
    id: "order-2",
    platillo: "Ensalada César",
    ingredientes: "Aderezo aparte",
    nota: "",
    alumno: "Carlos Martínez",
    nivel: "Secundaria",
    turno: "Comida",
    status: "en preparacion",
  },
  {
    id: "order-3",
    platillo: "Sándwich de Pavo",
    ingredientes: "Pan integral, sin tomate",
    nota: "Alérgico a los cacahuates",
    alumno: "Sofía Rodríguez",
    nivel: "Primaria",
    turno: "Desayuno",
    status: "pendiente",
  },
  {
    id: "order-4",
    platillo: "Tacos Dorados",
    ingredientes: "Con crema y queso",
    nota: "",
    alumno: "Diego Hernández",
    nivel: "Secundaria",
    turno: "Comida",
    status: "finalizado",
  },
  {
    id: "order-5",
    platillo: "Fruta Picada",
    ingredientes: "Solo manzana y uva",
    nota: "Para recoger a las 10:00 AM",
    alumno: "Laura González",
    nivel: "Primaria",
    turno: "Desayuno",
    status: "pendiente",
  },
  {
    id: "order-6",
    platillo: "Pasta Alfredo",
    ingredientes: "Extra pollo",
    nota: "",
    alumno: "Juan Pérez",
    nivel: "Preparatoria",
    turno: "Comida",
    status: "en preparacion",
  },
  {
    id: "order-7",
    platillo: "Pizza de Pepperoni",
    ingredientes: "Doble queso",
    nota: "Cortar en 8 rebanadas",
    alumno: "María López",
    nivel: "Secundaria",
    turno: "Comida",
    status: "pendiente",
  },
  {
    id: "order-8",
    platillo: "Jugo de Naranja",
    ingredientes: "Natural, sin azúcar",
    nota: "Con hielo",
    alumno: "Pedro Ramírez",
    nivel: "Primaria",
    turno: "Desayuno",
    status: "en preparacion",
  },
  {
    id: "order-9",
    platillo: "Burrito de Res",
    ingredientes: "Sin frijoles",
    nota: "",
    alumno: "Valeria Castro",
    nivel: "Preparatoria",
    turno: "Comida",
    status: "pendiente",
  },
  {
    id: "order-10",
    platillo: "Agua de Horchata",
    ingredientes: "Poca azúcar",
    nota: "Vaso grande",
    alumno: "Ricardo Soto",
    nivel: "Secundaria",
    turno: "Comida",
    status: "finalizado",
  },
  {
    id: "order-11",
    platillo: "Hot Dog",
    ingredientes: "Con ketchup y mostaza",
    nota: "Sin pepinillos",
    alumno: "Fernanda Díaz",
    nivel: "Primaria",
    turno: "Comida",
    status: "pendiente",
  },
  {
    id: "order-12",
    platillo: "Licuado de Plátano",
    ingredientes: "Con leche de almendras",
    nota: "",
    alumno: "Jorge Torres",
    nivel: "Preparatoria",
    turno: "Desayuno",
    status: "en preparacion",
  },
  {
    id: "order-13",
    platillo: "Cereal con Leche",
    ingredientes: "Leche entera",
    nota: "Tazón grande",
    alumno: "Gabriela Solís",
    nivel: "Kinder",
    turno: "Desayuno",
    status: "pendiente",
  },
  {
    id: "order-14",
    platillo: "Mini Pizzas",
    ingredientes: "Solo queso",
    nota: "Sin orilla",
    alumno: "Roberto Vega",
    nivel: "Kinder",
    turno: "Comida",
    status: "pendiente",
  },
  {
    id: "order-15",
    platillo: "Yogurt con Granola",
    ingredientes: "Yogurt natural",
    nota: "",
    alumno: "Andrea Luna",
    nivel: "Primaria",
    turno: "Desayuno",
    status: "finalizado",
  },
  {
    id: "order-16",
    platillo: "Sopa de Verduras",
    ingredientes: "Sin sal",
    nota: "Tibia",
    alumno: "Luis Mendoza",
    nivel: "Secundaria",
    turno: "Comida",
    status: "pendiente",
  },
  {
    id: "order-17",
    platillo: "Torta de Jamón",
    ingredientes: "Sin mayonesa",
    nota: "Con aguacate",
    alumno: "Paula Herrera",
    nivel: "Preparatoria",
    turno: "Comida",
    status: "en preparacion",
  },
];

// Definir el orden de prioridad de los niveles educativos
const nivelOrder = {
  Kinder: 1,
  Primaria: 2,
  Secundaria: 3,
  Preparatoria: 4,
};

/**
 * Renderiza las tarjetas de pedidos en sus respectivas columnas.
 */
function renderOrders() {
  // Limpia las columnas antes de volver a renderizar
  document.getElementById("pendiente-cards").innerHTML = "";
  document.getElementById("en-preparacion-cards").innerHTML = "";
  document.getElementById("finalizado-cards").innerHTML = "";

  // Ordenar los pedidos por nivel educativo antes de renderizar
  const sortedOrders = [...orders].sort((a, b) => {
    return nivelOrder[a.nivel] - nivelOrder[b.nivel];
  });

  sortedOrders.forEach((order) => {
    const card = document.createElement("div");
    card.id = order.id;
    card.className = `bg-white p-4 rounded-lg shadow-sm border border-gray-200 cursor-grab active:cursor-grabbing ${
      order.status === "finalizado" ? "opacity-80" : ""
    }`;
    card.setAttribute("draggable", true); // Hace la tarjeta arrastrable

    // Contenido de la tarjeta
    card.innerHTML = `
                    <h3 class="font-bold text-gray-900 mb-1">${
                      order.platillo
                    }</h3>
                    <p class="text-sm text-gray-600"><strong>Alumno:</strong> ${
                      order.alumno
                    }</p>
                    <p class="text-xs text-gray-500"><strong>Nivel:</strong> ${
                      order.nivel
                    } | <strong>Turno:</strong> ${order.turno}</p>
                    ${
                      order.ingredientes
                        ? `<p class="text-xs text-gray-500"><strong>Ingredientes:</strong> ${order.ingredientes}</p>`
                        : ""
                    }
                    ${
                      order.nota
                        ? `<p class="text-xs text-gray-500"><strong>Nota:</strong> ${order.nota}</p>`
                        : ""
                    }
                `;

    // Añade la tarjeta a la columna correcta, verificando que el elemento exista
    const targetElement = document.getElementById(`${order.status}-cards`);
    if (targetElement) {
      targetElement.appendChild(card);
    } else {
      console.error(
        `Error: Elemento con ID ${order.status}-cards no encontrado. Asegúrate de que el ID del estado en los datos de prueba coincida con el ID de la columna Kanban.`
      );
    }

    // Añade event listeners para el arrastrar
    card.addEventListener("dragstart", dragStart);
    card.addEventListener("dragend", dragEnd);
  });
}

/**
 * Maneja el inicio del arrastre de una tarjeta.
 * @param {DragEvent} event
 */
function dragStart(event) {
  event.dataTransfer.setData("text/plain", event.target.id); // Guarda el ID de la tarjeta que se arrastra
  event.target.classList.add("dragging"); // Añade clase para feedback visual
}

/**
 * Permite soltar elementos en un área.
 * @param {DragEvent} event
 */
function allowDrop(event) {
  event.preventDefault(); // Necesario para permitir el drop
  // Añade clase para feedback visual al arrastrar sobre la columna
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

/**
 * Maneja el evento de arrastrar y salir de un área.
 * @param {DragEvent} event
 */
function dragLeave(event) {
  // Elimina clase de feedback visual al salir de la columna
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

/**
 * Maneja el soltar de una tarjeta en una columna.
 * @param {DragEvent} event
 */
function drop(event) {
  event.preventDefault();
  const cardId = event.dataTransfer.getData("text/plain");
  const draggedCard = document.getElementById(cardId);

  // Determina la columna de destino
  let targetColumn = event.target;
  while (targetColumn && !targetColumn.classList.contains("kanban-column")) {
    targetColumn = targetColumn.parentElement;
  }

  if (targetColumn) {
    // Elimina la clase de feedback visual
    targetColumn.classList.remove("drag-over");

    // Obtiene el nuevo status de la columna de destino
    const newStatus = targetColumn.id.replace("-column", "");

    // Actualiza el estado del pedido en los datos
    const orderIndex = orders.findIndex((order) => order.id === cardId);
    if (orderIndex > -1) {
      orders[orderIndex].status = newStatus;
    }

    // Vuelve a renderizar todas las tarjetas para reflejar el cambio
    renderOrders();
  }
}

/**
 * Maneja el final del arrastre de una tarjeta.
 * @param {DragEvent} event
 */
function dragEnd(event) {
  event.target.classList.remove("dragging"); // Elimina la clase de arrastre
  const columns = document.querySelectorAll(".kanban-column");
  columns.forEach((column) => column.classList.remove("drag-over"));
}

// Renderiza los pedidos cuando la página carga
document.addEventListener("DOMContentLoaded", renderOrders);
