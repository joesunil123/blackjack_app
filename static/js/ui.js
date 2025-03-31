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

export function setupInfoToggle() {
  const toggleBtn = document.getElementById("toggleInfoBtn");
  if (!toggleBtn) return;

  const targetId = toggleBtn.dataset.toggleTarget || "infoBox";
  const infoBox = document.getElementById(targetId);
  if (!infoBox) return;

  const textOpen = toggleBtn.dataset.toggleTextOpen || "−";
  const textClosed = toggleBtn.dataset.toggleTextClosed || "+ Info";

  toggleBtn.addEventListener("click", function () {
    const isVisible = infoBox.style.display === "block";
    infoBox.style.display = isVisible ? "none" : "block";
    toggleBtn.textContent = isVisible ? textClosed : textOpen;
  });
}
  
  