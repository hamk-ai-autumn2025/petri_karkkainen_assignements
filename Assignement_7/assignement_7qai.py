import whisper
import numpy as np
import time
import os
import subprocess
import tempfile

# For translation
from deep_translator import GoogleTranslator

# For TTS
from gtts import gTTS

# Supported languages
LANGUAGES = {
    'english': 'en',
    'swedish': 'sv',
    'german': 'de',
    'french': 'fr',
    'spanish': 'es',
    'italian': 'it',
    'estonian': 'et'
}

def select_language():
    print("\nAvailable languages:")
    for i, lang in enumerate(LANGUAGES, 1):
        print(f"{i}. {lang.capitalize()}")
    while True:
        try:
            choice = int(input("\nSelect target language (1-7): "))
            if 1 <= choice <= 7:
                return list(LANGUAGES.values())[choice - 1]
        except ValueError:
            pass
        print("Enter 1-7")

def record_audio(duration=10):
    """Record audio using sounddevice"""
    try:
        import sounddevice as sd
    except ImportError:
        print("❌ Please install sounddevice: pip install sounddevice")
        exit(1)

    print(f"\n🎙️  Recording for {duration} seconds... (speak naturally!)")
    sample_rate = 16000

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )

    for i in range(duration, 0, -1):
        print(f"   Recording... {i}s", end='\r')
        time.sleep(1)
    print("\n✅ Recording finished")

    sd.wait()
    return audio.flatten(), sample_rate

def transcribe_with_whisper(audio, sample_rate):
    """Transcribe using Whisper (offline)"""
    print("🧠 Transcribing with Whisper AI...")

    # Save to temp WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_wav = f.name

    import soundfile as sf
    sf.write(temp_wav, audio, sample_rate)

    # Load base model (fastest)
    model = whisper.load_model("base")
    result = model.transcribe(temp_wav, fp16=False)

    os.unlink(temp_wav)

    text = result['text'].strip()
    lang = result['language']
    print(f"📝 Detected ({lang.upper()}): {text}")
    return text, lang

def translate_text(text, target_lang):
    """Translate using Google Translate"""
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        result = translator.translate(text)
        lang_name = [k for k, v in LANGUAGES.items() if v == target_lang][0].capitalize()
        print(f"🌍 Translated ({lang_name}): {result}")
        return result
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return None

def speak_with_gtts(text, lang_code):
    """Speak using Google TTS (natural voice)"""
    print("🔊 Speaking with Google-quality voice...")

    try:
        # Create temp MP3
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_mp3 = f.name

        # Generate speech
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(temp_mp3)

        # Play with mpg123 (installed via pacman)
        subprocess.run(["mpg123", "-q", temp_mp3], check=True)

        # Cleanup
        os.unlink(temp_mp3)
        return True
    except Exception as e:
        print(f"❌ TTS error: {e}")
        return False

def main():
    print("🤖 AI Voice Interpreter (Natural Speech + Offline STT)")
    print("=" * 55)

    target_lang = select_language()
    start_time = time.time()

    # Record
    try:
        audio, sr = record_audio(duration=10)
    except Exception as e:
        print(f"🎤 Mic error: {e}")
        return

    # Transcribe
    text, detected_lang = transcribe_with_whisper(audio, sr)
    if not text:
        return

    # Translate
    translated = translate_text(text, target_lang)
    if not translated:
        return

    # Speak
    speak_with_gtts(translated, target_lang)

    print(f"\n⏱️  Total time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
