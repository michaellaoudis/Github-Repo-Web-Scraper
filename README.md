# GitHub Repository Web Scraper

### Disclaimer

This tool is provided for educational and authorized security testing purposes only. The author, Michael Laoudis, accepts no responsibility for misuse. Always obtain written permission before testing any target.

<hr>

Developers may accidentally commit sensitive data, such as API keys, passwords, and private tokens to public repositories. This Python tool automates the manual process of searching through public repositories using the command-line.

Given a target GitHub username or organization, it will:

- Enumerate all public repositories (optionally including forks)
- Filter files by extension (e.g. `.env`, `.json`, `.py`)
- Scan every matching file for user-defined keywords (e.g. `password`, `secret`, `api_key`)
- Report exact file paths, line numbers, and direct GitHub URLs for each match


## Requirements

- Python 3.10+
- `requests` library

      pip3 install requests


A GitHub personal access token is recommended for 5,000 requests/hour to query the GitHub API. Without one, you are limited to 60 requests/hour. Generate one at https://github.com/settings/tokens (only the `public_repo` read scope is needed).

## Installation

    git clone https://github.com/michaellaoudis/GitHub-Repo-Web-Scraper.git
    cd GitHub-Repo-Web-Scraper
    pip3 install requests

## Usage

    python3 github_scraper.py -u <username> [options]

| Flag | Description |
|------|-------------|
| `-u` / `--user` | Target GitHub username or organization **(required)** |
| `-t` / `--token` | GitHub personal access token (strongly recommended) |
| `-k` / `--keywords` | Path to newline-separated keywords file |
| `-e` / `--extensions` | Path to newline-separated file extensions file |
| `-o` / `--output` | Write findings to a file (results also print to stdout) |
| `--all-repos` | Include forked repositories (skipped by default) |

<hr>

## Dependency Files

The tool relies on two plain-text configuration files.
- Lines beginning with # are treated as comments and ignored.

1. `keywords.txt` (one keyword per line, case-insensitive):

       password
       secret
       api_key

2. `extensions.txt` (one file extension per line):

       .env
       .py
       .json
       .yaml
       .config




## Output

Example keyword match:

    [+] Keyword match: password
    Repo : targetuser/project
    File : config/settings.py  (line 42)
    URL  : https://github.com/targetuser/project/blob/HEAD/config/settings.py
    Text : DB_PASSWORD = "laoudis3"

A summary is printed at the end showing total repositories scanned, files checked, and keyword matches found.


## Rate Limiting

The tool handles GitHub's rate limiting automatically. It detects 403/429 responses, reads the Retry-After header, and waits before retrying. A small delay between file requests (0.05s) is also included to avoid triggering secondary rate limits.

You may check your remaining quota at the start of a session by watching the startup output:

    [*] GitHub API rate limit: 4823/5000 requests remaining
