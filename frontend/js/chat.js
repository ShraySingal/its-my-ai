/**
 * IT'S MY AI — Chat Feed & Response Modes (Sections 7, 36, 37)
 */

class ChatManager {
  constructor() {
    this.messagesContainer = document.getElementById("chat-messages");
    this.history = [];
    this.responseModeSelect = document.getElementById("response-mode-select");

    this.bindEvents();
  }

  getCurrentMode() {
    return this.responseModeSelect ? this.responseModeSelect.value : "NORMAL";
  }

  addUserMessage(text) {
    this.history.push({ role: "user", content: text });
    this.renderBubble("user", text);
  }

  addAIMessage(text, metadata = {}) {
    this.history.push({ role: "assistant", content: text });
    this.renderBubble("assistant", text, metadata);
  }

  renderBubble(role, content, metadata = {}) {
    if (!this.messagesContainer) return;

    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role === "user" ? "user-bubble" : "ai-bubble"}`;

    const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const authorName = role === "user" ? "OPERATOR" : "IT'S MY AI";
    const avatar = role === "user" ? "👤" : "◈";

    let tagsHtml = "";
    if (role === "assistant") {
      const mode = metadata.mode || this.getCurrentMode();
      const provider = metadata.provider ? metadata.provider.toUpperCase() : "AI";
      tagsHtml = `
        <div class="bubble-tags">
          <span class="badge-safe">${provider}</span>
          <span class="badge-tag">${mode}</span>
          ${metadata.latency_ms ? `<span class="badge-tag">${metadata.latency_ms}ms</span>` : ""}
        </div>
      `;
    }

    bubble.innerHTML = `
      <div class="bubble-header">
        <span class="bubble-avatar">${avatar}</span>
        <span class="bubble-author">${authorName}</span>
        <span class="bubble-time">${timeStr}</span>
      </div>
      <div class="bubble-body">${this.escapeHtml(content).replace(/\n/g, "<br>")}</div>
      ${tagsHtml}
    `;

    this.messagesContainer.appendChild(bubble);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  escapeHtml(str) {
    const p = document.createElement("p");
    p.textContent = str;
    return p.innerHTML;
  }

  bindEvents() {
    // Quick Command Chips
    document.querySelectorAll(".chip-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const cmd = btn.getAttribute("data-cmd");
        if (cmd && window.app) {
          window.app.handleCommandInput(cmd);
        }
      });
    });
  }
}

window.chat = new ChatManager();
