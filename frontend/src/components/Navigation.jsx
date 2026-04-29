import { useEffect, useState } from "react";
import logoMark from "../assets/ali-logo-mark.png";

export function Navigation({ currentPage, onNavigate }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 60);
    handleScroll();
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header className={`site-nav ${scrolled ? "is-scrolled" : ""}`}>
      <div className="site-nav__inner container">
        <button className="brand-mark ghost-button" type="button" onClick={() => onNavigate("landing")}>
          <span className="brand-mark__glyph">
            <img className="brand-mark__logo" src={logoMark} alt="ALI project logo" />
          </span>
          <span className="brand-mark__text">ALI</span>
        </button>
        <nav className="nav-actions" aria-label="Primary navigation">
          {currentPage === "landing" && (
            <a className="nav-link" href="#services">
              See how it works
            </a>
          )}
          <button className="ghost-button" type="button" onClick={() => onNavigate("login")}>
            Log In
          </button>
          <button className="primary-button" type="button" onClick={() => onNavigate("signup")}>
            Sign Up
          </button>
        </nav>
      </div>
    </header>
  );
}
