import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from transformers import pipeline
import torch
from typing import List
import re
import os

# Initialize session state
if "results" not in st.session_state:
    st.session_state.results = []
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "search_error" not in st.session_state:
    st.session_state.search_error = ""
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# App title
st.title("News Search & Summarizer")
st.markdown("Search and summarize news articles with political bias filtering")

# Sidebar inputs
with st.sidebar:
    st.header("Search Parameters")
    query = st.text_input("Enter search term or category:", value="technology")

    # Time period selection
    time_period = st.selectbox(
        "Time period:",
        ["Any time", "Today", "Yesterday", "This week", "This month", "This year"],
        index=0
    )

    # Custom date range
    use_custom_dates = st.checkbox("Use custom date range")
    start_date = None
    end_date = None
    if use_custom_dates:
        start_date = st.date_input("Start date", value=datetime.now() - timedelta(days=7))
        end_date = st.date_input("End date", value=datetime.now())

    # Political bias slider
    political_bias = st.slider(
        "Political bias (left=-100, neutral=0, right=100):",
        min_value=-100,
        max_value=100,
        value=0,
        step=10
    )

    # Search history
    st.header("Search History")
    for i, search in enumerate(st.session_state.search_history):
        if st.button(f"{search['query']} ({search['date']})", key=f"history_{i}"):
            st.session_state.results = search['results']
            st.session_state.summary = search['summary']
            st.session_state.search_error = ""
            query = search['query']
            time_period = search['time_period']
            political_bias = search['bias']

