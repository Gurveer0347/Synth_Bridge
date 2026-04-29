import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

function renderApp() {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  act(() => {
    root.render(<App />);
  });
  return { host, root };
}

describe("App", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    document.body.innerHTML = "";
  });

  it("renders the ALI product hero and transitions into the tool page", () => {
    const { host, root } = renderApp();

    expect(host.textContent).toContain("Connect Any Two Tools.");
    expect(host.textContent).toContain("No Code. No Setup. No Waiting.");
    expect(host.textContent).toContain("What ALI Does For You");

    const signupButton = Array.from(host.querySelectorAll("button")).find((button) =>
      button.textContent.includes("Sign Up"),
    );
    act(() => {
      signupButton.click();
    });

    expect(host.textContent).toContain("Create your account");

    act(() => {
      host.querySelector("form").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
      vi.advanceTimersByTime(900);
    });

    expect(host.textContent).toContain("Tool A");
    expect(host.textContent).toContain("Run ALI");

    act(() => {
      root.unmount();
    });
  });
});
