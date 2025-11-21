**Note: This folder only includes two code samples from this project to help reviewers learn about our workflow quickly.**

---

# The Impact of Media Coverage on Candidate Favorability: A Custom-Built Dictionary Approach to China-Related News in the 2024 U.S. Presidential Election

## Project Overview
This project investigates how media coverage related to China during the 2024 U.S. presidential election influenced candidate favorability. We analyze media content from **Fox News (right-leaning)** and **The New York Times (left-leaning)**, examining both the **intensity** (frequency and ratio of China-related news) and **framing** (sentiment analysis). Additionally, we explore how economic factors (inflation, unemployment, and consumption growth) interact with media coverage to shape public perception.

### **Key Research Questions**
1. How does media coverage related to China impact candidate favorability?
2. Does sentiment framing in China-related news differ across partisan media?
3. What role do economic factors play in mediating media influence?

## **Methodology**
- **Data Collection**: Scraped ~22,000 articles from NYT and ~24,600 from Fox News using APIs and custom web scrapers.
- **Filtering**: Used a predefined dictionary of China-related keywords to identify relevant articles.
- **Sentiment Analysis**: Applied **TextBlob, VADER, and BERT** models to assess sentiment polarity.
- **Topic Modeling**: Utilized **LDA (Latent Dirichlet Allocation)** to extract dominant themes in coverage.
- **Regression Analysis**: Modeled the relationship between media sentiment, article volume, economic indicators, and candidate favorability.

## **Main Findings**
### **1. Media Coverage on China Affects Candidate Favorability**
- **Increased media attention on China correlated with shifts in public perception.**
- **Negative sentiment in NYT coverage had a stronger effect on reducing Democratic favorability**, especially among White and Hispanic voters.
- **Fox News’ China-related coverage** had a **stronger negative impact on Democrats** compared to NYT.

### **2. Sentiment Framing and Partisan Influence**
- NYT articles were **more balanced but leaned slightly positive**, whereas **Fox News had a stronger negative bias**.
- Sentiment effects were not uniform—**opinion and business articles** showed the most variation.
- **Higher ratios of China-related articles in both outlets increased political polarization.**

### **3. Economic Factors Amplified Media Effects**
- **Higher unemployment rates and inflation worsened Democratic favorability**, reinforcing negative media sentiment.
- **Consumption growth correlated with increased Republican favorability**, suggesting optimism about economic conditions played a role.
- The interaction of **economic downturns and media negativity** particularly impacted Harris and Biden’s favorability.

## **Significance of the Research**
- **Political Polarization & Information Asymmetry**: Shows how partisan media shapes voter perception.
- **Electoral Decision-Making**: Helps understand how media narratives about foreign policy influence elections.
- **Political Communication**: Examines the interplay between sentiment framing, news volume, and demographic preferences.


## **Repository Structure**  

### **1. Data Cleaning & Wrangling**  
Contains raw datasets, scripts for handling missing values, and aggregated datasets for analysis.  
- **Raw Data** – Includes CSV and Excel files with scraped news articles and political favorability data.  
- **Refill & Check Missing** – Jupyter notebooks for handling missing data and aggregating weekly datasets.  

### **2. Data Collection**  
Scripts for scraping news data from NYT and Fox News.  
#### **Fox News Scraper & Filter**  
- `foxnews_scraper_all.py` – Main script for scraping Fox News articles.  
- `foxnews_filter_scrape_fulltext.py` – Filters and scrapes full text from Fox News.  
- `combined_china_keywords.csv` – Keywords used to filter China-related articles.  
- **Data Files:**  
  - `all_article_foxnews2024.csv` – All scraped articles from Fox News.  
  - `China_article_foxnews2024.csv` – Filtered China-related articles from Fox News.  
  - `all_article_foxnews2024_cleaned.csv` – Cleaned dataset for Fox News.  

#### **NY Times Scraper & Filter**  
- `nyt_scraper_v3.py` – Main script for scraping NYT articles.  
- `combined_china_keywords.csv` – Keywords used to filter China-related articles.  
- **Data Files:**  
  - `all_article_nyt2024.csv` – All scraped articles from NYT.  
  - `China_article_nyt2024.csv` – Filtered China-related articles from NYT.  

