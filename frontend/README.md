# Monopoly Bench Frontend

Render-only React UI for the Monopoly LLM benchmark.

## Responsibilities
- Renders the board, tokens, ownership, mortgages, and an event feed + inspector from server-provided snapshots/events.
- Connects to the backend WebSocket at `/ws` and polls `/run/status` for run metadata.
- Must not implement Monopoly rules or infer legality; engine is authoritative.

## Dev
From repo root:

```bash
cd frontend
npm ci
npm run dev
```

## Build
```bash
cd frontend
npm run build
```

## Package manager
Use Node.js 22.12+ and npm. Commit `package-lock.json` when dependencies change; use `npm ci` to install the locked dependencies and `npm install` when updating them.
