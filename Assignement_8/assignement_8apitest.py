import os
import speech_recognition as sr
from deep_translator import GoogleTranslator
import time
import random

def get_voice_input():
    """Capture voice input in English only"""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("\nPlease speak your image description in English...")
    print("Speak clearly and wait for processing...")
    print("Listening for up to 20 seconds (or until 3 seconds of silence)...")
    print("You should see a 'Processing...' message when you finish speaking.")

    # Suppress ALSA warnings
    os.environ["ALSA_PCM_CARD"] = "0"
    os.environ["ALSA_PCM_DEVICE"] = "0"

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        # Set pause threshold to 3 seconds before considering speech ended
        recognizer.pause_threshold = 3.0
        audio = recognizer.listen(source, timeout=20)

    print("Processing your speech... Please wait.")

    try:
        # Only recognize in English
        text = recognizer.recognize_google(audio, language="en-US")
        return text
    except sr.WaitTimeoutError:
        print("Listening timed out. Please try again with clearer speech.")
        return None
    except sr.UnknownValueError:
        print("Could not understand audio. Please try again.")
        return None
    except sr.RequestError as e:
        print(f"Error with speech recognition service: {e}")
        return None

def simulate_image_generation(prompt):
    """Simulate image generation (since no API key)"""
    print(f"\nSimulating image generation for: '{prompt}'")

    # Simulate processing time
    print("Processing request...")
    time.sleep(2)

    # Generate a simulated response
    image_id = f"img_{random.randint(10000, 99999)}"
    image_url = f"https://example.com/generated/{image_id}.png"

    print(f"Generated image ID: {image_id}")
    print(f"Image URL: {image_url}")
    print("\n[In a real implementation, this would be a real image]")
    return image_url

def main():
    print("AI Image Generation Assistant (Simulated)")
    print("="*45)

    # Step 1: Inform user about English-only support
    print("Step 1: This program supports only English voice input")

    # Step 2: Get voice input
    print("\nStep 2: Recording your description...")
    user_input = get_voice_input()

    if user_input is None:
        print("Failed to capture voice input. Exiting.")
        return

    print(f"\nRecognized text: {user_input}")

    # Step 3: Generate image (simulated)
    print("\nStep 3: Generating your image...")
    image_url = simulate_image_generation(user_input)

    if image_url:
        print("\nStep 4: Image generated successfully!")
        print("You can view your image at the URL above.")
    else:
        print("\nImage generation failed. Please check your input and try again.")

if __name__ == "__main__":
    main()
