import { useEffect, useMemo, useState } from "react";
import Prism from "prismjs";
import "prismjs/components/prism-python";
import "prismjs/themes/prism-tomorrow.css";

export function CodeWindow({ code }) {
  const [visibleCode, setVisibleCode] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!code) return undefined;

    let index = 0;
    const interval = window.setInterval(() => {
      index += Math.max(1, Math.floor(code.length / 180));
      setVisibleCode(code.slice(0, index));
      if (index >= code.length) {
        window.clearInterval(interval);
      }
    }, 18);

    return () => window.clearInterval(interval);
  }, [code]);

  const highlighted = useMemo(() => {
    return Prism.highlight(visibleCode || "", Prism.languages.python, "python");
  }, [visibleCode]);

  if (!code) return null;

  return (
    <section className="code-window">
      <div className="code-window__bar">
        <span>AI-Generated Bridge Code</span>
        <button
          className="icon-button"
          type="button"
          onClick={async () => {
            await navigator.clipboard?.writeText(code);
            setCopied(true);
            window.setTimeout(() => setCopied(false), 1200);
          }}
        >
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre aria-label="Generated Python bridge code">
        <code className="language-python" dangerouslySetInnerHTML={{ __html: highlighted }} />
      </pre>
    </section>
  );
}
