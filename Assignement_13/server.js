const express = require('express');
// We are using the built-in fetch, so no need to require('node-fetch')
const path = require('path');

const app = express();
const PORT = 5000;

// Serve static files from 'public' directory
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// Retrieve API key from environment variable
const HF_API_KEY = process.env.HF_API_KEY;
if (!HF_API_KEY) {
    console.error("Error: HF_API_KEY environment variable is not set.");
    process.exit(1);
}

app.post('/generate-image', async (req, res) => {
    const { prompt, negative_prompt, aspect_ratio } = req.body;

    if (!prompt) {
        return res.status(400).json({ error: 'Prompt is required' });
    }

    let width = 800;
    let height = 600;
    switch (aspect_ratio) {
        case '1:1':
            width = height = 768;
            break;
        case '16:9':
            width = 1024; height = 576;
            break;
        case '9:16':
            width = 576; height = 1024;
            break;
        case '4:3':
            width = 1024; height = 768;
            break;
        case '3:4':
            width = 768; height = 1024;
            break;
        default:
            width = 800; height = 600;
    }

    try {
        console.log("Sending request to HF API with prompt:", prompt, "negative_prompt:", negative_prompt, "width:", width, "height:", height);

        // Use the model ID you prefer
        const modelId = "stabilityai/stable-diffusion-xl-base-1.0"; // You can change this

        const response = await fetch(
            `https://api-inference.huggingface.co/models/${modelId}`,
            {
                headers: {
                    Authorization: `Bearer ${HF_API_KEY}`,
                    'Content-Type': 'application/json',
                },
                method: "POST",
                body: JSON.stringify({
                    inputs: prompt,
                    parameters: {
                        negative_prompt: negative_prompt || "",
                        width: width,
                        height: height,
                        num_inference_steps: 20,
                    }
                }),
            }
        );

        if (!response.ok) {
            const errorText = await response.text(); // Get error details
            console.error("HF API Error:", response.status, errorText);
            throw new Error(`API Error: ${response.status} - ${errorText}`);
        }

        // Get the image data as an ArrayBuffer
        const imageArrayBuffer = await response.arrayBuffer();

        // Convert ArrayBuffer to Buffer
        const imageBuffer = Buffer.from(imageArrayBuffer);

        // Set the correct content type
        res.setHeader('Content-Type', 'image/jpeg'); // Or image/png depending on the model
        res.send(imageBuffer); // Send the buffer directly

    } catch (error) {
        console.error("Error calling Hugging Face API:", error);
        res.status(500).json({
            error: 'Failed to generate image',
            details: error.message
        });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
