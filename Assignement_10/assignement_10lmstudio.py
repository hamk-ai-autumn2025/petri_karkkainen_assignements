import json
import requests
import re

def get_dictionary_entry(word):
    # LM Studio default server address
    url = "http://localhost:1234/v1/chat/completions"

    headers = {
        "Content-Type": "application/json"
    }

    # Create a more specific prompt to guide the model
    prompt = f"""
Create a dictionary entry for the word '{word}'.
If the word is in English, provide all information in English.
If the word is in another language, provide the definition in English but all other fields (synonyms, antonyms, examples) in the original language.
Respond in JSON format with these exact keys:
{{
    "word": "{word}",
    "definition": "...",
    "synonyms": [...],
    "antonyms": [...],
    "examples": [...]
}}
Example response for 'dog':
{{
    "word": "dog",
    "definition": "A domesticated mammal (Canis lupus familiaris), related to the wolf.",
    "synonyms": ["canine", "pooch"],
    "antonyms": [],
    "examples": [
        "The dog barked loudly.",
        "Dogs are loyal pets."
    ]
}}
Example response for 'kissa' (Finnish):
{{
    "word": "kissa",
    "definition": "A small domesticated carnivorous mammal with soft fur.",
    "synonyms": ["kisuli", "kisurit"],
    "antonyms": ["koira"],
    "examples": [
        "Kissa nukkuu sohvalla.",
        "Talossa asuu kaksi kissaa."
    ]
}}
"""

    payload = {
        "model": "",  # Leave empty to use the loaded model in LM Studio
        "messages": [
            {"role": "system", "content": "You are a multilingual dictionary assistant. Provide definitions in English but synonyms, antonyms, and examples in the original language if it's not English. Always respond with valid JSON and nothing else. Do not include any text before or after the JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,  # Lower temperature for more consistent outputs
        "max_tokens": 500,
        "top_p": 0.9
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        content = data['choices'][0]['message']['content']

        # Extract JSON from response - try multiple approaches
        # First try: Look for complete JSON object
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            json_str = json_match.group()
            # Fix common formatting issues
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*\]', ']', json_str)
            # Remove any trailing text after the JSON
            json_str = json_str.split('\n\n')[0]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Second try: Look for JSON inside code blocks
        code_block_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', content)
        if code_block_match:
            json_str = code_block_match.group(1)
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*\]', ']', json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # If JSON parsing fails, return default structure
        return {
            "word": word,
            "definition": "Definition not available",
            "synonyms": [],
            "antonyms": [],
            "examples": []
        }

    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to LM Studio. Please ensure LM Studio is running with a model loaded.")
        return {
            "word": word,
            "definition": "Connection error - LM Studio not running?",
            "synonyms": [],
            "antonyms": [],
            "examples": []
        }
    except requests.exceptions.Timeout:
        print("Error: Request to LM Studio timed out.")
        return {
            "word": word,
            "definition": "Request timed out",
            "synonyms": [],
            "antonyms": [],
            "examples": []
        }
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return {
            "word": word,
            "definition": "Request error",
            "synonyms": [],
            "antonyms": [],
            "examples": []
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "word": word,
            "definition": "Definition not available",
            "synonyms": [],
            "antonyms": [],
            "examples": []
        }

def main():
    while True:
        word = input("Word? ")
        if not word.strip():
            break
        entry = get_dictionary_entry(word.strip())
        print(json.dumps(entry, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
