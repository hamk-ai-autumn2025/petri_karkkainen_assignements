import os
import openai
import speech_recognition as sr
from translate import Translator
import time

# Configuration
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese'
}

def setup_api_key():
    """Setup OpenAI API key from environment variable"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set your OPENAI_API_KEY environment variable.")
        exit(1)
    openai.api_key = api_key

def recognize_language(text):
    """Simple language detection based on keywords (basic implementation)"""
    # This is a simplified approach - in practice, use langdetect library
    # For demo purposes, we'll use a basic keyword approach
    text_lower = text.lower()
    if any(word in text_lower for word in ['el', 'la', 'de', 'que', 'no']):
        return 'es'
    elif any(word in text_lower for word in ['le', 'la', 'de', 'que', 'pas']):
        return 'fr'
    elif any(word in text_lower for word in ['der', 'die', 'und', 'in', 'den']):
        return 'de'
    # Add more language detections as needed
    return 'en'  # Default to English

def get_voice_input():
    """Capture voice input from user"""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("\nPlease speak your image description...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing speech...")
        text = recognizer.recognize_google(audio)
        detected_lang = recognize_language(text)
        return text, detected_lang
    except sr.UnknownValueError:
        print("Could not understand audio. Please try again.")
        return None, None
    except sr.RequestError as e:
        print(f"Error with speech recognition service: {e}")
        return None, None

def translate_to_english(text, source_lang):
    """Translate text to English if needed"""
    if source_lang == 'en':
        return text

    try:
        translator = Translator(to_lang="en", from_lang=source_lang)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def generate_image(prompt):
    """Generate image using OpenAI DALL-E API"""
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        print(f"\nGenerated image URL: {image_url}")
        print("\nNote: In a complete implementation, you would display or save the image here.")
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def main():
    print("AI Image Generation Assistant")
    print("="*40)

    # Step 1: Setup
    print("Step 1: Setting up API...")
    setup_api_key()

    # Step 2: Language support info
    print("\nStep 2: Supported languages:")
    for code, name in SUPPORTED_LANGUAGES.items():
        print(f"  - {name} ({code})")

    # Step 3: Get voice input
    print("\nStep 3: Recording your description...")
    user_input, detected_lang = get_voice_input()

    if user_input is None:
        print("Failed to capture voice input. Exiting.")
        return

    print(f"\nDetected language: {SUPPORTED_LANGUAGES.get(detected_lang, 'Unknown')}")

    # Step 4: Handle unsupported languages
    if detected_lang not in SUPPORTED_LANGUAGES:
        print(f"\nWarning: Detected language ({SUPPORTED_LANGUAGES.get(detected_lang, 'Unknown')}) is not directly supported!")
        print("Available languages:", ", ".join([f"{name} ({code})" for code, name in SUPPORTED_LANGUAGES.items()]))
        print("Attempting translation to English...")

        translated_input = translate_to_english(user_input, detected_lang)
        if translated_input is None:
            print("Translation failed. Please try again in a supported language.")
            return
        print(f"Original: {user_input}")
        print(f"Translated: {translated_input}")
        final_prompt = translated_input
    else:
        final_prompt = user_input

    # Step 5: Generate image
    print("\nStep 4: Generating your image...")
    image_url = generate_image(final_prompt)

    if image_url:
        print("\nStep 5: Image generated successfully!")
        print("You can view your image at the URL above.")
    else:
        print("\nImage generation failed. Please check your input and try again.")

if __name__ == "__main__":
    main()
