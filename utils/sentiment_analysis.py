# utils/sentiment_analysis.py

import pandas as pd
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(df):
    if "content" not in df.columns:
        raise ValueError("Missing 'content' column for sentiment analysis")

    sentiments = []
    for text in df["content"]:
        if pd.isna(text):
            sentiments.append({"neg": 0, "neu": 0, "pos": 0, "compound": 0})
            continue
        score = analyzer.polarity_scores(text)
        sentiments.append(score)

    sentiment_df = pd.DataFrame(sentiments)
    df = pd.concat([df, sentiment_df], axis=1)

    # Optional: Add label
    df["sentiment"] = df["compound"].apply(lambda x: "positive" if x > 0.05 else "negative" if x < -0.05 else "neutral")

    return df
