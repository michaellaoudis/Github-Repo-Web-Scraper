# Github Repository Web Scraper

#### **Disclaimer**:
- This tool is intended to be used ethically towards Github Profiles with the intent of reporting sensitively stored public information to the Github Profile Owner
- If sensitive information is discovered using this tool, the author, Michael Laoudis, assumes no responsibility or liability for the actions of any parties having utilized it
- For Bug Bounty Programs, abide by the set scope and only use this tool on company or developer related profiles if permitted
<hr><br>

## Description

The `Github Repository Web Scraper` is a reconnaissance tool used to perform information gathering (passive foot-printing) on Github profiles' public repositories. A malicious attacker would find value in discovering sensitive information publicly stored by developers. Information disclosure of test credentials or cryptographic keys left in code could lead to escalated attacks against the victim.

Having been given a target Github profile URL, this tool will recursively scrape every public folder and file in every repository for your desired file types and matching text. 

For example, let's say I wanted to search through repositories for only JavaScript files with lines containing the text "password". Rather than spending hours performing manually scanning, I would edit the dependency text files referenced below and execute the tool to retrieve the results in seconds.

<hr><br>

## Dependencies

1. Programming Language: `Python3`
2. Browser: `Google Chrome`

3. Install `Webdriver Manager`

        pip install webdriver_manager

4. Install `Selenium` 

        pip install selenium

5. Text Files: `sensitive-keywords.txt`, `target-filetypes.txt`
6. After storing the program files locally, in `github-web-scraper.py`, alter the variables `fileTypesFilePath` and `keywordsFilePath` to reflect where you stored the text files referenced in Dependencies (4) <br/><br/>

Example:


        fileTypesFilePath = 'D:\\Projects\\Python\\WebAppSec\\Github-Repo-Web-Scraper\\target-filetypes.txt'

        keywordsFilePath = 'D:\\Projects\\Python\\WebAppSec\\Github-Repo-Web-Scraper\\sensitive-keywords.txt'

<hr><br>

## Usage 

1. To run the program, syntax is as follows:  
`python \path\github-web-scraper.py "https://github.com/targetProfile"` <br/><br/>


Example:

        python D:\Github-Repo-Web-Scraper\github-web-scraper.py "https://github.com/michaellaoudis"


2. To filter for specific file types against your target's repositories:
- Edit the `target-filetypes.txt` file
- Each file type should rest on its own line in format `".extension"` <br/><br/>

Example:

        .js
        .py
        .json
        .php

3. To filter for specific keywords against your target's repositories:
- Edit the `sensitive-keywords.txt` file
- Each keyword should rest on its own line <br/><br/>

Example:

        username
        password
        key

<br/><br/>

- **This tool searches for case-insensitive matching strings**
- Keyword `"UsER"` will be converted to -> `"user"` at runtime
- Similarly, the target's files will be scraped then converted to lower-case for matching against your desired keywords
- Special characters are accepted <br/><br/>

<hr><br>

## Sample Output
<br>

        (+) Scraping GitHub profile...

        (+) Keyword "password" found at: https://github.com/michaellaoudis/Python/blob/main/Test-Target/Javascript-Target.js
        (-) Here's the text:
        "in in nunc. class aptent taciti username=michael password=laoudis sociosqu ad litora torquent per conubia nostra, per inceptos hymenaeos. donec ullamcorper fringilla eros. fusce in sapien eu purus dapibus commodo. cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. cras faucibus condimentum odio. sed ac ligula. aliquam at eros. etiam at ligula et tellus ullamcorper ultrices. in fermentum, lorem non cursus porttitor, diam urna accumsan lacus, sed interdum wisi nibh nec nisl."

        (+) Keyword "key" found at: https://github.com/michaellaoudis/Python/blob/main/Test-Target/More-Fake-Creds.html
        (-) Here's the text:
        "donec ut est in lectus consequat consequat. key=michael123 etiam eget dui. aliquam erat volutpat. sed at lorem in nunc porta tristique. proin nec augue. quisque aliquam tempor magna. pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. nunc ac magna. maecenas odio dolor, vulputate vel, auctor ac, accumsan id, felis. pellentesque cursus 
        sagittis felis."        

        (+) Keyword "password" found at: https://github.com/michaellaoudis/Python/blob/main/Test-Target/PHP-Target.php
        (-) Here's the text:
        "in in nunc. class aptent taciti username=mich43l password=l40udi$ sociosqu ad litora torquent per conubia nostra, per inceptos hymenaeos. donec ullamcorper fringilla eros. fusce in sapien eu purus dapibus commodo. cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. cras faucibus condimentum odio. sed ac ligula. aliquam at eros. etiam at ligula et tellus ullamcorper ultrices. in fermentum, lorem non cursus porttitor, diam urna accumsan lacus, sed interdum wisi nibh nec nisl."

