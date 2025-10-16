// server.js - Backend for LM Studio Chat Interface (Updated for Model Listing)
const express = require('express');
const axios = require('axios'); // Use axios for HTTP requests
const path = require('path'); // To serve the HTML file

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware to parse JSON bodies
app.use(express.json());

// Serve static files (like your HTML file) from the current directory
app.use(express.static(path.join(__dirname)));

// Define the LM Studio API base URL (adjust port if LM Studio uses a different one)
const LM_STUDIO_BASE_URL = 'http://localhost:1234/v1'; // Default port for LM Studio

// GET route to serve the main HTML file at the root path
app.get('/', (req, res) => {
    // Adjust the filename if you named your HTML file differently
    res.sendFile(path.join(__dirname, 'llm-chat.html'));
});

// GET route to fetch available models from LM Studio
app.get('/api/models', async (req, res) => {
    try {
        console.log('Fetching models from LM Studio...');
        const response = await axios.get(`${LM_STUDIO_BASE_URL}/models`, {
            timeout: 5000 // 5 second timeout for listing models
        });

        // LM Studio's /models endpoint typically returns an object like:
        // { "object": "list", "data": [ { "id": "model-id", "object": "model", ... }, ... ] }
        const models = response.data.data.map(model => model.id);
        console.log('Models fetched from LM Studio:', models);
        res.json(models);

    } catch (error) {
        console.error('Error fetching models from LM Studio:', error.message);
        if (error.response) {
            console.error('Response data:', error.response.data);
            console.error('Response status:', error.response.status);
        } else if (error.request) {
            console.error('No response received from LM Studio server.');
        }
        res.status(500).json({ error: `Failed to fetch models from LM Studio: ${error.message}` });
    }
});

// POST route to handle chat requests
app.post('/api/chat', async (req, res) => {
    const { model, message } = req.body;

    // Validate incoming data
    if (!message) {
        return res.status(400).json({ error: 'Message is required' });
    }
    // Note: 'model' here is the ID selected by the user, expected to match LM Studio's loaded model
    // LM Studio often uses the currently loaded model regardless, but we pass the ID along.

    try {
        console.log(`Sending chat request to LM Studio for model: ${model}`);
        // Prepare the request payload for LM Studio's /v1/chat/completions endpoint
        const lmStudioPayload = {
            model: model, // The model ID selected by the user
            messages: [
                { role: "user", content: message }
            ],
            // You can add other parameters here if LM Studio supports them via API
            // temperature: 0.7,
            // max_tokens: 500,
        };

        // Make the request to the LM Studio API
        const response = await axios.post(`${LM_STUDIO_BASE_URL}/chat/completions`, lmStudioPayload, {
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 30000 // 30 second timeout for chat completion
        });

        // Extract the assistant's reply from the LM Studio response
        let assistantReply = response.data.choices[0].message.content;

        // Clean the response to remove <think> and <thinking> tags
        // This regex removes the tags and any content between them, including nested tags
        assistantReply = assistantReply.replace(/<think(?:ing)?>(?:.|\n)*?<\/think(?:ing)?>/gi, '').trim();

        console.log('Assistant reply received from LM Studio (cleaned):', assistantReply);

        // Send the cleaned reply back to the frontend
        res.json({ response: assistantReply });

    } catch (error) {
        console.error('Error calling LM Studio API for chat:', error.message);
        if (error.response) {
            console.error('Response data:', error.response.data);
            console.error('Response status:', error.response.status);
        } else if (error.request) {
            console.error('No response received from LM Studio server.');
        }

        // Send an error message back to the frontend
        res.status(500).json({ error: `LM Studio API Error: ${error.message}` });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log(`LM Studio API is expected at: ${LM_STUDIO_BASE_URL}`);
});
