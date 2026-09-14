/**
 * IT'S MY AI — API Client & Telemetry WebSocket Layer
 */

class ApiClient {
  constructor() {
    this.baseUrl = window.location.protocol.startsWith("http") ? window.location.origin : "http://127.0.0.1:8000";
    this.ws = null;
    this.telemetryListeners = [];
    this.auditListeners = [];
    this.stateListeners = [];
    this.initWebSocket();
  }

  initWebSocket() {
    const isHttp = window.location.protocol.startsWith("http");
    const wsHost = isHttp ? window.location.host : "127.0.0.1:8000";
    const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProto}//${wsHost}/ws`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log("[IT'S MY AI] WebSocket connected.");
      };

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "telemetry" && msg.data) {
            this.telemetryListeners.forEach(fn => fn(msg.data));
          } else if (msg.type === "hologram_state" && msg.state) {
            this.stateListeners.forEach(fn => fn(msg.state));
          }
        } catch (e) {
          console.error("WS Parse Error:", e);
        }
      };

      this.ws.onclose = () => {
        // Auto reconnect after 3 seconds
        setTimeout(() => this.initWebSocket(), 3000);
      };
    } catch (e) {
      console.warn("WebSocket unavailable. Falling back to HTTP polling.");
    }
  }

  onTelemetry(fn) {
    this.telemetryListeners.push(fn);
  }

  onStateChange(fn) {
    this.stateListeners.push(fn);
  }

  async sendChatMessage(messages, responseMode = "NORMAL", confirmedTool = null, confirmedParams = null) {
    const res = await fetch(`${this.baseUrl}/api/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages,
        response_mode: responseMode,
        confirmed_tool: confirmedTool,
        confirmed_params: confirmedParams
      })
    });
    return await res.json();
  }

  async getProviders() {
    const res = await fetch(`${this.baseUrl}/api/ai/providers`);
    return await res.json();
  }

  async switchProvider(providerName) {
    const res = await fetch(`${this.baseUrl}/api/ai/providers/switch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider_name: providerName })
    });
    return await res.json();
  }

  async getTelemetry() {
    const res = await fetch(`${this.baseUrl}/api/system/status`);
    return await res.json();
  }

  async getAuditLogs(limit = 30) {
    const res = await fetch(`${this.baseUrl}/api/system/audit?limit=${limit}`);
    return await res.json();
  }

  async getDevices() {
    const res = await fetch(`${this.baseUrl}/api/devices`);
    return await res.json();
  }

  async scanNetwork() {
    const res = await fetch(`${this.baseUrl}/api/security/network`);
    return await res.json();
  }

  async runSecurityScan() {
    const res = await fetch(`${this.baseUrl}/api/security/scan`);
    return await res.json();
  }

  async executeTool(name, parameters = {}, isConfirmed = false) {
    const res = await fetch(`${this.baseUrl}/api/tools/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, parameters, is_confirmed: isConfirmed })
    });
    return await res.json();
  }

  async getMemories(query = "") {
    const res = await fetch(`${this.baseUrl}/api/memory?q=${encodeURIComponent(query)}`);
    return await res.json();
  }

  async storeMemory(content, category = "fact") {
    const res = await fetch(`${this.baseUrl}/api/memory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, category })
    });
    return await res.json();
  }

  async getTodos(category = null, completed = null, search = null) {
    const params = new URLSearchParams();
    if (category && category !== "all") params.append("category", category);
    if (completed !== null && completed !== undefined) params.append("completed", completed);
    if (search) params.append("search", search);
    const qs = params.toString() ? `?${params.toString()}` : "";
    const res = await fetch(`${this.baseUrl}/api/todos${qs}`);
    return await res.json();
  }

  async createTodo(title, priority = "medium", category = "general", dueDate = null) {
    const res = await fetch(`${this.baseUrl}/api/todos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, priority, category, due_date: dueDate })
    });
    return await res.json();
  }

  async toggleTodo(todoId, completed = null) {
    const res = await fetch(`${this.baseUrl}/api/todos/${encodeURIComponent(todoId)}/toggle`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed })
    });
    return await res.json();
  }

  async deleteTodo(todoId) {
    const res = await fetch(`${this.baseUrl}/api/todos/${encodeURIComponent(todoId)}`, {
      method: "DELETE"
    });
    return await res.json();
  }

  async clearCompletedTodos() {
    const res = await fetch(`${this.baseUrl}/api/todos/completed/clear`, {
      method: "DELETE"
    });
    return await res.json();
  }
}

window.api = new ApiClient();
