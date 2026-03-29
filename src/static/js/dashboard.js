/**
 * SOC Dashboard – FINAL STABLE VERSION (NULL-SAFE)
 */

document.addEventListener("DOMContentLoaded", () => {

  const WINDOW_SIZE = 300;
  let dashboardData = null;
  let lastTimelineIndex = -1;

  // ===== DOM =====
  const chartContainer = document.getElementById("anomalyChart");
  const canvas = document.getElementById("chartCanvas");
  const ctx = canvas.getContext("2d");

  const attackBtn = document.getElementById("attackButton");
  const themeBtn = document.getElementById("themeToggle");

  const timelineEl = document.getElementById("timeline");

  const endpointTable = document.getElementById("endpointTable");
  const endpointTbody =
    endpointTable.querySelector("tbody") || endpointTable;

  // ================= FETCH DATA =================
  async function fetchData() {
    try {
      const res = await fetch("/api/data");
      const data = await res.json();

      if (!data || !Array.isArray(data.errors)) return;

      dashboardData = data;

      updateKPIs(data);
      drawGraph(data.errors.slice(-WINDOW_SIZE), data.threshold);
      updateTimeline(data);
      updateEndpointTable(data);

    } catch (err) {
      console.error("Fetch failed:", err);
    }
  }

  // ================= KPIs =================
  function updateKPIs(data) {
    document.getElementById("totalSamples").innerText = data.total_samples;
    document.getElementById("anomalies").innerText = data.anomalies;
    document.getElementById("threshold").innerText =
      data.threshold.toFixed(4);
  }

  // ================= GRAPH =================
  function drawGraph(errors, threshold) {
    if (!errors.length) return;

    const dpr = window.devicePixelRatio || 1;
    const width = chartContainer.clientWidth;
    const height = 300;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    ctx.clearRect(0, 0, width, height);

    const padding = 40;
    const maxVal = Math.max(...errors, threshold * 1.2);
    const xStep = (width - padding * 2) / (errors.length - 1);

    // Grid
    ctx.strokeStyle = "#2a2f3a";
    for (let i = 0; i <= 5; i++) {
      const y = padding + ((height - padding * 2) / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }

    // Threshold
    const ty = height - padding - (threshold / maxVal) * (height - padding * 2);
    ctx.strokeStyle = "#ef4444";
    ctx.setLineDash([6, 6]);
    ctx.beginPath();
    ctx.moveTo(padding, ty);
    ctx.lineTo(width - padding, ty);
    ctx.stroke();
    ctx.setLineDash([]);

    // Line
    ctx.strokeStyle = "#4db8d9";
    ctx.lineWidth = 2;
    ctx.beginPath();
    errors.forEach((v, i) => {
      const x = padding + i * xStep;
      const y = height - padding - (v / maxVal) * (height - padding * 2);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  // ================= TIMELINE =================
  function updateTimeline(data) {
    const indices = data.anomaly_indices;
    const errors = data.errors;
    const threshold = data.threshold;

    if (!indices.length) {
      timelineEl.innerHTML =
        `<p class="empty-state">No incidents detected</p>`;
      return;
    }

    const newOnes = indices.filter(i => i > lastTimelineIndex);
    if (!newOnes.length) return;

    lastTimelineIndex = indices[indices.length - 1];

    timelineEl.innerHTML = newOnes
      .slice(-5)
      .reverse()
      .map(idx => {
        const score = errors[idx];
        let severity = "low";

        if (score > threshold * 1.5) severity = "critical";
        else if (score > threshold * 1.2) severity = "high";
        else if (score > threshold) severity = "medium";

        return `
          <div class="timeline-item timeline-item-${severity}">
            <strong>${severity.toUpperCase()}</strong>
            – WS-ENDPOINT-${idx}
          </div>
        `;
      })
      .join("");
  }

  // ================= ENDPOINT TABLE =================
  function updateEndpointTable(data) {
    endpointTbody.innerHTML = "";

    const indices = data.anomaly_indices.slice(-6).reverse();
    const threshold = data.threshold;

    if (!indices.length) {
      endpointTbody.innerHTML =
        `<tr><td colspan="4" class="empty-state">No active endpoints</td></tr>`;
      return;
    }

    indices.forEach(idx => {
      const score = data.errors[idx];
      let severity = "LOW";
      let status = "Monitoring";

      if (score > threshold * 1.5) {
        severity = "CRITICAL";
        status = "Isolate";
      } else if (score > threshold * 1.2) {
        severity = "HIGH";
        status = "Investigating";
      } else if (score > threshold) {
        severity = "MEDIUM";
        status = "Warning";
      }

      endpointTbody.innerHTML += `
        <tr>
          <td>WS-ENDPOINT-${idx}</td>
          <td>1</td>
          <td>${severity}</td>
          <td>${status}</td>
        </tr>
      `;
    });
  }

  // ================= ATTACK =================
  async function simulateAttack() {
    try {
      attackBtn.disabled = true;
      await fetch("/api/simulate_attack", { method: "POST" });
      setTimeout(fetchData, 1000);
      setTimeout(fetchData, 3000);
    } finally {
      attackBtn.disabled = false;
    }
  }

  // ================= THEME =================
  function toggleTheme() {
    document.body.classList.toggle("dark");
    localStorage.setItem(
      "soc-theme",
      document.body.classList.contains("dark") ? "dark" : "light"
    );
  }

  if (localStorage.getItem("soc-theme") === "dark") {
    document.body.classList.add("dark");
  }

  // ================= EVENTS =================
  attackBtn.addEventListener("click", simulateAttack);
  themeBtn.addEventListener("click", toggleTheme);

  window.addEventListener("resize", () => {
    if (dashboardData) {
      drawGraph(
        dashboardData.errors.slice(-WINDOW_SIZE),
        dashboardData.threshold
      );
    }
  });

  // ================= START =================
  fetchData();
  setInterval(fetchData, 5000);
});
