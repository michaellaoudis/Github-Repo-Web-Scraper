#!/usr/bin/env python3
"""
GitHub Repository Web Scraper built by Michael Laoudis
For use by authorized security testers only.

Usage:
    python3 github_scraper.py -u <github_username> [-t <token>] [-k keywords.txt] [-e extensions.txt] [-o output.txt]
    python3 github_scraper.py -u targetorg -t ghp_xxxx -k sensitive-keywords.txt -e target-filetypes.txt

Positional flags:
    -u / --user         Target GitHub username or organisation (required)
    -t / --token        GitHub personal access token (strongly recommended — raises rate limit from 60 to 5000 req/hr)
    -k / --keywords     Path to a newline-separated list of sensitive keywords to search for
    -e / --extensions   Path to a newline-separated list of file extensions to inspect (e.g. .py .env .json)
    -o / --output       Optional path to write findings to a file (findings are always printed to stdout too)
    --all-repos         Also include forked repositories (skipped by default)
"""

import sys
import argparse
import time
import base64
import re
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("[!] 'requests' not found. Run: pip3 install requests")


# Colors
RESET  = "\033[0m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
BOLD   = "\033[1m"

def c(colour, text):
    return f"{colour}{text}{RESET}"


# GitHub API

BASE = "https://api.github.com"

class GitHubClient:

    def __init__(self, token: str | None):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "gh-security-scraper",
        })

        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

        self._check_rate_limit_on_start()


    def _check_rate_limit_on_start(self):
        r = self.session.get(f"{BASE}/rate_limit")
        if r.ok:
            remaining = r.json()["rate"]["remaining"]
            limit     = r.json()["rate"]["limit"]
            print(c(CYAN, f"[*] GitHub API rate limit: {remaining}/{limit} requests remaining"))
            if remaining < 10:
                print(c(YELLOW, "[!] Rate limit critically low. Consider providing a token with -t."))


    def _get(self, url: str, params: dict = None) -> requests.Response | None:
        for attempt in range(4):
            r = self.session.get(url, params=params)

            if r.status_code == 200:
                return r

            if r.status_code in (403, 429):
                # GitHub uses both codes for rate limiting
                retry_after = int(r.headers.get("Retry-After", 30))
                print(c(YELLOW, f"[!] Rate-limited. Waiting {retry_after}s…"))
                time.sleep(retry_after)
                continue

            if r.status_code == 404:
                return None

            print(c(YELLOW, f"[!] HTTP {r.status_code} for {url}"))
            return None

        print(c(RED, f"[-] Giving up on {url} after retries."))
        return None


    def get_repos(self, user: str, include_forks: bool = False) -> list[dict]:
        repos = []
        page  = 1

        while True:
            r = self._get(
                f"{BASE}/users/{user}/repos",
                params={"per_page": 100, "page": page, "type": "public"}
            )
            if not r:
                break

            batch = r.json()
            if not batch:
                break

            for repo in batch:
                if not include_forks and repo.get("fork"):
                    continue
                repos.append(repo)

            page += 1

        return repos


    def get_tree(self, owner: str, repo: str, default_branch: str) -> list[dict]:
        r = self._get(
            f"{BASE}/repos/{owner}/{repo}/git/trees/{default_branch}",
            params={"recursive": "1"}
        )
        if not r:
            return []

        data = r.json()

        if data.get("truncated"):
            print(c(YELLOW, f"[!] Tree truncated for {owner}/{repo} (very large repo)."))

        return [item for item in data.get("tree", []) if item.get("type") == "blob"]


    def get_file_content(self, owner: str, repo: str, path: str) -> str | None:
        r = self._get(f"{BASE}/repos/{owner}/{repo}/contents/{path}")
        if not r:
            return None

        data = r.json()

        if isinstance(data, list):
            return None

        encoding = data.get("encoding")
        content  = data.get("content", "")
        size     = data.get("size", 0)

        if size > 1_000_000:
            print(c(YELLOW, f"    [~] Skipping large file ({size//1024} KB): {path}"))
            return None

        if encoding == "base64":
            try:
                return base64.b64decode(content).decode("utf-8", errors="replace")
            except Exception:
                return None

        return None


# Helper functions

def load_lines(filepath: str, label: str) -> list[str]:
    p = Path(filepath)
    if not p.is_file():
        sys.exit(c(RED, f"[!] {label} file not found: {filepath}"))

    lines = [
        l.strip().lower()
        for l in p.read_text().splitlines()
        if l.strip() and not l.startswith("#")
    ]

    print(c(CYAN, f"[*] Loaded {len(lines)} {label}: {lines[:6]}{'…' if len(lines) > 6 else ''}"))
    return lines


