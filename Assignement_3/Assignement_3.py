import os
import openai
from datetime import datetime

def get_user_input():
    """Get all user input including file naming preference"""
    
    # Get API key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("Please set your OPENAI_API_KEY environment variable")
        return None
    
    # Get themes
    print("Enter 3 themes/subjects for your heavy metal song:")
    themes = []
    for i in range(3):
        theme = input(f"Theme {i+1}: ").strip()
        if not theme:
            theme = "metal"
        themes.append(theme)
    
    # Get LLM model
    print("\nAvailable LLM models (recommended for creative tasks):")
    print("1. gpt-4-turbo (best for creative writing)")
    print("2. gpt-4o (balanced performance)")
    print("3. gpt-4 (high quality but slower)")
    print("4. gpt-3.5-turbo (fast, good for basic tasks)")
    
    model_choices = {
        "1": "gpt-4-turbo",
        "2": "gpt-4o", 
        "3": "gpt-4",
        "4": "gpt-3.5-turbo"
    }
    
    while True:
        choice = input("\nSelect model (1-4, default 1): ").strip() or "1"
        if choice in model_choices:
            model = model_choices[choice]
            break
        else:
            print("Invalid choice. Please select 1-4.")
    
    # Get LLM parameters
    print("\nLLM Parameters (default values shown):")
    
    try:
        temperature = float(input("Temperature (0.0-2.0, default 0.8): ") or "0.8")
        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
    except ValueError:
        print("Invalid temperature. Using default: 0.8")
        temperature = 0.8
    
    try:
        top_p = float(input("Top-p (0.0-1.0, default 0.9): ") or "0.9")
        if not 0.0 <= top_p <= 1.0:
            raise ValueError("Top-p must be between 0.0 and 1.0")
    except ValueError:
        print("Invalid top-p. Using default: 0.9")
        top_p = 0.9
    
    try:
        presence_penalty = float(input("Presence Penalty (-2.0 to 2.0, default 0.6): ") or "0.6")
        if not -2.0 <= presence_penalty <= 2.0:
            raise ValueError("Presence penalty must be between -2.0 and 2.0")
    except ValueError:
        print("Invalid presence penalty. Using default: 0.6")
        presence_penalty = 0.6
    
    try:
        frequency_penalty = float(input("Frequency Penalty (-2.0 to 2.0, default 0.0): ") or "0.0")
        if not -2.0 <= frequency_penalty <= 2.0:
            raise ValueError("Frequency penalty must be between -2.0 and 2.0")
    except ValueError:
        print("Invalid frequency penalty. Using default: 0.0")
        frequency_penalty = 0.0
    
    # Ask about saving files
    save_files = input("\nDo you want to save the lyrics to text files? (y/n, default y): ").strip().lower()
    if save_files in ['n', 'no']:
        save_files = False
    else:
        save_files = True
    
    filename_suggestion = f"heavy_metal_song_{'_'.join(themes[:3])}.txt"
    
    if save_files:
        print(f"\nSuggested filename: {filename_suggestion}")
        custom_filename = input("Enter filename (or press Enter to use suggestion): ").strip()
        if not custom_filename:
            custom_filename = filename_suggestion
        # Ensure .txt extension
        if not custom_filename.endswith('.txt'):
            custom_filename += '.txt'
    else:
        custom_filename = None
    
    return {
        "themes": themes,
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "save_files": save_files,
        "filename": custom_filename
    }

def create_system_prompt(themes: list) -> str:
    """Create a system prompt optimized for heavy metal SEO"""
    return f"""You are a creative heavy metal songwriter specializing in melodic metal lyrics.
Your task is to write SEO-optimized, highly creative lyrics that combine the following themes:
{', '.join(themes)}

Key requirements:
1. Use as many synonyms and variations as possible for each concept
2. Create powerful, emotional, and vivid imagery
3. Incorporate heavy metal terminology and atmosphere
4. Write in a melodic metal style with clear verses, choruses, and bridges
5. Ensure content is original and not copied from existing songs
6. Include thematic elements that connect all three themes
7. Use descriptive adjectives and metaphors to enhance SEO value

Structure your output as:
- Verse 1
- Verse 2  
- Chorus (repeating)
- Bridge
- Final Chorus (repeating)

Remember: Heavy metal lyrics should be intense, dramatic, and emotionally powerful while maintaining musical flow."""

def create_prompt(themes: list, system_prompt: str) -> str:
    """Create the main prompt combining all themes"""
    combined_themes = ', '.join(themes)
    return f"""Write a melodic heavy metal song combining these themes: {combined_themes}

The song should be:
- Highly creative and original
- Rich in synonyms and varied vocabulary for SEO optimization
- Structured with verses, chorus, and bridge
- Emotionally powerful with intense imagery
- Suitable for melodic metal style

Create 3 distinct versions of this song with the same themes but different approaches to storytelling and musical phrasing."""

def generate_lyrics_with_api(openai_api_key: str, params: dict) -> list:
    """Generate lyrics using OpenAI API"""
    
    # Set up OpenAI client
    openai.api_key = openai_api_key
    
    try:
        # Create system prompt
        system_prompt = create_system_prompt(params["themes"])
        
        # Create main prompt
        prompt = create_prompt(params["themes"], system_prompt)
        
        response = openai.ChatCompletion.create(
            model=params["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=params["temperature"],
            top_p=params["top_p"],
            presence_penalty=params["presence_penalty"],
            frequency_penalty=params["frequency_penalty"],
            max_tokens=2048,
            n=3  # Generate 3 versions
        )
        
        # Extract the generated lyrics
        lyrics_versions = [choice.message.content.strip() for choice in response.choices]
        
        return lyrics_versions
        
    except Exception as e:
        print(f"Error generating lyrics: {str(e)}")
        return ["Error: Could not generate lyrics due to API error"]

def save_lyrics_to_files(themes: list, lyrics_versions: list, filename: str):
    """Save each version to a separate file"""
    if not filename:
        filename = f"heavy_metal_song_{'_'.join(themes[:3])}.txt"
    
    # If filename doesn't end with .txt, add it
    if not filename.endswith('.txt'):
        filename += '.txt'
    
    # Create base filename without extension for version numbering
    base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    for i, lyrics in enumerate(lyrics_versions):
        version_filename = f"{base_name}_v{i+1}.txt"
        with open(version_filename, 'w', encoding='utf-8') as f:
            f.write(f"=== Heavy Metal Song Version {i+1} ===\n")
            f.write(f"Themes: {', '.join(themes)}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(lyrics)
            f.write("\n\n")
        print(f"Saved to {version_filename}")

def main():
    """Main function"""
    
    # Get user input
    params = get_user_input()
    
    if not params:
        return
    
    # Get API key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    # Generate lyrics
    print("\nGenerating lyrics with OpenAI API...")
    lyrics_versions = generate_lyrics_with_api(openai_api_key, params)
    
    # Display results
    for i, lyrics in enumerate(lyrics_versions):
        print(f"\n{'='*60}")
        print(f"LYRICS VERSION {i+1}")
        print(f"{'='*60}")
        print(lyrics)
        print(f"{'='*60}\n")
    
    # Save files if requested
    if params["save_files"]:
        save_lyrics_to_files(params["themes"], lyrics_versions, params["filename"])
        print("\nAll versions saved successfully!")
    else:
        print("\nLyrics generated but not saved to files.")

if __name__ == "__main__":
    main()
