# GitHub Repository Web Scraper

#### **Disclaimer**:
- This tool is intended to be used ethically towards GitHub Profiles with the intent of reporting sensitively stored public information to the GitHub Profile Owner
- If sensitive information is discovered using this tool, the author, Michael Laoudis, assumes no responsibility or liability for the actions of any parties having utilized it
- For Bug Bounty Programs, abide by the set scope and only use this tool on company or developer related profiles if permitted
<br>

## Description

The `GitHub Repository Web Scraper` is a reconnaissance tool used to perform information gathering (passive foot-printing) on GitHub profiles' public repositories. A malicious attacker would find value in discovering sensitive information publicly stored by developers. Information disclosure of test credentials or cryptographic keys left in code could lead to escalated attacks against the victim.

Having been given a target GitHub profile URL, this tool will recursively scrape every public folder and file in every repository for your desired file types and matching text. 

For example, let's say I wanted to search through repositories for only JavaScript files with lines containing the text "password". Rather than spending hours performing manual scanning, I would edit the dependency text files referenced below and execute the tool to retrieve these results in seconds.
<br>

## Dependency

        pip3 install requests

## Usage 

    python3 github_scraper.py -u <github_username> [-t <token>] [-k keywords.txt] [-e extensions.txt] [-o output.txt]
    python3 github_scraper.py -u targetorg -t ghp_xxxx -k sensitive-keywords.txt -e target-filetypes.txt

        Positional flags:
            -u / --user         Target GitHub username or organisation (required)
            -t / --token        GitHub personal access token (strongly recommended — raises rate limit from 60 to 5000 req/hr)
            -k / --keywords     Path to a newline-separated list of sensitive keywords to search for
            -e / --extensions   Path to a newline-separated list of file extensions to inspect (e.g. .py .env .json)
            -o / --output       Optional path to write findings to a file (findings are always printed to stdout too)
            --all-repos         Also include forked repositories (skipped by default)

## Sample Output
<br>

        python3 github_scraper.py -u michaellaoudis -k keywords.txt -e file-types.txt
        
        [*] GitHub API rate limit: 60/60 requests remaining
        [*] Loaded 4 keywords: ['key', 'secret', 'password', 'user']
        [*] Loaded 4 extensions: ['.py', '.js', '.php', '.html']
        
        [*] Fetching repositories for: michaellaoudis
        
        [*] Found 4 repositories to scan.
        
        [>] Scanning: michaellaoudis/Bug-Bounty-Reports  (branch: master)
            [*] 0 file(s) match extension filter out of 1 total.
        [>] Scanning: michaellaoudis/Python  (branch: main)
            [*] 1458 file(s) match extension filter out of 3288 total.
        
        [+] Keyword match: password
            Repo : michaellaoudis/Python
            File : Javascript-Target.js  (line 26)
            URL  : https://github.com/michaellaoudis/Python/blob/main/Test-Target/Javascript-Target.js
            Text : password=laoudis

