# Carina AI Command Center

An interactive front-end demo for exploring how AI agents, projects, approvals, and operational signals could be supervised from one focused workspace.

## Demo versus local live

The hosted interface is an interactive demo. Its agents, projects, events, activity points, voice state, OpenClaw state, and phone-bridge state are simulated in the browser. It does not capture microphone audio, connect to a phone, run automations, call agent backends, expose a wallet, or display real financial values.

The interface labels this clearly as `HOSTED DEMO — ACTIVE` and `LOCAL LIVE — NOT CONNECTED`. A future local-live mode will require an authenticated orchestration backend and explicit local credentials; that backend is not part of this repository yet.

## Highlights

- Voice-style wake and stop controls that preview listening animations without capturing audio.
- A multi-agent routing view for Maya, Karina, Hermes, and Codex.
- Project progress, activity, and system-health surfaces.
- A visual systems engine with animated event flow.
- Sample activity scores and points for exploring information hierarchy without monetary claims.
- Responsive layouts and reduced-motion support.

## Current boundary

Carina is a polished front-end prototype. The next integration step is to connect selected surfaces to an authenticated local orchestration backend without weakening the approval boundaries or changing the hosted demo into an implied live system.

## Stack

- React 19 and TypeScript
- Next.js-compatible routing through vinext
- Vite and the Cloudflare development toolchain
- Tailwind CSS
- OpenAI Sites project configuration

## Run locally

Node.js 22.13 or newer is required.

```bash
npm install
npm run dev
```

## Verify

```bash
npm run lint
npm test
```

`npm test` performs a production build and checks the rendered loading surface.

## Project structure

- `app/` contains the command-center interface and global styling.
- `tests/` verifies the generated page output.
- `public/` contains static assets.
- `.openai/hosting.json` preserves the OpenAI Sites project binding.
- `vite.config.ts` configures local and hosted runtime behavior.

## Principles

The interface is designed around visible system state, deliberate approval points, accessible motion, and honest separation between simulated product concepts and working integrations.
