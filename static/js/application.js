import { updateWinningsColor, bindInfoToggle} from "./ui.js";
import { renderWinningsChart } from "./chart.js";

document.addEventListener("turbo:load", () => {
  // Grab data from DOM
  const winningsDisplay = document.getElementById("winnings-display");
  const winningsValue = winningsDisplay
    ? parseFloat(winningsDisplay.dataset.winnings || "0")
    : 0;
    console.log("Doing load");
  updateWinningsColor(winningsValue);
  renderWinningsChart();
  bindInfoToggle();
})

document.addEventListener("DOMContentLoaded", bindInfoToggle);
document.addEventListener("turbo:before-stream-render", () => {
  requestAnimationFrame(() => {
    console.log("Before stream");
    bindInfoToggle();
  });
});