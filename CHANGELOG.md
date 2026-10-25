# Changelog

## 0.2.0 — 2026-10-25

### Added
- `cve-to-pr-remediation` (added on main as 0.1.0) extended to 0.2.0:
  - Dated advisory summaries in `references/advisories.md` for PHP2Shell (CVE-2026-109618/109619), Node2Shell (CVE-2026-111497), the LiteLLM 1.107.0 compromised release and the eMudhra intermediate CA key compromise.
  - Optional read-only `scripts/inventory.sh`: runtime pins in Dockerfiles, compose, version files, manifests and CI; Python brotli, certifi and LiteLLM pins; LiteLLM image tags; LiteLLM host indicators; disabled TLS verification and custom CA bundles.
  - Compromised-release incident path, TLS trust-store guidance, and rebuild/restart requirements in the operator runbook.
- `supabase-firebase-hardening` skill with Supabase (RLS, views, SECURITY DEFINER functions, storage, column escalation) and Firebase (Firestore, RTDB, Storage rules, emulator tests) references.
- Reference files for existing skills: AI-generated code defect patterns (`secure-code-review`), client-side and AI-tool/MCP config exposure (`secrets-hygiene`), compromised releases, slopsquatting and install-time code (`sbom-dependency-review`), and a starter CI security workflow (`devsecops-pipeline-review`).
- Installer `--update` option (replaces only folders that already hold the same skill).
- Validator checks that files referenced by a skill exist and that helper scripts declare an interpreter; CI lints helper scripts with shellcheck.
- Tests for `--update`, missing references, and the inventory script on synthetic fixtures.

### Changed
- `vibe-security-check` hands off to `supabase-firebase-hardening` and `cve-to-pr-remediation` where relevant; `sbom-dependency-review` hands confirmed compromised releases to `cve-to-pr-remediation`.
- Skill versions bumped to 0.2.0.

## 0.1.0
- Initial five skills, offline installer, Cowork packaging, validator and tests.
- `cve-to-pr-remediation` skill with verification gates G1–G7 and a synthetic worked example.
