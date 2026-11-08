
/* =====================================================
   FLOATING ACTIONS
   - Back To Top Visibility
   - Smooth Scroll
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    const backToTop = document.getElementById("back-to-top");

    if (!backToTop) return;


    // Configuration
    const SCROLL_THRESHOLD = 350;

    let ticking = false;


    // =================================================
    // Update Back To Top Visibility
    // =================================================

    function updateBackToTop() {

        const shouldShow = window.scrollY > SCROLL_THRESHOLD;

        backToTop.dataset.visible = String(shouldShow);

        backToTop.disabled = !shouldShow;

        backToTop.setAttribute(
            "aria-hidden",
            String(!shouldShow)
        );

    }


    // =================================================
    // Optimized Scroll Listener
    // =================================================

    window.addEventListener("scroll", () => {

        if (ticking) return;

        ticking = true;

        window.requestAnimationFrame(() => {

            updateBackToTop();

            ticking = false;

        });

    }, { passive: true });


    // =================================================
    // Scroll To Top
    // =================================================

    backToTop.addEventListener("click", () => {

        const prefersReducedMotion = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;

        window.scrollTo({
            top: 0,
            behavior: prefersReducedMotion ? "auto" : "smooth"
        });

    });


    // Initial State
    updateBackToTop();

});
