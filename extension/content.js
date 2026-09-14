/**
 * IT'S MY AI — Browser Companion Content Script
 * Extracts structured DOM content and executes safe automation commands.
 */

(() => {
  // Listen for extraction or automation commands from popup/background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GET_PAGE_DATA") {
      try {
        const pageData = extractPageContext();
        sendResponse({ success: true, data: pageData });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
      return true;
    }

    if (request.action === "FLASH_STATUS") {
      showHUDNotification(request.text || "IT'S MY AI Synced", request.color || "#00f0ff");
      sendResponse({ success: true });
      return true;
    }
  });

  /**
   * Extract readable textual context from the current page
   */
  function extractPageContext() {
    const selectedText = window.getSelection() ? window.getSelection().toString().trim() : "";
    const title = document.title || "";
    const url = window.location.href;

    // Extract main text (strip script, style, nav)
    const clone = document.body.cloneNode(true);
    const elementsToRemove = clone.querySelectorAll("script, style, noscript, nav, footer, header, svg, [aria-hidden='true']");
    elementsToRemove.forEach(el => el.remove());

    let rawText = clone.innerText || clone.textContent || "";
    // Clean up excessive whitespace
    const cleanText = rawText.replace(/\s+/g, " ").trim();

    // Cap at 4000 characters to prevent memory bloating and conserve API tokens
    const trimmedText = cleanText.length > 4000 ? cleanText.substring(0, 4000) + "... [Content Truncated]" : cleanText;

    return {
      title,
      url,
      selectedText: selectedText || null,
      text: selectedText ? selectedText : trimmedText,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Lightweight futuristic floating HUD notification on the web page
   */
  function showHUDNotification(message, color = "#00f0ff") {
    let hud = document.getElementById("its-my-ai-hud-banner");
    if (!hud) {
      hud = document.createElement("div");
      hud.id = "its-my-ai-hud-banner";
      hud.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 2147483647;
        background: rgba(10, 16, 26, 0.92);
        color: #e2f1ff;
        border: 1px solid ${color};
        box-shadow: 0 0 16px rgba(0, 240, 255, 0.3);
        border-radius: 8px;
        padding: 10px 18px;
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 13px;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
        backdrop-filter: blur(8px);
        transition: opacity 0.3s ease, transform 0.3s ease;
        opacity: 0;
        transform: translateY(10px);
      `;
      document.body.appendChild(hud);
    }

    hud.innerHTML = `
      <span style="width: 8px; height: 8px; border-radius: 50%; background: ${color}; box-shadow: 0 0 8px ${color};"></span>
      <span>${escapeHtml(message)}</span>
    `;

    hud.style.opacity = "1";
    hud.style.transform = "translateY(0)";

    setTimeout(() => {
      hud.style.opacity = "0";
      hud.style.transform = "translateY(10px)";
    }, 3200);
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
})();
