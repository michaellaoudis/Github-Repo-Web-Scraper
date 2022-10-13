# Github Repository Web Scraper
# Built by Michael Laoudis
# ------------------------------------------------------------------------------------
#   To run this tool, usage is as follows: "python filePath "targetUrl""
#       Example Usage:  python D:\\Recon\\github-web-scraper.py "https://github.com/michaellaoudis"
# ------------------------------------------------------------------------------------
#   For using a local path of Selenium instead:
#       from fileinput import filename
#       cdp = 'D:\\Projects\\Bug-Bounty\\Dev-Tools\\chromedriver_win32\\chromedriver.exe'                            # Chrome Driver path
#       driver = webdriver.Chrome(executable_path=cdp, options=options)                                              # Use Google Chrome for this tool
# ------------------------------------------------------------------------------------

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

def get_Repo_Files(repo_link, fileTypesPayload, keywordsPayload):
    
    driver.get(repo_link)                                                                                             # e.g. https://github.com/michaellaoudis/Python
    fileLinks = []                                                                                                    # Stores URL links to each file in the repository

    #Identify each file in repository
    scrapedFiles = driver.find_elements(by=By.XPATH, value="//a[@class='js-navigation-open Link--primary']")

    # Collect all the file URLs and store in list <fileLinks>
    for url in scrapedFiles:                                                 
        fileLinks.append(url.get_attribute("href"))
    
    for url in fileLinks:
        # Check if repository file is a folder
        if "/tree/" in url:
            driver.get(str(url))
            time.sleep(3)
            scrapedSubFiles = driver.find_elements(by=By.XPATH, value="//a[@class='js-navigation-open Link--primary']")
            for subFile in scrapedSubFiles:
                fileLinks.append(subFile.get_attribute("href"))
            fileLinks.remove(url)
            continue
        # Check if repository file is not a folder
        elif "/blob/" in url:
            for fileType in fileTypesPayload:
                if url.endswith(f"{fileType}"):
                    get_Raw_Contents(url, keywordsPayload)

# In Repositories tab, identify all repos and set up valid URLs so program can scrape each of them
def identifyRepos(targetUrl, fileTypesPayload, keywordsPayload):
    driver.get(f"{targetUrl}")                                     # Github page to scrape
    repoTab = driver.find_element(By.PARTIAL_LINK_TEXT, "Repositories")                                             # Click Repositories tab
    repoTab.click()
    time.sleep(3)
    scrapedRepos = driver.find_elements(By.XPATH, "//a[@itemprop='name codeRepository']")                           # Scrapes all repository listings
    
    repoNames = []                                                                                                  # Stores all identified repo names from 'Repositories' tab
    repoLinks = []                                                                                                  # Stores URL links to each repo

    # # Store repository names in list <repoNames>
    for repo in scrapedRepos:
        repoNames.append(repo.text)
    
    # # Add the repo name to our starting URL and store as a full path in <repo_link>. Append multiple <repo_link> to list <repoLinks>
    for name in repoNames:
        repo_link = f"{targetUrl}/{name}"                                                                           # e.g. https://github.com/michaellaoudis/Python                             
        repoLinks.append(repo_link)                                             
        get_Repo_Files(repo_link, fileTypesPayload, keywordsPayload)                                                # Call function <get_Repo_Files> and pass along (repository link, target file types, sensitive keywords)                                                     

# Set up targeted file types (txt file) to scrape for
def fileTypes_File(targetUrl, keywordsPayload):
    fileTypesFilePath = 'D:\\Projects\\Python\\WebAppSec\\Github-Repo-Web-Scraper\\target-filetypes.txt'
    fileTypesFile = open(fileTypesFilePath, 'r')

    file = fileTypesFile.readlines()
    fileTypesPayload = []

    for filetype in file:
        filetype = filetype.strip('\n')
        fileTypesPayload.append(filetype)
    identifyRepos(targetUrl, fileTypesPayload, keywordsPayload)                                                     # Call function <identifyRepos> and pass along (target url, target file types, sensitive keywords)
    fileTypesFile.close()

# Set up sensitive keywords (txt file) to scrape for
def keywords_File(targetUrl):
    keywordsFilePath = 'D:\\Projects\\Python\\WebAppSec\\Github-Repo-Web-Scraper\\sensitive-keywords.txt'                
    keywordsFile = open(keywordsFilePath, 'r')                          
    file = keywordsFile.readlines()
    keywordsPayload = []
    for keyword in file:
        keyword = keyword.strip('\n').lower()
        keywordsPayload.append(keyword)
    fileTypes_File(targetUrl, keywordsPayload)                                                                      # Call function <fileTypes_File> and pass along (target url, sensitive keywords)                                                                         
    keywordsFile.close()

def main():
    if len(sys.argv) !=2:                                                # If program is run without name of program and target URL,
        print("(+) Usage: %s <url>" % sys.argv[0])                       # Print usage: (name of program), (url)
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)                                                     # Exit program
    
    targetUrl = sys.argv[1]
    print("(+) Scraping GitHub profile...")
    keywords_File(targetUrl)
   
if __name__ == "__main__":
    main()

driver.quit()

