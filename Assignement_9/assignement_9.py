import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw
import io
import base64
import requests
import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class ProductDescriptionGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Description Generator")
        self.root.geometry("1200x700")

        # Variables
        self.images = []
        self.image_paths = []
        self.current_image_index = 0
        self.current_image = None
        self.current_annotation = None
        self.annotation_mode = False
        self.annotation_points = []
        self.annotation_id = None
        self.annotations = {}
        self.display_image = None
        self.scale_x = 1.0
        self.scale_y = 1.0

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(left_frame, bg="white", width=600, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.start_annotation)
        self.canvas.bind("<B1-Motion>", self.draw_annotation)
        self.canvas.bind("<ButtonRelease-1>", self.end_annotation)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        ctrl_frame = tk.Frame(right_frame)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(ctrl_frame, text="Load Images", command=self.load_images).pack(fill=tk.X)
        tk.Button(ctrl_frame, text="Clear All", command=self.clear_all).pack(fill=tk.X, pady=(5, 0))

        nav_frame = tk.Frame(ctrl_frame)
        nav_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Button(nav_frame, text="Previous", command=self.previous_image).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(nav_frame, text="Next", command=self.next_image).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.annotation_btn = tk.Button(ctrl_frame, text="Enable Annotation", command=self.toggle_annotation)
        self.annotation_btn.pack(fill=tk.X, pady=(5, 0))

        tk.Label(right_frame, text="User Input (Optional):").pack(anchor=tk.W)
        self.user_input = tk.Text(right_frame, height=3)
        self.user_input.pack(fill=tk.X, pady=(0, 10))

        tk.Label(right_frame, text="Generated Description:").pack(anchor=tk.W)
        self.description_area = tk.Text(right_frame, height=8, wrap=tk.WORD)
        self.description_area.pack(fill=tk.X, pady=(0, 10))

        tk.Label(right_frame, text="Marketing Slogan:").pack(anchor=tk.W)
        self.slogan_area = tk.Text(right_frame, height=3, wrap=tk.WORD)
        self.slogan_area.pack(fill=tk.X, pady=(0, 10))

        self.generate_btn = tk.Button(right_frame, text="Generate Description", command=self.generate_descriptions)
        self.generate_btn.pack(fill=tk.X, pady=(5, 0))

        self.print_btn = tk.Button(right_frame, text="Print to PDF", command=self.print_to_pdf)
        self.print_btn.pack(fill=tk.X, pady=(5, 0))

        self.exit_btn = tk.Button(right_frame, text="Exit Application", command=self.exit_application)
        self.exit_btn.pack(fill=tk.X, pady=(5, 0))

        self.status_label = tk.Label(right_frame, text="", fg="blue")
        self.status_label.pack(fill=tk.X, pady=(5, 0))

        self.thumbnail_frame = tk.Frame(left_frame)
        self.thumbnail_frame.pack(fill=tk.X, pady=(10, 0))
        tk.Label(self.thumbnail_frame, text="Image Gallery:").pack(anchor=tk.W)

    def load_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Product Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )

        if not file_paths:
            return

        self.images = []
        self.image_paths = list(file_paths)
        self.current_image_index = 0
        self.annotations = {}

        for path in file_paths:
            img = Image.open(path)
            self.images.append(img)

        self.create_thumbnail_gallery()
        self.show_current_image()

    def create_thumbnail_gallery(self):
        for widget in self.thumbnail_frame.winfo_children():
            if widget != self.thumbnail_frame.winfo_children()[0]:
                widget.destroy()

        thumbnail_frame = tk.Frame(self.thumbnail_frame)
        thumbnail_frame.pack(fill=tk.X)

        for i, img in enumerate(self.images):
            thumbnail = img.copy()
            thumbnail.thumbnail((80, 80), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(thumbnail)

            btn = tk.Button(
                thumbnail_frame,
                image=photo,
                command=lambda idx=i: self.select_image(idx),
                width=80,
                height=80
            )
            btn.image = photo
            btn.pack(side=tk.LEFT, padx=5)

            label = tk.Label(thumbnail_frame, text=str(i+1), font=("Arial", 8))
            label.place(x=5, y=5)

    def select_image(self, index):
        self.current_image_index = index
        self.show_current_image()

    def show_current_image(self):
        if not self.images:
            return

        self.current_image = self.images[self.current_image_index].copy()

        if self.current_image_index not in self.annotations:
            self.annotations[self.current_image_index] = Image.new("RGBA", self.current_image.size, (0, 0, 0, 0))

        self.current_annotation = self.annotations[self.current_image_index].copy()

        self.display_image = self.current_image.copy()
        self.display_image.thumbnail((600, 400), Image.Resampling.LANCZOS)

        original_width, original_height = self.current_image.size
        display_width, display_height = self.display_image.size

        self.scale_x = original_width / display_width
        self.scale_y = original_height / display_height

        annotated_img = self.display_image.copy()

        if self.current_annotation and any(pixel[3] > 0 for pixel in self.current_annotation.getdata()):
            annotated_img = self.display_image.copy()
            annotation_scaled = self.current_annotation.copy()
            annotation_scaled.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)

            if annotation_scaled.mode != 'RGBA':
                annotation_scaled = annotation_scaled.convert('RGBA')

            annotated_img.paste(annotation_scaled, (0, 0), annotation_scaled)

        self.photo = ImageTk.PhotoImage(annotated_img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.status_label.config(text=f"Image {self.current_image_index + 1} of {len(self.images)}")

    def previous_image(self):
        if len(self.images) > 1:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.show_current_image()

    def next_image(self):
        if len(self.images) > 1:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.show_current_image()

    def toggle_annotation(self):
        self.annotation_mode = not self.annotation_mode
        self.annotation_btn.config(
            text="Disable Annotation" if self.annotation_mode else "Enable Annotation"
        )

    def start_annotation(self, event):
        if not self.annotation_mode:
            return
        self.annotation_points = [(event.x, event.y)]

    def draw_annotation(self, event):
        if not self.annotation_mode:
            return

        self.annotation_points.append((event.x, event.y))

        if len(self.annotation_points) > 1:
            self.canvas.delete(self.annotation_id)
            self.annotation_id = self.canvas.create_line(
                self.annotation_points,
                fill="red",
                width=3,
                smooth=True
            )

    def end_annotation(self, event):
        if not self.annotation_mode:
            return

        original_width, original_height = self.current_image.size
        display_width, display_height = self.display_image.size

        scale_x = original_width / display_width
        scale_y = original_height / display_height

        scaled_points = [
            (int(x * scale_x), int(y * scale_y))
            for x, y in self.annotation_points
        ]

        draw = ImageDraw.Draw(self.current_annotation)
        draw.line(scaled_points, fill=(255, 0, 0, 200), width=3)

        self.annotations[self.current_image_index] = self.current_annotation

        self.show_current_image()

        self.annotation_points = []
        self.annotation_id = None

    def clear_all(self):
        self.images = []
        self.image_paths = []
        self.current_image_index = 0
        self.current_image = None
        self.current_annotation = None
        self.annotations = {}
        self.canvas.delete("all")
        self.description_area.delete(1.0, tk.END)
        self.slogan_area.delete(1.0, tk.END)
        self.user_input.delete(1.0, tk.END)
        self.status_label.config(text="")

        for widget in self.thumbnail_frame.winfo_children():
            if widget != self.thumbnail_frame.winfo_children()[0]:
                widget.destroy()

    def generate_descriptions(self):
        if not self.current_image:
            messagebox.showwarning("No Image", "Please load an image first")
            return

        user_text = self.user_input.get(1.0, tk.END).strip()

        try:
            # Create image with annotations
            img_with_annotations = self.current_image.copy()
            if self.current_annotation:
                img_with_annotations.paste(self.current_annotation, (0, 0), self.current_annotation)

            # Convert image to base64
            img_buffer = io.BytesIO()
            img_with_annotations.save(img_buffer, format="PNG")
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

            # Prepare prompt
            prompt = "Describe this product in detail and create a marketing slogan. "
            if user_text:
                prompt += f"Additional context: {user_text}. "

            # Configuration - users should set these in environment variables
            api_url = os.getenv("LLM_API_URL", "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large")
            api_key = os.getenv("LLM_API_KEY")

            if not api_key:
                messagebox.showerror("Error", "LLM_API_KEY environment variable not set")
                return

            headers = {"Authorization": f"Bearer {api_key}"}

            payload = {
                "inputs": img_base64,
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.7
                }
            }

            response = requests.post(api_url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "No description generated")
                else:
                    generated_text = str(result)

                lines = generated_text.split('\n')
                description = lines[0] if lines else "Product description not available"
                slogan = lines[1] if len(lines) > 1 else ""

                self.description_area.delete(1.0, tk.END)
                self.description_area.insert(tk.END, description)

                self.slogan_area.delete(1.0, tk.END)
                self.slogan_area.insert(tk.END, slogan)
            elif response.status_code == 503:
                messagebox.showwarning("Model Loading",
                    "Model is currently loading. This may take 1-2 minutes. Please try again shortly.")
            elif response.status_code == 429:
                messagebox.showwarning("Rate Limited",
                    "Rate limit exceeded. Please wait before trying again.")
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Unknown error occurred")
                except json.JSONDecodeError:
                    error_msg = response.text or f"HTTP {response.status_code}"

                messagebox.showerror("API Error", f"Failed to generate description: {error_msg}")

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to the API. Please check your internet connection.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate description: {str(e)}")

    def print_to_pdf(self):
        if not self.current_image:
            messagebox.showwarning("No Image", "Please load an image first")
            return

        filename = simpledialog.askstring("Save PDF", "Enter PDF filename (without .pdf):", initialvalue="product_description")
        if not filename:
            return

        if not filename.endswith('.pdf'):
            filename += '.pdf'

        try:
            c = pdf_canvas.Canvas(filename, pagesize=letter)
            width, height = letter

            img_path = self.image_paths[self.current_image_index]
            img = Image.open(img_path)
            max_width = 400
            max_height = 400
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            temp_img_path = "temp_image.png"
            img.save(temp_img_path)

            c.drawImage(temp_img_path, 50, height - 250, width=400, height=400, preserveAspectRatio=True)

            styles = getSampleStyleSheet()
            c.drawString(50, height - 300, "Product Description:")
            description_text = self.description_area.get(1.0, tk.END).strip()
            p = Paragraph(description_text, styles['Normal'])
            p.wrap(500, 200)
            p.drawOn(c, 50, height - 350)

            c.drawString(50, height - 400, "Marketing Slogan:")
            slogan_text = self.slogan_area.get(1.0, tk.END).strip()
            p = Paragraph(slogan_text, styles['Normal'])
            p.wrap(500, 100)
            p.drawOn(c, 50, height - 450)

            user_input_text = self.user_input.get(1.0, tk.END).strip()
            if user_input_text:
                c.drawString(50, height - 500, "User Input:")
                p = Paragraph(user_input_text, styles['Normal'])
                p.wrap(500, 100)
                p.drawOn(c, 50, height - 550)

            if self.current_annotation and any(pixel[3] > 0 for pixel in self.current_annotation.getdata()):
                c.drawString(50, height - 600, "Annotations: Red markings indicate target product areas.")

            c.showPage()
            c.save()

            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)

            messagebox.showinfo("Success", f"PDF saved as {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")

    def exit_application(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductDescriptionGenerator(root)
    root.mainloop()
