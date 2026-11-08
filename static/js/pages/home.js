/* =====================================================
   HOME PAGE - Contact form
   - Live character counter
   - AJAX submit (falls back to a normal POST without JS)
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("[data-contact-form]");
    if (!form) return;

    const message = document.getElementById("contact-message");
    const counter = document.getElementById("message-counter");
    const status = document.getElementById("contact-status");
    const submit = document.getElementById("contact-submit");
    const submitText = document.getElementById("contact-submit-text");

    const STATUS_BASE = "rounded-lg border px-3 py-2 text-xs leading-6 ";
    const STATUS_OK = "border-emerald-400/30 bg-emerald-500/10 text-emerald-200";
    const STATUS_ERROR = "border-red-400/30 bg-red-500/10 text-red-200";


    function updateCounter() {
        if (!message || !counter) return;
        counter.textContent = `${message.value.length} / ${message.maxLength}`;
    }

    function showStatus(text, ok) {
        if (!status) return;
        status.className = STATUS_BASE + (ok ? STATUS_OK : STATUS_ERROR);
        status.textContent = text;
    }

    function setBusy(busy) {
        if (submit) submit.disabled = busy;
        if (submitText) submitText.textContent = busy ? "Sending..." : "Send Message";
    }


    if (message) {
        message.addEventListener("input", updateCounter);
        updateCounter();
    }

    form.addEventListener("submit", async event => {

        // Native validation first (form is novalidate so we control messages)
        if (!form.checkValidity()) {
            event.preventDefault();
            form.reportValidity();
            return;
        }

        // No fetch support: let the browser do a normal POST
        if (!window.fetch) return;

        event.preventDefault();
        setBusy(true);

        try {
            const response = await fetch(form.dataset.endpoint || form.action, {
                method: "POST",
                body: new FormData(form),
                headers: { "X-Requested-With": "XMLHttpRequest" },
                credentials: "same-origin"
            });

            const data = await response.json();

            showStatus(data.message || "Something went wrong.", Boolean(data.ok));

            if (data.ok) {
                form.reset();
                updateCounter();
            }

        } catch (error) {
            showStatus("Network error. Please try again.", false);
        } finally {
            setBusy(false);
        }
    });

});
