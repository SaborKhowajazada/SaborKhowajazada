import os
import json
import html
import urllib.request
from datetime import datetime, timezone

USERNAME = os.getenv("GITHUB_USERNAME", "SaborKhowajazada")
TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "github-profile-stats"
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def github_api(path):
    url = f"https://api.github.com{path}"
    request = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def get_all_repos():
    repos = []
    page = 1

    while True:
        data = github_api(f"/users/{USERNAME}/repos?per_page=100&page={page}")

        if not data:
            break

        repos.extend(data)
        page += 1

    return repos


user = github_api(f"/users/{USERNAME}")
repos = get_all_repos()

total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
total_forks = sum(repo.get("forks_count", 0) for repo in repos)

public_repos = user.get("public_repos", 0)
followers = user.get("followers", 0)
following = user.get("following", 0)

updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

svg = f"""
<svg width="520" height="230" viewBox="0 0 520 230" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="520" height="230" rx="16" fill="#0d1117"/>
  <rect x="1" y="1" width="518" height="228" rx="15" stroke="#30363d"/>

  <text x="30" y="45" fill="#58a6ff" font-size="24" font-family="Arial, sans-serif" font-weight="700">
    {html.escape(USERNAME)}'s GitHub Stats
  </text>

  <text x="30" y="90" fill="#c9d1d9" font-size="18" font-family="Arial, sans-serif">
    Public repos: {public_repos}
  </text>

  <text x="30" y="120" fill="#c9d1d9" font-size="18" font-family="Arial, sans-serif">
    Total stars: {total_stars}
  </text>

  <text x="30" y="150" fill="#c9d1d9" font-size="18" font-family="Arial, sans-serif">
    Total forks: {total_forks}
  </text>

  <text x="270" y="90" fill="#c9d1d9" font-size="18" font-family="Arial, sans-serif">
    Followers: {followers}
  </text>

  <text x="270" y="120" fill="#c9d1d9" font-size="18" font-family="Arial, sans-serif">
    Following: {following}
  </text>

  <text x="30" y="200" fill="#8b949e" font-size="14" font-family="Arial, sans-serif">
    Last updated: {updated_at}
  </text>
</svg>
"""

with open("github-stats.svg", "w", encoding="utf-8") as file:
    file.write(svg)
