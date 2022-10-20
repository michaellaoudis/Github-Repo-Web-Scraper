# Github Repository Web Scraper
# Built by Michael Laoudis
# ------------------------------------------------------------------------------------
#   To run this tool, usage is as follows: "python filePath "targetUrl""
#       Example Usage:  python D:\\Recon\\github-web-scraper.py "https://github.com/michaellaoudis"
# ------------------------------------------------------------------------------------
#   For using a local path of Selenium instead:
#       from fileinput import filename
#       cdp = 'D:\\Projects\\Bug-Bounty\\Dev-Tools\\chromedriver_win32\\chromedriver.exe'                            # Local Path to Chrome Driver downloaded from: https://chromedriver.chromium.org/downloads
#       driver = webdriver.Chrome(executable_path=cdp, options=options)                                              # Use Google Chrome for this tool
# ------------------------------------------------------------------------------------                               # Check current Chrome version: Open Chrome > Settings > About Chrome
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, sys

# Silence runtime USB device errors stemming from some chromedriver issue
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Selenium installs newest Chrome vers. on execution
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)                                                               # Use Google Chrome for this tool

# Get Raw HTML of discovered target files and check for keywords
def get_Raw_Contents(fileLink, keywordsPayload):
    driver.get(fileLink)
    raw = driver.find_element(By.ID, "raw-url").click()                                                             # Click on 'Raw' button
    time.sleep(2)
    html = driver.page_source.lower()                                                                               # Scrape page source
    html = f"{html}"
    for fileLine in html.split("\n"):
        for keyword in keywordsPayload:
            if keyword in fileLine:
                print(f"(+) Keyword \"{keyword}\" found at: {fileLink}")
                print(f"(-) Here's the text: \n\"{fileLine}\"\n")

# Scrape folders recursively for target file extensions
def get_Repo_Files(repo_link, fileTypesPayload, keywordsPayload):
    driver.get(repo_link)                                                                                             # e.g. https://github.com/michaellaoudis/Python
    fileLinks = []                                                                                                    # Stores URL links to each file in the repository

    # Identify each file in repository
    time.sleep(2)
    scrapedFiles = driver.find_elements(by=By.XPATH, value="//a[@class='js-navigation-open Link--primary']")

    # Collect all the file URLs and store in list <fileLinks>
    for url in scrapedFiles:                                                 
        fileLinks.append(url.get_attribute("href"))
    
    for url in fileLinks:
        # Check if repository file is a folder
        if "/tree/" in url:                                                                                         # Continue scraping contents inside folders until no folders are left to look through
            driver.get(str(url))                                                                            
            time.sleep(3)
            scrapedSubFiles = driver.find_elements(by=By.XPATH, value="//a[@class='js-navigation-open Link--primary']")
            for subFile in scrapedSubFiles:
                fileLinks.append(subFile.get_attribute("href"))
            fileLinks.remove(url)                                                                                   # Remove the scraped folder we looked through already
            continue
        # Check if repository file is not a folder
        elif "/blob/" in url:
            for fileType in fileTypesPayload:
                if url.endswith(f"{fileType}"):                                                                     # Check if file extension matches your target file type 
                    get_Raw_Contents(url, keywordsPayload)                                                          # If it matches, get the raw html to check for target keywords

# In Repositories tab, identify all repos and set up valid URLs to them for scraping
def identify_Repos(targetUrl, fileTypesPayload, keywordsPayload):
    driver.get(f"{targetUrl}")                                     # Github page to scrape
    repoTab = driver.find_element(By.PARTIAL_LINK_TEXT, "Repositories")                                             # Click Repositories tab
    repoTab.click()
    time.sleep(3)
    scrapedRepos = driver.find_elements(By.XPATH, "//a[@itemprop='name codeRepository']")                           # Scrapes all repository listings
    
    repoNames = []                                                                                                  # Stores all identified repo names from 'Repositories' tab                                                                                                 # Stores URL links to each repo

    # Store repository names in list <repoNames>
    for repo in scrapedRepos:
        repoNames.append(repo.text)
    
    # Add the repo name to our starting URL and store as a full path in <repo_link>. Append multiple <repo_link> to list <repoLinks>
    for name in repoNames:
        repo_link = f"{targetUrl}/{name}"                                                                           # e.g. https://github.com/michaellaoudis/Python                                                                         
        get_Repo_Files(repo_link, fileTypesPayload, keywordsPayload)                                                # Call function <get_Repo_Files> and pass along (repository link, target file types, sensitive keywords)                                                     

# Set up targeted file types (txt file) to scrape for
def fileTypes_File(targetUrl, keywordsPayload):
    fileTypesFilePath = 'D:\\Projects\\Github-Repo-Web-Scraper\\target-filetypes.txt'
    fileTypesFile = open(fileTypesFilePath, 'r')
    file = fileTypesFile.readlines()
    fileTypesPayload = []
    
    # Collect target file extensions from each line in target-filetypes.txt
    for filetype in file:
        filetype = filetype.strip('\n')
        fileTypesPayload.append(filetype)
    fileTypesFile.close()
    identify_Repos(targetUrl, fileTypesPayload, keywordsPayload)                                                     # Call function <identifyRepos> and pass along (target url, target file types, sensitive keywords)

# Set up sensitive keywords (txt file) to scrape for
def keywords_File(targetUrl):
    keywordsFilePath = 'D:\\Projects\\Github-Repo-Web-Scraper\\sensitive-keywords.txt'                
    keywordsFile = open(keywordsFilePath, 'r')                          
    file = keywordsFile.readlines()
    keywordsPayload = []
    
    # Collect target keywords from each line in sensitive-keywords.txt
    for keyword in file:
        keyword = keyword.strip('\n').lower()
        keywordsPayload.append(keyword)
    keywordsFile.close()
    fileTypes_File(targetUrl, keywordsPayload)                                                                      # Call function <fileTypes_File> and pass along (target url, sensitive keywords)                                                                         

def main():
    try:
        targetUrl = sys.argv[1]
        print("(+) Scraping GitHub profile...\n")
        keywords_File(targetUrl)
    except:
        print('(+) An error has occurred. Please check your usage follows the format:\t python %s "https://github.com/targetProfile"' % sys.argv[0])
        driver.quit()                                                                                               # Close failed Chrome browser
        sys.exit(-1)                                                                                                # Exit program
   
if __name__ == "__main__":
    main()

driver.quit()

