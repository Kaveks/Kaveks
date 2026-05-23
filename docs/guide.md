# Project Guide

## Overview

This is the **GitHub profile repository** for [@kaveks](https://github.com/kaveks) (Patrick Mbugua), a Fullstack Developer based in Kenya. Because the repository name matches the GitHub username, its `README.md` automatically renders on the public GitHub profile page.

The repo has one active script that generates a multi-year contribution chart and a GitHub Actions workflow that keeps it updated automatically.

---

## Repository structure

```
kaveks/
├── README.md                          # GitHub profile page
├── generate_contributions.py          # Chart generation script
├── contributions.png                  # Generated chart (committed by CI bot)
├── Makefile                           # install and generate targets
├── requirements.txt                   # Pinned Python dependencies
├── .github/
│   └── workflows/
│       └── contributions.yml          # Automation workflow
├── docs/
│   └── guide.md                       # This file
└── .venv/                             # Local Python venv (gitignored)
```

---

## Local setup

### Prerequisites

- Python 3.11+
- Git

### Create and activate the virtual environment

Ubuntu's system Python is PEP 668-protected, so a venv is required:

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

`make install` runs `pip install -r requirements.txt`, which installs all pinned dependencies. The `.venv/` directory is gitignored — never commit it.

---

## Regenerating the contribution chart

### With a GitHub token (recommended — full history)

```bash
source .venv/bin/activate
make generate GH_TOKEN=<github_token>
```

Or set the variable in the environment:

```bash
export GH_TOKEN=<github_token>
make generate
```

The token is a classic Personal Access Token from [github.com/settings/tokens](https://github.com/settings/tokens). **No scopes are required** for public contribution data — a token with zero scopes is enough.

The script uses the GitHub GraphQL API to fetch contribution data from the year the account was created up to today, then renders a matplotlib chart with:

- A bar chart showing total contributions per year (left panel)
- A heatmap showing monthly contribution density per year (right panel)

Output is saved as `contributions.png` in the repo root.

### Without a token (limited fallback)

```bash
source .venv/bin/activate
make generate
```

Falls back to the public Events REST API. Only captures the last ~90 days. Useful for testing the chart rendering locally, not for the real chart.

### Script internals

| Function                             | Purpose                                     |
| ------------------------------------ | ------------------------------------------- |
| `fetch_yearly_contributions_graphql` | Fetches full history via GraphQL API        |
| `fetch_recent_events_rest`           | Fallback via REST public events             |
| `_graphql_request`                   | Low-level GraphQL POST helper               |
| `plot_contributions`                 | Renders the matplotlib figure and saves PNG |
| `main`                               | Entry point — dispatches to GraphQL or REST |

The chart uses a Tokyo Night dark color scheme (`#1a1b27` background, `#7aa2f7` accent, `viridis` heatmap colormap).

---

## GitHub Actions workflow

**File:** `.github/workflows/contributions.yml`

**Triggers:**

- Every push or merge to `main`
- Every day at 00:00 UTC (midnight)
- Manually via the Actions tab

**What it does:**

1. Checks out the repo
2. Sets up Python 3.11
3. Runs `make install` to install pinned dependencies from `requirements.txt`
4. Runs `make generate` with `GH_TOKEN` and `GITHUB_USERNAME` injected as environment variables
5. Commits `contributions.png` back to `main` if the chart changed

The workflow is idempotent — if the chart is unchanged since the last run, no commit is made.

### Required permissions

The workflow needs `permissions: contents: write` (already present in the file). If it still fails to push with a 403:

1. Go to the repo on GitHub
2. Settings → Actions → General → Workflow permissions
3. Select **Read and write permissions** → Save

### Trigger manually

```bash
gh run list --workflow=contributions.yml   # check recent runs
```

Or use the Actions tab → "Update contribution graph" → **Run workflow**.

---

## README design principles

The README renders on the GitHub profile page. These rules keep it clean and consistent:

- **Theme:** Tokyo Night across all badge widgets and stat cards — `theme=tokyonight`, `hide_border=true`
- **Badge grouping:** Languages / Frontend / Backend / DevOps & cloud / Tools — never one flat list
- **Only badge tools actually used** — see the tech stack below; don't add logos just because they look nice
- **Section order:** intro → about → connect → tech stack → trophies → stats → contribution history → quote
- **Primary follow action:** LinkedIn (`linkedin.com/in/254pmk`), not Twitter

### Stat services to use

| Widget                | Service URL                                                                     |
| --------------------- | ------------------------------------------------------------------------------- |
| Stats & top languages | `github-readme-stats-eight-theta.vercel.app` (community fork, not rate-limited) |
| Streak stats          | `streak-stats.demolab.com`                                                      |
| Trophies              | `github-profile-trophy.vercel.app`                                              |

Do **not** use `github-readme-stats.vercel.app` (canonical service — heavy rate limits, produces broken camo URLs) or `github-readme-streak-stats.herokuapp.com` (Heroku endpoint is dead).

---

## Tech stack reference

Only these tools should appear in the README badge section:

| Category           | Tools                                                                  |
| ------------------ | ---------------------------------------------------------------------- |
| Languages          | TypeScript, JavaScript, Python, Kotlin, Bash                           |
| Frontend           | React, Next.js, Tailwind CSS, shadcn/ui, Redux                         |
| Backend            | Django, FastAPI, Node.js, PostgreSQL, MongoDB, Redis, RabbitMQ, Celery |
| DevOps / Cloud     | Docker, Kubernetes, AWS, GCP, Jenkins, Linux, Nginx, Grafana           |
| Tools              | Git, Figma, Postman                                                    |
| Currently learning | Kotlin Multiplatform, Mifos Mobile, Fineract, Mifos Wallet             |

---

## Commit conventions

- Short imperative messages: `Update tech stack`, `Fix LinkedIn badge`, `Add FastAPI to backend`
- The Actions bot uses `chore: update contribution graph` — match that prefix for automation-related commits
- Never commit `.venv/`, `__pycache__/`, token files, or preview PNGs

---

## Quick reference

| Task                           | Command                                                  |
| ------------------------------ | -------------------------------------------------------- |
| Activate venv                  | `source .venv/bin/activate`                              |
| Install dependencies           | `make install`                                           |
| Regenerate chart (with token)  | `make generate GH_TOKEN=<token>`                         |
| Regenerate chart (no token)    | `make generate`                                          |
| Install + generate in one step | `make all GH_TOKEN=<token>`                              |
| Preview README locally         | `pip install grip && grip README.md`                     |
| Trigger workflow manually      | Actions tab → "Update contribution graph" → Run workflow |
| Check workflow logs            | `gh run list --workflow=contributions.yml`               |

---

## Things to avoid

- Adding badges for tools the developer does not use
- Using the dead Heroku streak endpoint or the rate-limited canonical stats service
- Replacing LinkedIn with Twitter as the primary follow action
- Hardcoding a GitHub token anywhere in tracked files — pass it as an argument only
- Committing `contributions.png` from a local run ahead of a CI bot run (causes merge conflicts)
- Restructuring the README into a single flat badge dump — the grouped layout is intentional
