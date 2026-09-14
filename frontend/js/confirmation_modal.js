/**
 * IT'S MY AI — Command Confirmation Modal (Section 25)
 * Enforces explicit authorization before Level 3 & 4 sensitive/dangerous actions.
 */

class ConfirmationModal {
  constructor() {
    this.modal = document.getElementById("confirmation-modal");
    this.badge = document.getElementById("modal-danger-badge");
    this.title = document.getElementById("modal-action-title");
    this.warning = document.getElementById("modal-warning-text");
    this.detailsBox = document.getElementById("modal-details-box");
    this.btnConfirm = document.getElementById("modal-btn-confirm");
    this.btnCancel = document.getElementById("modal-btn-cancel");

    this.pendingAction = null;
    this.bindEvents();
  }

  show(actionData, onConfirm, onCancel) {
    this.pendingAction = { actionData, onConfirm, onCancel };

    const level = actionData.permission_level || 4;
    if (this.badge) {
      this.badge.innerText = level === 4 ? "LEVEL 4 // DANGEROUS ACTION" : "LEVEL 3 // SENSITIVE ACTION";
      this.badge.style.color = level === 4 ? "var(--ruby-neon)" : "var(--amber-neon)";
    }

    if (this.title) {
      this.title.innerText = `Authorization Required: ${actionData.tool_name || 'System Command'}`;
    }

    if (this.warning) {
      this.warning.innerText = actionData.warning_message || actionData.reason || "This operation modifies persistent state.";
    }

    if (this.detailsBox) {
      this.detailsBox.innerHTML = `
        <div><strong>TARGET TOOL:</strong> ${actionData.tool_name}</div>
        <div><strong>PARAMETERS:</strong> ${JSON.stringify(actionData.parameters || {})}</div>
        <div><strong>SECURITY PROTOCOL:</strong> Explicit Operator Consent Required</div>
      `;
    }

    if (this.modal) this.modal.classList.remove("hidden");
  }

  hide() {
    if (this.modal) this.modal.classList.add("hidden");
    this.pendingAction = null;
  }

  bindEvents() {
    if (this.btnConfirm) {
      this.btnConfirm.addEventListener("click", () => {
        if (this.pendingAction && this.pendingAction.onConfirm) {
          this.pendingAction.onConfirm(this.pendingAction.actionData);
        }
        this.hide();
      });
    }

    if (this.btnCancel) {
      this.btnCancel.addEventListener("click", () => {
        if (this.pendingAction && this.pendingAction.onCancel) {
          this.pendingAction.onCancel(this.pendingAction.actionData);
        }
        this.hide();
      });
    }
  }
}

window.confirmationModal = new ConfirmationModal();
