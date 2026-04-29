# ALI Sandbox + Self-Healing Demo

Gurveer Singh's module for the ALI hackathon project. It runs AI-generated Python bridge code in a subprocess, captures failures, classifies errors, retries with repaired code, and optionally sends the final alert to Discord.

## Quick Demo

```powershell
python demo.py --failure bad_endpoint --mode safe_demo
python demo.py --failure wrong_field --mode safe_demo
```

For a real Discord message, set a webhook and use `discord_live`:

```powershell
$env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
python demo.py --failure missing_auth --mode discord_live
```

If `DISCORD_WEBHOOK_URL` is missing, `discord_live` prints the payload and exits successfully instead of crashing.

For a no-demo live run, set both HubSpot and Discord credentials:

```powershell
$env:HUBSPOT_PRIVATE_APP_TOKEN="pat-na1-..."
$env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
python demo.py --mode full_live --timeout 30
```

`full_live` does not use simulated lead data. It searches HubSpot contacts through the live CRM Search API, takes the newest contact, and posts that contact to Discord. If either credential is missing, it fails clearly instead of falling back to demo data.

## Flask API

Install Flask:

```powershell
python -m pip install -r requirements.txt
```

Run the API:

```powershell
python -m ali_sandbox.api
```

Call the endpoint:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/run -ContentType "application/json" -Body '{"demo_failure":"bad_endpoint","mode":"safe_demo"}'
```

Fully live API call:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/run -ContentType "application/json" -Body '{"mode":"full_live","timeout_seconds":30}'
```

## Premium React Frontend

Savneet's frontend is implemented as a Vite/React app in `frontend/`. It keeps the four roadmap pages: landing, signup, login, and the ALI tool interface.

Run the backend:

```powershell
python -m ali_sandbox.api
```

Run the frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open the URL Vite prints, usually `http://localhost:5173/`. The frontend calls the existing Flask `/run` endpoint. If Flask is unavailable during visual testing, the UI falls back to a local demo response instead of breaking.

Frontend checks:

```powershell
cd frontend
npm test -- --run
npm run lint
npm run build
```

## Judge Script

The honest framing is:

> The subprocess execution, timeout, stderr capture, error classification, retry routing, and repaired second attempt are real. `safe_demo` simulates HubSpot for reliability. `discord_live` simulates HubSpot but can post to real Discord. `full_live` uses real HubSpot and real Discord credentials with no simulated lead data.

Subprocess is safer than `exec()` because generated code runs in a separate child process and can be killed on timeout. This demo also blocks a small set of obviously destructive operations before execution, but it is still a hackathon sandbox rather than a production-grade container jail.
