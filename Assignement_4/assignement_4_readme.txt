Installation Requirements:
To use this tool, you need to install the following dependencies:

pip install beautifulsoup4 python-docx PyPDF2 requests

Usage Examples:
# Summarize a text file
python assignement_4.py document.txt

# Process multiple files and custom query
python assignement_4.py file1.txt file2.pdf --query "Explain the key points"

# Process URL with output to file
python assignement_4.py https://example.com/page.html --output result.txt

# Process CSV and DOCX with specific model
python assignement_4.py data.csv docx_file.docx --model gpt-4 --query "Summarize the content"
