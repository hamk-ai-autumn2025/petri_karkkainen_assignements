Before use:
# Install
pip install openai-whisper deep-translator gTTS pydub sounddevice soundfile

# Install system dependency for audio playback
sudo pacman -S mpg123  # For playing MP3s

Usage:
Speak naturally for 10 seconds (pauses are fine!)
Whisper transcribes everything offline
Google Translate converts to your language
'Natural-sounding' Google voice speaks the result
🌐 Note: gTTS requires internet, but Whisper works offline.
