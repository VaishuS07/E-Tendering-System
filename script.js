document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const requiredFields = form.querySelectorAll("[required]");

            let valid = true;

            requiredFields.forEach(function (field) {

                if (field.value.trim() === "") {
                    valid = false;
                    field.style.border = "2px solid red";
                } else {
                    field.style.border = "";
                }

            });

            if (!valid) {
                event.preventDefault();
                alert("Please fill all required fields.");
            }

        });

    });


    const deleteButtons = document.querySelectorAll(".delete-btn");

    deleteButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const result = confirm(
                "Are you sure you want to delete this record?"
            );

            if (!result) {
                event.preventDefault();
            }

        });

    });


    const amountFields = document.querySelectorAll(
        'input[name="tender_amount"], input[name="bid_amount"]'
    );

    amountFields.forEach(function (field) {

        field.addEventListener("input", function () {

            if (parseFloat(field.value) < 0) {
                field.value = "";
                alert("Amount cannot be negative.");
            }

        });

    });


    const deadline = document.querySelector(
        'input[name="deadline"]'
    );

    if (deadline) {

        const today = new Date().toISOString().split("T")[0];

        deadline.setAttribute("min", today);

    }

});