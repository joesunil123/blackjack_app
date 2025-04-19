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

export function bindInfoToggle() {
  const checkbox = document.getElementById("infoToggle");
  if (!checkbox) return;
  console.log("Found checkbox");
  // Restore saved state
  const saved = localStorage.getItem("infoToggleState");
  if (saved !== null) {
    console.log("Previous:");
    console.log(saved);
    checkbox.checked = saved === "true";
    console.log("Restored:");
    console.log(checkbox.checked);
  }

  // Avoid rebinding
  if (!checkbox.dataset.bound) {
    checkbox.addEventListener("change", () => {
      console.log("Checkbox changed:", checkbox.checked);
      localStorage.setItem("infoToggleState", checkbox.checked);
    });
    checkbox.dataset.bound = "true";
  }
}
  