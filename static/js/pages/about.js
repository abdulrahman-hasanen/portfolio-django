function initAboutPage() {
    console.log("About JS Loaded");

    initAboutCountUp();
    initAboutReveal();
    initAboutGsap();
    initAboutPhotoTilt();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAboutPage);
} else {
    initAboutPage();
}

/* =========================================================
   COUNT-UP - ABOUT DETAILS
========================================================= */

function initAboutCountUp() {
    const counters = document.querySelectorAll("[data-count-up]");

    console.log("Counters Found:", counters.length);

    if (!counters.length) return;

    const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    const setFinalValues = () => {
        counters.forEach((counter) => {
            counter.textContent = counter.dataset.countUp;
        });
    };

    if (
        prefersReducedMotion ||
        !("IntersectionObserver" in window)
    ) {
        setFinalValues();
        return;
    }

    const animateCounter = (counter) => {
        const target = Number(counter.dataset.countUp);

        if (!Number.isFinite(target)) return;

        const duration = target >= 1000 ? 1500 : 1000;
        const startTime = performance.now();

        const tick = (now) => {
            const progress = Math.min(
                (now - startTime) / duration,
                1
            );

            const eased = 1 - Math.pow(1 - progress, 3);

            const currentValue = Math.round(target * eased);

            counter.textContent = currentValue;

            if (progress < 1) {
                requestAnimationFrame(tick);
            } else {
                counter.textContent = currentValue;
            }
        };

        requestAnimationFrame(tick);
    };

    const observer = new IntersectionObserver(
        (entries, observerInstance) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;

                animateCounter(entry.target);
                observerInstance.unobserve(entry.target);
            });
        },
        {
            threshold: 0.2
        }
    );

    counters.forEach((counter) => {
        observer.observe(counter);
    });
}