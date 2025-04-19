export function updateWinningsColor(value) {
  const winningsDisplay = document.getElementById("winnings-display");
  if (!winningsDisplay) return;

  if (value > 0) {
    winningsDisplay.style.color = "green";
  } else if (value < 0) {
    winningsDisplay.style.color = "red";
  } else {
    winningsDisplay.style.color = "black";
  }
}
  