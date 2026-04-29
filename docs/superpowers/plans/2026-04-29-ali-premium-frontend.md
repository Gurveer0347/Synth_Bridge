# ALI Premium Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the premium ALI frontend and connect it safely to the existing Flask sandbox.

**Architecture:** A new Vite/React app lives in `frontend/`. Flask keeps the existing `/run` and `/health` behavior, with additive CORS and helper fields for the UI. The frontend animates the PDF's five-stage pipeline while awaiting the real final backend response.

**Tech Stack:** React, Vite, GSAP, Three.js, Prism, Vitest, Flask, Python unittest.

---

### Task 1: Backend Frontend Contract

**Files:**
- Create: `tests/test_frontend_contract.py`
- Modify: `ali_sandbox/api.py`

- [ ] Write failing tests for CORS headers and `attempts_count`.
- [ ] Run `python -m unittest tests.test_frontend_contract -v` and confirm failure.
- [ ] Add an `after_request` CORS hook and normalize `/run` responses with `attempts_count`.
- [ ] Run `python -m unittest tests.test_frontend_contract tests.test_sandbox -v` and confirm success.

### Task 2: React Project and Frontend Helper Tests

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/src/api/aliClient.js`
- Create: `frontend/src/api/aliClient.test.js`
- Create: `frontend/src/data/pipeline.js`

- [ ] Scaffold Vite/React in `frontend/`.
- [ ] Add Vitest.
- [ ] Write failing tests for `normalizeRunResponse`, `buildFallbackResponse`, and `PIPELINE_STAGES`.
- [ ] Run `npm test -- --run` and confirm failure.
- [ ] Implement the helper modules.
- [ ] Run frontend tests and confirm success.

### Task 3: Premium UI Components

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/main.jsx`
- Create: `frontend/src/components/NetworkCanvas.jsx`
- Create: `frontend/src/components/LandingPage.jsx`
- Create: `frontend/src/components/AuthPage.jsx`
- Create: `frontend/src/components/ToolPage.jsx`
- Create: `frontend/src/components/UploadZone.jsx`
- Create: `frontend/src/components/PipelineTimeline.jsx`
- Create: `frontend/src/components/CodeWindow.jsx`
- Create: `frontend/src/components/ResultCard.jsx`
- Modify: `frontend/src/styles.css`

- [ ] Build reusable components from the design spec.
- [ ] Add GSAP entrance, scroll, and page transition animations.
- [ ] Add a lightweight Three.js morphing network canvas.
- [ ] Add responsive CSS with the PDF palette and fonts.
- [ ] Keep button labels, section copy, and pipeline stage copy aligned with the PDFs.

### Task 4: Integration and Verification

**Files:**
- Modify: `README.md`

- [ ] Add frontend run instructions.
- [ ] Run backend tests.
- [ ] Run frontend tests.
- [ ] Run `npm run build`.
- [ ] Start Flask and Vite dev servers.
- [ ] Inspect the site in the in-app browser and check landing, auth transition, tool run, code reveal, and result state.
