/**
 * IT'S MY AI — Master Application Controller
 * Wires communication, hologram states, voice events, settings, and confirmation flows.
 */

class AppController {
  constructor() {
    this.cmdInput = document.getElementById("command-input");
    this.sendBtn = document.getElementById("btn-send-command");
    this.providerNameEl = document.getElementById("active-provider-name");
    this.latencyEl = document.getElementById("telemetry-latency");
    this.secScoreEl = document.getElementById("security-score-val");
    this.radarBtn = document.getElementById("btn-toggle-radar");
    this.sleepBtn = document.getElementById("btn-toggle-sleep");
    this.settingsBtn = document.getElementById("btn-open-settings");
    this.settingsModal = document.getElementById("settings-modal");
    this.closeSettingsBtn = document.getElementById("btn-close-settings");
    this.saveSettingsBtn = document.getElementById("btn-save-settings");
    this.providerSelect = document.getElementById("settings-provider-select");

    this.isSleeping = false;
    this.bindEvents();
    this.syncInitialState();
  }

  async syncInitialState() {
    try {
      const pData = await window.api.getProviders();
      if (pData && pData.active && this.providerNameEl) {
        this.providerNameEl.innerText = pData.active.toUpperCase();
        if (this.providerSelect) this.providerSelect.value = pData.active;
      }
    } catch (e) {
      console.warn("Initial sync failed:", e);
    }
  }

  async handleCommandInput(rawText) {
    if (!rawText || !rawText.trim()) return;
    const text = rawText.trim();

    if (this.cmdInput) this.cmdInput.value = "";

    // 1. Post to Chat
    window.chat.addUserMessage(text);

    // 2. Set Hologram to Thinking
    window.hologram.setState("THINKING");

    try {
      const mode = window.chat.getCurrentMode();
      const res = await window.api.sendChatMessage(window.chat.history, mode);

      // Latency indicator
      if (res.latency_ms && this.latencyEl) {
        this.latencyEl.innerText = `${res.latency_ms} ms`;
      }

      // Check if dangerous action needs explicit confirmation
      if (res.requires_confirmation && res.confirmation_data) {
        window.hologram.setState("EXECUTING");
        window.confirmationModal.show(
          res.confirmation_data,
          // On Confirm:
          async (confirmedData) => {
            window.hologram.setState("THINKING");
            const confRes = await window.api.sendChatMessage(
              window.chat.history,
              mode,
              confirmedData.tool_name,
              confirmedData.parameters
            );
            window.chat.addAIMessage(confRes.text, {
              provider: confRes.provider,
              latency_ms: confRes.latency_ms,
              mode
            });
            window.voice.speak(confRes.text);
            window.hologram.setState("SUCCESS");
            window.systemMonitor.refreshAuditLogs();
          },
          // On Abort:
          () => {
            window.chat.addAIMessage("Action aborted by operator. Security boundary preserved.");
            window.hologram.setState("IDLE");
            window.voice.speak("Action cancelled.");
          }
        );
        return;
      }

      // Check if radar toggle was triggered
      if (res.tool_calls && res.tool_calls.some(tc => tc.name === "toggle_radar_view")) {
        window.radar.toggleView();
      }

      // Render AI response
      window.chat.addAIMessage(res.text, {
        provider: res.provider,
        latency_ms: res.latency_ms,
        mode
      });

      // Voice response
      window.voice.speak(res.text);

      // Hologram state
      if (res.hologram_state) {
        window.hologram.setState(res.hologram_state);
      } else {
        window.hologram.setState("SPEAKING");
      }

      // Refresh telemetry & audit stream
      window.systemMonitor.refreshAuditLogs();

    } catch (err) {
      console.error("Command Execution Error:", err);
      window.hologram.setState("ERROR");
      window.chat.addAIMessage("Communication error with AI brain. Degraded fallback active.", { mode: "ERROR" });
      window.voice.speak("Subsystem error encountered.");
    }
  }

