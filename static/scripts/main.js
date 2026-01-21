// Scroll Reveal Animation
function reveal() {
    var reveals = document.querySelectorAll(".reveal");
    for (var i = 0; i < reveals.length; i++) {
        var windowHeight = window.innerHeight;
        var elementTop = reveals[i].getBoundingClientRect().top;
        var elementVisible = 150;
        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add("active");
        }
    }
}

window.addEventListener("scroll", reveal);

// Initial call to reveal elements already in view
window.addEventListener("DOMContentLoaded", reveal);

function selectHotel(hotelId) {
    const hotelSelect = document.getElementById('hotelSelect');
    const bookingForm = document.getElementById('mainBookingForm');
    
    if (hotelSelect && bookingForm) {
        hotelSelect.value = hotelId;
        bookingForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Date restriction logic
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = [
        document.getElementById('check_in_booking'), 
        document.querySelector('input[name="check_in"]')
    ];
    
    dateInputs.forEach(input => {
        if(input) input.setAttribute('min', today);
    });
});

