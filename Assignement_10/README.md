# LLM-Powered Dictionary Generator

A Python program that generates dictionary entries (definition, synonyms, antonyms, and examples) for any given word using a local LLM via LM Studio.

## Features

- Generates dictionary entries in JSON format
- Handles both English and non-English words
- Provides definitions in English with synonyms/antonyms/examples in the original language
- Uses local LLM to avoid API costs and maintain privacy
- Works with multiple popular open-source models

## Requirements

- Python 3.7+
- LM Studio installed and running
- A compatible LLM model loaded in LM Studio

## Installation

1. Install the required Python package:
   ```bash
   pip install requests
   ```

2. Download and install [LM Studio](https://lmstudio.ai/)

3. Load a compatible model in LM Studio (see recommended models below)

4. Start the local server in LM Studio (click "Start Server" in the bottom-left corner)

## Usage

1. Run the program:
   ```bash
   python dictionary_generator.py
   ```

2. Enter a word when prompted:
   ```
   Word? programming
   ```

3. The program will output a JSON dictionary entry:
   ```json
   {
     "word": "programming",
     "definition": "The process of designing, writing, testing, debugging, and maintaining the source code of computer programs.",
     "synonyms": [
       "coding",
       "development"
     ],
     "antonyms": [],
     "examples": [
       "Learning programming requires practice.",
       "She is studying computer programming."
     ]
   }
   ```

4. Enter another word or press Enter to exit

## Recommended Models

The following models work well with this program and offer a good balance between performance and size:

### Top Recommendations

1. **Meta Llama 3.1 8B Instruct** (7.3GB)
   - Excellent instruction following
   - Good multilingual capabilities
   - Very effective for dictionary generation
   - Requires 16GB+ RAM

2. **Mistral-Nemo-Instruct-2407** (7.3GB)
   - Strong reasoning and language understanding
   - Good for structured outputs
   - Requires 16GB+ RAM

3. **MiniStral-8B-Instruct-2410** (4.9GB)
   - Smaller size but still effective
   - Good performance for the size
   - Requires 12GB+ RAM

### Alternative Options

4. **OpenHermes-2.5-Mistral-7B** (4.1GB)
   - Well-trained for instruction following
   - Good for structured tasks
   - Requires 12GB+ RAM

5. **Nous-Hermes-2-Mistral-7B-DPO** (4.1GB)
   - Focused on instruction following
   - Good for various NLP tasks
   - Requires 12GB+ RAM

6. **Zephyr-7B-Alpha/Beta** (3.7GB)
   - Smaller size option
   - Decent performance for basic tasks
   - Requires 8GB+ RAM

## Model Setup in LM Studio

1. Open LM Studio
2. Click on the "Download Models" tab
3. Search for one of the recommended models
4. Click "Download" next to your chosen model
5. Wait for the download to complete
6. Select the downloaded model from the dropdown
7. Click "Load" to load the model
8. Click "Start Server" to start the local inference server
9. The server will be available at `http://localhost:1234`

## Troubleshooting

- **Connection Error**: Ensure LM Studio server is running and model is loaded
- **No JSON Output**: Some models may not follow the format perfectly - try with a different model
- **Slow Responses**: Larger models require more processing time and memory
- **Memory Issues**: Ensure your system has enough RAM for the chosen model

## Notes

- The quality of output depends heavily on the chosen model
- Non-English words may not always return synonyms in the original language depending on the model's training
- For best results, use models with 7B+ parameters
- The program works offline once LM Studio is set up with a model

## License

This project is open-source and free to use.
