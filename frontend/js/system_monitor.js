/**
 * IT'S MY AI — System Telemetry Monitor & Audit Stream
 * Implements Section 1 (4 GB RAM telemetry) & Section 46 (Audit Logging).
 */

class SystemMonitor {
  constructor() {
    this.cpuVal = document.getElementById("cpu-percent-val");
    this.cpuBar = document.getElementById("cpu-progress-bar");
    this.ramVal = document.getElementById("ram-percent-val");
    this.ramBar = document.getElementById("ram-progress-bar");
    this.ramSub = document.getElementById("ram-usage-sub");
    this.diskVal = document.getElementById("disk-percent-val");
    this.diskSub = document.getElementById("disk-space-sub");
    this.batteryVal = document.getElementById("battery-percent-val");
    this.batterySub = document.getElementById("battery-plug-sub");
    this.auditContainer = document.getElementById("audit-stream-container");

    this.initListeners();
    this.pollInitialTelemetry();
  }

  initListeners() {
    if (window.api) {
      window.api.onTelemetry((data) => this.updateTelemetry(data));
    }

    const auditBtn = document.getElementById("btn-run-sec-check");
    if (auditBtn) {
      auditBtn.addEventListener("click", () => {
        if (window.app) window.app.handleCommandInput("It's My AI, check my system security.");
      });
    }
  }

  async pollInitialTelemetry() {
    try {
      const data = await window.api.getTelemetry();
      if (data) this.updateTelemetry(data);
      this.refreshAuditLogs();
    } catch (e) {
      console.warn("Telemetry init error:", e);
    }
  }

  updateTelemetry(data) {
    if (!data) return;

    // CPU
    if (data.cpu_percent !== undefined && this.cpuVal) {
      const cpu = Math.round(data.cpu_percent);
      this.cpuVal.innerText = `${cpu}%`;
      if (this.cpuBar) this.cpuBar.style.width = `${Math.min(cpu, 100)}%`;
    }

    // RAM (Strict 4 GB RAM monitoring)
    if (data.ram && this.ramVal) {
      const ram = Math.round(data.ram.percent);
      this.ramVal.innerText = `${ram}%`;
      if (this.ramBar) this.ramBar.style.width = `${Math.min(ram, 100)}%`;
      if (this.ramSub) {
        this.ramSub.innerText = `${data.ram.used_gb} GB / ${data.ram.total_gb} GB usable`;
      }
    }

    // Disk
    if (data.disk && this.diskVal) {
      this.diskVal.innerText = `${Math.round(data.disk.percent)}%`;
      if (this.diskSub) this.diskSub.innerText = `${data.disk.free_gb} GB Free`;
    }

    // Battery
    if (data.battery && this.batteryVal) {
      this.batteryVal.innerText = `${data.battery.percent}%`;
      if (this.batterySub) {
        this.batterySub.innerText = data.battery.power_plugged ? "AC Plugged" : "Battery Discharging";
      }
    }
  }

  async refreshAuditLogs() {
    if (!this.auditContainer) return;
    try {
      const res = await window.api.getAuditLogs(10);
      if (res && res.events) {
        this.auditContainer.innerHTML = "";
        res.events.forEach(ev => {
          const item = document.createElement("div");
          item.className = "audit-item";
          const timeStr = new Date(ev.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
          const level = ev.permission_level || 1;
          item.innerHTML = `
            <span class="audit-time">${timeStr}</span>
            <span class="audit-badge level-${level}">L${level}</span>
            <span class="audit-desc" title="${ev.action}">${ev.action}</span>
          `;
          this.auditContainer.appendChild(item);
        });
      }
    } catch (e) {
      console.warn("Audit refresh error:", e);
    }
  }
}

window.systemMonitor = new SystemMonitor();
