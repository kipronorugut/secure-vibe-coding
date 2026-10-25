# Beyond CVEs: compromised releases, hallucinated packages and install-time code

A vulnerability scan answers "does a known-vulnerable version exist here?". It does not answer "did we install something malicious?". AI-assisted development adds two risks: agents add dependencies quickly, and they sometimes suggest packages that don't exist.

## 1. Compromised legitimate releases

A trusted project publishes a malicious version after an attacker obtains publishing credentials or build access. Recent example: **LiteLLM 1.107.0** (21 October 2026) shipped a credential stealer and remote code loader in its PyPI wheels and official Docker images; floating image tags briefly pointed at the infected build. See `cve-to-pr-remediation` → `references/advisories.md` for response steps.

What to check:
- Is any lockfile, requirements file or Dockerfile pinned to a version named in a current compromise advisory?
- Are versions unpinned (`>=`, `^`, `latest`, floating image tags) so a bad release could have been installed automatically?
- Were images pulled by tag rather than by digest during the compromise window?

Controls to recommend, proportionate to the project:
- Commit lockfiles; install with `npm ci`, `pnpm install --frozen-lockfile`, `pip install --require-hashes` or `uv sync --locked`.
- Pin container images by digest (`image@sha256:...`).
- Consider a short **release-age delay** for new versions where the package manager supports it (for example pnpm `minimumReleaseAge`, uv `exclude-newer`, npm `--before`), so freshly published — possibly malicious — versions are not adopted the same day. Confirm option names in the installed tool's help.
- Use a private registry proxy/mirror where available, and purge known-bad versions from caches.

A compromised release is an **incident**: hosts that installed it may already have leaked credentials. Escalate rather than "upgrade and move on".

## 2. Hallucinated and look-alike packages ("slopsquatting")

AI assistants sometimes reference packages that don't exist; attackers register those names. For each **newly added** dependency, verify with consent (registry lookups use the network):

- The package exists on the official registry and is the intended one (exact spelling, expected publisher and source repository).
- Warning signs: very recent first publication, very low downloads, no repository link, a name one character off a popular package, scope impersonation (e.g. fake `@types/` or vendor scopes), a single new maintainer.

Do not install a suspicious package to inspect it. Ask the user to confirm.

## 3. Install-time and startup code

Malicious packages often run code at install or interpreter start rather than when imported:

- **npm:** `preinstall`, `install`, `postinstall` scripts. In `package-lock.json`, packages with install scripts are marked `"hasInstallScript": true`. Consider `--ignore-scripts` for CI installs where the build allows it, and allowlists for packages that genuinely need scripts.
- **Python:** `.pth` files and `sitecustomize.py` in site-packages execute at every interpreter start; `setup.py` executes during source installs. Prefer wheels from trusted sources, and check new `.pth` files after installs.
- **Build tools and CI actions:** treat third-party actions and build plugins as dependencies — pin to full commit SHAs.

## 4. Reporting

Keep these categories separate in the findings table: `known vulnerable` (CVE match with evidence), `known compromised release` (advisory match), `suspicious / unverified package`, and `not verified`. Never present a package as malicious without a cited source.
