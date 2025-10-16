# LM Studio Chat Interface (Sidebar Model Selection)

This project provides a modern web-based chat interface for interacting with large language models (LLMs) running locally on your machine via [LM Studio](https://lmstudio.ai/). It fetches the list of models available in your LM Studio server and allows you to select and chat with them directly from the browser sidebar.

## Features

*   **Modern Web UI:** A sleek, responsive chat interface built with HTML, CSS, and JavaScript.
*   **Local LLM Interaction:** Communicates with language models running on your local LM Studio server.
*   **Dynamic Model Listing:** Automatically retrieves and displays the list of models available in LM Studio.
*   **Sidebar Model Selection:** Choose the active model for your chat session using the sidebar.
*   **Thought Tag Cleaning:** Automatically removes `<think>`, `<thinking>`, `</think>`, `</thinking>`, and similar tags from model responses for a cleaner chat log.
*   **No API Keys Required:** Designed specifically for local LM Studio usage, eliminating the need for external API keys.

## Prerequisites

*   **Node.js:** Ensure you have Node.js installed on your system. You can download it from [nodejs.org](https://nodejs.org/).
*   **LM Studio:** Download and install LM Studio from [lmstudio.ai](https://lmstudio.ai/). Ensure it is running and serving models locally (typically on `http://localhost:1234`).

## Installation

1.  **Clone or Download:** Obtain the project files (`server.js`, `llm-chat.html`, potentially a `package.json` if you created one, and this `README.md`).
2.  **Navigate:** Open a terminal or command prompt and navigate to the directory containing the downloaded project files.
3.  **Install Dependencies:** Run the following command to install the required Node.js packages (`express` and `axios`):
    ```bash
    npm install express axios
    ```
    *(Note: If you encounter permission issues, you might need to run `npm install --save express axios`)*

## Configuration

*   **LM Studio Server:** Ensure LM Studio is running. The default API address expected by the server is `http://localhost:1234/v1`. If your LM Studio instance uses a different port, you need to update the `LM_STUDIO_BASE_URL` constant in `server.js` accordingly.

## Usage

1.  **Start LM Studio:** Open the LM Studio application on your computer. Load the model you intend to use, or ensure the model you want is available for loading.
2.  **Start the Web Server:** In your terminal/command prompt, within the project directory, run:
    ```bash
    node server.js
    ```
    You should see output confirming the server is running (e.g., `Server is running on http://localhost:5000`).
3.  **Open the Web Interface:** Open your web browser and navigate to `http://localhost:5000`.
4.  **Select a Model:** The sidebar will populate with models fetched from LM Studio. Click on a model name in the sidebar to select it for your chat session. The initial message in the chat area will update to reflect the selected model.
5.  **Chat:** Type your message in the input field at the bottom and press Enter or click the send button. The message will be sent to the selected model via your local LM Studio server. The response, with thought tags cleaned, will appear in the chat window.

## Troubleshooting

*   **"Cannot GET /" Error:** Ensure you are running `node server.js` and accessing `http://localhost:5000`.
*   **"Loading..."/Models not appearing:** Check the terminal where `server.js` is running for errors related to fetching models from LM Studio. Ensure LM Studio is running on the expected address (`http://localhost:1234` by default) and that its API server is active. Check the browser's developer console (F12) for JavaScript errors.
*   **Chat not working:** Verify the model selected in the sidebar is the one loaded in the LM Studio application's UI. Check the browser console and server terminal for errors during the chat request/response process.
*   **CORS Errors:** These are unlikely with this setup as the Node.js server acts as a proxy, but ensure no other applications are interfering with `localhost` requests.

## Security Note

This project is intended for local development and personal use only. It does not implement authentication or authorization mechanisms. Do not expose this server publicly without adding appropriate security measures.

## License

This project is intended for educational purposes.
