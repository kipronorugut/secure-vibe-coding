# Secure Vibe Coding

**Free, open-source security skills for AI-assisted developers.**

**Author:** Kiprono Rugut — independent cybersecurity practitioner.  
**Tagline:** Vibe code faster. Ship safer.

A vendor-neutral Agent Skills toolkit for Claude Code, Claude Cowork, Cursor, and OpenAI Codex. Use it to review AI-generated software, prioritize security issues, examine dependencies and SBOMs, spot secrets, assess CI/CD security, harden Supabase/Firebase back ends, and turn security advisories into verified patches. These are **assistive review workflows**, not substitutes for testing, specialist assessment, or a security guarantee.

> **Independent project.** This repository is the personal open-source work of Kiprono Rugut. It is not an official project of, or endorsed by, any employer, client, or other company. Do not contribute confidential or employer-owned materials.

## Seven skills

| Skill | What it helps with | Invocation example |
| --- | --- | --- |
| `vibe-security-check` | Pre-release app security triage | "Use vibe-security-check on my app before deployment" |
| `secure-code-review` | Evidence-led code review | "Review this pull request using secure-code-review" |
| `sbom-dependency-review` | SBOM and dependency review | "Use sbom-dependency-review to inspect this repo" |
| `secrets-hygiene` | Safe credentials and secret handling | "Use secrets-hygiene on configuration files" |
| `devsecops-pipeline-review` | CI/CD and supply-chain controls | "Review our GitHub Actions with devsecops-pipeline-review" |
| `cve-to-pr-remediation` | Convert CVEs and vendor advisories into verified fixes and reviewable PRs | "Use cve-to-pr-remediation to assess this advisory and prepare a patch PR" |
| `supabase-firebase-hardening` | Supabase RLS and Firebase security-rules review | "Check my Supabase RLS policies before launch" |

All skills follow the [Agent Skills specification](https://agentskills.io/specification), use a plain `SKILL.md` and require **no paid API, account, or scanner** for instruction-only analysis. Optional local scanners require their own installation. **CVE-to-PR starts read-only and never patches, opens a PR, deploys or declares remediation complete without the appropriate authorization and evidence.** Findings are not verified unless the agent has supporting evidence.

## Start with an advisory

If your team has received a CVE, GHSA or vendor notice, install only the remediation skill and ask your agent to turn the notice into a verified change plan:

```bash
python3 tools/install.py --agent cursor --project /path/to/your/app --skill cve-to-pr-remediation
```

Example agent prompt:

> Use `cve-to-pr-remediation`. Verify this advisory against primary vendor sources, assess whether our *running* versions are affected, and prepare the smallest supported fix and an evidence-backed PR draft. Begin read-only. Do not change files, fetch dependencies, run commands or open a PR without my approval. Mark deployment verification separately from merge status.

The skill covers application dependencies, language runtimes, container images, trust stores and operational mitigations. It will not invent fixed versions or claim a GitHub change proves production remediation. See [example workflow](docs/cve-to-pr-example.md).

### Patching right now? (October 2026)

Teams have been told to patch **PHP2Shell** (CVE-2026-109618/109619) and **Node2Shell** (CVE-2026-111497), respond to the **compromised LiteLLM 1.107.0** release, and update trust stores after the **eMudhra intermediate CA key compromise**. The advisory says *what* to upgrade; it rarely says *where* that version is pinned in your code. `cve-to-pr-remediation` ships dated summaries of these advisories and an optional read-only inventory script that finds runtime pins in Dockerfiles, compose files, version files, CI and lockfiles, LiteLLM 1.107.0 pins and images, LiteLLM host indicators, and disabled TLS verification.

> Use `cve-to-pr-remediation` for PHP2Shell, Node2Shell, the LiteLLM 1.107.0 compromise and the eMudhra CA compromise. Begin read-only: run the inventory, show me every place the runtime, package and CA trust are pinned, and draft the smallest fix. List what must be rebuilt, restarted, rotated and verified after deploy.

If the LiteLLM check finds the compromised version or host indicators, **treat it as an incident, not an upgrade**: do not run Python or pip on that host until it is cleaned up, and rotate every credential it could reach. The bundled summaries are dated — always confirm fixed versions against the vendor advisory.

## Quick install: project-level

Clone or download this repository, open a terminal in it, and run:

```bash
# Python 3.10+; replace /path/to/your/app with the developer's own project
python3 tools/install.py --agent cursor --project /path/to/your/app
python3 tools/install.py --agent claude --project /path/to/your/app
python3 tools/install.py --agent codex --project /path/to/your/app
```

**Do not run all three unless using all three agents.** The installer copies the skill directories into the chosen project's conventional directory without overwriting existing skills. To upgrade a previous install to this version, add `--update` (it only replaces folders that already contain the same skill).

| Agent | Project install | Personal install |
| --- | --- | --- |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` |

For all-project installation:

```bash
python3 tools/install.py --agent codex --scope user
```

To install one skill:

```bash
python3 tools/install.py --agent cursor --project /path/to/your/app --skill vibe-security-check
```

To inspect the installer before running it, open `tools/install.py`. It uses only Python's standard library; it does not download dependencies or execute code from the target project. By default it refuses to overwrite installed skills (unless `--update` is given) and refuses symbolic-link destinations. The installer changes **files** in the target project or user skill directory; it does not run security scans.

## Claude Cowork / Claude.ai

Open **Customize > Skills > + > Create skill > Upload a skill** in Claude. Upload one of the **individual** ZIP archives from a release, for example `vibe-security-check.zip`. Do not upload the full repository ZIP as though it were a single skill. Enable the imported skill. Cowork runs skills in its own environment and may lack access to your local source or terminal; upload/present the files to review and verify tool availability. ZIPs can be built locally with:

```bash
python3 tools/package_cowork.py
```

## Manual install

Copy any `skills/<skill-name>/` folder into one of the project directories above. The agent discovers its `SKILL.md`. Reopen or refresh the agent if necessary.

## Safe use

- Review unfamiliar third-party skills before installing them. Instructions can request powerful actions.
- Work only in repositories and systems you own or are authorized to review.
- Start with read-only analysis. **Ask permission** before changing files, installing packages, accessing the network, or uploading source/artifacts.
- Never paste raw credentials into a chat, log, report, pull request, or external service.
- Cite exact file locations and state uncertainty. Do not manufacture scan results, CVEs, risk scores, or assurance claims.
- SBOM generation documents observed components, not a guarantee of full dependency coverage.
- If an optional scanner is missing, describe how to install it; do not claim its checks ran.
- `skills/cve-to-pr-remediation/scripts/inventory.sh` is read-only: it reads files and lists a few well-known paths, makes no network calls and changes nothing. Read it before running it.

## Validate and package

```bash
python3 tools/validate_skills.py
python3 -m unittest discover -s tests -v
python3 tools/package_cowork.py
```

## References

- [Agent Skills standard](https://agentskills.io/specification)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Cursor Agent Skills](https://cursor.com/docs/skills)
- [ChatGPT and Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude custom skill upload](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
- [Supabase Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Firebase Security Rules](https://firebase.google.com/docs/rules)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [NIST SSDF](https://csrc.nist.gov/Projects/ssdf)
- [CycloneDX](https://cyclonedx.org/) and [SPDX](https://spdx.dev/)

## License & contributing

MIT licensed. Issues, documentation fixes, test cases, and evidence-led improvements welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).