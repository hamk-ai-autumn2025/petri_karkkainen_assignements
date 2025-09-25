import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from PIL import Image, ImageTk
import io
import os
import requests
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
import torch
from diffusers import StableDiffusionPipeline

class FreeImageToTextToImageGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Free Image-to-Text-to-Image Generator")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize models (will be loaded when needed)
        self.caption_model = None
        self.image_gen_model = None
        self.is_models_loaded = False
        
        # Create UI elements
        self.create_widgets()
        
        # Status label
        self.status_label = tk.Label(root, text="Ready", bg="#f0f0f0", fg="#333333")
        self.status_label.pack(pady=5)
        
        # Load models in background
        self.load_models_async()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Free Image-to-Text-to-Image Generator", 
                              font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#2c3e50")
        title_label.pack(pady=(0, 20))
        
        # Model status frame
        model_frame = ttk.Frame(main_frame)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.model_status_label = tk.Label(model_frame, text="Loading models...", 
                                          bg="#f0f0f0", fg="#333333")
        self.model_status_label.pack()
        
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
        
    def load_models_async(self):
        """Load models in a separate thread to avoid blocking the UI"""
        def load_models():
            try:
                # Load BLIP model for image captioning
                self.caption_model = pipeline("image-to-text", 
                                             model="Salesforce/blip-image-captioning-base",
                                             device=0 if torch.cuda.is_available() else -1)
                
                # Load Stable Diffusion model for image generation
                self.image_gen_model = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    safety_checker=None  # Disable safety checker for faster processing
                )
                
                if torch.cuda.is_available():
                    self.image_gen_model = self.image_gen_model.to("cuda")
                    
                self.is_models_loaded = True
                self.root.after(0, self.update_model_status)
            except Exception as e:
                self.root.after(0, lambda: self.model_status_label.config(
                    text=f"Error loading models: {str(e)}"))
        
        # Start loading in background thread
        threading.Thread(target=load_models, daemon=True).start()
        
    def update_model_status(self):
        """Update the model status display"""
        if self.is_models_loaded:
            self.model_status_label.config(text="Models loaded successfully")
            self.desc_button.config(state=tk.NORMAL)
            self.gen_button.config(state=tk.NORMAL)
        else:
            self.model_status_label.config(text="Loading models...")
            
    def load_image(self):
        """Load an image from file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            try:
                # Load and display the image
                self.image = Image.open(file_path)
                
                # Resize for display while maintaining aspect ratio
                max_size = (600, 400)
                self.image.thumbnail(max_size, Image.LANCZOS)
                
                # Convert to PhotoImage for tkinter
                self.photo = ImageTk.PhotoImage(self.image)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
                
                # Enable buttons
                self.desc_button.config(state=tk.NORMAL)
                self.status_label.config(text="Image loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                
    def generate_description(self):
        """Generate a description of the image using BLIP model"""
        if not self.is_models_loaded or not hasattr(self, 'image'):
            messagebox.showwarning("Warning", "Please load an image first")
            return
            
        # Disable buttons during processing
        self.desc_button.config(state=tk.DISABLED)
        self.status_label.config(text="Generating description...")
        
        def process_caption():
            try:
                # Generate caption using BLIP model
                caption = self.caption_model(self.image)[0]['generated_text']
                
                # Update UI on main thread
                self.root.after(0, lambda: self.update_description(caption))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", 
                    f"Failed to generate description: {str(e)}"))
                self.root.after(0, lambda: self.desc_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.status_label.config(text="Ready"))
                
        # Start processing in background thread
        threading.Thread(target=process_caption, daemon=True).start()
        
    def update_description(self, caption):
        """Update the description text box"""
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(tk.END, caption)
        self.desc_button.config(state=tk.NORMAL)
        self.gen_button.config(state=tk.NORMAL)
        self.status_label.config(text="Description generated")
        
    def generate_image(self):
        """Generate a new image based on the description"""
        if not self.is_models_loaded:
            messagebox.showwarning("Warning", "Models are still loading")
            return
            
        # Get the description from text box
        description = self.desc_text.get(1.0, tk.END).strip()
        
        if not description:
            messagebox.showwarning("Warning", "Please generate a description first")
            return
            
        # Disable buttons during processing
        self.gen_button.config(state=tk.DISABLED)
        self.status_label.config(text="Generating image...")
        
        def process_image_generation():
            try:
                # Generate image using Stable Diffusion
                generated_image = self.image_gen_model(
                    description,
                    num_inference_steps=20,  # Adjust for quality vs speed
                    guidance_scale=7.5      # Controls how closely to follow the prompt
                ).images[0]
                
                # Update UI on main thread
                self.root.after(0, lambda: self.update_generated_image(generated_image))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", 
                    f"Failed to generate image: {str(e)}"))
                self.root.after(0, lambda: self.gen_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.status_label.config(text="Ready"))
                
        # Start processing in background thread
        threading.Thread(target=process_image_generation, daemon=True).start()
        
    def update_generated_image(self, image):
        """Update the generated image display"""
        # Convert PIL Image to PhotoImage
        photo = ImageTk.PhotoImage(image)
        self.gen_canvas.delete("all")
        self.gen_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        
        # Keep reference to prevent garbage collection
        self.gen_canvas.image = photo
        
        self.gen_button.config(state=tk.NORMAL)
        self.status_label.config(text="Image generated successfully")
        
    def reset_all(self):
        """Reset the entire application"""
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
    app = FreeImageToTextToImageGenerator(root)
    
    # Handle window closing
    def on_closing():
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
