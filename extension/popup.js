/**
 * IT'S MY AI — Browser Companion Popup Controller
 */

const BACKEND_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", async () => {
  const statusBadge = document.getElementById("statusBadge");
  const statusText = document.getElementById("statusText");
  const pageTitle = document.getElementById("pageTitle");
  const pageUrl = document.getElementById("pageUrl");
  const outputContent = document.getElementById("outputContent");
  const btnSummarize = document.getElementById("btnSummarize");
  const btnExtract = document.getElementById("btnExtract");
  const btnSendMemory = document.getElementById("btnSendMemory");
  const btnClear = document.getElementById("btnClear");
  const customPrompt = document.getElementById("customPrompt");
  const btnSend = document.getElementById("btnSend");

  let currentTab = null;
  let cachedPageData = null;

  // 1. Get Active Tab Info
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs && tabs.length > 0) {
      currentTab = tabs[0];
      pageTitle.textContent = currentTab.title || "Untitled Page";
      pageUrl.textContent = currentTab.url || "";
    }
  } catch (err) {
    pageTitle.textContent = "Unable to read active tab";
  }

  // 2. Check Backend Health
  async function checkHealth() {
    try {
      const res = await fetch(`${BACKEND_URL}/health`, { method: "GET" });
      if (res.ok) {
        statusBadge.className = "status-indicator online";
        statusText.textContent = "ONLINE";
        return true;
      }
    } catch (e) {
      // offline
    }
    statusBadge.className = "status-indicator offline";
    statusText.textContent = "OFFLINE";
    return false;
  }

  await checkHealth();

  // 3. Helper to extract page data from content script
  async function getPageData() {
    if (cachedPageData) return cachedPageData;
    if (!currentTab || !currentTab.id) {
      throw new Error("No active browser tab found.");
    }

    return new Promise((resolve, reject) => {
      chrome.tabs.sendMessage(currentTab.id, { action: "GET_PAGE_DATA" }, (res) => {
        if (chrome.runtime.lastError) {
          // Content script may not be injected on chrome:// or restricted pages
          resolve({
            title: currentTab.title || "",
            url: currentTab.url || "",
            text: `Web Page: ${currentTab.title} (${currentTab.url})`
          });
        } else if (res && res.success) {
          cachedPageData = res.data;
          resolve(res.data);
        } else {
          resolve({
            title: currentTab.title || "",
            url: currentTab.url || "",
            text: `Web Page: ${currentTab.title} (${currentTab.url})`
          });
        }
      });
    });
  }

  // 4. Send Query to IT'S MY AI Backend
  async function queryAssistant(promptMessage) {
    outputContent.textContent = "Thinking... contacting IT'S MY AI neural core...";
    try {
      const res = await fetch(`${BACKEND_URL}/api/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [
            { role: "user", content: promptMessage }
          ],
          response_mode: "ACTION"
        })
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const data = await res.json();
      outputContent.textContent = data.text || "No textual response received.";
    } catch (err) {
      outputContent.textContent = `[CONNECTION ERROR] Could not contact IT'S MY AI backend at ${BACKEND_URL}.\n\nEnsure backend is running (python start.py).`;
    }
  }

  // Action: Summarize Page
  btnSummarize.addEventListener("click", async () => {
    try {
      const page = await getPageData();
      const prompt = `Please provide a concise 3-5 bullet point executive summary of this webpage:\n\nTitle: ${page.title}\nURL: ${page.url}\n\nContent:\n${page.text}`;
      await queryAssistant(prompt);
    } catch (err) {
      outputContent.textContent = `Error: ${err.message}`;
    }
  });

  // Action: Extract Key Points
  btnExtract.addEventListener("click", async () => {
    try {
      const page = await getPageData();
      const prompt = `Extract the key facts, statistics, names, and action items from this webpage:\n\nTitle: ${page.title}\nURL: ${page.url}\n\nContent:\n${page.text}`;
      await queryAssistant(prompt);
    } catch (err) {
      outputContent.textContent = `Error: ${err.message}`;
    }
  });

  // Action: Save to Long-Term Memory
  btnSendMemory.addEventListener("click", async () => {
    try {
      const page = await getPageData();
      outputContent.textContent = "Saving webpage reference to long-term memory...";

      const res = await fetch(`${BACKEND_URL}/api/memory`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: `Web Bookmark & Context: "${page.title}" (${page.url})`,
          category: "project",
          tags: ["web", "bookmark", "browser-companion"]
        })
      });

      if (res.ok) {
        outputContent.textContent = `[SAVED] Page memorized successfully!\n\nReference: ${page.title}\nURL: ${page.url}`;
      } else {
        outputContent.textContent = `Failed to save memory. Status: ${res.status}`;
      }
    } catch (err) {
      outputContent.textContent = `Error storing memory: ${err.message}`;
    }
  });

  // Custom Prompt Submission
  async function submitCustomPrompt() {
    const text = customPrompt.value.trim();
    if (!text) return;
    customPrompt.value = "";

    try {
      const page = await getPageData();
      const fullPrompt = `Context from active webpage:\nTitle: ${page.title}\nURL: ${page.url}\n\nUser Question: ${text}\n\nRelevant Web Content:\n${page.text}`;
      await queryAssistant(fullPrompt);
    } catch (err) {
      await queryAssistant(text);
    }
  }

  btnSend.addEventListener("click", submitCustomPrompt);
  customPrompt.addEventListener("keydown", (e) => {
    if (e.key === "Enter") submitCustomPrompt();
  });

  // Clear feed
  btnClear.addEventListener("click", () => {
    outputContent.textContent = "Ready. Select an action above or type a question.";
  });
});
