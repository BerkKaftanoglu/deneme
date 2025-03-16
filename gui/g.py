import sys
import threading
import time
import predict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QMessageBox, QVBoxLayout, QWidget, QDialog, QHBoxLayout,
    QListWidget, QListWidgetItem, QShortcut
)
from PyQt5.QtGui import QPixmap, QFont, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QFileInfo

def evaluate_image(image_path):
    return predict.predict(image_path)

class ResultPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Result")
        self.setFixedSize(400, 250)
        self.setStyleSheet(parent.styleSheet())

        self.layout = QVBoxLayout(self)
        
        self.result_label = QLabel("", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.result_label)
        
        self.close_button = QPushButton("Close", self)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6A6B6E;
                color: white;
                font-size: 18px;
                border-radius: 20px;
                border: none;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #eb6143; }
            QPushButton:pressed { background-color: #a23a24; }
            """
        )
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)
        self.close_button.hide()

    def set_result(self, real_probability, fake_probability):
        self.result_label.setText(
            f"Real: {real_probability:.2f}\n\nFake: {fake_probability:.2f}"
        )
        self.close_button.show()

class ImageClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Real/Fake Classifier")
        self.setGeometry(100, 100, 1200, 800)
        self.current_theme = "dark"
        self.set_theme()

        self.history = []
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left Panel
        left_panel = QWidget()
        self.layout = QVBoxLayout(left_panel)
        self.main_layout.addWidget(left_panel, stretch=2)

        # Image Canvas
        self.canvas = QLabel(self)
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setFixedSize(700, 500)
        self.layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        self.add_image_text()

        # Metadata
        self.meta_label = QLabel("", self)
        self.meta_label.setStyleSheet("color: inherit; font-size: 12px;")
        self.meta_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.meta_label)

        # Load Button
        self.load_button = QPushButton("📁 Load Image", self)
        self.load_button.setStyleSheet(
            "QPushButton { font-size: 18px; padding: 12px 24px; }"
        )
        self.load_button.clicked.connect(self.load_image)
        self.layout.addWidget(self.load_button, alignment=Qt.AlignCenter)

        # Theme Button
        self.theme_button = QPushButton("🌓 Switch Theme", self)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.layout.addWidget(self.theme_button)

        # Right Panel (History)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.main_layout.addWidget(right_panel, stretch=1)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                color: #333333;
                border-radius: 10px;
                padding: 10px;
            }
            QListWidget::item {
                border-bottom: 1px solid #DDDDDD;
                padding: 8px;
            }
        """)
        right_layout.addWidget(QLabel("📚 History:"))
        right_layout.addWidget(self.history_list)

        # Keyboard Shortcuts
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.load_image)
        self.setAcceptDrops(True)
        self.is_loading = False
        self.popup = ResultPopup(self)

    def set_theme(self, theme=None):
        theme = theme or self.current_theme
        self.current_theme = theme
        if theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #943051;
                    color: white;
                }
                QPushButton {
                    background-color: #6A6B6E;
                    border-radius: 20px;
                }
                QListWidget {
                    background-color: #4A4B4E;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F5F5F5;
                    color: #333333;
                }
                QPushButton {
                    background-color: #E0E0E0;
                    border-radius: 20px;
                }
                QListWidget {
                    background-color: #FFFFFF;
                    color: #333333;
                }
            """)

    def toggle_theme(self):
        self.set_theme("light" if self.current_theme == "dark" else "dark")
        self.popup.setStyleSheet(self.styleSheet())

    def add_image_text(self):
        self.canvas.setText("Drag & drop your image here\nor use the load button below")
        self.canvas.setFont(QFont("Arial", 24))
        self.canvas.setStyleSheet("color: rgba(255, 255, 255, 128);")

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
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.process_image(file_path)
                break

    def process_image(self, file_path):
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                raise ValueError("Invalid image file")
                
            pixmap = pixmap.scaled(700, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.canvas.setPixmap(pixmap)
            self.canvas.setText("")

            # Show metadata
            file_info = QFileInfo(file_path)
            meta_text = f"""
                📐 Dimensions: {pixmap.width()}x{pixmap.height()}
                💾 Size: {file_info.size()/1024:.1f} KB
                📅 Modified: {file_info.lastModified().toString('yyyy-MM-dd HH:mm')}
            """
            self.meta_label.setText(meta_text)

            # Add to history
            history_entry = f"{file_info.fileName()} - {time.strftime('%H:%M:%S')}"
            self.history_list.insertItem(0, QListWidgetItem(history_entry))

            self.show_loading_popup()
            threading.Thread(target=self.evaluate_and_show_result, args=(file_path,), daemon=True).start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process image: {str(e)}")

    def show_loading_popup(self):
        self.is_loading = True
        self.popup.result_label.setText("Analyzing image...")
        self.popup.close_button.hide()
        self.popup.show()
        self.animate_loading()

    def animate_loading(self):
        if self.is_loading:
            dots = (self.popup.result_label.text().count('.') % 3) + 1
            self.popup.result_label.setText("Analyzing image" + "." * dots)
            QTimer.singleShot(500, self.animate_loading)

    def evaluate_and_show_result(self, file_path):
        real_probability, fake_probability = evaluate_image(file_path)
        self.is_loading = False
        self.popup.set_result(real_probability, fake_probability)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageClassifierApp()
    window.show()
    sys.exit(app.exec_())