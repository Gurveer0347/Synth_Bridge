import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, describe, expect, it } from "vitest";

import { ToolPage } from "./ToolPage";

function renderTool() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  act(() => {
    root.render(<ToolPage />);
  });
  return { host, root };
}

describe("ToolPage", () => {
  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("loads demo docs and enables the run button", () => {
    const { host, root } = renderTool();

    const runButton = Array.from(host.querySelectorAll("button")).find((button) =>
      button.textContent.includes("Run ALI"),
    );
    const loadButton = Array.from(host.querySelectorAll("button")).find((button) =>
      button.textContent.includes("Load Demo Docs"),
    );

    expect(runButton.disabled).toBe(true);

    act(() => {
      loadButton.click();
    });

    expect(host.textContent).toContain("HubSpot_API_Docs.md");
    expect(host.textContent).toContain("Discord_Webhook_Docs.md");
    expect(runButton.disabled).toBe(false);

    act(() => {
      root.unmount();
    });
  });
});
