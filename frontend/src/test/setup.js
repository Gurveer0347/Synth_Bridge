import { vi } from "vitest";

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

window.matchMedia =
  window.matchMedia ||
  vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));

window.scrollTo = vi.fn();
window.requestAnimationFrame = window.requestAnimationFrame || ((callback) => window.setTimeout(callback, 16));
window.cancelAnimationFrame = window.cancelAnimationFrame || ((id) => window.clearTimeout(id));
