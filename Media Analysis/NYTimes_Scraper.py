'''
Author: Yixin Ding

This script retrieves New York Times articles using the NYT Archive API, then filters for China-related content using keyword matching. 
It implements a dual-approach scraping strategy: first attempting to fetch article text via direct HTTP requests with browser cookies, 
then falling back to a headless Selenium browser when needed. The script features intelligent rate limiting, verification handling, and exponential backoff for retries. 
It processes articles month by month, saving both the complete dataset and a filtered subset of China-related articles with their full text.

Reference: 
https://developer.nytimes.com/docs/archive-product/1/overview;
https://selenium-python.readthedocs.io/;
https://pypi.org/project/browser-cookie3/;
https://pypi.org/project/fake-useragent/

AI used only for code comments and modifications.
'''
import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import re
import browser_cookie3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent  # For rotating user agents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set up API configuration
API_KEY = 'kpnXggi7Pvf68T5NA4e9EGfE2Dsiz0Wq'
ARCHIVE_BASE_URL = 'https://api.nytimes.com/svc/archive/v1'

# Load NYT cookies from Chrome
nyt_cookies = browser_cookie3.chrome(domain_name='nytimes.com')
NYT_COOKIES = {cookie.name: cookie.value for cookie in nyt_cookies}

# Load China keywords from CSV file
def load_china_keywords(csv_file="combined_china_keywords.csv"):
    """Load and return list of China-related keywords from CSV"""
    df = pd.read_csv(csv_file)
    return df["keyword"].str.lower().tolist()

CHINA_KEYWORDS = load_china_keywords()

# Text normalization function
def normalize_text(text):
    """Convert text to lowercase and strip special characters"""
    if text:
        return ' '.join(re.findall(r'\b\w+\b', text.lower())).strip()
    return ''

# Define relevant news desk categories
relevant_news_desks = {
    "Foreign", "Politics", "Opinion", "World", "National", "Washington",
    "Business", "Technology", "Science", "Climate", "Investigative",
    "Editorial", "Upshot", "SundayBusiness", "Real Estate", "Podcasts",
    "Briefing", "Photos", "Business Day", "NYTNow", "Election Analytics"
}

# Filter articles by news desk
def is_relevant_article(article):
    """Check if article belongs to relevant news desk categories"""
    news_desk = article.get("news_desk", "").strip()
    return not news_desk or news_desk in relevant_news_desks

# Check for China-related content
def is_china_related(article):
    """Determine if article is China-related based on keywords"""
    headline = article.get("headline", {}).get("main", "")
    abstract = article.get("abstract", "")
    
    normalized_headline = normalize_text(headline)
    normalized_abstract = normalize_text(abstract)
    
    headline_match = any(re.search(rf'\b{re.escape(keyword)}\b', normalized_headline) for keyword in CHINA_KEYWORDS)
    abstract_match = any(re.search(rf'\b{re.escape(keyword)}\b', normalized_abstract) for keyword in CHINA_KEYWORDS)
    
    return headline_match or abstract_match

# CRUCIAL PART 1: Enhanced WebDriver Initialization with Headless Mode
def init_headless_selenium():
    """
    Initialize Chrome WebDriver with headless mode and optimized settings
    This is crucial for running browser in background without GUI
    """
    options = Options()
    # CRUCIAL: Headless mode configuration
    options.add_argument("--headless=new")  # Modern headless mode
    
    # EFFICIENCY IMPROVEMENTS: Browser optimizations
    options.add_argument("--disable-gpu")  # Reduces resource usage
    options.add_argument("--no-sandbox")  # Bypasses OS security model
    options.add_argument("--disable-dev-shm-usage")  # Handles memory better
    options.add_argument("--disable-infobars")  # Removes info bars
    options.add_argument("--disable-extensions")  # Disables extensions
    options.add_argument("--disable-notifications")  # Disables notifications
    
    # CRUCIAL: Anti-detection measures
    options.add_argument(f"user-agent={UserAgent().random}" + "at yixinding@uchicago.edu for research purpose")
    options.add_argument("--window-size=1920,1080")
    
    # EFFICIENCY: Prefs to disable images and JavaScript (optional)
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Disable images
        "javascript.enabled": False  # Disable JavaScript if not needed
    }
    options.add_experimental_option("prefs", prefs)
    
    return webdriver.Chrome(options=options)

# CRUCIAL PART 2: Enhanced scraping with intelligent wait and retry logic
def scrape_full_text(url, document_type, max_retries=3):
    """
    Enhanced scraping function with retry mechanism and intelligent waiting
    """
    if document_type == "multimedia":
        return None

    # First try with requests for efficiency
    try:
        response = requests.get(
            url, 
            headers={"User-Agent": UserAgent().random}, 
            cookies=NYT_COOKIES, 
            timeout=10
        )
        
        if response.status_code == 200 and "verify you're not a robot" not in response.text.lower():
            return extract_text_from_response(response.content)
    except Exception as e:
        logging.warning(f"Initial request failed, switching to headless: {e}")

    # CRUCIAL PART 3: Headless browser fallback with retry logic
    for attempt in range(max_retries):
        driver = None
        try:
            driver = init_headless_selenium()
            
            # EFFICIENCY: Set page load timeout
            driver.set_page_load_timeout(20)
            
            # CRUCIAL: Intelligent wait for page load
            driver.get(url)
            
            # EFFICIENCY: Smart waiting for content
            wait = WebDriverWait(driver, 10)
            paragraphs = wait.until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "p"))
            )
            
            # CRUCIAL: Handle verification
            if "verify you're not a robot" in driver.page_source.lower():
                logging.warning(f"Verification detected on attempt {attempt + 1}")
                handle_verification(driver)
            
            # EFFICIENCY: Extract text with improved parsing
            full_text = extract_text_from_driver(driver)
            
            if is_valid_text(full_text):
                return full_text
                
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
            
        finally:
            if driver:
                driver.quit()

