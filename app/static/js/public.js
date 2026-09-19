document.addEventListener("DOMContentLoaded", function () {

    // ==========================
    // AOS Animation
    // ==========================
    if (typeof AOS !== "undefined") {
        AOS.init({
            duration: 700,
            once: true
        });
    }

    // ==========================
    // Hero Swiper
    // ==========================
    if (typeof Swiper !== "undefined" && document.querySelector(".heroSwiper")) {

        new Swiper(".heroSwiper", {

            loop: true,

            effect: "fade",

            speed: 1000,

            autoplay: {
                delay: 5000,
                disableOnInteraction: false
            },

            pagination: {
                el: ".swiper-pagination",
                clickable: true
            },

            navigation: {
                nextEl: ".swiper-button-next",
                prevEl: ".swiper-button-prev"
            }

        });

    }

    // ==========================
    // Back To Top Button
    // ==========================
    const backToTop = document.getElementById("backToTop");

    if (backToTop) {

        window.addEventListener("scroll", function () {

            if (window.scrollY > 300) {
                backToTop.style.display = "block";
            } else {
                backToTop.style.display = "none";
            }

        });

        backToTop.addEventListener("click", function () {

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        });

    }

    // ==========================
    // Animated Counters
    // ==========================
    document.querySelectorAll(".counter").forEach(counter => {

        const target = parseInt(counter.dataset.target) || 0;

        let current = 0;

        const increment = target / 100;

        function updateCounter() {

            current += increment;

            if (current >= target) {

                counter.textContent = target.toLocaleString();

            } else {

                counter.textContent = Math.floor(current).toLocaleString();

                requestAnimationFrame(updateCounter);

            }

        }

        updateCounter();

    });

});