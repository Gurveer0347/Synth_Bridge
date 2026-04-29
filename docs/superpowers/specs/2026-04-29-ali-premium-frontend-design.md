# ALI Premium Frontend Design

## Goal

Build a premium, luxury-minimalist ALI website that matches `ALI_Project_Summary.pdf` and `Savneet_Frontend_Roadmap_V2.pdf`, while staying synced with Gurveer's existing Flask sandbox backend.

## Product Experience

The site presents ALI as an autonomous integration product, not a generic hackathon page. Judges should understand the story in one flow: two API docs go in, ALI maps fields, generated Python appears, the sandbox runs, and the result is delivered.

The required surfaces are:

- Landing page with the exact roadmap hero copy: "Connect Any Two Tools. No Code. No Setup. No Waiting."
- Sign up page with a premium demo auth card and animated transition into the tool.
- Log in page with the same system and a simpler form.
- ALI tool interface with document upload zones, request text, staged pipeline animation, generated code display, and result card.

## Visual System

Use the PDF palette as the base:

- `#060D1A` page background
- `#2563EB` accent blue
- `#0D9488` success teal
- `#F59E0B` running amber
- `#EF4444` error red
- `#94A3B8` muted text

Use Syne for display headings, DM Sans for body text, and JetBrains Mono for generated code. The interface should feel dark, precise, and expensive, with restrained gradients and real spacing. Avoid marketing clutter.

## Architecture

Create a new Vite/React frontend under `frontend/` so the existing Python package remains isolated. Use React state for page transitions instead of introducing a router. Use GSAP for scroll and page motion, Three.js for the morphing network canvas, and Prism for Python code highlighting.

Keep backend changes additive:

- Preserve existing `/run` request and response behavior.
- Preserve `/health`.
- Add CORS headers for the Vite app.
- Add frontend-friendly summary fields such as `attempts_count` without removing the current `attempts` list.

The current Flask `/run` response is final, not streamed. The frontend will animate the five roadmap stages while the request is in flight, then reconcile with the real final response.

## Core Components

- `Navigation`: fixed frosted nav with ALI brand and login/signup controls.
- `Hero`: exact PDF copy with morphing network background and GSAP word reveals.
- `LandingSections`: value cards, team strips, demo preview, and CTA.
- `AuthPage`: reusable signup/login view with glowing card and transition.
- `ToolPage`: orchestrates uploads, request prompt, pipeline run, code reveal, and result reset.
- `UploadZone`: drag-and-drop document selector with ready states.
- `PipelineTimeline`: five ALI stages from the roadmap with running/success/error states.
- `CodeWindow`: typewriter Python reveal and syntax highlighting.
- `ResultCard`: success, error, and neutral result states.

## Data Flow

The tool page collects two documentation files and an instruction. Because the current backend only accepts JSON demo parameters, the first integration will call `/run` with JSON while preserving the uploaded filenames in the UI. The request defaults to `safe_demo` for reliable judging and can be switched internally to `discord_live` or `full_live` later.

The UI helper normalizes backend data into:

- `success`
- `generatedCode`
- `finalCode`
- `output`
- `error`
- `attemptsCount`
- `stage`

## Error Handling

If Flask is not reachable, the frontend displays a polished local demo result instead of a broken page. If Flask returns `success: false`, the result card shows the backend's plain-English error and leaves the generated code visible for inspection. The upload button remains disabled until both upload zones have files.

## Testing

Backend tests verify that CORS is present and the existing `/run` contract remains backward-compatible while exposing `attempts_count`. Frontend unit tests verify response normalization, stage sequencing, and fallback behavior. A production build plus in-app browser inspection verifies the final UI.

## Constraints

The project folder is not a git repository, so design and plan files cannot be committed here. The implementation should avoid destructive changes and keep Gurveer's sandbox tests passing.
