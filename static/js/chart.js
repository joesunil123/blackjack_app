let winningsChart;

export function renderWinningsChart() {
  const chartElem = document.getElementById("winningsChart");
  if (!chartElem) return;

  const labels = JSON.parse(chartElem.dataset.labels || "[]");
  const dataPoints = JSON.parse(chartElem.dataset.points || "[]");
  const lastValue = dataPoints[dataPoints.length - 1] || 0;
  const chartColor = lastValue > 0 ? "green" : lastValue < 0 ? "red" : "black";

  const ctx = chartElem.getContext("2d");

  if (winningsChart) {
    winningsChart.destroy();
  }

  winningsChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        data: dataPoints,
        borderColor: chartColor,
        backgroundColor: chartColor,
        pointBackgroundColor: chartColor,
        pointBorderColor: chartColor,
        fill: false,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }},
      scales: { y: { beginAtZero: true }}
    }
  });
}
