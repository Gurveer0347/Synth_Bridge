import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

import { AuthPage } from "./components/AuthPage";
import { LandingPage } from "./components/LandingPage";
import { Navigation } from "./components/Navigation";
import { ToolPage } from "./components/ToolPage";

function App() {
  const [page, setPage] = useState("landing");
  const stageRef = useRef(null);

  const navigate = (nextPage) => {
    if (nextPage === page) return;
    setPage(nextPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  useEffect(() => {
    if (!stageRef.current) return undefined;
    const context = gsap.context(() => {
      gsap.fromTo(
        stageRef.current,
        { autoAlpha: 0, y: 20 },
        { autoAlpha: 1, y: 0, duration: 0.45, ease: "power3.out" },
      );
    }, stageRef.current);
    return () => context.revert();
  }, [page]);

  return (
    <div className="app-shell">
      <Navigation currentPage={page} onNavigate={navigate} />
      <div className="page-stage" ref={stageRef}>
        {page === "landing" && <LandingPage onNavigate={navigate} />}
        {page === "signup" && <AuthPage mode="signup" onNavigate={navigate} />}
        {page === "login" && <AuthPage mode="login" onNavigate={navigate} />}
        {page === "tool" && <ToolPage />}
      </div>
    </div>
  );
}

export default App;
