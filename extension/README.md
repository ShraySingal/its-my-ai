# IT'S MY AI — Browser Companion Extension (Manifest V3)

A futuristic browser intelligence companion connecting live web browsing sessions directly to your personal **IT'S MY AI** Command Center.

---

## ⚡ Key Capabilities

1. **Active Tab Intelligence**:
   - Inspects the current page's DOM context without sending data to external third parties.
   - Summarizes long articles, documentation, or news in seconds via your local IT'S MY AI backend.
2. **Instant Memory Storing**:
   - Save bookmarks, articles, research topics, and code documentation directly into IT'S MY AI's persistent memory (`/api/memory`).
3. **Key Point Extraction**:
   - Extracts actionable items, names, statistics, and main takeaways.
4. **Context Menu Actions**:
   - Right-click any text selection on any webpage:
     - `IT'S MY AI: Summarize Selection`
     - `IT'S MY AI: Analyze Web Page`
5. **In-Page Holographic Notifications**:
   - Floating cyan HUD toast updates confirming analysis directly on the web page.

---

## 🚀 How to Install in Chrome / Edge / Brave

1. Open your browser and navigate to the Extensions page:
   - **Chrome**: `chrome://extensions`
   - **Edge**: `edge://extensions`
   - **Brave**: `brave://extensions`
2. Enable **"Developer mode"** (toggle in the top-right corner).
3. Click the **"Load unpacked"** button in the top-left.
4. Browse to and select the `extension` folder inside this project:
   ```
   c:\Users\shray\OneDrive\Desktop\It's My AI\extension
   ```
5. Pin the **IT'S MY AI** extension to your browser toolbar.

---

## ⚙️ How to Use

1. **Start the IT'S MY AI backend**:
   Double-click `start.bat` or run:
   ```cmd
   python start.py
   ```
2. The extension badge will show **`ON`** (cyan).
3. Click the extension icon on any webpage to open the mini-HUD:
   - Click **`[ Summarize Page ]`** for an instant briefing.
   - Click **`[ Extract Key Points ]`** for facts and action items.
   - Click **`[ Save to Memory ]`** to bookmark and index the page into your memory database.
   - Or type any custom question into the prompt box!
