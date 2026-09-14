/**
 * IT'S MY AI — 3D Holographic Network Radar (Section 28)
 * Visualizes authorized subnet devices orbiting the central AI command node.
 */

class RadarEngine {
  constructor(hologramEngine) {
    this.hologram = hologramEngine;
    this.radarGroup = new THREE.Group();
    this.radarGroup.visible = false;
    this.hologram.scene.add(this.radarGroup);
    this.devices = [];
    this.sweepAngle = 0;
    this.isActive = false;

    this.createRadarGeometry();
  }

  createRadarGeometry() {
    // 1. Concentric Range Rings
    const ringRadii = [0.8, 1.5, 2.3];
    ringRadii.forEach(r => {
      const circleGeo = new THREE.BufferGeometry();
      const points = [];
      for (let i = 0; i <= 64; i++) {
        const theta = (i / 64) * Math.PI * 2;
        points.push(new THREE.Vector3(r * Math.cos(theta), r * Math.sin(theta), 0));
      }
      circleGeo.setFromPoints(points);
      const circleMat = new THREE.LineBasicMaterial({
        color: 0x00f0ff,
        transparent: true,
        opacity: 0.25
      });
      const ringLine = new THREE.Line(circleGeo, circleMat);
      this.radarGroup.add(ringLine);
    });

    // Crosshairs
    const lineMat = new THREE.LineBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.2 });
    const hGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-2.5, 0, 0),
      new THREE.Vector3(2.5, 0, 0)
    ]);
    const vGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, -2.5, 0),
      new THREE.Vector3(0, 2.5, 0)
    ]);
    this.radarGroup.add(new THREE.Line(hGeo, lineMat));
    this.radarGroup.add(new THREE.Line(vGeo, lineMat));

    // Sweeping Radar Line
    const sweepGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(2.4, 0, 0)
    ]);
    this.sweepMat = new THREE.LineBasicMaterial({
      color: 0x00ff88,
      transparent: true,
      opacity: 0.75
    });
    this.sweepLine = new THREE.Line(sweepGeo, this.sweepMat);
    this.radarGroup.add(this.sweepLine);

    // Initial devices
    this.loadNetworkNodes();
  }

  loadNetworkNodes() {
    const rawDevices = [
      { name: "Primary Laptop", type: "Laptop", ip: "192.168.1.105", dist: 0.0, color: 0x00f0ff, angle: 0 },
      { name: "Gateway Router", type: "Router", ip: "192.168.1.1", dist: 0.8, color: 0x00f0ff, angle: Math.PI / 4 },
      { name: "It's My AI Mobile", type: "Phone", ip: "192.168.1.142", dist: 1.5, color: 0x00ff88, angle: -Math.PI / 3 },
      { name: "Smart TV", type: "TV", ip: "192.168.1.178", dist: 2.3, color: 0xffaa00, angle: (3 * Math.PI) / 4 },
      { name: "Printer", type: "Printer", ip: "192.168.1.190", dist: 2.3, color: 0x888888, angle: -Math.PI * 0.8 }
    ];

    rawDevices.forEach(d => {
      const nodeGeo = new THREE.SphereGeometry(d.dist === 0 ? 0.12 : 0.08, 12, 12);
      const nodeMat = new THREE.MeshBasicMaterial({ color: d.color });
      const nodeMesh = new THREE.Mesh(nodeGeo, nodeMat);

      nodeMesh.position.x = d.dist * Math.cos(d.angle);
      nodeMesh.position.y = d.dist * Math.sin(d.angle);
      nodeMesh.position.z = 0;

      // Connecting line to center if not center
      if (d.dist > 0) {
        const connGeo = new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(nodeMesh.position.x, nodeMesh.position.y, 0)
        ]);
        const connMat = new THREE.LineBasicMaterial({
          color: d.color,
          transparent: true,
          opacity: 0.3
        });
        this.radarGroup.add(new THREE.Line(connGeo, connMat));
      }

      this.radarGroup.add(nodeMesh);
      this.devices.push({ ...d, mesh: nodeMesh });
    });
  }

  toggleView() {
    this.isActive = !this.isActive;
    this.radarGroup.visible = this.isActive;
    this.hologram.setVisible(!this.isActive);

    const overlay = document.getElementById("radar-hud-overlay");
    const title = document.getElementById("hologram-mode-title");
    const btn = document.getElementById("btn-toggle-radar");

    if (this.isActive) {
      if (overlay) overlay.classList.remove("hidden");
      if (title) title.innerText = "NETWORK RADAR // ACTIVE";
      if (btn) btn.classList.add("active");
      this.hologram.setState("NETWORK SCAN");
    } else {
      if (overlay) overlay.classList.add("hidden");
      if (title) title.innerText = "HOLOGRAM CORE // ONLINE";
      if (btn) btn.classList.remove("active");
      this.hologram.setState("IDLE");
    }
  }

  updateSweep() {
    if (!this.isActive) return;
    this.sweepAngle -= 0.03;
    this.sweepLine.rotation.z = this.sweepAngle;
  }
}

window.radar = new RadarEngine(window.hologram);

// Hook sweep update into animation loop
const originalAnimate = window.hologram.animate.bind(window.hologram);
window.hologram.animate = function(currentTime) {
  if (window.radar) window.radar.updateSweep();
  originalAnimate(currentTime);
};