  toggleSleep() {
    this.isSleeping = !this.isSleeping;
    if (this.isSleeping) {
      window.hologram.setState("SLEEP");
      if (this.sleepBtn) this.sleepBtn.classList.add("active");
      document.getElementById("state-label").innerText = "STANDBY // LOW POWER";
    } else {
      window.hologram.setState("IDLE");
      if (this.sleepBtn) this.sleepBtn.classList.remove("active");
      document.getElementById("state-label").innerText = "ONLINE // IDLE";
    }
  }

  bindEvents() {
    // Send button & enter key
    if (this.sendBtn) {
      this.sendBtn.addEventListener("click", () => {
        if (this.cmdInput) this.handleCommandInput(this.cmdInput.value);
      });
    }

    if (this.cmdInput) {
      this.cmdInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          this.handleCommandInput(this.cmdInput.value);
        }
      });
    }

    // Radar Toggle
    if (this.radarBtn) {
      this.radarBtn.addEventListener("click", () => window.radar.toggleView());
    }

    // Sleep Toggle
    if (this.sleepBtn) {
      this.sleepBtn.addEventListener("click", () => this.toggleSleep());
    }

    // Theme Selector
    const themeSelect = document.getElementById("theme-selector");
    if (themeSelect) {
      themeSelect.addEventListener("change", (e) => {
        if (window.hologram) window.hologram.setTheme(e.target.value);
      });
    }

    // Document Attachment & Upload
    const attachBtn = document.getElementById("btn-attach-doc");
    const fileInput = document.getElementById("doc-file-input");
    if (attachBtn && fileInput) {
      attachBtn.addEventListener("click", () => fileInput.click());
      fileInput.addEventListener("change", async () => {
        if (!fileInput.files || fileInput.files.length === 0) return;
        const file = fileInput.files[0];
        window.chat.addUserMessage(`[Uploaded Document] Analyzing file: ${file.name}`);
        window.hologram.setState("THINKING");

        const formData = new FormData();
        formData.append("file", file);
        formData.append("question", "Provide a comprehensive summary of this document and extract key highlights.");

        try {
          const resp = await fetch("/api/documents/upload", {
            method: "POST",
            body: formData
          });
          const data = await resp.json();
          if (data && data.analysis) {
            window.chat.addAIMessage(data.analysis, { provider: data.provider, latency_ms: data.latency_ms });
            window.hologram.setState("SUCCESS");
          } else {
            window.chat.addAIMessage(`Document analysis failed: ${data.detail || "Unknown error"}`);
            window.hologram.setState("ERROR");
          }
        } catch (err) {
          window.chat.addAIMessage(`Upload error: ${err.message}`);
          window.hologram.setState("ERROR");
        }
        fileInput.value = "";
      });
    }
    if (this.settingsBtn && this.settingsModal) {
      this.settingsBtn.addEventListener("click", () => this.settingsModal.classList.remove("hidden"));
    }
    if (this.closeSettingsBtn && this.settingsModal) {
      this.closeSettingsBtn.addEventListener("click", () => this.settingsModal.classList.add("hidden"));
    }
    if (this.saveSettingsBtn) {
      this.saveSettingsBtn.addEventListener("click", async () => {
        const prov = this.providerSelect.value;
        await window.api.switchProvider(prov);
        if (this.providerNameEl) this.providerNameEl.innerText = prov.toUpperCase();
        if (this.settingsModal) this.settingsModal.classList.add("hidden");
        window.chat.addAIMessage(`Inference provider switched to ${prov.toUpperCase()}.`);
        window.hologram.setState("SUCCESS");
      });
    }

    // Keyboard Hotkeys: 'r' for Radar, 't' for Tasks, 'Escape' to close modal
    window.addEventListener("keydown", (e) => {
      const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
      const isInput = activeTag === "input" || activeTag === "textarea" || activeTag === "select";

      if (!isInput && (e.key === "r" || e.key === "R")) {
        window.radar.toggleView();
      } else if (!isInput && (e.key === "t" || e.key === "T")) {
        if (window.todos) window.todos.toggle();
      } else if (e.key === "Escape") {
        if (this.settingsModal) this.settingsModal.classList.add("hidden");
        if (window.confirmationModal) window.confirmationModal.hide();
        if (window.todos) window.todos.close();
      }
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.app = new AppController();
  console.log("[IT'S MY AI] Command Center initialized successfully.");
});
