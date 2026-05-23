# CLAUDE.md

Project instructions for Claude Code. Read this before doing anything in this repo.

## What this repo is

This is the **GitHub profile repo** for user `kaveks` (Patrick Mbugua). It's the special repo where the name matches the username, so its `README.md` renders on the GitHub profile page at https://github.com/kaveks.

It is NOT a typical application. It contains:

- `README.md` — the profile README that visitors see
- `generate_contributions.py` — Python script that fetches GitHub contribution data via the GraphQL API and renders a multi-year matplotlib chart
- `contributions.png` — the generated chart, referenced by the README
- `.github/workflows/contributions.yml` — GitHub Actions workflow that re-runs the script every Monday at 06:00 UTC and commits the updated PNG back to the repo

## About the developer

- **Name:** Patrick Mbugua
- **Role:** Fullstack developer (not frontend-only — keep this correct everywhere)
- **Location:** Kenya
- **GitHub:** kaveks
- **LinkedIn:** linkedin.com/in/254pmk (this is the primary social — "Follow me" buttons should point here, not Twitter)
- **Twitter:** patokaveks (secondary)
- **Email:** pkaveks2@gmail.com
- **Portfolio:** know-patrick.vercel.app( use links insertion)

## Tech stack the developer actually uses

When updating the README's tech stack section, these are the real tools — don't add things from a generator's full catalog just because they have nice logos.

- **Languages:** TypeScript, JavaScript, Python, Kotlin, Bash
- **Frontend:** React, Next.js, Tailwind CSS, shadcn/ui, Redux
- **Backend:** Django, FastAPI, Node.js, PostgreSQL, MongoDB, Redis, RabbitMQ, Celery
- **DevOps/Cloud:** Docker, Kubernetes, AWS, GCP, Jenkins, Linux, Nginx, Grafana
- **Tools:** Git, Figma, Postman
- **Currently learning:** Kotlin Multiplatform, Mifos Mobile, Fineract, Mifos Wallet

## Local development

### Python environment

Ubuntu's system Python is PEP 668-protected, so always use a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install matplotlib numpy
```

The `.venv/` directory is gitignored — never commit it.

### Regenerating the contribution chart locally

```bash
source .venv/bin/activate
make generate GH_TOKEN=<github_token>
```

The token is a classic personal access token from github.com/settings/tokens. **No scopes are required** for public contribution data. The script falls back to the public events REST API (last ~90 days only) if no token is supplied — fine for testing, not for the real chart.

Output is always `contributions.png` in the repo root.

### Commit conventions

- Use short imperative messages: `Update tech stack`, `Fix LinkedIn badge`, `Add FastAPI to backend`
- The Actions bot uses `chore: update contribution graph` — match that prefix if making related changes
- Don't commit `.venv/`, `contributions_preview.png`, `__pycache__/`, or any token files

## README design principles

The README has been deliberately cleaned up from a generator-spewed version. When editing it:

- **Keep the tokyonight theme** across all shield badges and stat widgets — color consistency matters
- **Group badges by category** (Languages / Frontend / Backend / DevOps / Tools) — don't dump them all in one block
- **Only badge tools the developer actually uses** — see the list above
- **Stats services:** use `github-readme-stats-eight-theta.vercel.app` (a community fork) instead of `github-readme-stats.vercel.app` — the canonical service rate-limits heavily and produces broken `camo.githubusercontent.com` URLs
- **Streak stats:** use `streak-stats.demolab.com`, NOT the old `github-readme-streak-stats.herokuapp.com` (Heroku endpoint is dead)
- **Trophy widget:** include `Reviews` in the `title=` parameter; place trophies BEFORE stats in document order
- **Follow buttons:** LinkedIn, not Twitter
- **Section order:** intro → about → connect → tech stack → trophies → stats → contribution history → quote

## GitHub Actions workflow

The workflow in `.github/workflows/contributions.yml` needs:

- `permissions: contents: write` at the workflow level (it's already there) — without this, the commit step gets a 403
- If the workflow still fails to push: go to repo Settings → Actions → General → Workflow permissions → "Read and write permissions" → Save
- The auto-injected `GITHUB_TOKEN` secret has enough scope to read the owner's public contribution data; no PAT setup needed

The workflow is idempotent — if the chart hasn't changed since the last run, it skips the commit.

## Things to NOT do

- Don't add Heroku, badges for tools the developer doesn't use, or every framework with a pretty logo
- Don't replace LinkedIn with Twitter as the primary "follow" action
- Don't use the rate-limited `github-readme-stats.vercel.app` endpoint
- Don't hardcode a GitHub token anywhere in tracked files(will be injected on the github repo itself as variable) — only pass it as an argument
- Don't commit `contributions.png` from a local run before pushing other changes if you're worried about merge conflicts with the bot — let the workflow regenerate it instead
- Don't restructure the README into a single mega-list of badges — the grouped layout is intentional

## Quick task reference

| Task                      | Command                                                            |
| ------------------------- | ------------------------------------------------------------------ |
| Activate venv             | `source .venv/bin/activate`                                        |
| Regenerate chart          | `python generate_contributions.py kaveks <token>`                  |
| Preview README locally    | `grip README.md` (if `pip install grip`) or push to a draft branch |
| Trigger workflow manually | Actions tab → "Update contribution graph" → Run workflow           |
| Check workflow logs       | `gh run list --workflow=contributions.yml`                         |
