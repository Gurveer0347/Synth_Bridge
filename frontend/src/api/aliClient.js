const FALLBACK_CODE = `import json

lead = {
    "first_name": "Aarav",
    "last_name": "Mehta",
    "email": "aarav@example.com",
    "company": "Trae Labs",
}

payload = {
    "content": (
        "New HubSpot lead: "
        f"{lead['first_name']} {lead['last_name']} "
        f"<{lead['email']}> from {lead['company']}"
    )
}

print("Fetched simulated HubSpot lead")
print("Discord alert payload:")
print(json.dumps(payload, indent=2))
print("SUCCESS")`;

export function normalizeRunResponse(payload = {}) {
  const attempts = Array.isArray(payload.attempts) ? payload.attempts : [];
  const generatedCode = payload.generated_code || "";
  const finalCode = payload.final_code || generatedCode;

  return {
    success: Boolean(payload.success),
    generatedCode,
    finalCode,
    output: payload.output || "",
    error: payload.error ?? null,
    attempts,
    attemptsCount: Number.isFinite(payload.attempts_count) ? payload.attempts_count : attempts.length,
    stage: payload.stage || "failed",
    fromFallback: Boolean(payload.fromFallback),
  };
}

export function buildFallbackResponse(error) {
  return {
    success: true,
    generatedCode: FALLBACK_CODE,
    finalCode: FALLBACK_CODE,
    output: "Fetched simulated HubSpot lead\nDiscord alert payload:\nSUCCESS",
    error: `Running local demo because Flask is unavailable: ${error.message}`,
    attempts: [{ attempt: 1, success: true }],
    attemptsCount: 1,
    stage: "done",
    fromFallback: true,
  };
}

export async function runAliBridge({ apiBase = "http://localhost:5000", mode = "safe_demo" } = {}) {
  try {
    const response = await fetch(`${apiBase}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode,
        demo_failure: "wrong_field",
        timeout_seconds: 5,
      }),
    });
    const payload = await response.json();
    return normalizeRunResponse(payload);
  } catch (error) {
    return buildFallbackResponse(error);
  }
}
