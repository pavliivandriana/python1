import time
import json
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from collections import Counter


def collect_news(url):
    options = Options()
    options.headless = True  
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)  
        
        headlines = driver.find_elements(By.CSS_SELECTOR, "h2")
        news_titles = [headline.text for headline in headlines if headline.text != '']
        
        if not news_titles:
            print("No news found on the page.")
        return news_titles

    except Exception as e:
        print(f"Error while collecting news: {e}")
        return []
    finally:
        driver.quit()

def save_news_to_json(news_titles, filename="news.json"):
    if not news_titles:
        print("No news to save.")
        return
    
    if os.path.exists(filename):
        choice = input(f"The file {filename} already exists. Overwrite (O) or append (A)? ").strip().lower()
        if choice == 'o':
            mode = 'w'
        elif choice == 'a':
            mode = 'a'
        else:
            print("Invalid choice!")
            return
    else:
        mode = 'w'
    
    with open(filename, mode, encoding="utf-8") as f:
        json.dump(news_titles, f, ensure_ascii=False, indent=4)
    print(f"News saved to file {filename}.")

def load_news_from_json(filename="news.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            news_titles = json.load(f)
        return pd.DataFrame(news_titles, columns=["Title"])
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
        return pd.DataFrame(columns=["Title"])

def analyze_keywords(news_df, keywords):
    word_count = Counter()
    
    for title in news_df['Title']:
        for word in keywords:
            if word.lower() in title.lower():
                word_count[word] += 1
    
    return word_count

def visualize_keyword_frequency(word_count):
    if not word_count:
        print("No data to visualize.")
        return

    words = list(word_count.keys())
    counts = list(word_count.values())
    
    plt.bar(words, counts, color='skyblue')
    plt.xlabel("Keywords")
    plt.ylabel("Frequency")
    plt.title("Keyword Frequency in News")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def export_to_yaml(word_count, filename="keywords_analysis.yaml"):
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(word_count, f, allow_unicode=True)
    print(f"Results saved to file {filename}.")

def news_generator(news_df):
    for index, row in news_df.iterrows():
        yield row['Title']

if __name__ == "__main__":
    url = "https://www.bbc.com/news" 
    keywords = ["war", "economy", "technology", "health", "politics"] 

    news_titles = collect_news(url)
    
    save_news_to_json(news_titles)
    
    news_df = load_news_from_json()
    
    word_count = analyze_keywords(news_df, keywords)
    
    visualize_keyword_frequency(word_count)

    export_to_yaml(word_count)
    
    generator = news_generator(news_df)
    for news in generator:
        print(news)
