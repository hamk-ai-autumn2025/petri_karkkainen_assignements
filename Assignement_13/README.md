# AI Image Generator Web Interface

This project provides a simple web interface to generate images using Hugging Face's text-to-image models. It uses a Node.js backend to securely handle the Hugging Face API key and communicate with the Hugging Face Inference API, and an HTML/JavaScript frontend for user interaction.

## Features

*   Generates images from text prompts using Hugging Face models.
*   Supports negative prompts to refine generation.
*   Allows selection of image aspect ratio (4:3, 16:9, 9:16, 1:1, 3:4).
*   Secure handling of the Hugging Face API key via environment variables.
*   Displays the generated image directly in the browser.
*   **New:** Includes a "Download Image" button. The downloaded file is named based on the prompt text and includes a timestamp (e.g., `prompt_text_YYYYMMDD_HHMMSS.jpg`).

## Prerequisites

*   **Node.js:** Version 18.0 or higher (to use the built-in `fetch` API).
*   **npm:** Node.js package manager (usually comes with Node.js).
*   **Hugging Face Account:** You need an account on [Hugging Face](https://huggingface.co) to get an API token.
*   **Hugging Face API Token:** Obtain your User Access Token from your Hugging Face profile settings.

## Setup

1.  **Clone or Download:** Get the project files to your local machine.
2.  **Navigate:** Open a terminal and navigate to the project directory (where `server.js` is located).
3.  **Install Dependencies:** Run the following command to install the required Node.js package (`express`).
    ```bash
    npm install express
    ```
    *(Note: `node-fetch` is not needed as the final solution uses the built-in `fetch` API available in Node.js v18+)*
4.  **Set Environment Variable:**
    *   On Linux/macOS (using Fish shell as mentioned):
        *   Open your Fish configuration file (e.g., `~/.config/fish/config.fish`).
        *   Add the following line, replacing `YOUR_HUGGING_FACE_API_TOKEN` with your actual token:
            ```fish
            set -gx HF_API_KEY "YOUR_HUGGING_FACE_API_TOKEN"
            ```
        *   Save the file and restart your terminal, or run `source ~/.config/fish/config.fish` to load the variable.
    *   On Windows (Command Prompt):
        ```cmd
        set HF_API_KEY=YOUR_HUGGING_FACE_API_TOKEN
        ```
    *   On Windows (PowerShell):
        ```powershell
        $env:HF_API_KEY="YOUR_HUGGING_FACE_API_TOKEN"
        ```

## Usage

1.  **Start the Server:** In your project terminal, run:
    ```bash
    node server.js
    ```
    You should see a message like `Server running on http://localhost:5000`.
2.  **Open the Web Interface:** Open your web browser and go to `http://localhost:5000`.
3.  **Configure and Generate:**
    *   Enter your desired image prompt in the "Prompt" field.
    *   Optionally, enter terms you want to avoid in the "Negative Prompt" field.
    *   Select the desired aspect ratio from the dropdown.
    *   Click the "Generate Image" button.
4.  **View Result:** If successful, the generated image will appear below the button after a short processing time.
5.  **Download Image:** Once an image is generated, the "Download Image" button will become active. Click it to download the image to your browser's default download location with a filename based on the prompt and a timestamp.

## Troubleshooting

*   **`Error: HF_API_KEY environment variable is not set.`:** Ensure you have correctly set the `HF_API_KEY` environment variable as described in the Setup section and restarted your terminal/server if necessary.
*   **`Error: Failed to generate image` (in browser) / `TypeError: ...` (in terminal):** Check the terminal running `node server.js` for specific error messages from the Hugging Face API or Node.js. Common issues might be related to the API token permissions, the specific model being used, or rate limits on the free tier.
*   **Image does not appear / Page is empty:** Verify that the prompt is not empty. Check the browser's developer console (F12) for errors. Check the Network tab in the developer tools for the `/generate-image` request status.
*   **"Download Image" button doesn't work:** Ensure an image has been successfully generated first. Check the browser's developer console for errors.

## Important Notes

*   **API Usage:** Generating images consumes your Hugging Face API quota. Be mindful of your usage, especially if not on a free tier.
*   **Model:** The default model used is `stabilityai/stable-diffusion-xl-base-1.0`. You can change this in the `server.js` file if you wish to use a different model.
*   **Security:** The API key is securely handled on the server-side and is never exposed to the browser.
*   **Download Location:** The browser controls the final download location based on its settings. The filename is suggested by the application.

## Files

*   `server.js`: The Node.js backend application.
*   `public/index.html`: The HTML frontend interface (including the download button).
*   `README.md`: This file.
