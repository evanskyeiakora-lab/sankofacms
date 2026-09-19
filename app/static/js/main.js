/*
=========================================================
 Apex Citizens of Ghana CMS
 Main JavaScript File
=========================================================
*/

document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // Sticky Navbar
    // ==========================================
    const navbar = document.querySelector(".navbar");

    if (navbar) {
        window.addEventListener("scroll", function () {
            if (window.scrollY > 50) {
                navbar.classList.add("sticky-top", "shadow-sm");
            } else {
                navbar.classList.remove("shadow-sm");
            }
        });
    }

    // ==========================================
    // Scroll To Top Button
    // ==========================================
    const scrollBtn = document.getElementById("scrollTop");

    if (scrollBtn) {

        window.addEventListener("scroll", function () {

            if (window.pageYOffset > 300) {
                scrollBtn.classList.add("show");
            } else {
                scrollBtn.classList.remove("show");
            }

        });

        scrollBtn.addEventListener("click", function () {

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        });

    }

    // ==========================================
    // Hero Swiper Slider
    // ==========================================
    if (document.querySelector(".heroSwiper")) {

        new Swiper(".heroSwiper", {

            loop: true,

            speed: 1000,

            autoplay: {
                delay: 5000,
                disableOnInteraction: false
            },

            effect: "fade",

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

    // ==========================================
    // Counter Animation
    // ==========================================
    const counters = document.querySelectorAll(".counter");

    counters.forEach(counter => {

        const target = Number(counter.dataset.target);

        if (!target) return;

        let current = 0;

        const increment = Math.ceil(target / 100);

        const update = () => {

            current += increment;

            if (current >= target) {

                counter.innerText = target;

            } else {

                counter.innerText = current;

                requestAnimationFrame(update);

            }

        };

        update();

    });

    // ==========================================
    // Smooth Scrolling
    // ==========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {

        anchor.addEventListener("click", function (e) {

            const target = document.querySelector(this.getAttribute("href"));

            if (target) {

                e.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth"
                });

            }

        });

    });

    // ==========================================
    // Active Navigation Link
    // ==========================================
    const currentPath = window.location.pathname;

    document.querySelectorAll(".navbar-nav .nav-link").forEach(link => {

        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }

    });

    // ==========================================
    // Fade-in Animation
    // ==========================================
    const fadeElements = document.querySelectorAll(".fade-up");

    if ("IntersectionObserver" in window) {

        const observer = new IntersectionObserver(entries => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {

                    entry.target.classList.add("show");

                    observer.unobserve(entry.target);

                }

            });

        });

        fadeElements.forEach(el => observer.observe(el));

    }

});

// ==========================================
// AOS Animation
// ==========================================
if (typeof AOS !== "undefined") {

    AOS.init({
        duration: 800,
        once: true
    });

}

const counters = document.querySelectorAll(".counter");

counters.forEach(counter => {

    const updateCounter = () => {

        const target = +counter.dataset.target;
        const count = +counter.innerText;

        const increment = Math.max(1, Math.ceil(target / 100));

        if (count < target) {

            counter.innerText = count + increment;

            setTimeout(updateCounter, 20);

        } else {

            counter.innerText = target;

        }

    };

    updateCounter();

});