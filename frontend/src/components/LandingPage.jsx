import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import { NetworkCanvas } from "./NetworkCanvas";

gsap.registerPlugin(ScrollTrigger);

const services = [
  ["01", "Semantic Field Choreography", "ALI reads the docs and lets matching fields find each other by meaning."],
  ["02", "Connector-Free Bridges", "Any documented API can become part of the flow without waiting for a marketplace plugin."],
  ["03", "Self-Healing Sandbox", "Failures become feedback loops, so the bridge repairs itself instead of stopping cold."],
  ["04", "Inspectable Python", "The bridge is not magic fog. You see the exact Python that was generated and run."],
];

const teams = [
  ["Startups", "Connect your CRM to your chat tool without hiring a backend engineer."],
  ["Dev Teams", "Stop writing integration code. Focus on your actual product."],
  ["Ops Teams", "Link enterprise tools that were never meant to talk to each other."],
];

export function LandingPage({ onNavigate }) {
  const rootRef = useRef(null);
  const sublineRef = useRef(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return undefined;

    const lines = [
      "ALI reads your API docs and builds the bridge automatically.",
      "Drop two files. Describe what you want. Done.",
      "Your tools. Connected. No engineer needed.",
    ];
    let lineIndex = 0;
    let charIndex = lines[0].length;
    let deleting = false;
    let timeoutId;

    const type = () => {
      const current = lines[lineIndex];
      if (sublineRef.current) {
        sublineRef.current.textContent = current.slice(0, charIndex);
      }
      if (!deleting && charIndex < current.length) {
        charIndex += 1;
        timeoutId = window.setTimeout(type, 45);
      } else if (!deleting) {
        deleting = true;
        timeoutId = window.setTimeout(type, 1600);
      } else if (charIndex > 0) {
        charIndex -= 1;
        timeoutId = window.setTimeout(type, 22);
      } else {
        deleting = false;
        lineIndex = (lineIndex + 1) % lines.length;
        timeoutId = window.setTimeout(type, 240);
      }
    };

    type();

    const context = gsap.context(() => {
      gsap.from(".hero-title span", {
        y: 70,
        autoAlpha: 0,
        duration: 0.9,
        stagger: 0.1,
        ease: "power4.out",
      });
      gsap.from(".hero-content .eyebrow, .hero-subline, .hero-actions, .scroll-hint, .hero-note", {
        y: 24,
        autoAlpha: 0,
        duration: 0.75,
        stagger: 0.08,
        ease: "power3.out",
        delay: 0.2,
      });
      gsap.from(".glass-artifact, .orbit-chip, .artifact-node", {
        scale: 0.82,
        rotate: -8,
        autoAlpha: 0,
        duration: 0.9,
        stagger: 0.08,
        ease: "back.out(1.6)",
        delay: 0.15,
      });
      gsap.from(".service-card", {
        y: 42,
        autoAlpha: 0,
        stagger: 0.12,
        duration: 0.7,
        ease: "power3.out",
        scrollTrigger: {
          trigger: "#services",
          start: "top 70%",
        },
      });
      gsap.from(".team-strip", {
        x: -70,
        autoAlpha: 0,
        stagger: 0.12,
        duration: 0.8,
        ease: "expo.out",
        scrollTrigger: {
          trigger: ".team-stack",
          start: "top 72%",
        },
      });
      gsap.from(".demo-preview", {
        scale: 0.96,
        autoAlpha: 0,
        duration: 0.8,
        ease: "power3.out",
        scrollTrigger: {
          trigger: ".demo-preview",
          start: "top 76%",
        },
      });
    }, root);

    return () => {
      window.clearTimeout(timeoutId);
      context.revert();
    };
  }, []);

  return (
    <main className="page landing-page" ref={rootRef}>
      <section className="hero-section">
        <NetworkCanvas />
        <div className="grid-glow" />
        <div className="hero-content container">
          <div className="hero-copy">
            <div className="eyebrow">Autonomous Integration Layer</div>
            <h1 className="hero-title">
              <span>Connect Any Two Tools.</span>
              <span>No Code. No Setup. No Waiting.</span>
            </h1>
            <p className="hero-subline">
              <span className="typed-value" ref={sublineRef}>
                ALI reads your API docs and builds the bridge automatically.
              </span>
            </p>
            <p className="hero-note">Dynamic middleware that reads API docs and builds bridges autonomously.</p>
            <div className="hero-actions">
              <button className="primary-button pulse-button" type="button" onClick={() => onNavigate("signup")}>
                Get Started Free
              </button>
              <a className="secondary-button" href="#services">
                See how it works
              </a>
            </div>
            <a className="scroll-hint" href="#services">
              Drop two docs. Get a live bridge.
            </a>
          </div>

          <aside className="hero-art" aria-label="ALI bridge sculpture">
            <div className="orbit-chip orbit-chip--one">RAG</div>
            <div className="orbit-chip orbit-chip--two">Sandbox</div>
            <div className="orbit-chip orbit-chip--three">Self-heal</div>
            <div className="glass-artifact">
              <span className="artifact-node artifact-node--a">HubSpot</span>
              <span className="artifact-node artifact-node--b">Discord</span>
              <span className="artifact-node artifact-node--c">Python</span>
              <div className="artifact-core">
                <strong>ALI</strong>
                <small>bridge compiler</small>
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section className="landing-section" id="services">
        <div className="container">
          <p className="section-kicker">The bridge studio</p>
          <h2 className="section-title">What ALI Does For You</h2>
          <p className="section-copy">
            ALI turns API documentation into a working integration pipeline with semantic mapping, generated code,
            sandbox execution, and autonomous retry.
          </p>
          <div className="service-grid">
            {services.map(([icon, title, copy]) => (
              <article className="service-card" key={title}>
                <div className="service-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="landing-section">
        <div className="container">
          <p className="section-kicker">Who gets unstuck</p>
          <h2 className="section-title">Built For Teams Who Move Fast.</h2>
          <div className="team-stack">
            {teams.map(([title, copy]) => (
              <article className="team-strip" key={title}>
                <h3>{title}</h3>
                <p>{copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="landing-section">
        <div className="container">
          <p className="section-kicker">Live bridge preview</p>
          <h2 className="section-title">Drop two docs. Get a live bridge.</h2>
          <div className="demo-preview">
            <div className="doc-tile">
              <strong>HubSpot API Docs</strong>
              <div className="doc-lines">
                <span />
                <span />
                <span />
              </div>
            </div>
            <div className="brain-core">
              <span>ALI</span>
            </div>
            <div className="discord-tile">
              <strong>Discord #sales-alerts</strong>
              <p>New Lead: John Doe, Acme Corp.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-section cta-section">
        <div className="container">
          <div className="footer-marquee" aria-hidden="true">
            ALI / BRIDGE / HEAL / RUN
          </div>
          <h2 className="section-title">Ready to connect your tools?</h2>
          <p className="section-copy">A final loud moment for the judges: one interface, two documents, one working bridge.</p>
          <div className="hero-actions">
            <button className="primary-button" type="button" onClick={() => onNavigate("signup")}>
              Start for Free
            </button>
          </div>
          <p className="footer-line">Team ALI | Antarjot | Japneet | Gurveer | Savneet</p>
        </div>
      </section>
    </main>
  );
}
