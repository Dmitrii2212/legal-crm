for (const formset of document.querySelectorAll("[data-formset]")) {
    const total = formset.querySelector("input[name$='-TOTAL_FORMS']");
    const maximum = Number(formset.dataset.formsetMax);
    const rows = formset.querySelector("[data-formset-rows]");
    const prototype = formset.querySelector("[data-formset-prototype]");
    const addButton = formset.querySelector("[data-formset-add]");

    addButton.hidden = false;
    addButton.disabled = Number(total.value) >= maximum;
    addButton.addEventListener("click", () => {
        const index = Number(total.value);
        rows.insertAdjacentHTML("beforeend", prototype.innerHTML.replaceAll("__prefix__", String(index)));
        total.value = index + 1;
        addButton.disabled = Number(total.value) >= maximum;
        rows.lastElementChild.querySelector("input:not([type=hidden])")?.focus();
    });

    function updateDeletedRow(checkbox) {
        const row = checkbox.closest("[data-formset-row]");
        for (const field of row.querySelectorAll("input:not([type=hidden]), select, textarea")) {
            if (field !== checkbox) {
                field.disabled = checkbox.checked;
            }
        }
    }

    for (const checkbox of rows.querySelectorAll("input[name$='-DELETE']:checked")) {
        updateDeletedRow(checkbox);
    }
    rows.addEventListener("change", (event) => {
        if (event.target.matches("input[name$='-DELETE']")) {
            updateDeletedRow(event.target);
        }
    });
}
