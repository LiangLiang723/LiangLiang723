#!/usr/bin/env python3
"""Fetch compact GitHub profile statistics without overwriting the last good data on failure."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "linear" / "profile-stats.json"
DEFAULT_GRAPHQL_URL = "https://api.github.com/graphql"
QUERY = """
query ProfileStats($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar { totalContributions }
    }
  }
}
"""


def graphql_request(url: str, token: str, query: str, variables: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps({"query": query, "variables": variables}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "LiangLiang723-profile-workflow",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("GitHub GraphQL response must be an object")
    errors = payload.get("errors")
    if errors:
        raise RuntimeError(f"GitHub GraphQL errors: {errors}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("GitHub GraphQL response is missing data")
    return data


def choose_primary_language(language_edges: list[dict[str, object]]) -> str:
    totals: Counter[str] = Counter()
    for edge in language_edges:
        if not isinstance(edge, dict):
            continue
        size = edge.get("size")
        node = edge.get("node")
        if not isinstance(size, int) or size < 0 or not isinstance(node, dict):
            continue
        name = node.get("name")
        if isinstance(name, str) and name.strip():
            totals[name.strip()] += size
    if not totals:
        return "—"
    return totals.most_common(1)[0][0]


def build_stats(payload: dict[str, object]) -> dict[str, object]:
    user = payload.get("user")
    if not isinstance(user, dict):
        raise ValueError("GitHub user was not found")
    repositories = user.get("repositories")
    contributions_collection = user.get("contributionsCollection")
    if not isinstance(repositories, dict) or not isinstance(contributions_collection, dict):
        raise ValueError("GitHub response is missing repository or contribution data")
    total_count = repositories.get("totalCount")
    nodes = repositories.get("nodes")
    calendar = contributions_collection.get("contributionCalendar")
    if not isinstance(total_count, int) or total_count < 0:
        raise ValueError("Invalid public repository count")
    if not isinstance(nodes, list) or not isinstance(calendar, dict):
        raise ValueError("Invalid repository language or contribution data")
    contributions = calendar.get("totalContributions")
    if not isinstance(contributions, int) or contributions < 0:
        raise ValueError("Invalid contribution count")
    language_edges: list[dict[str, object]] = []
    for repository in nodes:
        if not isinstance(repository, dict):
            continue
        languages = repository.get("languages")
        if not isinstance(languages, dict):
            continue
        edges = languages.get("edges")
        if isinstance(edges, list):
            language_edges.extend(edge for edge in edges if isinstance(edge, dict))
    return {
        "public_repos": total_count,
        "contributions": contributions,
        "primary_language": choose_primary_language(language_edges),
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def atomic_write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "").strip()
    url = os.environ.get("GITHUB_GRAPHQL_URL", DEFAULT_GRAPHQL_URL).strip() or DEFAULT_GRAPHQL_URL
    if not token or not owner:
        print("ERROR: GITHUB_TOKEN and GITHUB_REPOSITORY_OWNER are required.", file=sys.stderr)
        return 1
    try:
        payload = graphql_request(url, token, QUERY, {"login": owner})
        stats = build_stats(payload)
        if OUT.is_file():
            previous = json.loads(OUT.read_text(encoding="utf-8"))
            keys = ("public_repos", "contributions", "primary_language")
            if all(previous.get(key) == stats.get(key) for key in keys):
                print(f"Profile stats for {owner} are unchanged.")
                return 0
        atomic_write(OUT, stats)
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        print(f"ERROR: Unable to update profile stats; preserving previous data: {exc}", file=sys.stderr)
        return 1
    print(f"Updated profile stats for {owner}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
