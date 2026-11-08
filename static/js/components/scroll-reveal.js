
document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll("[data-reveal]");

    if (!elements.length) return;

    // Respect reduced motion
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        return;
    }

    // Fallback for unsupported browsers
    if (!("IntersectionObserver" in window)) {
        return;
    }

    // Enable CSS reveal system
    document.documentElement.classList.add("js-reveal-ready");

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;

            const element = entry.target;
            const delay = Number(element.dataset.revealDelay) || 0;

            element.style.setProperty("--reveal-delay", `${delay}ms`);
            element.dataset.revealed = "true";

            observer.unobserve(element);
        });
    }, {
        threshold: 0.12,
        rootMargin: "0px 0px -40px 0px"
    });

    elements.forEach(element => observer.observe(element));
});
