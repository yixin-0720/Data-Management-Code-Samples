# **NY Times Scraper (2024)**
## **Author: Yixin Ding**
This Python script fetches and processes news articles from The New York Times (NYT) Archive API for a specified year. It filters articles by pre-defined **news desk** categories, checks for **China-related** content based on a list of keywords, and extracts **full text** from the article webpages whenever possible. The final data is then saved into CSV files.

---

## **Overview**
1. **NYT Archive API Integration**  
   - Retrieves monthly archives of articles for the specified year using the NYT Archive API.  
   - Implements exponential backoff to handle potential rate-limiting (HTTP 429) responses.

2. **Cookie Usage**  
   - Utilizes `browser_cookie3` to automatically load and use NYT cookies from your local Chrome installation. This helps bypass certain paywalls or "verify you're not a robot" checks.

3. **China-Related Filtering**  
   - Reads keywords from `combined_china_keywords.csv` and uses them (in lowercase) to check if an article is **China-related** by scanning its headline and abstract.

4. **Web Scraping for Full Text**  
   - Attempts to scrape the full text of **China-related** articles using a two-step approach:
     1. **Direct Requests**: First tries to download the article HTML with standard `requests`.  
     2. **Headless Selenium**: If direct requests fail or trigger robot verification, it falls back to a headless Selenium-driven Chrome browser to extract the article’s text.

5. **Robust Error Handling**  
   - Implements retry mechanisms and **exponential backoff** for network requests and page loads in Selenium.  
   - Detects “verify you’re not a robot” prompts to trigger additional waiting or re-tries.

6. **Data Export**  
   - Saves *all retrieved articles* into `all_article_nyt2024.csv`.  
   - Saves *only China-related articles (with full text)* into `China_article_nyt2024.csv`.

## **File and Directory Structure**
1. combined_china_keywords.csv          # CSV containing China-related keywords
2. nyt_scraper_v3.py                    # main Python script with the code
3. all_article_nyt2024.csv              # Output file - all articles for the chosen year in selected news desks
4. China_article_nyt2024.csv            # Output file - only China-related articles with full text
5. README.md                            # This README file

## **Requirements**
1. **Python 3.7+**  
2. **Chrome Browser** installed.  
3. **ChromeDriver** compatible with your installed Chrome version (if using Selenium).  
4. **Python Libraries**:
   - `requests`
   - `pandas`
   - `time` (standard library)
   - `bs4` (BeautifulSoup)
   - `re` (standard library)
   - `browser_cookie3`
   - `selenium`
   - `logging` (standard library)
   - `fake_useragent`

You may install the additional Python libraries using:
```bash
pip install requests pandas beautifulsoup4 browser-cookie3 selenium fake-useragent
```

## **Setup & Configuration**
1.	**API Key**
	•	Replace API_KEY in the script with your NYT Archive API key.
2.	**ChromeDriver**
	•	Download ChromeDriver that matches your Chrome version.
	•	Make sure the chromedriver binary is in your system’s PATH or specify its location in your Selenium configuration if needed.
3.	**China Keywords CSV**
	•	Ensure combined_china_keywords.csv is located in the same directory (or update the path in the script).
4.	**Browser Cookies**
	•	The script automatically loads NYT cookies from Chrome via browser_cookie3. Make sure you’re logged into nytimes.com on Chrome if your subscription or login status is needed for paywalled articles.

## **Usage**
1.	**Adjust the script**
	•	Place your API key in API_KEY.
	•	Update any file paths if you have a custom directory structure.
2.	**Run the Script**
	•	From your terminal or command prompt, navigate to the directory containing script.py and run:
```bash
python script.py
```

## **Contact**
Author: Yixin Ding
For any questions or collaboration opportunities, feel free to reach out:
📧 Email: yixinding@uchicago.edu
🚀 University of Chicago