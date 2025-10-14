# News Search & Summarizer

A Streamlit web application that searches for the latest news articles, filters by political bias and time period, and provides AI-powered summaries.

## Features

- Search news articles by keyword or category
- Filter by time period (today, yesterday, last week, etc.) or custom date range
- Adjust political bias (left, neutral, right) using a slider
- View article summaries with source links
- Access search history with one-click recall
- Fallback summarization when AI model fails

## Requirements

- Python 3.8+
- Serper API key (free tier available at [serper.dev](https://serper.dev))

## Installation

1. Clone or download the project files
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install streamlit requests transformers torch beautifulsoup4
   ```

## Setup

1. Obtain a Serper API key from [serper.dev](https://serper.dev)
2. Set your API key as an environment variable:
   - **Linux/macOS:**
     ```bash
     export SERPER_API_KEY="your_api_key_here"
     ```
   - **Windows (Command Prompt):**
     ```cmd
     set SERPER_API_KEY=your_api_key_here
     ```
   - **Windows (PowerShell):**
     ```powershell
     $env:SERPER_API_KEY="your_api_key_here"
     ```
   - **Alternative:**
     Create a `.env` file in your project directory with:
     ```
     SERPER_API_KEY=your_api_key_here
     ```
     Then install `python-dotenv`: `pip install python-dotenv` and add `from dotenv import load_dotenv; load_dotenv()` to the top of the script.

## Usage

1. Run the application:
   ```bash
   streamlit run assignement_14.py
   ```

2. The app will open in your browser at `http://localhost:8501`

3. Use the sidebar to configure your search:
   - Enter a search term (e.g., "technology", "politics")
   - Select a time period or specify custom dates
   - Adjust the political bias slider (-100 for left, 0 for neutral, 100 for right)

4. Click "Search & Summarize" to run your query

5. View results in the main panel:
   - Expandable articles with source, date, and content preview
   - Direct links to source articles
   - AI-generated summary of all results

6. Access previous searches from the "Search History" section in the sidebar

## Notes

- The application uses the Hugging Face BART model for summarization, which runs on CPU
- First-time execution will download the model (~1.6GB)
- If summarization fails, a fallback summary will be generated
- VPNs may interfere with search results; disable if needed
- Free Serper API tier allows 2,500 calls/month

## Troubleshooting

- If you see "No news articles found", try broadening your search term or time range
- If CUDA errors occur, ensure environment variables are set correctly
- For slow performance, ensure you have a stable internet connection
- If the app crashes, check your API key validity in Serper dashboard
