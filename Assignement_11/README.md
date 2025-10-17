# Scientific Article Generator

This Node.js application generates structured scientific articles in Markdown and PDF format based on a user-provided topic. It leverages a locally running language model via [LM Studio](https://lmstudio.ai/) for text generation and converts the output to a styled PDF.

## Features

*   **Prompt-based Generation:** Generates a complete scientific article based on a user-input topic.
*   **Structured Format:** Produces articles with standard sections like Abstract, Introduction, Literature Review, Methodology, Results/Analysis, Discussion, Conclusion, and References (APA style).
*   **Markdown Output:** Generates the article content in Markdown format.
*   **PDF Conversion:** Converts the generated Markdown into a formatted PDF document.
*   **User Input:** Prompts the user for the article topic and author name.
*   **Dynamic Naming:** Names the output files (`<topic>-by-<author>-<date>.md` and `<topic>-by-<author>-<date>.pdf`) based on the user input and the current date (YYYY-MM-DD).
*   **Document Metadata:** Includes the author's name and the generation date within the PDF content itself.
*   **Configurable Model:** Allows specifying the model used in LM Studio via a configuration variable.

## Prerequisites

*   **Node.js:** Ensure you have Node.js installed on your system.
*   **LM Studio:** Install and set up [LM Studio](https://lmstudio.ai/).
*   **A Suitable LLM:** Download and load a capable language model within LM Studio (e.g., `qwen/qwen3-4b-2507` as used in the example, or others like `meta-llama-3.1-8b-instruct`).
*   **LM Studio API:** Ensure the LM Studio API server is running and the desired model is loaded. The application expects the API to be available at the default address `http://localhost:1234/v1`.

## Installation

1.  Clone or download this repository to your local machine.
2.  Navigate to the project directory in your terminal.
3.  Install the required Node.js dependencies:
    ```bash
    npm install
    ```
    This will install `openai`, `marked`, `puppeteer`, and their dependencies.

## Configuration

1.  Open the `lm_studio_article_generator.js` file in a text editor.
2.  Locate the line: `const LM_STUDIO_MODEL_NAME = "qwen/qwen3-4b-2507";`
3.  Change the string value `"qwen/qwen3-4b-2507"` to the exact name of the model you intend to use in LM Studio (as it appears in the LM Studio interface or API endpoint). Save the file.

## Usage

1.  **Start LM Studio:** Launch LM Studio.
2.  **Load Model:** Load the model you configured in the previous step (`LM_STUDIO_MODEL_NAME`).
3.  **Enable API:** Ensure the "Enable API" option is active in LM Studio (usually found in the API settings).
4.  **Run the Script:** In your terminal, navigate to the project directory and run:
    ```bash
    node lm_studio_article_generator.js
    ```
5.  **Follow Prompts:** The script will prompt you to enter the topic and author name for the article.
6.  **Wait:** The application will connect to LM Studio, generate the article content, convert it to PDF, and save both the Markdown and PDF files in the same directory where the script is located. The filenames will follow the pattern `<sanitized_topic>-by-<sanitized_author>-<YYYY-MM-DD>.md` and `<sanitized_topic>-<sanitized_author>-<YYYY-MM-DD>.pdf`.

## Output

*   **Markdown File:** Contains the raw generated article content in Markdown format, including the title, author, and date at the beginning.
*   **PDF File:** A formatted PDF document containing the article content with adjusted margins and the author/date information included near the top.

## Notes

*   The quality and accuracy of the generated content heavily depend on the chosen language model and the effectiveness of the prompt used within the script.
*   Generating the article content can take some time, depending on the complexity of the topic, the length specified in the script (`max_tokens`), and the performance of your local machine and the loaded model.
*   The PDF conversion step uses `puppeteer` and applies basic CSS for styling, including page margins. You can modify the CSS within the `markdownToPdf` function in the script if you wish to adjust the layout further.
*   Invalid characters for filenames (like `/`, `\`, `?`, etc.) in the topic or author name will be replaced with hyphens (`-`).
