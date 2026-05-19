import os
import json
import html
import urllib.request
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone

USERNAME = os.getenv("GITHUB_USERNAME", "SaborKhowajazada")
TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "github-profile-stats"
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def github_api(path, with_headers=False):
    url = f"https://api.github.com{path}"
    request = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode("utf-8"))

        if with_headers:
            return data, response.headers

        return data


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


def get_last_page_from_link_header(link_header):
    if not link_header:
        return None

    parts = link_header.split(",")

    for part in parts:
        if 'rel="last"' in part:
            start = part.find("<") + 1
            end = part.find(">")
            url = part[start:end]

            query = parse_qs(urlparse(url).query)
            page = query.get("page", [None])[0]

            if page:
                return int(page)

    return None


def count_commits_for_repo(owner, repo_name):
    try:
        data, headers = github_api(
            f"/repos/{owner}/{repo_name}/commits?author={USERNAME}&per_page=1",
            with_headers=True
        )

        last_page = get_last_page_from_link_header(headers.get("Link"))

        if last_page:
            return last_page

        return len(data)

    except Exception:
        return 0


user = github_api(f"/users/{USERNAME}")
repos = get_all_repos()

public_repos = user.get("public_repos", 0)
total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
total_forks = sum(repo.get("forks_count", 0) for repo in repos)

total_commits = 0

for repo in repos:
    owner = repo.get("owner", {}).get("login", USERNAME)
    repo_name = repo.get("name")
    total_commits += count_commits_for_repo(owner, repo_name)

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
    Total commits: {total_commits}
  </text>

  <text x="30" y="150" fill="#c9d1d9" font-size="18" font-family="Arial, sans-serif">
    Total stars: {total_stars}
  </text>

  <text x="270" y="90" fill="#c9d1d9" font-size="18" font-family="Arial, sans-serif">
    Total forks: {total_forks}
  </text>

  <text x="30" y="200" fill="#8b949e" font-size="14" font-family="Arial, sans-serif">
    Last updated: {updated_at}
  </text>
</svg>
"""

with open("github-stats.svg", "w", encoding="utf-8") as file:
    file.write(svg)
