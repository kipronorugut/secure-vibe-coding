# Contributing

Thanks for improving **Secure Agent Skills for Developers**. Use the [research proposal](.github/ISSUE_TEMPLATE/research_proposal.yml) template for new skills and the [security skill issue](.github/ISSUE_TEMPLATE/security_skill_issue.yml) template for reproducible defects.

- Use original work and public information. Do not submit client data, nonpublic findings, access credentials, or employer-owned content.
- Preserve Agent Skills frontmatter and portable instructions.
- Keep the default workflow read-only; require consent for edits, external traffic, uploads and installation of tools.
- Attach a synthetic example showing that a proposed change improves review quality. State false-positive risks.
- Run `python3 tools/validate_skills.py` and `python3 -m unittest discover -s tests -v`.
- Avoid unverified compliance claims and avoid using brand trademarks as endorsements.
- Advisory summaries in `skills/cve-to-pr-remediation/references/advisories.md` must cite public sources and carry an "as of" date. Update the dated table in `scripts/inventory.sh` in the same change, with a test fixture.
- Helper scripts must stay read-only, offline and pass `shellcheck -S warning`.

By submitting a contribution, you agree it is offered under the repository's MIT license.