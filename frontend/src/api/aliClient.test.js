import { describe, expect, it } from "vitest";

import { buildFallbackResponse, normalizeRunResponse } from "./aliClient";

describe("normalizeRunResponse", () => {
  it("maps Gurveer's Flask response into frontend-friendly fields", () => {
    const normalized = normalizeRunResponse({
      success: true,
      generated_code: "print('first attempt')",
      final_code: "print('SUCCESS')",
      output: "SUCCESS",
      error: null,
      attempts: [{ attempt: 1 }, { attempt: 2 }],
      stage: "done",
    });

    expect(normalized).toEqual({
      success: true,
      generatedCode: "print('first attempt')",
      finalCode: "print('SUCCESS')",
      output: "SUCCESS",
      error: null,
      attempts: [{ attempt: 1 }, { attempt: 2 }],
      attemptsCount: 2,
      stage: "done",
      fromFallback: false,
    });
  });

  it("uses attempts_count when a response omits the attempts list", () => {
    const normalized = normalizeRunResponse({
      success: false,
      generated_code: "raise RuntimeError('bad auth')",
      output: "",
      error: "Authentication failed.",
      attempts_count: 3,
      stage: "failed",
    });

    expect(normalized.attempts).toEqual([]);
    expect(normalized.attemptsCount).toBe(3);
    expect(normalized.finalCode).toBe("raise RuntimeError('bad auth')");
  });
});

describe("buildFallbackResponse", () => {
  it("returns a polished local demo result when Flask is unavailable", () => {
    const fallback = buildFallbackResponse(new Error("Failed to fetch"));

    expect(fallback.success).toBe(true);
    expect(fallback.fromFallback).toBe(true);
    expect(fallback.finalCode).toContain("Discord alert payload");
    expect(fallback.output).toContain("SUCCESS");
    expect(fallback.error).toContain("local demo");
  });
});
