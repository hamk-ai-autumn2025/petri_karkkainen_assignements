# Amazon Product Description Enhancer

A Streamlit application that extracts product information from Amazon URLs and generates enhanced product descriptions using AI.

## Features

- **Product Information Extraction**: Extracts product name, price, rating, and description from Amazon product pages
- **AI-Powered Enhancement**: Uses Hugging Face's text generation model to create compelling product descriptions
- **Multi-Region Support**: Works with various Amazon domains (e.g., .com, .co.uk, .de, .fr, .es, .it, .ca, .au, .in, .jp, .cn, .nl, .sg, .mx, .br, .ae)
- **JSON Output**: Exports product data in structured JSON format
- **User-Friendly Interface**: Clean, intuitive Streamlit interface

## Prerequisites

- Python 3.7 or higher
- Streamlit
- Requests
- BeautifulSoup4
- Hugging Face API key (optional, for AI enhancement)

## Installation

1. Clone the repository or download the script:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install streamlit requests beautifulsoup4
   ```

4. If you want to use the Hugging Face API for enhanced descriptions:
   - Sign up for a [Hugging Face account](https://huggingface.co/)
   - Get your API token from [Hugging Face Settings](https://huggingface.co/settings/tokens)
   - Set the API token as an environment variable:
     ```bash
     export HF_API_KEY="your_hugging_face_api_key_here"
     ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run assignement_15.py
   ```

2. Open your web browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`).

3. Enter an Amazon product URL in the input field.

4. Click the "✨ Enhance Product Description" button.

5. View the extracted product information and the AI-enhanced description.

6. Download the JSON output if needed.

## How It Works

1. **Input**: The user provides an Amazon product URL.
2. **Scraping**: The application uses `requests` and `BeautifulSoup` to fetch and parse the HTML of the product page.
3. **Extraction**: It extracts product details (name, price, rating, description) by looking for specific HTML elements and JSON data within script tags.
4. **Enhancement**: If a Hugging Face API key is provided, it uses the API to generate an enhanced description based on the extracted information. Otherwise, it uses a local enhancement method.
5. **Display**: The original and enhanced product information is displayed in the Streamlit interface.
6. **Export**: Users can download the product data as a JSON file.

## Limitations

- Amazon's dynamic content loading can make scraping challenging, and results may vary depending on the specific product page structure.
- Amazon may block requests from automated tools. Use responsibly and respect their robots.txt and terms of service.
- The application currently only supports Amazon sites.
- The fallback enhancement method (without Hugging Face API) is less sophisticated than the AI-powered one.

## Troubleshooting

- **"Not found" for product details**: This usually means the specific product page structure wasn't recognized by the scraping logic. The app handles dynamic content but some pages may still be problematic.
- **Enhanced description shows prompt text**: This indicates the Hugging Face API call failed or the fallback method was used with incomplete data. Check your API key if you have one.
- **Script errors**: Ensure all dependencies are installed correctly and the Python version is compatible.

## Files

- `assignement_15.py`: The main Streamlit application script
- `README.md`: This file

## Contributing

Contributions are welcome! Feel free to fork the repository, make changes, and submit pull requests.
