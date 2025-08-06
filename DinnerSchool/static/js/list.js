// Mostrar/ocultar botón eliminar según selección
const selectAll = document.getElementById("selectAll");
const rowCheckboxes = document.querySelectorAll(".rowCheckbox");
const deleteBtnContainer = document.getElementById("deleteBtnContainer");
function updateDeleteBtn() {
  const anyChecked = Array.from(rowCheckboxes).some((cb) => cb.checked);
  deleteBtnContainer.style.display = anyChecked ? "flex" : "none";
}
selectAll.addEventListener("change", function () {
  rowCheckboxes.forEach((cb) => {
    cb.checked = selectAll.checked;
  });
  updateDeleteBtn();
});
rowCheckboxes.forEach((cb) => {
  cb.addEventListener("change", function () {
    if (!cb.checked) selectAll.checked = false;
    else if (Array.from(rowCheckboxes).every((cb) => cb.checked))
      selectAll.checked = true;
    updateDeleteBtn();
  });
});
