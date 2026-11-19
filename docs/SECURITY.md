# Security

> Prototype / proof-of-concept demo by Stuff Studios. These protections are tested in CI on every push. It's still a training tool, not a hardened production service, so run it on an event network rather than the open internet when you can.

## What is locked down

### Answers and spoilers
| Protection | How |
|---|---|
| No real flags in the repo | Flags live only in `config/flags.env` and `ctfd/build/`, both git ignored. A test fails the build if either is ever committed |
| Spoilers encrypted | The walkthrough, solver, judge guide, slate card and tested flag set are stored only in `staff/ghost-vector-staff.7z` (AES-256, file names encrypted too). CI checks that no plain-text copy is tracked |
| Spoilers scrubbed from history | The old plain-text walkthrough, solver and tested marker codes were removed from all past commits |
| Answers never stored in plain text by the app | The terminal compares SHA256 hashes in constant time. The master coordinate exists only as a hash |
| No answers in player files | Tests confirm that no flag or code appears as plain text in any downloadable file or page |

### The recovery terminal
| Protection | Setting |
|---|---|
| Content Security Policy | `default-src 'none'`, scripts and styles from the site only, no inline script, no framing |
| Other headers | `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy: no-referrer`, `Permissions-Policy`, `Cross-Origin-Opener-Policy` |
| Rate limiting | 12 attempts per minute per client on each check endpoint (`RATE_LIMIT`, `RATE_WINDOW`), plus a 0.4 s delay per check |
| Input limits | JSON only, 2 KB body cap, 200 characters per field, type checked |
| Downloads | Served only from a fixed allow-list. Path tricks and the hash file return 404 |
| Session cookie | `HttpOnly`, `SameSite=Strict`, and `Secure` when `COOKIE_SECURE=1` (use it behind HTTPS) |
| Weak secret key | If `SECRET_KEY` is missing, too short or still the example value, the app uses a random key and logs a warning |
| Error pages | Short JSON messages, never stack traces |

### The container
| Protection | Setting |
|---|---|
| Network binding | Compose publishes the terminal on host loopback by default. Event access requires an explicit private `HOST_BIND_IP` |
| Non-root | Runs as the `ctf` user |
| Read-only filesystem | `read_only: true`. Only the data volume and a small `/tmp` can be written |
| No Linux capabilities | `cap_drop: ALL` and `no-new-privileges` |
| Resource caps | 256 MB memory, 128 processes, 1 CPU |
| Request limits | gunicorn caps the request line and header count |
| Pinned dependencies | Exact versions in `app/requirements.txt`, audited with pip-audit |
| Patched and trimmed image | Debian security updates applied at build time, and build-only tools (setuptools, wheel) removed |

## Automated checks (CI)

- **bandit:** static security analysis of the Python code.
- **pip-audit:** known vulnerabilities in the dependencies.
- **Trivy:** scans the built Docker image and fails on fixable HIGH or CRITICAL issues. One entry is ignored in `.trivyignore` with a written reason: a setuptools CVE reported from the base image's build history, while CI separately proves setuptools isn't in the image.
- **Spoiler guard:** fails if a plain-text walkthrough, solver, staff folder or `config/flags.env` is ever tracked.
- **Hardening check:** confirms the running container is read-only, has dropped all capabilities, isn't running as root, and sends the security headers.
- **Unit tests:** cover the CSP, headers, rate limits, size caps, input validation, cookie flags and path traversal.

## Running it safely

- Put the terminal behind HTTPS (for example Caddy or nginx) when it's reachable beyond a local network. Then set `COOKIE_SECURE=1` and `TRUST_PROXY=1`.
- Use a long random `SECRET_KEY` and a strong staff pack password (at least 12 characters, ideally 20 or more).
- Don't leave `staff-unlocked/` or `ctfd/build/` on shared machines.
- Make new flags and a new seed for every event, even if a previous event's answers leaked.

## Reporting a problem

Open a GitHub issue **without** any flags or exploit details, or contact the Stuff Studios maintainers directly.
