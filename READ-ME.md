# Github Repository Web Scraper

#### **Disclaimer**:
- This tool is intended to be used ethically towards Github Profiles with the intent of reporting sensitively stored public information to the Github Profile Owner
- If sensitive information is discovered using this tool, the author, Michael Laoudis, assumes no responsibility or liability for the actions of any parties having utilized it
- For Bug Bounty Programs, abide by the set scope and only use this tool on company or developer related profiles if permitted

## Description
<hr>


## Dependencies
<hr>

1. Programming Language: `Python`

2. Install `Webdriver Manager`

        pip install webdriver-manager

3. Install `Selenium` 

        pip install selenium

3. Text Files: `sensitive-keywords.txt`, `target-filetypes.txt`
4. After storing the program files locally, in `github-web-scraper.py`, alter the variables `fileTypesFilePath` and `keywordsFilePath` to reflect where you stored the text files referenced in Dependencies (4)

- Example:


        fileTypesFilePath = 'D:\\Projects\\Python\\WebAppSec\\Github-Repo-Web-Scraper\\target-filetypes.txt'

        keywordsFilePath = 'D:\\Projects\\Python\\WebAppSec\\Github-Repo-Web-Scraper\\sensitive-keywords.txt'

## Usage
<hr>

1. To run the program, syntax is as follows:  
`python file_path\github-web-scraper.py`

- Example:

        python D:\Github-Repo-Web-Scraper\github-web-scraper.py

2. 