# EFFICIENCY: Helper functions for better code organization and reusability
def extract_text_from_response(content):
    """Efficiently extract text from response content"""
    soup = BeautifulSoup(content, "html.parser")
    paragraphs = soup.find_all("p")
    return " ".join(p.get_text().strip() for p in paragraphs if p.text.strip())

def extract_text_from_driver(driver):
    """Extract text from webdriver with improved efficiency"""
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    return " ".join(p.text for p in paragraphs if p.text.strip())

def is_valid_text(text):
    """Validate extracted text"""
    return text and len(text.split()) >= 10

def handle_verification(driver):
    """Handle verification process if needed"""
    logging.warning("Verification handling...")
    time.sleep(5)  # Allow time for verification process

# Fetch articles from NYT API
def fetch_articles_with_archive(year, month):
    """Fetch articles from NYT Archive API with rate limiting"""
    logging.info(f"Fetching articles for {year}-{month:02d}...")
    url = f"{ARCHIVE_BASE_URL}/{year}/{month}.json"
    params = {'api-key': API_KEY}
    
    retries = 0
    max_retries = 10
    base_delay = 2
    
    while retries < max_retries:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()['response']['docs']
        elif response.status_code == 429:
            wait_time = min(base_delay * (2 ** retries), 60)
            logging.warning(f"Rate limit exceeded for {year}-{month:02d}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
        else:
            logging.error(f"Error {response.status_code} for {year}-{month:02d}")
            return []
    
    logging.error(f"Failed to fetch articles for {year}-{month:02d} after {max_retries} retries.")
    return []

# Parse initial article data
def parse_articles_first_pass(articles):
    """Extract basic information from articles without full text"""
    parsed_articles = []
    seen_urls = set()

    for article in articles:
        if is_relevant_article(article):
            web_url = article.get("web_url", "")
            if web_url in seen_urls:
                continue
            seen_urls.add(web_url)

            document_type = article.get("document_type", "").lower()
            news_desk = article.get("news_desk", "").strip() or "Unknown"

            article_info = {
                'headline': article.get("headline", {}).get("main", None),
                'pub_date': article.get('pub_date', None),
                'web_url': web_url,
                'news_desk': news_desk,
                'document_type': document_type,
                'snippet': article.get('snippet', None),
                'abstract': article.get('abstract', None),
                'lead_paragraph': article.get('lead_paragraph', None),
                'is_china_related': is_china_related(article)
            }
            parsed_articles.append(article_info)

    return pd.DataFrame(parsed_articles)

# Process China-related articles
def add_full_text_to_china_articles(df):
    """Fetch full text for China-related articles"""
    logging.info("Fetching full text for China-related articles...")
    
    china_df = df[df['is_china_related'] == True].copy()
    
    total = len(china_df)
    for i, (idx, row) in enumerate(china_df.iterrows()):
        date = row['pub_date'].split('T')[0] if row['pub_date'] else 'Unknown'
        full_text = scrape_full_text(row['web_url'], row['document_type'])
        china_df.at[idx, 'full_text'] = full_text
        
        if full_text:
            logging.info(f"Article {i+1}/{total} [{date}]: Success ({len(full_text.split())} words)")
        else:
            logging.warning(f"Article {i+1}/{total} [{date}]: Failed")
        
        time.sleep(1)
    
    return china_df

# Main execution function
def main(year):
    """Main function to fetch and process NYT articles"""
    all_articles = []
    
    for i, month in enumerate(range(1, 13)):
        month_articles = fetch_articles_with_archive(year, month)
        all_articles.extend(month_articles)
        
        if (i + 1) % 3 == 0:
            logging.info("Pausing for 10 seconds to prevent hitting the NYT API rate limit...")
            time.sleep(10)
    
    if all_articles:
        logging.info("Parsing all articles (without full text)...")
        all_articles_df = parse_articles_first_pass(all_articles)
        
        all_articles_df.to_csv(f'all_article_nyt{year}.csv', index=False)
        logging.info(f"All articles saved to all_article_nyt{year}.csv. Total: {len(all_articles_df)}")
        
        china_count = all_articles_df['is_china_related'].sum()
        logging.info(f"Found {china_count} China-related articles. Fetching full text...")
        
        if china_count > 0:
            china_articles_df = add_full_text_to_china_articles(all_articles_df)
            
            china_articles_df.to_csv(f'China_article_nyt{year}.csv', index=False)
            logging.info(f"China-related articles saved to China_article_nyt{year}.csv. Total: {len(china_articles_df)}")
    else:
        logging.warning("No articles retrieved.")

if __name__ == "__main__":
    main(2024)
