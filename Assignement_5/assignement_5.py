import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import openai
from PIL import Image, ImageTk
import io
import os
import base64

class ImageToTextToImageGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Image-to-Text-to-Image Generator")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Initialize API key from environment variable
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            messagebox.showerror("Error", "OPENAI_API_KEY environment variable not set")
            self.root.destroy()
            return

        # Set API key
        openai.api_key = self.api_key

        # Create UI elements
        self.create_widgets()

        # Status label
        self.status_label = tk.Label(root, text="Ready", bg="#f0f0f0", fg="#333333")
        self.status_label.pack(pady=5)

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text="Image-to-Text-to-Image Generator",
                              font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        title_label.pack(pady=(0, 20))

        # Image Frame
        image_frame = ttk.LabelFrame(main_frame, text="Image", padding="10")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Canvas for displaying image
        self.canvas = tk.Canvas(image_frame, bg="white", height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # Load image button
        self.load_button = ttk.Button(button_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=(0, 5))

        # Generate description button
        self.desc_button = ttk.Button(button_frame, text="Generate Description",
                                     command=self.generate_description, state=tk.DISABLED)
        self.desc_button.pack(side=tk.LEFT, padx=(0, 5))

        # Generate image button
        self.gen_button = ttk.Button(button_frame, text="Generate Image",
                                    command=self.generate_image, state=tk.DISABLED)
        self.gen_button.pack(side=tk.LEFT, padx=(0, 5))

        # Reset button
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_all)
        self.reset_button.pack(side=tk.LEFT, padx=(0, 5))

        # Description text box
        desc_frame = ttk.LabelFrame(main_frame, text="Image Description", padding="10")
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.desc_text = tk.Text(desc_frame, wrap=tk.WORD, height=6)
        scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=self.desc_text.yview)
        self.desc_text.configure(yscrollcommand=scrollbar.set)
        self.desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Generated image frame
        gen_frame = ttk.LabelFrame(main_frame, text="Generated Image", padding="10")
        gen_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.gen_canvas = tk.Canvas(gen_frame, bg="white", height=250)
        self.gen_canvas.pack(fill=tk.BOTH, expand=True)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )

        if file_path:
            try:
                self.image = Image.open(file_path)
                self.display_image(self.image, self.canvas)
                self.load_button.config(text="Change Image")
                self.desc_button.config(state=tk.NORMAL)
                self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")

    def display_image(self, image, canvas):
        # Clear canvas
        canvas.delete("all")

        # Resize image to fit canvas while maintaining aspect ratio
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width == 0 or canvas_height == 0:
            canvas_width = 400
            canvas_height = 300

        image.thumbnail((canvas_width, canvas_height), Image.LANCZOS)

        # Convert to PhotoImage for display
        photo = ImageTk.PhotoImage(image)
        canvas.image = photo  # Keep reference to avoid garbage collection

        # Center the image
        x = (canvas_width - image.width) // 2
        y = (canvas_height - image.height) // 2

        canvas.create_image(x, y, anchor=tk.NW, image=photo)

    def generate_description(self):
        if not hasattr(self, 'image'):
            messagebox.showerror("Error", "Please load an image first")
            return

        # Disable buttons during processing
        self.desc_button.config(state=tk.DISABLED)
        self.gen_button.config(state=tk.DISABLED)
        self.status_label.config(text="Generating description...")

        # Run in separate thread to avoid freezing GUI
        thread = threading.Thread(target=self._generate_description_thread)
        thread.daemon = True
        thread.start()

    def _generate_description_thread(self):
        try:
            # Prepare image for API call - convert to base64
            buffered = io.BytesIO()
            self.image.save(buffered, format="JPEG")
            img_bytes = buffered.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image in detail. Include colors, shapes, objects, and any notable features."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )

            description = response.choices[0].message.content

            # Update GUI on main thread
            self.root.after(0, self._update_description, description)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate description:\n{str(e)}"))
            self.root.after(0, lambda: self.desc_button.config(state=tk.NORMAL))
            self.status_label.config(text="Ready")

    def _update_description(self, description):
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(tk.END, description)
        self.desc_button.config(state=tk.NORMAL)
        self.gen_button.config(state=tk.NORMAL)
        self.status_label.config(text="Description generated")

    def generate_image(self):
        description = self.desc_text.get(1.0, tk.END).strip()
        if not description:
            messagebox.showerror("Error", "No description available to generate image")
            return

        # Disable buttons during processing
        self.desc_button.config(state=tk.DISABLED)
        self.gen_button.config(state=tk.DISABLED)
        self.status_label.config(text="Generating image...")

        # Run in separate thread to avoid freezing GUI
        thread = threading.Thread(target=self._generate_image_thread, args=(description,))
        thread.daemon = True
        thread.start()

    def _generate_image_thread(self, description):
        try:
            # Call DALL-E API
            response = openai.Image.create(
                prompt=description,
                n=1,
                size="1024x1024"
            )

            image_url = response['data'][0]['url']

            # Download and display the generated image
            import requests
            from PIL import Image

            img_data = requests.get(image_url).content
            generated_image = Image.open(io.BytesIO(img_data))

            # Update GUI on main thread
            self.root.after(0, self._update_generated_image, generated_image)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate image:\n{str(e)}"))
            self.root.after(0, lambda: self.desc_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.gen_button.config(state=tk.NORMAL))
            self.status_label.config(text="Ready")

    def _update_generated_image(self, image):
        self.display_image(image, self.gen_canvas)
        self.desc_button.config(state=tk.NORMAL)
        self.gen_button.config(state=tk.NORMAL)
        self.status_label.config(text="Image generated")

    def reset_all(self):
        # Reset all fields
        self.desc_text.delete(1.0, tk.END)
        self.canvas.delete("all")
        self.gen_canvas.delete("all")
        self.load_button.config(text="Load Image")
        self.desc_button.config(state=tk.DISABLED)
        self.gen_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ready")

        # Remove image reference
        if hasattr(self, 'image'):
            delattr(self, 'image')

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToTextToImageGenerator(root)

    # Handle window closing
    def on_closing():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
