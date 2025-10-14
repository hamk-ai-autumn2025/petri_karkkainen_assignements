import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urlparse
import os

# Set page config
st.set_page_config(
    page_title="Amazon Product Description Enhancer",
    page_icon="🛒",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .product-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .original-desc {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #000 !important;
    }
    .enhanced-desc {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
        color: #000 !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    /* Ensure text is readable in all elements */
    .original-desc * {
        color: #000 !important;
    }
    .enhanced-desc * {
        color: #000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header"><h1>🛒 Amazon Product Description Enhancer</h1></div>', unsafe_allow_html=True)

# Supported sites - Only Amazon
SUPPORTED_SITES = [
    "amazon.com", "amazon.co.uk", "amazon.de", "amazon.fr", "amazon.es", "amazon.it",
    "amazon.ca", "amazon.au", "amazon.in", "amazon.jp", "amazon.cn", "amazon.nl",
    "amazon.sg", "amazon.mx", "amazon.br", "amazon.ae"
]

st.info(f"Supported sites: {', '.join(SUPPORTED_SITES)}")

# Initialize session state
if 'product_data' not in st.session_state:
    st.session_state.product_data = None
if 'enhanced_description' not in st.session_state:
    st.session_state.enhanced_description = None

# Function to extract product info from URL
def extract_product_info(url):
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Remove www if present
        if domain.startswith('www.'):
            domain = domain[4:]

        # Check if site is supported
        if not any(supported in domain for supported in SUPPORTED_SITES):
            return {"error": f"Unsupported site: {domain}. Please use one of the supported Amazon sites."}

        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # Get the page content
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Initialize product data with the URL
        product_data = {
            "url": url,
            "name": "",
            "description": "",
            "price": "",
            "rating": ""
        }

        # Extract product information
        product_data.update(extract_amazon(soup, domain))

        return product_data

    except Exception as e:
        return {"error": f"Error extracting product info: {str(e)}"}

# Amazon-specific extraction function
def extract_amazon(soup, domain):
    data = {}

    # Product name - Try multiple selectors
    title_elem = (
        soup.find('span', id='productTitle') or
        soup.find('h1', {'data-testid': 'product-title'}) or
        soup.find('h1', class_='a-size-large') or
        soup.find('h1', class_='a-spacing-small') or
        soup.find('h1', class_='a-spacing-none')
    )
    data['name'] = title_elem.get_text(strip=True) if title_elem else "Not found"

    # PRICE EXTRACTION - Look in script tags for JSON data first
    price = "Not found"
    script_tags = soup.find_all('script', type='text/javascript')

    # Look for price in JSON data within script tags
    for script in script_tags:
        if script.string and ('price' in script.string or 'Price' in script.string):
            # Look for price in JSON format
            price_match = re.search(r'"price"\s*:\s*["\']?([\d.,]+)["\']?', script.string)
            if price_match:
                price_value = price_match.group(1)

                # Look for currency in the same script
                currency_match = re.search(r'"currencyCode"\s*:\s*["\']?([A-Z]{3})["\']?', script.string)
                if currency_match:
                    currency_code = currency_match.group(1)
                    # Map currency codes to symbols
                    currency_map = {
                        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
                        'CAD': 'C$', 'AUD': 'A$', 'INR': '₹', 'CNY': '¥',
                        'MXN': 'Mex$', 'BRL': 'R$', 'SGD': 'S$'
                    }
                    currency_symbol = currency_map.get(currency_code, currency_code)
                    price = f"{currency_symbol}{price_value}"
                    break
                else:
                    price = price_value
                    break

    # If not found in scripts, try visible HTML elements
    if price == "Not found":
        # Look for price in structured data
        price_elem = soup.find('span', class_='a-offscreen')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            # Extract currency and amount
            currency_match = re.search(r'[^\d.,\s]', price_text)
            amount_match = re.search(r'[\d.,]+', price_text)

            currency = currency_match.group() if currency_match else ''
            amount = amount_match.group() if amount_match else price_text

            price = f"{currency}{amount}"

    # If still not found, try other elements
    if price == "Not found":
        price_selectors = [
            'span.a-price-whole',
            'span.apexPriceToPay',
            'span[data-cy="price-recipe"]',
            'span.a-price',
            'span.priceBlockBuyingPriceString'
        ]
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price = price_elem.get_text(strip=True)
                break

    data['price'] = price

    # RATING EXTRACTION - Look in script tags for JSON data first
    rating = "Not found"
    for script in script_tags:
        if script.string:
            # Look for rating in JSON-LD structured data
            rating_match = re.search(r'"ratingValue"\s*:\s*["\']?([\d.]+)["\']?', script.string)
            if rating_match:
                rating = rating_match.group(1)
                break

    # If not found in scripts, try visible HTML elements
    if rating == "Not found":
        rating_elem = soup.find('span', class_='a-icon-alt')
        if rating_elem:
            rating_text = rating_elem.get_text()
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            rating = rating_match.group(1) if rating_match else "Not found"

    data['rating'] = rating

    # DESCRIPTION EXTRACTION - Look for product description in script tags first
    description = "No description available"

    # Try to find description in JSON-LD structured data
    for script in script_tags:
        if script.string and ('description' in script.string.lower() or 'productdescription' in script.string.lower()):
            desc_match = re.search(r'"description"\s*:\s*["\']([^"\']+)["\']', script.string)
            if desc_match:
                description = desc_match.group(1)
                break

    # If not found in scripts, try visible HTML elements
    if description == "No description available":
        # Look for the main product description
        desc_elem = soup.find('div', id='productDescription')
        if desc_elem:
            # Get all text content and clean it
            desc_text = desc_elem.get_text(strip=True)
            # Remove common Amazon metadata that appears in descriptions
            desc_text = re.sub(r'Dispatches fromAmazon.*?Returns.*?Read full return policy', '', desc_text)
            desc_text = re.sub(r'PaymentSecure transaction.*?We don’t share your credit card details', '', desc_text)
            desc_text = re.sub(r'Shipping & Returns.*?Learn more', '', desc_text)
            desc_text = re.sub(r'Amazon.*?Inc.*?All rights reserved', '', desc_text)
            desc_text = re.sub(r'Back to top.*?Get to Know UsCareers.*?Amazon.*?CaresGift a*?Smile', '', desc_text)
            # Remove delivery information
            desc_text = re.sub(r'FREE delivery.*?Details', '', desc_text)
            desc_text = re.sub(r'Get it as soon as.*?Details', '', desc_text)
            desc_text = re.sub(r'Delivered.*?Details', '', desc_text)

            # Limit to 500 characters
            description = desc_text[:500] if len(desc_text) > 500 else desc_text

    # If still no description, try feature bullets
    if description == "No description available":
        feature_bullets = soup.find('div', id='feature-bullets')
        if feature_bullets:
            desc_text = feature_bullets.get_text(strip=True)
            # Remove common Amazon metadata
            desc_text = re.sub(r'Dispatches fromAmazon.*?Returns.*?Read full return policy', '', desc_text)
            desc_text = re.sub(r'PaymentSecure transaction.*?We don’t share your credit card details', '', desc_text)
            desc_text = re.sub(r'Shipping & Returns.*?Learn more', '', desc_text)
            desc_text = re.sub(r'Amazon.*?Inc.*?All rights reserved', '', desc_text)
            # Remove delivery information
            desc_text = re.sub(r'FREE delivery.*?Details', '', desc_text)
            desc_text = re.sub(r'Get it as soon as.*?Details', '', desc_text)
            desc_text = re.sub(r'Delivered.*?Details', '', desc_text)

            description = desc_text[:500] if len(desc_text) > 500 else desc_text

    # If still no description, try other places
    if description == "No description available":
        desc_elems = soup.find_all('div', class_='a-spacing-base')
        for elem in desc_elems:
            elem_text = elem.get_text(strip=True)
            # Check if this element contains actual product info (not Amazon metadata)
            if len(elem_text) > 50 and not any(phrase in elem_text.lower() for phrase in
                ['dispatches from', 'payment', 'secure transaction', 'amazon', 'returns', 'delivery']):
                description = elem_text[:500]
                break

    data['description'] = description

    return data

# Function to enhance description using Hugging Face model
def enhance_description(product_data):
    try:
        # Create prompt for the LLM
        prompt = f"""You are a professional product copywriter. Rewrite the following product description to make it more compelling and persuasive, considering the price and rating (if available).

Product Name: {product_data.get('name', 'N/A')}
Price: {product_data.get('price', 'N/A')}
Rating: {product_data.get('rating', 'N/A')}
Original Description: {product_data.get('description', 'N/A')}

Enhanced Description:"""

        # Use Hugging Face's free inference API with a text generation model
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY', '')}"}

        # If no API key, use a simple enhancement
        if not os.getenv('HF_API_KEY'):
            # Simple enhancement without API
            enhanced = f"🌟 **{product_data.get('name', 'Product')}** 🌟\n\n"
            enhanced += f"**Price:** {product_data.get('price', 'N/A')}\n"
            if product_data.get('rating') and product_data['rating'] != "Not found" and product_data['rating'] != "Not available":
                enhanced += f"**Rating:** ⭐ {product_data.get('rating', 'N/A')}/5\n\n"

            # Add persuasive elements based on price and rating
            desc = product_data.get('description', 'No description available')
            if "Not found" not in desc and "No description" not in desc and len(desc) > 20:
                enhanced += f"**Why you'll love it:**\n{desc}\n\n"

            # Add value proposition
            if product_data.get('price') and "Not found" not in product_data['price']:
                try:
                    # Extract numeric price value
                    price_val = float(re.sub(r'[^\d.]', '', product_data['price']))
                    if price_val < 50:
                        enhanced += "💡 **Great value for money!** This affordable option delivers excellent quality without breaking the bank."
                    elif price_val < 200:
                        enhanced += "💎 **Premium quality at a reasonable price!** You're getting exceptional value with this purchase."
                    else:
                        enhanced += "🏆 **Top-tier product for discerning customers!** This premium item offers unmatched quality and features."
                except:
                    pass

            if product_data.get('rating') and product_data['rating'] != "Not found" and product_data['rating'] != "Not available":
                try:
                    rating_val = float(product_data['rating'])
                    if rating_val >= 4.5:
                        enhanced += "\n\n✅ **Highly rated by customers!** Join thousands of satisfied buyers who love this product."
                    elif rating_val >= 4.0:
                        enhanced += "\n\n👍 **Well-reviewed by customers!** Most buyers are very happy with their purchase."
                except:
                    pass

            enhanced += "\n\n✨ **Don't miss out on this excellent product!** ✨"
            return enhanced

        # If API key is available, use the model
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 300,
                "min_length": 100,
                "do_sample": False
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            # Return just the generated text, not the full prompt
            generated_text = result[0]['summary_text']
            # Remove any parts that look like the original prompt
            if "You are a professional product copywriter" in generated_text:
                # Try to extract just the enhanced description part
                if "Enhanced Description:" in generated_text:
                    parts = generated_text.split("Enhanced Description:")
                    if len(parts) > 1:
                        generated_text = parts[1].strip()
            return generated_text
        else:
            # If API returns error, use fallback
            enhanced = f"🌟 **{product_data.get('name', 'Product')}** 🌟\n\n"
            enhanced += f"**Price:** {product_data.get('price', 'N/A')}\n"
            if product_data.get('rating') and product_data['rating'] != "Not found" and product_data['rating'] != "Not available":
                enhanced += f"**Rating:** ⭐ {product_data.get('rating', 'N/A')}/5\n\n"

            # Add persuasive elements based on price and rating
            desc = product_data.get('description', 'No description available')
            if "Not found" not in desc and "No description" not in desc and len(desc) > 20:
                enhanced += f"**Why you'll love it:**\n{desc}\n\n"

            # Add value proposition
            if product_data.get('price') and "Not found" not in product_data['price']:
                try:
                    # Extract numeric price value
                    price_val = float(re.sub(r'[^\d.]', '', product_data['price']))
                    if price_val < 50:
                        enhanced += "💡 **Great value for money!** This affordable option delivers excellent quality without breaking the bank."
                    elif price_val < 200:
                        enhanced += "💎 **Premium quality at a reasonable price!** You're getting exceptional value with this purchase."
                    else:
                        enhanced += "🏆 **Top-tier product for discerning customers!** This premium item offers unmatched quality and features."
                except:
                    pass

            if product_data.get('rating') and product_data['rating'] != "Not found" and product_data['rating'] != "Not available":
                try:
                    rating_val = float(product_data['rating'])
                    if rating_val >= 4.5:
                        enhanced += "\n\n✅ **Highly rated by customers!** Join thousands of satisfied buyers who love this product."
                    elif rating_val >= 4.0:
                        enhanced += "\n\n👍 **Well-reviewed by customers!** Most buyers are very happy with their purchase."
                except:
                    pass

            enhanced += "\n\n✨ **Don't miss out on this excellent product!** ✨"
            return enhanced

    except Exception as e:
        # Fallback if anything goes wrong
        enhanced = f"🌟 **{product_data.get('name', 'Product')}** 🌟\n\n"
        enhanced += f"**Price:** {product_data.get('price', 'N/A')}\n"
        if product_data.get('rating') and product_data['rating'] != "Not found" and product_data['rating'] != "Not available":
            enhanced += f"**Rating:** ⭐ {product_data.get('rating', 'N/A')}/5\n\n"

        # Add persuasive elements based on price and rating
        desc = product_data.get('description', 'No description available')
        if "Not found" not in desc and "No description" not in desc and len(desc) > 20:
            enhanced += f"**Why you'll love it:**\n{desc}\n\n"

        # Add value proposition
        if product_data.get('price') and "Not found" not in product_data['price']:
            try:
                # Extract numeric price value
                price_val = float(re.sub(r'[^\d.]', '', product_data['price']))
                if price_val < 50:
                    enhanced += "💡 **Great value for money!** This affordable option delivers excellent quality without breaking the bank."
                elif price_val < 200:
                    enhanced += "💎 **Premium quality at a reasonable price!** You're getting exceptional value with this purchase."
                else:
                    enhanced += "🏆 **Top-tier product for discerning customers!** This premium item offers unmatched quality and features."
            except:
                pass

        if product_data.get('rating') and product_data['rating'] != "Not found" and product_data['rating'] != "Not available":
            try:
                rating_val = float(product_data['rating'])
                if rating_val >= 4.5:
                    enhanced += "\n\n✅ **Highly rated by customers!** Join thousands of satisfied buyers who love this product."
                elif rating_val >= 4.0:
                    enhanced += "\n\n👍 **Well-reviewed by customers!** Most buyers are very happy with their purchase."
            except:
                pass

        enhanced += "\n\n✨ **Don't miss out on this excellent product!** ✨"
        return enhanced

# Main app interface
url = st.text_input("Enter Amazon product URL", placeholder="https://www.amazon.com/product/...")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✨ Enhance Product Description", use_container_width=True):
        if url:
            with st.spinner("Extracting product information..."):
                product_data = extract_product_info(url)

                # Only proceed if extraction was successful
                if "error" not in product_data:
                    st.session_state.product_data = product_data
                    with st.spinner("Generating enhanced description..."):
                        enhanced_desc = enhance_description(product_data)
                        st.session_state.enhanced_description = enhanced_desc
                else:
                    st.error(product_data["error"])
                    st.session_state.product_data = None
                    st.session_state.enhanced_description = None
        else:
            st.warning("Please enter an Amazon product URL")

# Display results
if st.session_state.product_data and "error" not in st.session_state.product_data:
    st.markdown("## Product Information")

    # Create columns for product info
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Product Name", st.session_state.product_data.get('name', 'N/A')[:50] + "..." if len(st.session_state.product_data.get('name', '')) > 50 else st.session_state.product_data.get('name', 'N/A'))

    with col2:
        st.metric("Price", st.session_state.product_data.get('price', 'N/A'))

    with col3:
        rating = st.session_state.product_data.get('rating', 'N/A')
        if rating != "Not found" and rating != "Not available":
            st.metric("Rating", f"⭐ {rating}")
        else:
            st.metric("Rating", rating)

    with col4:
        # Safely get the domain from the URL stored in the product_data
        url_from_data = st.session_state.product_data.get('url', 'N/A')
        if url_from_data != 'N/A':
            domain = urlparse(url_from_data).netloc
        else:
            domain = 'N/A'
        st.metric("Source", domain)

    # Display original description
    st.markdown("### Original Description")
    original_desc = st.session_state.product_data.get("description", "No description available")
    st.markdown(f'<div class="original-desc">{original_desc}</div>', unsafe_allow_html=True)

    # Display enhanced description
    if st.session_state.enhanced_description:
        st.markdown("### Enhanced Description")
        enhanced_desc = st.session_state.enhanced_description
        # Clean up any remaining prompt text
        if "You are a professional product copywriter" in enhanced_desc:
            # Try to extract just the enhanced description part
            if "Enhanced Description:" in enhanced_desc:
                parts = enhanced_desc.split("Enhanced Description:")
                if len(parts) > 1:
                    enhanced_desc = parts[1].strip()
        st.markdown(f'<div class="enhanced-desc">{enhanced_desc}</div>', unsafe_allow_html=True)

        # JSON output
        st.markdown("### JSON Output")
        json_data = {
            "product_name": st.session_state.product_data.get('name', 'N/A'),
            "original_description": st.session_state.product_data.get('description', 'N/A'),
            "price": st.session_state.product_data.get('price', 'N/A'),
            "rating": st.session_state.product_data.get('rating', 'N/A'),
            "enhanced_description": enhanced_desc
        }
        st.json(json_data)

        # Download button
        st.download_button(
            label="Download JSON",
            data=json.dumps(json_data, indent=2),
            file_name="product_description.json",
            mime="application/json"
        )

# Instructions
st.markdown("---")
st.markdown("### How to use:")
st.markdown("1. Copy an Amazon product URL from any supported region")
st.markdown("2. Paste it into the input field above")
st.markdown("3. Click 'Enhance Product Description'")
st.markdown("4. View the original and enhanced descriptions, plus download as JSON")

# Footer
st.markdown("---")
st.markdown("Note: This app uses web scraping to extract product information. Amazon may block requests or change their structure, which could affect functionality.")
