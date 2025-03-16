import sys
import threading
import numpy as np
import time
import predict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QMessageBox, QVBoxLayout, QWidget, QDialog
)
from PyQt5.QtGui import QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QTimer

def evaluate_image(image_path):
    # time.sleep(5)
    return predict.predict(image_path)

class ResultPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Result")
        self.setFixedSize(400, 250)  # Fixed size for the pop-up
        self.setStyleSheet("background-color: #943051; color: white; font-size: 18px;")

        # Layout
        self.layout = QVBoxLayout(self)

        # Label to display the result
        self.result_label = QLabel("", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.result_label)
        
        # Close button (initially hidden)
        self.close_button = QPushButton("Close", self)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6A6B6E;
                color: white;
                font-size: 18px;
                border-radius: 20;
                border: none;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #eb6143;  /* Slightly lighter on hover */
            }
            QPushButton:pressed {
                background-color: #a23a24;  /* Darker when pressed */
            }
            """
        )
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)
        self.close_button.hide()  # Hide the button initially

    def set_result(self, real_probability, fake_probability):
        # Update the label with the result
        self.result_label.setText(
            f"Real: {real_probability:.2f}\n\nFake: {fake_probability:.2f}"
        )
        self.close_button.show()  # Show the close button

class ImageClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Real/Fake Classifier")
        self.setGeometry(100, 100, 800, 800)  # Set window size to 800x800
        self.setStyleSheet("background-color: #943051;")

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Canvas (QLabel) for displaying the image
        self.canvas = QLabel(self)
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setFixedSize(700, 500)  # Set canvas size
        self.layout.addWidget(self.canvas, alignment=Qt.AlignCenter)

        # Add "Image" text with 50% opacity to the canvas
        self.add_image_text()

        # Result label
        self.result_label = QLabel("", self)
        self.result_label.setStyleSheet("color: white; font-size: 14px;")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.result_label)

        # Load image button
        self.load_button = QPushButton("Load Image", self)
        self.load_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6A6B6E;
                color: white;
                font-size: 18px;
                border-radius: 20px;
                border: none;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #eb6143;  /* Slightly lighter on hover */
            }
            QPushButton:pressed {
                background-color: #a23a24;  /* Darker when pressed */
            }
            """
        )
        self.load_button.clicked.connect(self.load_image)
        self.layout.addWidget(self.load_button, alignment=Qt.AlignCenter)

        # Allow dragging and dropping images
        self.setAcceptDrops(True)

        # Variable to track loading state
        self.is_loading = False

        # Single pop-up for loading and result
        self.popup = ResultPopup(self)

    def add_image_text(self):
        # Create a semi-transparent text overlay
        self.canvas.setText("Drag & drop your image here\nor use the load button below")
        self.canvas.setFont(QFont("Arial", 24))
        self.canvas.setStyleSheet(
            "background-color: transparent; color: rgba(255, 255, 255, 128);"  # 50% opacity
        )

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.process_image(file_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.png', '.jpg', '.jpeg')):
                self.process_image(file_path)
                break

    def process_image(self, file_path):
        try:
            # Load and display the image
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(700, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.canvas.setPixmap(pixmap)
            self.canvas.setText("")  # Remove the "Image" text

            # Show loading pop-up
            self.show_loading_popup()

            # Start evaluation in a separate thread
            threading.Thread(target=self.evaluate_and_show_result, args=(file_path,), daemon=True).start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process image: {e}")

    def show_loading_popup(self):
        self.is_loading = True
        self.popup.result_label.setText("I'm thinking...")
        self.popup.close_button.hide()  # Hide the close button during loading
        self.popup.show()

        # Start the loading animation
        self.animate_loading()

    def animate_loading(self):
        if self.is_loading:
            current_text = self.popup.result_label.text()
            if current_text.endswith("..."):
                self.popup.result_label.setText("I'm thinking")
            else:
                self.popup.result_label.setText(current_text + ".")
            QTimer.singleShot(500, self.animate_loading)  # Update every 500ms

    def evaluate_and_show_result(self, file_path):
        # Evaluate the image
        real_probability, fake_probability = evaluate_image(file_path)

        # Stop the loading animation
        self.is_loading = False

        # Update the pop-up with the result
        self.popup.set_result(real_probability, fake_probability)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageClassifierApp()
    window.show()
    sys.exit(app.exec_())