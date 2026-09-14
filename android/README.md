# IT'S MY AI Mobile — Android Companion Application
**Companion client for IT'S MY AI Holographic Command Center (Section 19)**

## Requirements
- Android Studio Iguana / Hedgehog or newer
- JDK 17+
- Android SDK 34 (Minimum SDK: 26 / Android 8.0)

## Features
- **Battery Sync**: Real-time battery status pushed to laptop HUD.
- **WebSocket & Heartbeat**: Automatically registers phone in `devices.json` and Supabase cloud.
- **Futuristic Cyberpunk UI**: Jetpack Compose holographic theme matching the desktop HUD.
- **Permissions with Consent**: Declares camera, network, and battery permissions adhering strictly to Section 19.

## How to Build & Run
1. Open Android Studio.
2. Select **Open an Existing Project** and choose the `android/` directory.
3. In `ApiClient.kt`, set your laptop's local IP (e.g. `http://192.168.1.X:8000`). If running in the official Android Emulator, `http://10.0.2.2:8000` is used by default.
4. Click **Run 'app'** (`Shift + F10`) to deploy to your Android device or emulator.
5. Tap **"SYNC WITH LAPTOP COMMAND CENTER"** to pair.

<!-- build trigger -->
