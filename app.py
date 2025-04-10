import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_collection import fetch_news_articles
from utils.sentiment_analysis import analyze_sentiment
from utils.stock_data import fetch_stock_prices
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Stock Sentiment Analyzer", layout="wide")
st.title("📊 Stock Sentiment Analyzer")
st.markdown("Analyze sentiment from news articles and track how it aligns with stock price trends.")

# Sidebar Input
st.sidebar.header("Select Stock")
stock_symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL)", "AAPL")

st.sidebar.header("Date Range")
start_date = st.sidebar.date_input("Start Date", datetime(2025, 4, 1))
end_date = st.sidebar.date_input("End Date", datetime.now())

if st.sidebar.button("Fetch News"):
    try:
        st.info("Fetching news articles...")
        news_df = fetch_news_articles(stock_symbol, start_date, end_date)

        if not news_df.empty:
            st.success("News articles fetched successfully.")
            st.subheader("📰 News Articles")
            st.dataframe(news_df)

            # Sentiment Analysis
            st.info("Performing sentiment analysis...")
            analyzed_df = analyze_sentiment(news_df)
            st.subheader("📊 Sentiment Analysis Results")
            st.dataframe(analyzed_df[["title", "publishedAt", "sentiment", "compound"]])

            # Group by date for trend
            sentiment_over_time = analyzed_df.groupby("publishedAt")["compound"].mean().reset_index()
            sentiment_over_time["publishedAt"] = pd.to_datetime(sentiment_over_time["publishedAt"]).dt.date
            sentiment_over_time.rename(columns={"publishedAt": "Date", "compound": "Average Sentiment"}, inplace=True)

            # Fetch Stock Prices
            st.info("Fetching stock prices...")
            stock_df = fetch_stock_prices(stock_symbol, start_date, end_date)

            # Merge
            merged_df = pd.merge(sentiment_over_time, stock_df, on="Date", how="inner")

            # Line Chart
            st.subheader("📈 Sentiment vs. Stock Price")
            fig = px.line(merged_df, x="Date", y=["Average Sentiment", "Close"],
                          labels={"value": "Score", "variable": "Metric"},
                          title=f"{stock_symbol} - Sentiment and Stock Price Trend")

            # Custom colors for sentiment values
            fig.update_traces(line=dict(color='green') if "Average Sentiment" else dict(color='blue'))
            st.plotly_chart(fig, use_container_width=True)

            # Bar Chart: Sentiment Count by Date with Custom Colors
            sentiment_color_map = {"positive": "green", "neutral": "blue", "negative": "red"}

            daily_sentiment_counts = analyzed_df.groupby(["publishedAt", "sentiment"]).size().reset_index(name="count")
            daily_sentiment_counts["publishedAt"] = pd.to_datetime(daily_sentiment_counts["publishedAt"]).dt.date
            daily_sentiment_counts.rename(columns={"publishedAt": "Date"}, inplace=True)

            st.subheader("📊 Daily Sentiment Distribution")
            bar_fig = px.bar(
                daily_sentiment_counts,
                x="Date",
                y="count",
                color="sentiment",
                title="Daily Sentiment Breakdown",
                labels={"count": "Article Count", "sentiment": "Sentiment"},
                barmode="stack",
                color_discrete_map=sentiment_color_map  # Use custom color mapping for sentiments
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            # Pie Chart: Overall Sentiment with Custom Colors
            overall_sentiment = analyzed_df["sentiment"].value_counts().reset_index()
            overall_sentiment.columns = ["sentiment", "count"]

            st.subheader("🥧 Overall Sentiment Summary")
            pie_fig = px.pie(
                overall_sentiment,
                names="sentiment",
                values="count",
                title="Overall Sentiment Distribution",
                color="sentiment",  # Color by sentiment
                color_discrete_map=sentiment_color_map  # Custom color mapping
            )
            st.plotly_chart(pie_fig, use_container_width=True)

        else:
            st.warning("No news articles found for the selected range.")

    except Exception as e:
        st.error(f"Error: {e}")
