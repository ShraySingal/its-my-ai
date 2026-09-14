/**
 * IT'S MY AI — Browser Companion Service Worker
 * Manages background state, connection monitoring, and context menu actions.
 */

const BACKEND_URL = "http://127.0.0.1:8000";

// Check health of local IT'S MY AI backend on startup and alarm
chrome.runtime.onInstalled.addListener(() => {
  setupContextMenu();
  checkBackendHealth();
  chrome.alarms.create("backendHealthCheck", { periodInMinutes: 1 });
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "backendHealthCheck") {
    checkBackendHealth();
  }
});

function setupContextMenu() {
  chrome.contextMenus.create({
    id: "its_my_ai_summarize",
    title: "IT'S MY AI: Summarize Selection",
    contexts: ["selection"]
  });

  chrome.contextMenus.create({
    id: "its_my_ai_analyze_page",
    title: "IT'S MY AI: Analyze Web Page",
    contexts: ["page"]
  });
}

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (!tab || !tab.id) return;

  if (info.menuItemId === "its_my_ai_summarize" && info.selectionText) {
    sendToAssistant(
      `Please summarize this excerpt from "${tab.title}":\n\n${info.selectionText}`,
      tab.id
    );
  } else if (info.menuItemId === "its_my_ai_analyze_page") {
    chrome.tabs.sendMessage(tab.id, { action: "GET_PAGE_DATA" }, (res) => {
      if (res && res.success && res.data) {
        sendToAssistant(
          `Please analyze and summarize this web page:\nTitle: ${res.data.title}\nURL: ${res.data.url}\n\nContent:\n${res.data.text}`,
          tab.id
        );
      }
    });
  }
});

async function checkBackendHealth() {
  try {
    const res = await fetch(`${BACKEND_URL}/health`, { method: "GET" });
    if (res.ok) {
      chrome.action.setBadgeText({ text: "ON" });
      chrome.action.setBadgeBackgroundColor({ color: "#00f0ff" });
      return true;
    }
  } catch (err) {
    // Backend offline
  }
  chrome.action.setBadgeText({ text: "OFF" });
  chrome.action.setBadgeBackgroundColor({ color: "#556677" });
  return false;
}

async function sendToAssistant(promptText, tabId) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [
          { role: "user", content: promptText }
        ],
        response_mode: "ACTION"
      })
    });

    if (response.ok) {
      const data = await response.json();
      const preview = data.text ? data.text.substring(0, 60) + '...' : 'Task Completed';
      chrome.tabs.sendMessage(tabId, {
        action: "FLASH_STATUS",
        text: `IT'S MY AI: ${preview}`,
        color: "#00f0ff"
      });
    }
  } catch (err) {
    chrome.tabs.sendMessage(tabId, {
      action: "FLASH_STATUS",
      text: "IT'S MY AI backend offline. Please start backend.",
      color: "#ff3366"
    });
  }
}

