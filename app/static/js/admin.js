document.addEventListener("DOMContentLoaded", function () {

    /*
     * =====================================================
     * SIDEBAR TOGGLE
     * =====================================================
     */

    const sidebarToggle =
        document.querySelector("[data-sidebar-toggle]");

    const sidebar =
        document.querySelector(".sidebar");

    if (sidebarToggle && sidebar) {

        sidebarToggle.addEventListener("click", function () {

            sidebar.classList.toggle("show");

        });

    }


    /*
     * =====================================================
     * AUTO DISMISS ALERTS
     * =====================================================
     */

    const alerts =
        document.querySelectorAll(".alert[data-auto-dismiss]");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            alert.style.transition = "opacity 0.4s ease";

            alert.style.opacity = "0";

            setTimeout(function () {

                alert.remove();

            }, 400);

        }, 5000);

    });


    /*
     * =====================================================
     * DELETE CONFIRMATION
     * =====================================================
     */

    const deleteButtons =
        document.querySelectorAll("[data-confirm-delete]");

    deleteButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const message =
                button.dataset.confirmDelete ||
                "Are you sure you want to delete this item?";

            if (!confirm(message)) {

                event.preventDefault();

            }

        });

    });


    /*
     * =====================================================
     * IMAGE PREVIEW
     * =====================================================
     */

    const imageInputs =
        document.querySelectorAll(
            'input[type="file"][data-preview]'
        );

    imageInputs.forEach(function (input) {

        input.addEventListener("change", function () {

            const previewId =
                input.dataset.preview;

            const preview =
                document.getElementById(previewId);

            if (!preview || !input.files.length) {
                return;
            }

            const file =
                input.files[0];

            if (!file.type.startsWith("image/")) {
                return;
            }

            const reader =
                new FileReader();

            reader.onload = function (event) {

                preview.src =
                    event.target.result;

                preview.style.display =
                    "block";

            };

            reader.readAsDataURL(file);

        });

    });


    /*
     * =====================================================
     * TABLE SEARCH
     * =====================================================
     */

    const searchInputs =
        document.querySelectorAll(
            "[data-table-search]"
        );

    searchInputs.forEach(function (input) {

        const tableSelector =
            input.dataset.tableSearch;

        const table =
            document.querySelector(tableSelector);

        if (!table) {
            return;
        }

        input.addEventListener("input", function () {

            const search =
                input.value.toLowerCase().trim();

            const rows =
                table.querySelectorAll("tbody tr");

            rows.forEach(function (row) {

                const text =
                    row.textContent.toLowerCase();

                row.style.display =
                    text.includes(search)
                        ? ""
                        : "none";

            });

        });

    });

});