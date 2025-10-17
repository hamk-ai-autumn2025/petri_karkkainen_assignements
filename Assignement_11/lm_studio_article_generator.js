// lm_studio_article_generator.js
const OpenAI = require("openai"); // Use the OpenAI library
const fs = require("fs").promises;
const path = require("path");
const readline = require('readline'); // Built-in Node.js module for reading input
const marked = require("marked");
const puppeteer = require("puppeteer");

// --- Configuration ---
// Replace 'YOUR_SELECTED_MODEL_NAME' with the exact name of the model loaded in LM Studio
// Example: "models/mistral-7b-instruct-v0.3.Q4_K_M.gguf"
const LM_STUDIO_MODEL_NAME = "qwen/qwen3-4b-2507";
const LM_STUDIO_BASE_URL = "http://localhost:1234/v1"; // Default LM Studio API endpoint

// Initialize the OpenAI client, pointing to LM Studio
const openai = new OpenAI({
    baseURL: LM_STUDIO_BASE_URL, // Point to your local LM Studio server
    apiKey: "lm-studio", // LM Studio doesn't require a real API key, but the library needs one
});

// --- Helper function to get user input ---
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function askQuestion(question) {
    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            resolve(answer.trim()); // Trim whitespace from the answer
        });
    });
}

// --- Helper function to format date in APA style (YYYY-MM-DD) ---
function getAPAFormattedDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`; // YYYY-MM-DD format
}

async function generateArticleMarkdown(topic) {
    console.log(`Generating article for topic: "${topic}" using model: ${LM_STUDIO_MODEL_NAME} via LM Studio.`);

    const prompt = `You are a scientific article writer. Your task is to generate a structured scientific article in Markdown format based on the user's request. The article must include an Abstract, Introduction, Literature Review / Background, Methodology (if applicable), Results / Analysis, Discussion, Conclusion, and a References section formatted in APA style. Use appropriate Markdown headings (e.g., #, ##, ###).

    Generate a scientific article on the following topic: ${topic}`;

    try {
        const response = await openai.chat.completions.create({
            model: LM_STUDIO_MODEL_NAME, // Use the model loaded in LM Studio
            messages: [
                { role: "system", content: "You are a scientific article writer." },
                { role: "user", content: prompt }
            ],
            max_tokens: 3200, // Adjust based on desired length
            temperature: 0.7, // Adjust creativity
            stream: false, // For simplicity in this example
        });

        // console.log("Raw LM Studio response:", JSON.stringify(response, null, 2)); // Log for debugging

        const generatedText = response.choices[0]?.message?.content?.trim();

        if (!generatedText) {
            console.error("Error: No content found in the response from LM Studio.");
            console.error("Full response object:", JSON.stringify(response, null, 2));
            return null;
        }

        // console.log("\n--- Generated Article (Markdown) ---"); // Optional: Print if needed for debugging
        // console.log(generatedText);
        // console.log("\n--- End of Generated Article ---");

        return generatedText;

    } catch (error) {
        console.error("Error calling LM Studio API:", error.message);
        if (error.response) {
            console.error("API Error Details:", error.response.data);
            console.error("Status Code:", error.response.status);
        }
        return null;
    }
}

// --- Function to add author and date to the beginning of the Markdown content ---
function addAuthorAndDateToMarkdown(markdownContent, author, date) {
    // Split the content into lines
    const lines = markdownContent.split('\n');

    // Assume the first line is the main title (starts with #)
    const mainTitle = lines[0]; // This will be something like "# The Future of Cyber Warfare"
    const restOfContent = lines.slice(1).join('\n'); // Get all other lines

    // Create the header content using Markdown
    // Use the mainTitle from the generated content, then add author and date info
    const headerMarkdown = `${mainTitle}\n\n` + // Keep the original main title
    `**Author:** ${author}\n\n` +
    `**Date:** ${date}\n\n` +
    `---\n\n`; // Add a horizontal line for visual separation

    // Combine the header with the rest of the content (excluding the first line which was the title)
    return headerMarkdown + restOfContent;
}

// --- Function to convert Markdown to PDF using Puppeteer with adjusted margins ---
async function markdownToPdf(markdownContent, outputPath) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Convert Markdown to HTML
    const htmlContent = marked.parse(markdownContent);

    // CSS with adjusted margins (default is often 1 inch, let's try 0.5 inches)
    const styledHtml = `
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @page {
        margin: 0.5in; /* Adjust this value as needed (e.g., 0.4in, 0.6in) */
    }
    body {
        font-family: Arial, sans-serif;
        /* margin is for the content box *within* the page margin defined by @page */
        margin: 0;
        padding: 0;
    }
    h1, h2, h3 { color: #333; }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th { background-color: #f2f2f2; }
    </style>
    </head>
    <body>
    ${htmlContent}
    </body>
    </html>`;

    await page.setContent(styledHtml, { waitUntil: 'networkidle0' });

    await page.pdf({
        path: outputPath,
        format: 'A4',
            printBackground: true,
            margin: { // Optional: You can also set margins here, but @page CSS usually takes precedence
                // If both are set, the larger of the two might apply, or @page wins depending on the setup.
                // top: '0.5in', right: '0.5in', bottom: '0.5in', left: '0.5in'
            }
    });

    await browser.close();
    console.log(`PDF successfully saved to: ${outputPath}`);
}

// --- Main Execution ---
async function main() {
    console.log("=== Scientific Article Generator ===");

    // 1. Get topic and author from user input
    const topic = await askQuestion("Enter the topic for the scientific article: ");
    if (!topic) {
        console.error("Topic cannot be empty.");
        rl.close();
        return;
    }
    const author = await askQuestion("Enter the author name(s) for the article: ");
    if (!author) {
        console.error("Author name cannot be empty.");
        rl.close();
        return;
    }
    const date = getAPAFormattedDate(); // Get the current date

    console.log(`\nGenerating article on: "${topic}" by ${author} (Date: ${date})`);

    // Ensure LM Studio is running and the correct model is loaded before running this script

    // 2. Generate the article Markdown using LM Studio
    const markdown = await generateArticleMarkdown(topic);
    if (!markdown) {
        console.error("Failed to generate article content from LM Studio.");
        rl.close(); // Close readline interface
        return;
    }

    // 3. Add author and date information to the beginning of the Markdown content
    const markdownWithHeader = addAuthorAndDateToMarkdown(markdown, author, date);

    // 4. Define output paths based on topic, author, and date
    // Sanitize inputs for use in filenames (remove/replace invalid characters)
    const sanitize = (str) => str.replace(/[/\\?%*:|"<>]/g, '-'); // Replace invalid chars with '-'
    const sanitizedTopic = sanitize(topic);
    const sanitizedAuthor = sanitize(author);

    const baseFilename = `${sanitizedTopic}-by-${sanitizedAuthor}-${date}`;
    const markdownOutputPath = path.join(__dirname, `${baseFilename}.md`);
    const pdfOutputPath = path.join(__dirname, `${baseFilename}.pdf`);

    // 5. Save the generated Markdown (WITH header) to a file (optional, for review)
    try {
        await fs.writeFile(markdownOutputPath, markdownWithHeader);
        console.log(`Generated Markdown (with header) saved to: ${markdownOutputPath}`);
    } catch (writeError) {
        console.error("Error writing Markdown file:", writeError.message);
        // Even if writing the markdown file fails, we can still try to convert to PDF
    }

    // 6. Convert the Markdown (WITH header) to PDF
    try {
        await markdownToPdf(markdownWithHeader, pdfOutputPath);
    } catch (pdfError) {
        console.error("Error generating PDF:", pdfError.message);
    }

    console.log("\n=== Generation Complete ===");
    rl.close(); // Close readline interface
}

// Run the main function
main().catch(console.error);
