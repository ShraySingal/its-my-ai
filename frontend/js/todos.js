/**
 * IT'S MY AI — Holographic Task & To-Do Manager Controller
 * Manages reactive UI interactions, filtering, keyboard shortcuts, and API sync.
 */

class TodoManager {
  constructor() {
    this.modal = document.getElementById("todos-modal");
    this.openBtn = document.getElementById("btn-open-todos");
    this.closeBtn = document.getElementById("btn-close-todos");
    this.listContainer = document.getElementById("todos-list-container");
    this.titleInput = document.getElementById("new-todo-title");
    this.prioritySelect = document.getElementById("new-todo-priority");
    this.categorySelect = document.getElementById("new-todo-category");
    this.addBtn = document.getElementById("btn-add-todo");
    this.clearCompletedBtn = document.getElementById("btn-clear-completed-todos");
    this.searchInput = document.getElementById("todo-search-input");
    this.filterTabs = document.querySelectorAll(".todo-filter-tab");
    this.pendingBadge = document.getElementById("todos-pending-count");
    this.totalBadge = document.getElementById("todos-total-count");

    this.currentFilter = "all"; // 'all', 'pending', 'completed', 'high'
    this.searchQuery = "";
    this.todos = [];

    this.bindEvents();
  }

  init() {
    this.loadTodos();
  }

  bindEvents() {
    // Open / Close
    if (this.openBtn) {
      this.openBtn.addEventListener("click", () => this.open());
    }
    if (this.closeBtn) {
      this.closeBtn.addEventListener("click", () => this.close());
    }

    // Add Task
    if (this.addBtn) {
      this.addBtn.addEventListener("click", () => this.handleAdd());
    }
    if (this.titleInput) {
      this.titleInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          this.handleAdd();
        }
      });
    }

    // Clear Completed
    if (this.clearCompletedBtn) {
      this.clearCompletedBtn.addEventListener("click", async () => {
        try {
          await window.api.clearCompletedTodos();
          await this.loadTodos();
          if (window.chat) {
            window.chat.addAIMessage("Completed tasks cleared from storage.");
          }
        } catch (e) {
          console.error("Error clearing completed todos:", e);
        }
      });
    }

    // Search filter
    if (this.searchInput) {
      this.searchInput.addEventListener("input", (e) => {
        this.searchQuery = e.target.value.toLowerCase().trim();
        this.render();
      });
    }

    // Filter Tabs
    this.filterTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        this.filterTabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        this.currentFilter = tab.dataset.filter || "all";
        this.render();
      });
    });
  }

  open() {
    if (this.modal) {
      this.modal.classList.remove("hidden");
      this.loadTodos();
      setTimeout(() => {
        if (this.titleInput) this.titleInput.focus();
      }, 100);
    }
  }

  close() {
    if (this.modal) {
      this.modal.classList.add("hidden");
    }
  }

  toggle() {
    if (this.modal) {
      if (this.modal.classList.contains("hidden")) {
        this.open();
      } else {
        this.close();
      }
    }
  }

  async loadTodos() {
    try {
      const data = await window.api.getTodos();
      this.todos = (data && data.todos) ? data.todos : [];
      this.render();
    } catch (err) {
      console.error("Failed to load todos:", err);
    }
  }

  async handleAdd() {
    if (!this.titleInput) return;
    const title = this.titleInput.value.trim();
    if (!title) return;

    const priority = this.prioritySelect ? this.prioritySelect.value : "medium";
    const category = this.categorySelect ? this.categorySelect.value : "general";

    try {
      const res = await window.api.createTodo(title, priority, category);
      if (res && res.success) {
        this.titleInput.value = "";
        await this.loadTodos();
        if (window.hologram) window.hologram.setState("SUCCESS");
      }
    } catch (err) {
      console.error("Failed to add todo:", err);
    }
  }

  async handleToggle(todoId) {
    try {
      const res = await window.api.toggleTodo(todoId);
      if (res && res.success) {
        await this.loadTodos();
      }
    } catch (err) {
      console.error("Failed to toggle todo:", err);
    }
  }

  async handleDelete(todoId) {
    try {
      const res = await window.api.deleteTodo(todoId);
      if (res && res.success) {
        await this.loadTodos();
      }
    } catch (err) {
      console.error("Failed to delete todo:", err);
    }
  }

  render() {
    if (!this.listContainer) return;

    // Filter todos
    let filtered = [...this.todos];

    if (this.currentFilter === "pending") {
      filtered = filtered.filter((t) => !t.completed);
    } else if (this.currentFilter === "completed") {
      filtered = filtered.filter((t) => t.completed);
    } else if (this.currentFilter === "high") {
      filtered = filtered.filter((t) => t.priority === "high" || t.priority === "urgent");
    }

    if (this.searchQuery) {
      filtered = filtered.filter(
        (t) =>
          t.title.toLowerCase().includes(this.searchQuery) ||
          (t.category && t.category.toLowerCase().includes(this.searchQuery))
      );
    }

    // Update Counts
    const pendingCount = this.todos.filter((t) => !t.completed).length;
    if (this.pendingBadge) this.pendingBadge.innerText = `${pendingCount} PENDING`;
    if (this.totalBadge) this.totalBadge.innerText = `${this.todos.length} TOTAL`;

    // Render list
    if (filtered.length === 0) {
      this.listContainer.innerHTML = `
        <div class="todo-empty-state">
          <div class="empty-icon">◈</div>
          <div class="empty-title">NO DIRECTIVES FOUND</div>
          <div class="empty-sub">Add a new operational directive above or adjust active filters.</div>
        </div>
      `;
      return;
    }

    this.listContainer.innerHTML = filtered
      .map((item) => {
        const priorityClass = `priority-${item.priority || "medium"}`;
        const isDone = item.completed ? "completed" : "";
        const checkedAttr = item.completed ? "checked" : "";
        const formattedDate = item.created_at ? item.created_at.replace("T", " ").substring(0, 16) : "";

        return `
        <div class="todo-item ${isDone} ${priorityClass}" data-id="${item.id}">
          <label class="todo-checkbox-wrap" title="Toggle status">
            <input type="checkbox" class="todo-checkbox" ${checkedAttr} data-id="${item.id}" />
            <span class="custom-checkmark"></span>
          </label>
          <div class="todo-content">
            <div class="todo-title-row">
              <span class="todo-title">${this.escapeHtml(item.title)}</span>
              <span class="priority-pill ${priorityClass}">${(item.priority || "MED").toUpperCase()}</span>
            </div>
            <div class="todo-meta-row">
              <span class="todo-category-badge">#${this.escapeHtml(item.category || "general")}</span>
              <span class="todo-time">${formattedDate}</span>
            </div>
          </div>
          <button class="todo-delete-btn" data-id="${item.id}" title="Delete task">✕</button>
        </div>
      `;
      })
      .join("");

    // Bind item click listeners
    this.listContainer.querySelectorAll(".todo-checkbox").forEach((cb) => {
      cb.addEventListener("change", (e) => {
        const id = e.target.dataset.id;
        this.handleToggle(id);
      });
    });

    this.listContainer.querySelectorAll(".todo-delete-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const id = e.target.dataset.id;
        this.handleDelete(id);
      });
    });
  }

  escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.todos = new TodoManager();
  window.todos.init();
});
