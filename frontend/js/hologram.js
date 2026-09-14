/**
 * IT'S MY AI — 3D Holographic Interface (Three.js & WebGL)
 * Implements Sections 26, 27, 41:
 * - Central futuristic AI avatar core with rotating orbital rings and particle cloud
 * - 8 Interactive States (IDLE, LISTENING, THINKING, EXECUTING, SPEAKING, SUCCESS, ERROR, SLEEP)
 * - Strict 4 GB RAM / Low-GPU optimization with idle frame throttling
 */

class HologramEngine {
  constructor(containerId = "hologram-viewport", canvasId = "hologram-canvas") {
    this.container = document.getElementById(containerId);
    this.canvas = document.getElementById(canvasId);
    this.state = "IDLE";
    this.isRunning = true;
    this.targetFps = 45; // Smooth but low CPU usage
    this.lastFrameTime = 0;
    this.speechPulse = 0;

    this.initThree();
    this.createHologramObjects();
    this.bindEvents();
    this.animate(0);
  }

  initThree() {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(
      50,
      this.container.clientWidth / this.container.clientHeight,
      0.1,
      1000
    );
    this.camera.position.z = 4.8;

    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
      powerPreference: "low-power" // Optimized for 4 GB RAM / integrated graphics
    });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  }

  createHologramObjects() {
    this.hologramGroup = new THREE.Group();
    this.scene.add(this.hologramGroup);

    // 1. Central Core Sphere (Futuristic Wireframe Hologram)
    const coreGeo = new THREE.IcosahedronGeometry(0.9, 2);
    this.coreMaterial = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: true,
      transparent: true,
      opacity: 0.75
    });
    this.coreMesh = new THREE.Mesh(coreGeo, this.coreMaterial);
    this.hologramGroup.add(this.coreMesh);

    // Inner Glowing Solid Kernel
    const innerGeo = new THREE.OctahedronGeometry(0.45, 0);
    this.innerMaterial = new THREE.MeshBasicMaterial({
      color: 0x9d4edd,
      wireframe: true,
      transparent: true,
      opacity: 0.9
    });
    this.innerMesh = new THREE.Mesh(innerGeo, this.innerMaterial);
    this.hologramGroup.add(this.innerMesh);

    // 2. Primary Orbital Ring
    const ring1Geo = new THREE.TorusGeometry(1.5, 0.02, 16, 100);
    this.ring1Material = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.6
    });
    this.ring1 = new THREE.Mesh(ring1Geo, this.ring1Material);
    this.ring1.rotation.x = Math.PI / 3;
    this.hologramGroup.add(this.ring1);

    // 3. Secondary Counter-Rotating Ring
    const ring2Geo = new THREE.TorusGeometry(1.8, 0.015, 16, 100);
    this.ring2Material = new THREE.MeshBasicMaterial({
      color: 0x9d4edd,
      transparent: true,
      opacity: 0.5
    });
    this.ring2 = new THREE.Mesh(ring2Geo, this.ring2Material);
    this.ring2.rotation.y = Math.PI / 4;
    this.hologramGroup.add(this.ring2);

    // 4. Floating Particle Cloud (Lightweight - 180 particles)
    const particleCount = 180;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      const r = 1.3 + Math.random() * 1.5;

      positions[i] = r * Math.sin(phi) * Math.cos(theta);
      positions[i + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i + 2] = r * Math.cos(phi);
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.particleMaterial = new THREE.PointsMaterial({
      color: 0x00f0ff,
      size: 0.04,
      transparent: true,
      opacity: 0.65
    });
    this.particleCloud = new THREE.Points(particleGeo, this.particleMaterial);
    this.hologramGroup.add(this.particleCloud);
  }

  setState(newState) {
    this.state = newState.toUpperCase();
    console.log(`[Hologram] State transition: ${this.state}`);

    const badge = document.getElementById("hologram-state-badge");
    const title = document.getElementById("hologram-mode-title");
    const wave = document.getElementById("audio-wave-container");

    if (badge) badge.innerText = `STATE: ${this.state}`;

    switch (this.state) {
      case "IDLE":
        this.coreMaterial.color.setHex(0x00f0ff);
        this.innerMaterial.color.setHex(0x9d4edd);
        this.ring1Material.color.setHex(0x00f0ff);
        if (wave) wave.classList.remove("active");
        break;

      case "LISTENING":
        this.coreMaterial.color.setHex(0x00f0ff);
        this.innerMaterial.color.setHex(0x00ff88);
        this.ring1Material.color.setHex(0x00ff88);
        if (wave) wave.classList.add("active");
        break;

      case "THINKING":
        this.coreMaterial.color.setHex(0x9d4edd);
        this.innerMaterial.color.setHex(0x00f0ff);
        this.ring1Material.color.setHex(0x9d4edd);
        if (wave) wave.classList.remove("active");
        break;

      case "EXECUTING":
        this.coreMaterial.color.setHex(0xffaa00);
        this.innerMaterial.color.setHex(0xffaa00);
        this.ring1Material.color.setHex(0xffaa00);
        break;

      case "SPEAKING":
        this.coreMaterial.color.setHex(0x00f0ff);
        this.innerMaterial.color.setHex(0xffffff);
        if (wave) wave.classList.add("active");
        break;

      case "SUCCESS":
        this.coreMaterial.color.setHex(0x00ff88);
        this.innerMaterial.color.setHex(0x00ff88);
        this.ring1Material.color.setHex(0x00ff88);
        setTimeout(() => this.setState("IDLE"), 2500);
        break;

      case "ERROR":
        this.coreMaterial.color.setHex(0xff3366);
        this.innerMaterial.color.setHex(0xff3366);
        this.ring1Material.color.setHex(0xff3366);
        setTimeout(() => this.setState("IDLE"), 3000);
        break;

      case "SLEEP":
        this.coreMaterial.color.setHex(0x224455);
        this.innerMaterial.color.setHex(0x112233);
        this.ring1Material.color.setHex(0x113344);
        if (wave) wave.classList.remove("active");
        break;
    }
  }

  setSpeechPulse(intensity) {
    this.speechPulse = intensity;
  }

  animate(currentTime) {
    requestAnimationFrame((t) => this.animate(t));

    // Frame rate throttle for low CPU / 4 GB RAM
    const elapsed = currentTime - this.lastFrameTime;
    const interval = 1000 / this.targetFps;
    if (elapsed < interval) return;
    this.lastFrameTime = currentTime - (elapsed % interval);

    if (this.state === "SLEEP") {
      // Extremely slow rotation in sleep mode to minimize CPU
      this.hologramGroup.rotation.y += 0.001;
      this.renderer.render(this.scene, this.camera);
      return;
    }

    let rotSpeed = 0.005;
    let ringSpeed = 0.012;

    if (this.state === "THINKING") {
      rotSpeed = 0.02;
      ringSpeed = 0.035;
    } else if (this.state === "EXECUTING") {
      rotSpeed = 0.025;
      ringSpeed = 0.045;
    } else if (this.state === "SPEAKING") {
      const pulse = 1 + Math.sin(currentTime * 0.01) * 0.15 + this.speechPulse * 0.2;
      this.coreMesh.scale.set(pulse, pulse, pulse);
    } else {
      this.coreMesh.scale.set(1, 1, 1);
    }

    // Rotations
    this.coreMesh.rotation.x += rotSpeed;
    this.coreMesh.rotation.y += rotSpeed * 1.5;
    this.innerMesh.rotation.x -= rotSpeed * 1.8;
    this.innerMesh.rotation.z += rotSpeed;

    this.ring1.rotation.z += ringSpeed;
    this.ring2.rotation.x -= ringSpeed * 0.7;
    this.particleCloud.rotation.y += 0.002;

    this.renderer.render(this.scene, this.camera);
  }

  bindEvents() {
    window.addEventListener("resize", () => {
      if (!this.container) return;
      const width = this.container.clientWidth;
      const height = this.container.clientHeight;
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
    });

    // Reduce frame rate when tab is hidden to save power
    document.addEventListener("visibilitychange", () => {
      this.targetFps = document.hidden ? 10 : 45;
    });
  }

  setVisible(visible) {
    if (this.hologramGroup) {
      this.hologramGroup.visible = visible;
    }
  }

  setTheme(themeName) {
    const themes = {
      cyan: { core: 0x00f0ff, secondary: 0x9d4edd, cssPrimary: "#00f0ff" },
      amber: { core: 0xffaa00, secondary: 0xff4400, cssPrimary: "#ffaa00" },
      emerald: { core: 0x00ff88, secondary: 0x00aa55, cssPrimary: "#00ff88" },
      violet: { core: 0xb026ff, secondary: 0x7928ca, cssPrimary: "#b026ff" }
    };
    const t = themes[themeName] || themes.cyan;
    if (this.coreMaterial) this.coreMaterial.color.setHex(t.core);
    if (this.ring1Material) this.ring1Material.color.setHex(t.core);
    if (this.particleMaterial) this.particleMaterial.color.setHex(t.core);
    if (this.innerMaterial) this.innerMaterial.color.setHex(t.secondary);
    if (this.ring2Material) this.ring2Material.color.setHex(t.secondary);
    document.documentElement.style.setProperty('--hud-cyan', t.cssPrimary);
  }
}

window.hologram = new HologramEngine();
