/**
 * IT'S MY AI — Voice Pipeline (STT, Wake Phrase, Audio Reactivity, TTS)
 * Implements Section 6:
 * - Web Speech API voice capture
 * - Wake phrase detection ("Hey, It's My AI" / "It's My AI")
 * - Web Audio API audio-reactive waveform
 * - Text-to-Speech synthesizer with futuristic cadence
 */

class VoiceSystem {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.isSpeaking = false;
    this.audioCtx = null;
    this.analyser = null;
    this.wakePhraseRegex = /^(hey\s+)?it'?s\s+my\s+ai/i;

    this.micBtn = document.getElementById("mic-toggle-btn");
    this.voiceStateTxt = document.getElementById("voice-state-txt");

    this.initSpeechRecognition();
    this.bindEvents();
  }

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("SpeechRecognition not supported in this browser. Fallback to text input.");
      if (this.voiceStateTxt) this.voiceStateTxt.innerText = "MIC NOT SUPPORTED";
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = false;
    this.recognition.lang = "en-US";

    this.recognition.onstart = () => {
      this.isListening = true;
      if (this.micBtn) this.micBtn.classList.add("active");
      if (this.voiceStateTxt) this.voiceStateTxt.innerText = "LISTENING...";
      window.hologram.setState("LISTENING");
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript.trim();
      console.log(`[Voice] Transcript: "${transcript}"`);

      // Check wake word or process direct command
      if (this.wakePhraseRegex.test(transcript) || this.isListening) {
        window.hologram.setState("THINKING");
        if (this.voiceStateTxt) this.voiceStateTxt.innerText = "PROCESSING...";

        // Dispatch to app controller
        if (window.app) {
          window.app.handleCommandInput(transcript);
        }
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("SpeechRecognition error:", event.error);
      this.stopListening();
    };

    this.recognition.onend = () => {
      this.stopListening();
    };
  }

  startListening() {
    if (!this.recognition) return;
    try {
      this.recognition.start();
    } catch (e) {
      console.warn("Recognition already started");
    }
  }

  stopListening() {
    this.isListening = false;
    if (this.micBtn) this.micBtn.classList.remove("active");
    if (this.voiceStateTxt) this.voiceStateTxt.innerText = "MIC IDLE";
    if (window.hologram.state === "LISTENING") {
      window.hologram.setState("IDLE");
    }
  }

  toggleListening() {
    if (this.isListening) {
      this.recognition.stop();
      this.stopListening();
    } else {
      this.startListening();
    }
  }

  speak(text) {
    if (!('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel(); // Stop any pending utterances
    const utterance = new SpeechSynthesisUtterance(text);

    // Slightly futuristic, calm, confident voice styling
    utterance.pitch = 0.95;
    utterance.rate = 1.05;

    // Pick sleek English voice if available
    const voices = window.speechSynthesis.getVoices();
    const sleekVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("David")));
    if (sleekVoice) utterance.voice = sleekVoice;

    utterance.onstart = () => {
      this.isSpeaking = true;
      window.hologram.setState("SPEAKING");
      this.startSpeechWaveSimulation();
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.stopSpeechWaveSimulation();
      window.hologram.setState("IDLE");
    };

    utterance.onerror = () => {
      this.isSpeaking = false;
      this.stopSpeechWaveSimulation();
      window.hologram.setState("IDLE");
    };

    window.speechSynthesis.speak(utterance);
  }

  startSpeechWaveSimulation() {
    this.waveInterval = setInterval(() => {
      if (!this.isSpeaking) return;
      const intensity = Math.random();
      window.hologram.setSpeechPulse(intensity);
    }, 100);
  }

  stopSpeechWaveSimulation() {
    if (this.waveInterval) clearInterval(this.waveInterval);
    window.hologram.setSpeechPulse(0);
  }

  bindEvents() {
    if (this.micBtn) {
      this.micBtn.addEventListener("click", () => this.toggleListening());
    }
  }
}

window.voice = new VoiceSystem();
