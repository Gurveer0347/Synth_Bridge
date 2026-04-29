import { useState } from "react";

import { NetworkCanvas } from "./NetworkCanvas";

export function AuthPage({ mode, onNavigate }) {
  const isSignup = mode === "signup";
  const [loading, setLoading] = useState(false);

  const submit = (event) => {
    event.preventDefault();
    setLoading(true);
    window.setTimeout(() => {
      setLoading(false);
      onNavigate("tool");
    }, 850);
  };

  return (
    <main className="page auth-layout">
      <section className="auth-form-side">
        <form className="auth-card" onSubmit={submit}>
          <h1 className="auth-title">{isSignup ? "Create your account" : "Welcome back"}</h1>
          <p className="auth-subtitle">{isSignup ? "Join Team ALI" : "Log in to ALI"}</p>

          <div className="auth-fields">
            {isSignup && (
              <div className="field">
                <input id="full-name" placeholder=" " defaultValue="Savneet Kaur" />
                <label htmlFor="full-name">Full Name</label>
              </div>
            )}
            <div className="field">
              <input id="email" placeholder=" " type="email" defaultValue="you@example.com" />
              <label htmlFor="email">Email Address</label>
            </div>
            <div className="field">
              <input id="password" placeholder=" " type="password" defaultValue={isSignup ? "create-password" : "ali-demo"} />
              <label htmlFor="password">Password</label>
            </div>
          </div>

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? <span className="spinner" aria-label="Loading" /> : isSignup ? "Sign Up" : "Log In"}
          </button>

          <p className="auth-switch">
            {isSignup ? "Already have an account? " : "Don't have an account? "}
            <button className="link-button" type="button" onClick={() => onNavigate(isSignup ? "login" : "signup")}>
              {isSignup ? "Log in" : "Sign up"}
            </button>
          </p>
        </form>
      </section>

      <section className="auth-visual-side">
        <NetworkCanvas density={54} />
        <div className="grid-glow" />
        <div className="auth-panel-content">
          <div className="auth-logo">ALI</div>
          <p className="auth-tagline">Autonomous Integration Layer.</p>
          <div className="mini-metrics">
            <div className="metric">
              <strong>2</strong>
              <span>docs in</span>
            </div>
            <div className="metric">
              <strong>AI</strong>
              <span>thinks</span>
            </div>
            <div className="metric">
              <strong>1</strong>
              <span>bridge out</span>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
