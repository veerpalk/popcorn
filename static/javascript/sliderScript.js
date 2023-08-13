
// JavaScript for sliding images
const slider = document.querySelector('.slider');
const slides = document.querySelectorAll('.slide');
let currentIndex = 0;

function nextSlide() {
    currentIndex = (currentIndex + 1) % slides.length;
    updateSlider();
}

function updateSlider() {
    const translateValue = `translateX(-${currentIndex * 100}%)`;
    slider.style.transform = translateValue;
}

setInterval(nextSlide, 5000); // Change image every 5 seconds
