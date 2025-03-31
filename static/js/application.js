import { updateWinningsColor, setupInfoToggle } from "./ui.js";
import { renderWinningsChart } from "./chart.js";

document.addEventListener("turbo:load", () => {
  // Grab data from DOM
  const winningsDisplay = document.getElementById("winnings-display");
  const winningsValue = winningsDisplay
    ? parseFloat(winningsDisplay.dataset.winnings || "0")
    : 0;

  updateWinningsColor(winningsValue);
  setupInfoToggle();
  renderWinningsChart();
});