# Main content area
if st.button("Search & Summarize"):
    # Reset previous results and errors
    st.session_state.search_error = ""

    # Get API keys from environment variables
    serper_api_key = os.getenv("SERPER_API_KEY")

    if not serper_api_key:
        st.session_state.search_error = "Please set your SERPER_API_KEY environment variable"
        st.error(st.session_state.search_error)
        st.stop()
    elif not query:
        st.session_state.search_error = "Please enter a search query"
        st.error(st.session_state.search_error)
        st.stop()
    else:
        with st.spinner("Searching and summarizing news..."):
            # Build date filters
            date_filter = ""
            if use_custom_dates:
                if start_date and end_date:
                    date_filter = f"cdr:1,cd_min:{start_date.strftime('%m/%d/%Y')},cd_max:{end_date.strftime('%m/%d/%Y')}"
            else:
                period_map = {
                    "Today": "d",
                    "Yesterday": "d",
                    "This week": "w",
                    "This month": "m",
                    "This year": "y"
                }
                if time_period != "Any time":
                    tbs_val = f"qdr:{period_map[time_period]}"
                    if time_period == "Yesterday":
                        tbs_val = "cdr:1,cd_min:yesterday,cd_max:yesterday"
                    date_filter = tbs_val

            # Build search query with bias indicators
            bias_term = ""
            if political_bias < -30:
                bias_term = " (liberal OR left OR progressive)"
            elif political_bias > 30:
                bias_term = " (conservative OR right OR libertarian)"

            search_query = f"{query}{bias_term}"

            # Perform Google News search via Serper
            headers = {
                'X-API-KEY': serper_api_key,
                'Content-Type': 'application/json'
            }

            # Use the news endpoint directly
            search_payload = {
                "q": search_query,
                "gl": "US",  # Geographic location
                "hl": "en",  # Language
                "num": 20,   # Number of results
            }

            if date_filter:
                search_payload["tbs"] = date_filter

            try:
                st.info(f"Searching for: {search_query}")
                st.info(f"Date filter: {date_filter}")

                # Use the news-specific endpoint
                search_response = requests.post(
                    'https://google.serper.dev/news',
                    headers=headers,
                    data=json.dumps(search_payload)
                )

                if search_response.status_code != 200:
                    st.session_state.search_error = f"Serper API error: {search_response.status_code} - {search_response.text}"
                    st.error(st.session_state.search_error)
                    st.stop()

                search_data = search_response.json()
                st.info(f"API Response: {json.dumps(search_data, indent=2)[:500]}...")  # First 500 chars

                news_results = search_data.get("news", [])

                if not news_results:
                    st.session_state.search_error = "No news articles found for your query. This could be due to:\n- Restrictive search parameters\n- Serper API quota limits\n- Invalid API key\n- Query too specific"
                    st.warning(st.session_state.search_error)
                    st.stop()

                st.info(f"Found {len(news_results)} articles")

                # Extract article content
                articles = []
                for item in news_results[:10]:  # Limit to 10 articles
                    try:
                        article_response = requests.get(item["link"], timeout=10)
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(article_response.content, "html.parser")

                        # Extract text content (simplified approach)
                        paragraphs = soup.find_all('p')
                        content = " ".join([p.get_text() for p in paragraphs[:10]])  # First 10 paragraphs
                        content = re.sub(r'\s+', ' ', content)[:2000]  # Limit length and clean whitespace

                        articles.append({
                            "title": item["title"],
                            "snippet": item["snippet"],
                            "date": item.get("date", "Unknown"),
                            "source": item["source"],
                            "content": content,
                            "link": item["link"]  # Store the link
                        })
                    except Exception as e:
                        # Fallback to snippet if content extraction fails
                        articles.append({
                            "title": item["title"],
                            "snippet": item["snippet"],
                            "date": item.get("date", "Unknown"),
                            "source": item["source"],
                            "content": item["snippet"],
                            "link": item["link"]  # Store the link
                        })

                # Prepare content for summarization
                all_content = "\n\n".join([
                    f"Title: {a['title']}\nSource: {a['source']}\nDate: {a['date']}\nContent: {a['content'][:500]}"
                    for a in articles
                ])

                # Sanitize content to prevent index errors
                all_content = all_content.replace('\x00', '')  # Remove null bytes
                all_content = all_content.replace('\ufffd', '')  # Remove replacement characters

                # Initialize summarization pipeline with CPU only
                try:
                    # Set environment to use CPU only
                    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
                    torch.cuda.is_available = lambda: False

                    summarizer = pipeline(
                        "summarization",
                        model="facebook/bart-large-cnn",
                        device='cpu'  # Explicitly use CPU
                    )

                    # Summarize content with error handling
                    summary_result = summarizer(
                        all_content,
                        max_length=200,
                        min_length=50,
                        do_sample=False
                    )

                    st.session_state.summary = summary_result[0]['summary_text']
                except Exception as e:
                    # Fallback if summarization fails
                    st.session_state.summary = f"Summarization failed due to: {str(e)}. Showing key points:\n\n"
                    for i, article in enumerate(articles[:3]):  # Show first 3 articles
                        st.session_state.summary += f"{i+1}. {article['title']} - {article['snippet']}\n\n"

                st.session_state.results = articles

                # Add to search history (limit to 5)
                search_entry = {
                    "query": query,
                    "time_period": time_period,
                    "bias": political_bias,
                    "date": datetime.now().strftime("%m/%d %H:%M"),
                    "results": articles,
                    "summary": st.session_state.summary
                }
                st.session_state.search_history.insert(0, search_entry)
                st.session_state.search_history = st.session_state.search_history[:5]  # Keep only last 5

            except Exception as e:
                st.session_state.search_error = f"An error occurred: {str(e)}"
                st.error(st.session_state.search_error)
                import traceback
                st.error(f"Traceback: {traceback.format_exc()}")

# Display results only if there are no errors
if st.session_state.search_error:
    st.error(st.session_state.search_error)
elif st.session_state.results:
    st.subheader("Search Results")
    for i, article in enumerate(st.session_state.results):
        with st.expander(f"{article['title']} ({article['source']}) - {article['date']}"):
            st.write(f"**Source:** {article['source']}")
            st.write(f"**Date:** {article['date']}")
            st.write(f"**Summary:** {article['snippet']}")
            st.write(f"**Content Preview:** {article['content'][:300]}...")
            st.write(f"**[Read full article]({article['link']})**")  # Add link to source

    st.subheader("Summary")
    st.write(st.session_state.summary)

# Add disclaimer
st.markdown("---")
st.caption("Note: This application uses Google Serper API for news search and Hugging Face BART model for summarization. Political bias is approximated through keyword inclusion and source selection. Always verify important information from primary sources.")
