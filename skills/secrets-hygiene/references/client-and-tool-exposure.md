# Where AI-built apps leak secrets that scanners miss

Pattern scanners find hardcoded tokens. These leaks are often "correctly" stored in environment variables or config files and still exposed.

## 1. Public environment-variable prefixes

Variables with these prefixes are bundled into frontend code and visible to every visitor:

| Framework | Public prefix |
|---|---|
| Next.js | `NEXT_PUBLIC_` |
| Vite (React, Vue, Svelte) | `VITE_` |
| Create React App | `REACT_APP_` |
| Expo / React Native | `EXPO_PUBLIC_` |
| SvelteKit, Astro | `PUBLIC_` |
| Nuxt | `NUXT_PUBLIC_` |

**Publishable — acceptable in frontend:** Stripe `pk_` keys, Supabase anon/publishable key, Firebase web config, analytics site IDs, map keys restricted by referrer.

**Server-only — never behind a public prefix:** Supabase `service_role`/secret key; Stripe `sk_`/`rk_`; OpenAI, Anthropic, Gemini and other LLM keys; database URLs; JWT/session signing secrets; payment-provider secrets (e.g. M-Pesa Daraja consumer secret and passkey, Paystack/Flutterwave secret keys); AWS/GCP/Azure credentials; SMTP/SMS provider credentials; webhook signing secrets.

Also check frontend code for direct calls to paid AI APIs (for example `api.openai.com`, `api.anthropic.com`): these require a key in the browser and must move behind a server route.

## 2. AI coding-tool and MCP configuration

AI coding tools store tokens for model providers and MCP servers in config files. Treat these as secrets:

- Project-level files that can be committed by accident, such as `.cursor/mcp.json`, `.mcp.json`, `.vscode/mcp.json` and agent config folders. Use environment-variable references instead of literal tokens, and keep files with real values out of git.
- User-level files on developer machines, such as `~/.claude.json`, `~/.codex/config.toml`, `~/.cursor/` settings and provider CLI credential files. These are not in the repository, but they are on the machine — and recent supply-chain malware (for example the compromised LiteLLM 1.107.0 release in October 2026) specifically collected AI-coding-tool configuration along with cloud and SSH credentials.

If a developer machine or CI runner may have been compromised, include AI-provider keys and MCP server tokens in the rotation list.

## 3. Other common spots

- `.env` files committed before `.gitignore` was added (still in history).
- Example and test fixtures containing real values ("I'll replace it later").
- CI logs that echo environment variables or print config.
- Docker image layers (`COPY .env`, `ARG`/`ENV` with secrets) — secrets persist in image history even if deleted in a later layer.
- Mobile app bundles: anything in the app binary is public.
- Source maps published to production that include server-side code paths.

## 4. Correct order after exposure

1. Revoke/rotate the credential at the provider.
2. Review provider usage, billing and access logs for the exposure window.
3. Move the new value to a secret store or hosting-platform secret settings.
4. Remove from code; add ignore rules; commit only `.env.example` with placeholders.
5. Only then consider history rewriting (`git filter-repo`), noting it does not invalidate the old credential and affects all collaborators.
6. Add pre-commit and CI secret scanning to prevent recurrence.
