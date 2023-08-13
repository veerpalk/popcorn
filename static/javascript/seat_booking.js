window.addEventListener('load', () => {
  localStorage.clear();
  count.innerText = '0';
  total.innerText = '0';
  seats.forEach(seat => seat.classList.remove('selected'));
});

const container = document.querySelector(".container");
const seats = document.querySelectorAll(".row .seat:not(.sold)");
const count = document.getElementById("count");
const totalElement = document.getElementById('total');
const totalInput = document.getElementById('totalInput');
const movieSelect = document.getElementById("movie");

let ticketPrice = 15;

// Update total and count
function updateSelectedCount() {
  const selectedSeats = document.querySelectorAll(".row .seat.selected");

  const seatsIndex = [...selectedSeats].map((seat) => [...seats].indexOf(seat));

  const selectedSeatsCount = selectedSeats.length;

  count.innerText = selectedSeatsCount;
  
  totalElement.innerText = (selectedSeatsCount * ticketPrice).toFixed(2);
  totalInput.value = totalElement.innerText;

}

// Seat click event
container.addEventListener("click", (e) => {
  if (
    e.target.classList.contains("seat") &&
    !e.target.classList.contains("sold")
  ) {
    e.target.classList.toggle("selected");

    updateSelectedCount();
  }
});

// Initial count and total set
updateSelectedCount();

