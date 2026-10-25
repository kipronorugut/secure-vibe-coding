# Research methodology and assurance boundaries

This project publishes **practical, reproducible security workflows** for coding agents. It is an independent open-source contribution, not a certification authority or a substitute for a security assessment.

## Evidence hierarchy

| Evidence | How it is used |
| --- | --- |
| **Primary advisory** | Verify product identity, affected ranges, supported fixes, mitigation advice and last-updated date. Prefer vendor security bulletins and release notes. |
| **Repository artefact** | Locate manifests, lockfiles, source code, container definitions, CI workflows and configuration. Cite paths and lines. |
| **Resolved or built artefact** | Confirm installed dependencies, base images, runtimes, image digests and generated SBOMs where available. |
| **Runtime and deployed state** | Obtain evidence from the running service, image, host or deployed rules. A pull request or green CI run does **not** establish closure. |
| **Security operations evidence** | Correlate detection and incident information, residual exposure, compensating controls and remediation ownership. |

## Review workflow

1. **Scope.** Identify authorized repositories, services, environments and affected components.
2. **Verify.** Confirm official advisory identity and version ranges. Never treat an article headline as proof of exposure.
3. **Locate.** Trace declared, resolved, built and running components. Record unknowns explicitly.
4. **Plan.** Recommend minimal supported changes, regression tests, deployment actions and rollback.
5. **Approve.** Keep default operation read-only. Changes, network access and deployments require explicit authorization.
6. **Validate.** Distinguish tool checks and agent reasoning from the evidence that a production fix was deployed.
7. **Handover.** Document remaining risks, owners, detection considerations and evidence links.

## Findings and confidence

A credible finding includes a file path or configuration, relevant source evidence, preconditions, impact, fix and confidence. Prefer **"not verified"** over unfounded assurances.

Do not fabricate scanner runs, CVEs, vulnerability scores, exploitability or compliance outcomes. Scanner findings require triage; scanner absence is not evidence of safety.

## Quality evaluation

The repository includes [test and evaluation guidance](evaluation.md) and a [synthetic CVE-to-PR demonstration](cve-to-pr-example.md). Automated CI checks metadata, reference integrity, helpers and fixture-based test cases. It does **not** prove that an LLM consistently finds every vulnerability.

Useful evaluation measures include supported findings, false positives, seeded-defect detection, unauthorized file changes and exposure of sensitive data. Measure separately for each agent and report the fixture and version used.

## Maintaining advisory research

The [dated advisory notes](../skills/cve-to-pr-remediation/references/advisories.md) cover PHP2Shell, Node2Shell, LiteLLM 1.107.0 and eMudhra as of **25 October 2026**. These notes are reference material, not a live feed. Check the vendor's latest bulletin before applying a version or mitigation.

Updates should provide primary-source links, the date checked, affected and fixed versions where verified, a synthetic fixture and limitations. Keep the optional [inventory script](../skills/cve-to-pr-remediation/scripts/inventory.sh) aligned with the advisory notes.

## Ethics and independence

- Never include unpublished client incidents, employer information, private code, credentials or personal data.
- Test only owned or explicitly authorized systems.
- Report security weaknesses through [private disclosure guidance](../SECURITY.md).
- Neither the author nor a contributor speaks for an employer, client or software vendor.
- Regulatory compliance requires environment-specific control mapping and independent evidence. These skills **support** review and documentation; they do not confer compliance.

Use [CONTRIBUTING.md](../CONTRIBUTING.md) to propose an evidence-led change.
