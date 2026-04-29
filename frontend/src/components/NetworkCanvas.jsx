import { useEffect, useRef } from "react";
import * as THREE from "three";

export function NetworkCanvas({ density = 72 }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return undefined;
    if (import.meta.env.MODE === "test") {
      mount.dataset.fallback = "true";
      return undefined;
    }

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    } catch {
      mount.dataset.fallback = "true";
      return undefined;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    mount.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, 1, 0.1, 100);
    camera.position.z = 34;

    const particles = [];
    const geometry = new THREE.SphereGeometry(0.075, 10, 10);
    const material = new THREE.MeshBasicMaterial({ color: 0x7b2d26 });
    const group = new THREE.Group();
    scene.add(group);

    for (let index = 0; index < density; index += 1) {
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(
        (Math.random() - 0.5) * 42,
        (Math.random() - 0.5) * 24,
        (Math.random() - 0.5) * 18,
      );
      mesh.userData.speed = 0.12 + Math.random() * 0.28;
      mesh.userData.seed = Math.random() * Math.PI * 2;
      particles.push(mesh);
      group.add(mesh);
    }

    const linePositions = new Float32Array(density * 2 * 3);
    const lineGeometry = new THREE.BufferGeometry();
    lineGeometry.setAttribute("position", new THREE.BufferAttribute(linePositions, 3));
    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0x8a5a44,
      transparent: true,
      opacity: 0.14,
    });
    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(lines);

    let frameId = 0;
    let pointerX = 0;
    let pointerY = 0;

    const resize = () => {
      const { width, height } = mount.getBoundingClientRect();
      renderer.setSize(width, height, false);
      camera.aspect = width / Math.max(height, 1);
      camera.updateProjectionMatrix();
    };

    const onPointerMove = (event) => {
      const rect = mount.getBoundingClientRect();
      pointerX = ((event.clientX - rect.left) / Math.max(rect.width, 1) - 0.5) * 2;
      pointerY = -(((event.clientY - rect.top) / Math.max(rect.height, 1) - 0.5) * 2);
    };

    const animate = (time = 0) => {
      const t = time * 0.001;
      group.rotation.x = pointerY * 0.06 + Math.sin(t * 0.22) * 0.08;
      group.rotation.y = pointerX * 0.1 + Math.cos(t * 0.18) * 0.1;

      particles.forEach((particle, index) => {
        particle.position.y += Math.sin(t * particle.userData.speed + particle.userData.seed) * 0.004;
        particle.position.x += Math.cos(t * 0.2 + index) * 0.002;
      });

      let cursor = 0;
      for (let index = 0; index < particles.length - 1; index += 1) {
        const a = particles[index].position;
        const b = particles[(index + 7) % particles.length].position;
        linePositions[cursor] = a.x;
        linePositions[cursor + 1] = a.y;
        linePositions[cursor + 2] = a.z;
        linePositions[cursor + 3] = b.x;
        linePositions[cursor + 4] = b.y;
        linePositions[cursor + 5] = b.z;
        cursor += 6;
      }
      lineGeometry.attributes.position.needsUpdate = true;

      renderer.render(scene, camera);
      frameId = window.requestAnimationFrame(animate);
    };

    resize();
    window.addEventListener("resize", resize);
    mount.addEventListener("pointermove", onPointerMove);
    frameId = window.requestAnimationFrame(animate);

    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("resize", resize);
      mount.removeEventListener("pointermove", onPointerMove);
      geometry.dispose();
      material.dispose();
      lineGeometry.dispose();
      lineMaterial.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [density]);

  return <div className="network-canvas" ref={mountRef} aria-hidden="true" />;
}
