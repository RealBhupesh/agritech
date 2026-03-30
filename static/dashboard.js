(function () {
  const intervalSelect = document.getElementById("simIntervalSelect");
  const startBtn = document.getElementById("simStartBtn");
  const stopBtn = document.getElementById("simStopBtn");
  const lastUpdatedEl = document.getElementById("lastUpdated");
  const alertsList = document.getElementById("alertsList");

  const metricSoilEl = document.getElementById("metricSoilMoisture");
  const metricTempEl = document.getElementById("metricTemp");
  const metricHealthEl = document.getElementById("metricHealth");
  const metricWindEl = document.getElementById("metricWind");

  const sparkSoilCanvas = document.getElementById("sparkSoil");
  const sparkTempCanvas = document.getElementById("sparkTemp");
  const sparkWindCanvas = document.getElementById("sparkWind");

  const gaugeCanvas = document.getElementById("gaugeHealth");
  const mainCanvas = document.getElementById("mainTrendsChart");

  if (!intervalSelect || !startBtn || !stopBtn) return;

  if (!window.Chart) {
    // Chart.js is loaded via CDN in the template.
    console.warn("Chart.js not found");
    return;
  }

  const chartCommon = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 250 },
    plugins: { legend: { display: false } },
    elements: { point: { radius: 0 } },
  };

  const makeSpark = (canvas, borderColor, fillColor) => {
    const ctx = canvas.getContext("2d");
    return new Chart(ctx, {
      ...chartCommon,
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            data: [],
            borderColor: borderColor,
            borderWidth: 2,
            fill: true,
            backgroundColor: fillColor,
            tension: 0.35,
          },
        ],
      },
      options: {
        ...chartCommon,
        scales: {
          x: { display: false },
          y: { display: false },
        },
      },
    });
  };

  const soilBorder = "rgba(14,165,233,1)";
  const soilFill = "rgba(14,165,233,0.18)";
  const tempBorder = "rgba(22,163,74,1)";
  const tempFill = "rgba(22,163,74,0.14)";
  const windBorder = "rgba(14,165,233,0.95)";
  const windFill = "rgba(14,165,233,0.14)";

  const sparkSoil = makeSpark(sparkSoilCanvas, soilBorder, soilFill);
  const sparkTemp = makeSpark(sparkTempCanvas, tempBorder, tempFill);
  const sparkWind = makeSpark(sparkWindCanvas, windBorder, windFill);

  const gauge = (() => {
    const ctx = gaugeCanvas.getContext("2d");
    return new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Crop health", "Remaining"],
        datasets: [
          {
            data: [92, 8],
            backgroundColor: ["rgba(22,163,74,0.95)", "rgba(14,19,33,0.10)"],
            borderWidth: 0,
            hoverOffset: 0,
          },
        ],
      },
      options: {
        ...chartCommon,
        cutout: "72%",
        plugins: { legend: { display: false } },
      },
    });
  })();

  const mainChart = (() => {
    const ctx = mainCanvas.getContext("2d");
    return new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Soil Moisture (%)",
            data: [],
            yAxisID: "ySoil",
            borderColor: "rgba(14,165,233,1)",
            backgroundColor: "rgba(14,165,233,0.14)",
            borderWidth: 2,
            tension: 0.35,
            fill: true,
          },
          {
            label: "Temperature (°C)",
            data: [],
            yAxisID: "yTemp",
            borderColor: "rgba(22,163,74,1)",
            backgroundColor: "rgba(22,163,74,0.10)",
            borderWidth: 2,
            tension: 0.35,
            fill: true,
          },
        ],
      },
      options: {
        ...chartCommon,
        plugins: {
          legend: { display: true, position: "bottom", labels: { boxWidth: 10 } },
          tooltip: { mode: "index", intersect: false },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: "rgba(14,19,33,0.55)", font: { weight: 800 } },
          },
          ySoil: {
            grid: { color: "rgba(14,19,33,0.08)" },
            ticks: { color: "rgba(14,19,33,0.65)", font: { weight: 800 } },
            min: 0,
            max: 100,
          },
          yTemp: {
            position: "right",
            grid: { drawOnChartArea: false },
            ticks: { color: "rgba(14,19,33,0.65)", font: { weight: 800 } },
          },
        },
      },
    });
  })();

  let timer = null;
  let stepIndex = 0;

  const renderAlerts = (alerts) => {
    alertsList.innerHTML = "";
    if (!alerts || alerts.length === 0) {
      const empty = document.createElement("div");
      empty.className = "alert-empty";
      empty.textContent = "No alerts right now. Keep monitoring.";
      alertsList.appendChild(empty);
      return;
    }

    alerts.forEach((a) => {
      const item = document.createElement("div");
      item.className = "alert";
      item.setAttribute("role", "listitem");

      const badge = document.createElement("div");
      badge.className = `alert-badge alert-badge--${a.type || "info"}`;
      badge.textContent = a.type === "maintenance" ? "Maint" : a.type === "warning" ? "Warn" : "Info";

      const body = document.createElement("div");
      body.className = "alert-body";

      const title = document.createElement("div");
      title.className = "alert-title";
      title.textContent = a.title || "Alert";

      const detail = document.createElement("div");
      detail.className = "alert-detail";
      detail.textContent = a.detail || "";

      const meta = document.createElement("div");
      meta.className = "alert-meta";
      meta.textContent = `${a.minutesAgo} min ago`;

      body.appendChild(title);
      body.appendChild(detail);
      body.appendChild(meta);

      item.appendChild(badge);
      item.appendChild(body);
      alertsList.appendChild(item);
    });
  };

  const updateUI = (data) => {
    metricSoilEl.textContent = `${data.avg_soil_moisture}%`;
    metricTempEl.textContent = `${data.temperature}°C`;
    metricHealthEl.textContent = `${data.crop_health}%`;
    metricWindEl.textContent = `${data.wind_speed} km/h`;

    // Sparklines
    sparkSoil.data.labels = data.trend_labels;
    sparkSoil.data.datasets[0].data = data.soil_trend;
    sparkSoil.update();

    sparkTemp.data.labels = data.trend_labels;
    sparkTemp.data.datasets[0].data = data.temp_trend;
    sparkTemp.update();

    sparkWind.data.labels = data.trend_labels;
    sparkWind.data.datasets[0].data = data.wind_trend || [];
    sparkWind.update();

    // Gauge
    const health = Number(data.crop_health) || 0;
    gauge.data.datasets[0].data = [health, Math.max(0, 100 - health)];
    gauge.update();

    // Main chart
    mainChart.data.labels = data.trend_labels;
    mainChart.data.datasets[0].data = data.soil_trend;
    mainChart.data.datasets[1].data = data.temp_trend;
    mainChart.update();

    // Alerts
    renderAlerts(data.alerts);

    if (lastUpdatedEl) {
      lastUpdatedEl.textContent = new Date(data.at).toLocaleTimeString();
    }
  };

  const poll = async () => {
    const intervalMs = Number(intervalSelect.value) || 5000;
    startBtn.disabled = true;
    stopBtn.disabled = false;

    const res = await fetch(`/api/iot/sim/next?step=${stepIndex}`);
    if (!res.ok) return;
    const data = await res.json();
    updateUI(data);

    stepIndex += 1;

    // Keep polling on a fixed interval.
    timer = window.setTimeout(poll, intervalMs);
  };

  startBtn.addEventListener("click", () => {
    if (timer) window.clearTimeout(timer);
    stepIndex = 0;
    poll();
  });

  stopBtn.addEventListener("click", () => {
    if (timer) window.clearTimeout(timer);
    timer = null;
    startBtn.disabled = false;
    stopBtn.disabled = true;
  });

  // Start immediately to match the "live dashboard" experience.
  poll();
})();

