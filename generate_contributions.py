"""
Generate a multi-year GitHub contribution visualization.

Usage:
    python generate_contributions.py <github_username> [github_token]
"""

import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np


def fetch_yearly_contributions_graphql(username, token):
    user_query = """
    query($login: String!) {
      user(login: $login) { createdAt }
    }
    """
    user_data = _graphql_request(user_query, {"login": username}, token)
    created_at = user_data["data"]["user"]["createdAt"]
    start_year = int(created_at[:4])
    current_year = datetime.now(timezone.utc).year

    yearly = {}
    monthly = defaultdict(int)

    for year in range(start_year, current_year + 1):
        from_date = f"{year}-01-01T00:00:00Z"
        to_date = f"{year}-12-31T23:59:59Z" if year < current_year else \
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        contrib_query = """
        query($login: String!, $from: DateTime!, $to: DateTime!) {
          user(login: $login) {
            contributionsCollection(from: $from, to: $to) {
              contributionCalendar {
                totalContributions
                weeks { contributionDays { date contributionCount } }
              }
            }
          }
        }
        """
        result = _graphql_request(
            contrib_query,
            {"login": username, "from": from_date, "to": to_date},
            token,
        )
        cal = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        year_total = 0
        for week in cal["weeks"]:
            for day in week["contributionDays"]:
                d = datetime.fromisoformat(day["date"])
                count = day["contributionCount"]
                monthly[(d.year, d.month)] += count
                if d.year == year:
                    year_total += count
        yearly[year] = year_total
    return {"yearly": yearly, "monthly": dict(monthly)}


def _graphql_request(query, variables, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "contrib-grapher",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_recent_events_rest(username):
    print("WARN: No token — falling back to public events (last ~90 days only).")
    monthly = defaultdict(int)
    page = 1
    while page <= 10:
        url = f"https://api.github.com/users/{username}/events/public?per_page=100&page={page}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "contrib-grapher"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                events = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code}: {e.reason}")
            break
        if not events:
            break
        for ev in events:
            if ev["type"] in ("PushEvent", "PullRequestEvent", "IssuesEvent",
                              "PullRequestReviewEvent", "CreateEvent"):
                d = datetime.fromisoformat(ev["created_at"].replace("Z", "+00:00"))
                count = len(ev["payload"].get("commits", [])) if ev["type"] == "PushEvent" else 1
                monthly[(d.year, d.month)] += count
        page += 1
    yearly = defaultdict(int)
    for (y, _m), v in monthly.items():
        yearly[y] += v
    return {"yearly": dict(yearly), "monthly": dict(monthly)}


def plot_contributions(data, username, output_path, years_window=10):
    current_year = datetime.now(timezone.utc).year
    earliest_year = current_year - years_window + 1

    yearly = {y: c for y, c in data["yearly"].items() if y >= earliest_year}
    monthly = {(y, m): c for (y, m), c in data["monthly"].items() if y >= earliest_year}
    if not yearly:
        yearly = {current_year: 0}
    years = sorted(yearly.keys())

    bg = "#ffffff"; fg = "#24292f"; accent = "#0969da"; grid = "#d0d7de"
    plt.rcParams.update({
        "figure.facecolor": bg, "axes.facecolor": "#f6f8fa", "axes.edgecolor": grid,
        "axes.labelcolor": fg, "text.color": fg, "xtick.color": fg, "ytick.color": fg,
        "font.family": "DejaVu Sans",
    })

    fig = plt.figure(figsize=(14, 5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 2.2], wspace=0.15)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_heat = fig.add_subplot(gs[0, 1])

    counts = [yearly.get(y, 0) for y in years]
    bars = ax_bar.bar(years, counts, color=accent, edgecolor="white", linewidth=1.5)
    ax_bar.set_title("Contributions per year", fontsize=12, fontweight="bold", pad=10)
    ax_bar.set_xticks(years)
    ax_bar.set_xticklabels([str(y) for y in years], rotation=45, ha="right", fontsize=9)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.grid(axis="y", color=grid, linestyle="-", linewidth=0.5, alpha=0.8)
    ax_bar.set_axisbelow(True)
    for bar, c in zip(bars, counts):
        if c > 0:
            ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        f"{c:,}", ha="center", va="bottom", fontsize=8, color=fg)

    heat_years = sorted({y for (y, _m) in monthly.keys()}) or years
    matrix = np.zeros((len(heat_years), 12))
    for i, y in enumerate(heat_years):
        for m in range(1, 13):
            matrix[i, m - 1] = monthly.get((y, m), 0)
    vmax = max(matrix.max(), 1)
    im = ax_heat.imshow(matrix, aspect="auto", cmap="Blues", vmin=0, vmax=vmax,
                       interpolation="nearest")
    ax_heat.set_title("Contributions by month", fontsize=12, fontweight="bold", pad=10)
    ax_heat.set_xticks(range(12))
    ax_heat.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                             "Jul","Aug","Sep","Oct","Nov","Dec"], fontsize=9)
    ax_heat.set_yticks(range(len(heat_years)))
    ax_heat.set_yticklabels([str(y) for y in heat_years], fontsize=9)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = int(matrix[i, j])
            if v > 0:
                color = fg if v < vmax * 0.6 else "white"
                ax_heat.text(j, i, str(v), ha="center", va="center", fontsize=7, color=color)
    cbar = fig.colorbar(im, ax=ax_heat, fraction=0.025, pad=0.02)
    cbar.ax.tick_params(colors=fg, labelsize=8)
    cbar.outline.set_edgecolor(grid)

    total = sum(yearly.values())
    fig.suptitle(f"@{username}  -  {total:,} contributions across {len(years)} years",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=bg, edgecolor="none")
    print(f"Saved {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_contributions.py <username> [token]")
        sys.exit(1)
    username = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) > 2 else None
    if token:
        try:
            data = fetch_yearly_contributions_graphql(username, token)
        except Exception as e:
            print(f"GraphQL failed ({e}); falling back to REST.")
            data = fetch_recent_events_rest(username)
    else:
        data = fetch_recent_events_rest(username)
    plot_contributions(data, username, "contributions.png", years_window=10)


if __name__ == "__main__":
    main()
