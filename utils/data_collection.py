# utils/data_collection.py

import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news_articles(stock_symbol, start_date, end_date, page_size=50):
    url = "https://newsapi.org/v2/everything"
    headers = {"Authorization": NEWS_API_KEY}

    params = {
        "q": stock_symbol,
        "from": start_date,
        "to": end_date,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"NewsAPI Error: {response.status_code} - {response.text}")

    articles = response.json().get("articles", [])

    data = []
    for article in articles:
        data.append({
            "title": article.get("title"),
            "publishedAt": article.get("publishedAt", "")[:10],
            "content": article.get("content") or article.get("description"),
            "url": article["url"]
        })

    return pd.DataFrame(data)