---

### **3. Descriptive & Regression Analysis**  
Contains cleaned datasets and Jupyter notebooks for sentiment analysis, descriptive statistics, and regression modeling.  
#### **Data Files:**  
- `China_fox_clean.csv`, `China_nyt_clean.csv` – Cleaned datasets for both news sources.  
- `all_fox_week.csv`, `all_nyt_week.csv` – Weekly aggregated datasets.  
- `control_variables_favorability.xlsx` – External control data (e.g., unemployment, CPI).  

#### **Analysis Notebooks:**  
- `Descriptive_Analysis.ipynb` – Summary statistics and exploratory data analysis.  
- `Regression.ipynb` – Main regression analysis to assess media effects on candidate favorability.  

---

### **4. Text Analysis**  
Includes sentiment analysis, topic modeling, and word cloud visualizations.  
#### **Fox News Analysis**  
- `Bert.ipynb`, `Textblob.ipynb`, `Vedar.ipynb` – Sentiment analysis using different NLP models.  
- `FOX descriptive.ipynb` – Visualization of sentiment and media trends.  
- **Data Files:**  
  - `Chinafox_clean.csv`, `Chinafox_sentiment.csv` – Processed datasets for Fox News.  

#### **NYT Data Analysis**  
- `Bert.ipynb`, `Text Blob.ipynb`, `Vedar.ipynb` – Sentiment analysis models applied to NYT data.  
- **Data Files:**  
  - `China_article_nyt2024_sentiment.csv` – Sentiment analysis results for NYT.  

#### **Topic Modeling & WordClouds**  
- `LDA & WordCloud_FoxNews.py`, `LDA & WordCloud_NYTimes.py` – Topic modeling and visualization scripts.  
- **Generated Outputs:**  
  - `wordcloud_all_topics.png`, `topic_distribution.png` – Word clouds and topic distributions for news coverage.  

---

## **How to Run the Code**  

### **1. Set Up Environment & Install Dependencies**  
Ensure you have Python 3.8+ installed. Install required libraries using:  
```bash
pip install -r requirements.txt
```

### **2. Scrape Data (Optional, if using new data)**  
Run the scraping scripts to collect and filter news articles:  
```bash
python foxnews_scraper_all.py
python nyt_scraper_v3.py
```
Alternatively, use the pre-scraped data in the `data_collection` folder.

### **3. Preprocess Data**  
Handle missing values and aggregate weekly datasets:  
```bash
jupyter notebook Data_aggregation_weekly.ipynb
```

### **4. Perform Sentiment & Topic Analysis**  
Open and run Jupyter notebooks for sentiment analysis and NLP modeling:  
```bash
jupyter notebook Bert.ipynb
jupyter notebook Textblob.ipynb
jupyter notebook Vedar.ipynb
```

### **5. Run Regression Analysis**  
Use the cleaned and sentiment-processed data for regression modeling:  
```bash
jupyter notebook Regression.ipynb
```


## Data Sources
- **News Data**: Scraped from [The New York Times](https://www.nytimes.com/) and [Fox News](https://www.foxnews.com/).
- **Favorability Data**: [YouGov](https://today.yougov.com/).
- **Economic Data**: [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/).

---

## Required Libraries
See `requirements.txt` for a full list of dependencies.

---

## Group Contributions
- **Yixin Ding**: Topic Modeling & WordCloud, Data Collection(Scraper),Data Cleaning 
- **Jiahang Luo**: Regression functions and analysis,Data cleaning,Sentiment Analysis.
- **Pengrui Su**: Data collection(Download data),Data cleaning,data discription,Regression.

---

## Resources
- **In-class Presentation Slides**: https://github.com/macs30112-winter25/final-project-super-legend-decoders/blob/main/in_class_slides.pdf
- **Updated Presentation Slides**: https://github.com/macs30112-winter25/final-project-super-legend-decoders/blob/4313e08cfc455c3aaef937f9ab27d99ff427edc1/Final%20slide.pdf
- **Project Video**:https://drive.google.com/file/d/1A5JgNpgSsFmpb59hlSTfUjk42rezUSUG/view?usp=share_link
---
