# Product Description Generator

A Python application for generating product descriptions and marketing slogans from images using AI.

## Features

- Load multiple images
- Draw annotations to highlight target products
- Generate descriptions using AI models
- Export results to PDF
- User input for additional context

## Requirements

- Python 3.7+
- Required packages: `pip install pillow requests reportlab`

## Setup

### 1. Environment Variables

Set up your environment variables:

```bash
# For Fish shell:
set -gx LLM_API_URL "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
set -gx LLM_API_KEY "your_api_key_here"

# For Bash/Zsh:
export LLM_API_URL="https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
export LLM_API_KEY="your_api_key_here"

### 2. Supported Services
Configure the following environment variables based on your chosen service:

Hugging Face Inference API
- LLM_API_URL: https://api-inference.huggingface.co/models/{model_name}
- LLM_API_KEY: Your Hugging Face API token
- Recommended models:
    - Salesforce/blip-image-captioning-large
    - Salesforce/blip-image-captioning-base
    - nlpconnect/vit-gpt2-image-captioning
OpenAI API
- LLM_API_URL: https://api.openai.com/v1/chat/completions
- LLM_API_KEY: Your OpenAI API key
- Requires image-to-text model like gpt-4-vision-preview
Custom API
- Set LLM_API_URL to your endpoint
- Ensure your API accepts image base64 input and returns text
Usage
1. Set up your environment variables
2. Run the application: python product_generator.py
3. Load images using "Load Images"
4. Use "Enable Annotation" to draw around target products
5. Add context in the "User Input" field (optional)
6. Click "Generate Description"
7. Export to PDF with "Print to PDF"
Recommended LLMs
Vision Models
- BLIP-2 (Hugging Face): Salesforce/blip2-opt-2.7b
- BLIP (Hugging Face): Salesforce/blip-image-captioning-large
- ViT-GPT2 (Hugging Face): nlpconnect/vit-gpt2-image-captioning
Cloud Services
- OpenAI GPT-4 Vision: High accuracy, paid
- Google Gemini Pro Vision: Good performance, paid
- Anthropic Claude 3: Strong visual understanding, paid
Local Models
- LLaVA: Vision-language model, runs locally
- MiniGPT-4: Lightweight vision model
- BLIP-2: Efficient image captioning model
Troubleshooting
- API Error: Verify your API key and endpoint URL
- Rate Limiting: Wait before making additional requests
- Model Loading: Some models take 1-2 minutes to load on first use
- Connection Error: Check your internet connection