def scan_content(content: str, keywords: list[str]) -> list[tuple]:
    hits = []

    for lineno, raw_line in enumerate(content.splitlines(), 1):
        line_lower = raw_line.lower()

        for kw in keywords:
            if kw in line_lower:
                hits.append((kw, raw_line.strip(), lineno))

    return hits


def print_finding(repo_full: str, file_path: str, keyword: str, line: str, lineno: int, output_lines: list):
    file_url = f"https://github.com/{repo_full}/blob/HEAD/{file_path}#L{lineno}"

    msg_lines = [
        c(GREEN,  f"\n[+] Keyword match: {c(BOLD, keyword)}"),
        c(CYAN,   f"    Repo : {repo_full}"),
        c(CYAN,   f"    File : {file_path}  (line {lineno})"),
        c(CYAN,   f"    URL  : {file_url}"),
        c(YELLOW, f"    Text : {line[:300]}"),
    ]

    for m in msg_lines:
        print(m)

    clean = re.sub(r"\033\[[0-9;]*m", "", "\n".join(msg_lines))
    output_lines.append(clean)


# Main scanning

def scrape(args):
    client = GitHubClient(args.token)

    keywords   = load_lines(args.keywords,   "keywords")   if args.keywords   else []
    extensions = load_lines(args.extensions, "extensions") if args.extensions else []

    if not keywords:
        sys.exit(c(RED, "[!] No keywords loaded. Provide a keywords file with -k."))

    extensions = [e if e.startswith(".") else f".{e}" for e in extensions]

    output_lines: list[str] = []
    total_hits   = 0
    total_files  = 0

    print(c(BOLD, f"\n[*] Fetching repositories for: {args.user}\n"))
    repos = client.get_repos(args.user, include_forks=args.all_repos)

    if not repos:
        sys.exit(c(RED, f"[!] No public repositories found for '{args.user}'. Check the username."))

    print(c(CYAN, f"[*] Found {len(repos)} repositories to scan.\n"))

    for repo in repos:
        owner     = repo["owner"]["login"]
        repo_name = repo["name"]
        repo_full = repo["full_name"]
        branch    = repo.get("default_branch", "main")

        print(c(BOLD, f"[>] Scanning: {repo_full}  (branch: {branch})"))

        tree = client.get_tree(owner, repo_name, branch)
        if not tree:
            print(c(YELLOW, "    [~] Empty or inaccessible tree. Skipping."))
            continue

        if extensions:
            targets = [f for f in tree if Path(f["path"]).suffix.lower() in extensions]
        else:
            targets = tree

        print(c(CYAN, f"    [*] {len(targets)} file(s) match extension filter out of {len(tree)} total."))

        for file_entry in targets:
            file_path = file_entry["path"]
            total_files += 1

            content = client.get_file_content(owner, repo_name, file_path)
            if content is None:
                continue

            hits = scan_content(content, keywords)

            for (kw, line, lineno) in hits:
                total_hits += 1
                print_finding(repo_full, file_path, kw, line, lineno, output_lines)

            # Small delay to avoid triggering secondary rate limits
            time.sleep(0.05)

    summary = (
        f"\n{'='*60}\n"
        f"  Scan complete.\n"
        f"  Repos scanned : {len(repos)}\n"
        f"  Files checked : {total_files}\n"
        f"  Keyword hits  : {total_hits}\n"
        f"{'='*60}\n"
    )
    print(c(BOLD, summary))

    if args.output and output_lines:
        out_path = Path(args.output)
        out_path.write_text(summary + "\n".join(output_lines))
        print(c(GREEN, f"[+] Findings written to: {out_path.resolve()}"))
    elif args.output:
        print(c(YELLOW, "[~] No findings to write."))


# CLI argument parsing

def main():
    parser = argparse.ArgumentParser(
        description="GitHub repository sensitive-information scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("-u", "--user",       required=True,  help="Target GitHub username or organisation")
    parser.add_argument("-t", "--token",      default=None,   help="GitHub personal access token (recommended)")
    parser.add_argument("-k", "--keywords",   default=None,   help="Path to sensitive keywords file (one per line)")
    parser.add_argument("-e", "--extensions", default=None,   help="Path to target file extensions file (one per line, e.g. .env)")
    parser.add_argument("-o", "--output",     default=None,   help="Write findings to this file")
    parser.add_argument("--all-repos", action="store_true",   help="Include forked repositories")

    args = parser.parse_args()
    scrape(args)

if __name__ == "__main__":
    main()
