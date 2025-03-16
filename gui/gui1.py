import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import threading
import time

# Placeholder for your machine learning model
def evaluate_image(image_path):
    # Simulate a delay for the machine learning model
    time.sleep(3)  # Replace this with your actual model's processing time
    # Replace this with your actual machine learning model
    # For now, it returns a random ratio between 0 and 1
    ratio = np.random.rand()
    return ratio

class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Real/Fake Classifier")
        self.root.geometry("1200x700")  # Set window size to 1200x800
        self.root.resizable(False,False)
        self.root.configure(bg="#8B0082")  # Purple-ish background for the main window

        # Create a canvas for dropping images
        self.canvas = tk.Canvas(root, bg="#6E33D5", width=700, height=500)  # Orange-ish background for the canvas
        self.canvas.pack(pady=20)

        # Label to display the result
        self.result_label = tk.Label(root, text="", font=("Lexend", 14), bg="#8B0082", fg="white")  # Purple-ish background, white text
        self.result_label.pack(pady=10)

        # Button to load image from file explorer
        self.load_button = tk.Button(
            root,
            text="Load Image",
            command=self.load_image,
            bg="#6E33D5",  # Orange-ish background
            fg="white",  # White text
            font=("Lexend", 12),
            relief=tk.FLAT
        )
        self.load_button.pack(pady=10)

        # Allow dragging and dropping images
        self.canvas.bind("<Button-1>", self.on_drop)
        self.canvas.bind("<B1-Motion>", self.on_drop)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

        # Variable to track loading state
        self.is_loading = False

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.process_image(file_path)

    def on_drop(self, event):
        try:
            file_path = event.data.strip()
            if file_path.endswith(('.png', '.jpg', '.jpeg')):
                self.process_image(file_path)
        
        except Exception as e:
            None

    def process_image(self, file_path):
        try:
            # Load and display the image
            image = Image.open(file_path)
            image.thumbnail((700, 500))  # Resize image to fit the canvas
            photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo

            # Show loading pop-up
            self.show_loading_popup()

            # Start evaluation in a separate thread
            threading.Thread(target=self.evaluate_and_show_result, args=(file_path,), daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {e}")

    def show_loading_popup(self):
        self.is_loading = True
        self.loading_popup = tk.Toplevel(self.root)
        self.loading_popup.title("Processing")
        self.loading_popup.geometry("300x100")
        self.loading_popup.configure(bg="#8B0082")  # Purple-ish background for the pop-up

        # Loading label with animated text
        self.loading_label = tk.Label(
            self.loading_popup,
            text="I'm thinking...",
            font=("Lexend", 14),
            bg="#8B0082",  # Purple-ish background
            fg="white"  # White text
        )
        self.loading_label.pack(pady=20)

        # Start the loading animation
        self.animate_loading()

    def animate_loading(self):
        if self.is_loading:
            current_text = self.loading_label.cget("text")
            if current_text.endswith("..."):
                self.loading_label.config(text="I'm thinking")
            else:
                self.loading_label.config(text=current_text + ".")
            self.root.after(500, self.animate_loading)  # Update every 500ms

    def evaluate_and_show_result(self, file_path):
        # Evaluate the image
        ratio = evaluate_image(file_path)
        result = "Real" if ratio > 0.5 else "Fake"

        # Close the loading pop-up
        self.is_loading = False
        self.loading_popup.destroy()

        # Show the result in a pop-up
        self.show_result_popup(result, ratio)

    def show_result_popup(self, result, ratio):
        result_popup = tk.Toplevel(self.root)
        result_popup.title("Result")
        result_popup.geometry("300x150")
        result_popup.configure(bg="#4B0082")  # Purple-ish background for the result pop-up

        # Display the result
        result_label = tk.Label(
            result_popup,
            text=f"Result: {result}\nRatio: {ratio:.2f}",
            font=("Lexend", 14),
            bg="#8B0082",  # Purple-ish background
            fg="white"  # White text
        )
        result_label.pack(pady=20)

        # Close button
        close_button = tk.Button(
            result_popup,
            text="Close",
            command=result_popup.destroy,
            bg="#6E33D5",  # Orange-ish background
            fg="white",  # White text
            font=("Lexend", 12),
            relief=tk.FLAT
        )
        close_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.mainloop()