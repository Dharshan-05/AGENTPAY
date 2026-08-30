# Contributing to Arcanea Templates

Thanks for wanting to contribute. We keep things simple.

## Ways to Contribute

- **Fork and ship.** The best contribution is using the template to build something real. Link back if you publish.
- **File issues.** Bug reports, feature requests, or "this README section confused me" — all welcome.
- **Send PRs.** Small, focused changes land fastest.

## Before You PR

1. **Run the build.** Every template has a working `pnpm run build`. PRs must leave it green.
2. **Keep the MIT / Apache-2.0 license intact.** Don't add GPL or proprietary code.
3. **No required env vars.** If your change needs a secret, make it optional with a graceful fallback.
4. **Match the voice.** READMEs use second person, short sentences, no marketing fluff.
5. **One concern per PR.** A bug fix + a feature in one PR is two PRs.

## Design System Rules

- Background: `#09090b` · Primary: `#00bcd4` · Accent: `#ffd700`
- Glass: `bg-white/[0.03] border border-white/[0.06] backdrop-blur-sm`
- Fonts: Space Grotesk (display), Inter (body), JetBrains Mono (code)
- **NEVER** use Cinzel font
- Framer Motion: `domAnimation` not `domMax`, wrap in `LazyMotion`

## Code Style

- TypeScript strict where possible
- Functional React components, hooks over classes
- One component per file, named exports preferred
- No `any` unless genuinely unavoidable

## Issue Triage

We use GitHub Projects V2 to manage issues across all Arcanea template repos. Your issue will show up on the board within a day.

## Commit Messages

Conventional commits — `feat(scope): description`. Examples:
- `feat(byok): add Groq provider support`
- `fix(motion): LiquidGlass crash on unmount`
- `docs(readme): clarify BYOK flow diagram`

## License

By contributing, you agree that your contributions will be licensed under the same license as the template (MIT for most, Apache 2.0 for arcanea-chat-template).

## Questions?

Open an issue or reach out at https://arcanea.ai.
