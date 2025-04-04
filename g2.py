import sys
import threading
import time
import predict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QMessageBox, QVBoxLayout, QWidget, QDialog, QHBoxLayout,
    QListWidget, QListWidgetItem, QShortcut, QComboBox
)
from PyQt5.QtGui import QPixmap, QFont, QKeySequence, QColor, QLinearGradient, QPainter
from PyQt5.QtCore import Qt, QTimer, QFileInfo, QPoint

def evaluate_image(image_path, model_type):
    if model_type == "Large Model":
        return predict.predict_large(image_path)
    elif model_type == "Mobile Model":
        return predict.predict_mobile(image_path)
    else:  # Small Model
        time.sleep(24)
        return predict.predict(image_path)

class ResultPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Result")
        self.setFixedSize(500, 300)
        self.setStyleSheet(parent.styleSheet())
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Title
        self.title_label = QLabel("Analysis Result", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font: bold 24px Arial;
                color: #FFFFFF;
                padding: 10px;
            }
        """)
        self.layout.addWidget(self.title_label)

        # Result Content
        self.result_content = QWidget()
        result_layout = QVBoxLayout(self.result_content)
        result_layout.setSpacing(20)
        
        self.real_label = QLabel("Real:", self)
        self.real_label.setStyleSheet("font: 20px Arial; color: #4CAF50;")
        self.fake_label = QLabel("Fake:", self)
        self.fake_label.setStyleSheet("font: 20px Arial; color: #F44336;")
        
        result_layout.addWidget(self.real_label, 0, Qt.AlignCenter)
        result_layout.addWidget(self.fake_label, 0, Qt.AlignCenter)
        self.layout.addWidget(self.result_content)

        # Close Button
        self.close_button = QPushButton("Close", self)
        self.close_button.setFixedSize(120, 40)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #E91E63);
                color: white;
                font: bold 16px Arial;
                border-radius: 20px;
                border: 2px solid #FFFFFF;
            }
            QPushButton:hover { background-color: #eb6143; }
            QPushButton:pressed { background-color: #a23a24; }
        """)
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button, 0, Qt.AlignCenter)
        self.close_button.hide()

    def set_result(self, real_probability, fake_probability):
        self.real_label.setText(f"Real: {real_probability:.2f}%")
        self.fake_label.setText(f"Fake: {fake_probability:.2f}%")
        self.close_button.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(QPoint(0, 0), QPoint(self.width(), self.height()))
        gradient.setColorAt(0, QColor(33, 150, 243))
        gradient.setColorAt(1, QColor(233, 30, 99))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

class ImageClassifierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Real/Fake Classifier")
        self.setGeometry(100, 100, 1200, 800)
        self.current_theme = "dark"
        
        # Initialize popup before theme setup
        self.popup = ResultPopup(self)
        
        self.set_theme()
        
        self.history = []
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left Panel
        left_panel = QWidget()
        self.layout = QVBoxLayout(left_panel)
        self.main_layout.addWidget(left_panel, stretch=2)

        # Model Selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Small Model", "Large Model", "Mobile Model"])
        self.model_combo.setStyleSheet("""
            QComboBox {
                font: 16px Arial;
                padding: 8px;
                border-radius: 15px;
                background-color: #FFFFFF;
                color: #333333;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.layout.addWidget(self.model_combo, alignment=Qt.AlignCenter)

        # Image Canvas
        self.canvas = QLabel(self)
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setFixedSize(700, 500)
        self.layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        self.add_image_text()

        # Metadata
        self.meta_label = QLabel("", self)
        self.meta_label.setStyleSheet("color: inherit; font: 12px Arial;")
        self.meta_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.meta_label)

        # Load Button
        self.load_button = QPushButton("📁 Load Image", self)
        self.load_button.setStyleSheet("""
            QPushButton {
                font: bold 18px Arial;
                padding: 15px 30px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #E91E63);
                color: white;
                border-radius: 25px;
                border: 2px solid #FFFFFF;
            }
            QPushButton:hover { background-color: #eb6143; }
            QPushButton:pressed { background-color: #a23a24; }
        """)
        self.load_button.clicked.connect(self.load_image)
        self.layout.addWidget(self.load_button, alignment=Qt.AlignCenter)

        # Theme Button
        self.theme_button = QPushButton("🌓 Switch Theme", self)
        self.theme_button.setStyleSheet("""
            QPushButton {
                font: bold 16px Arial;
                padding: 12px 24px;
                background-color: #6A6B6E;
                color: white;
                border-radius: 20px;
                border: 2px solid #FFFFFF;
            }
            QPushButton:hover { background-color: #2196F3; }
        """)
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
                font: 14px Arial;
            }
            QListWidget::item {
                border-bottom: 1px solid #DDDDDD;
                padding: 8px;
            }
        """)
        right_layout.addWidget(QLabel("📚 History:", self))
        right_layout.addWidget(self.history_list)

        # Keyboard Shortcuts
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.load_image)
        self.setAcceptDrops(True)
        self.is_loading = False
        self.loading_phase = 0

    def set_theme(self, theme=None):
        theme = theme or self.current_theme
        self.current_theme = theme
        if theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #943051;
                    color: white;
                    font-family: Arial;
                }
                QPushButton { background-color: #6A6B6E; }
                QListWidget { background-color: #4A4B4E; }
            """)
        else:  # Blue-black theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #1A1A2E;
                    color: white;
                    font-family: Arial;
                }
                QPushButton { background-color: #16213E; }
                QListWidget { background-color: #0F3460; }
            """)
        self.popup.setStyleSheet(self.styleSheet())

    def toggle_theme(self):
        self.set_theme("blue" if self.current_theme == "dark" else "dark")

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

            # Metadata
            file_info = QFileInfo(file_path)
            meta_text = f"""
                📐 Dimensions: {pixmap.width()}x{pixmap.height()}
                💾 Size: {file_info.size()/1024:.1f} KB
                📅 Modified: {file_info.lastModified().toString('yyyy-MM-dd HH:mm')}
            """
            self.meta_label.setStyleSheet("color: rgb(255, 255, 255);")
            self.meta_label.setText(meta_text)

            # Add to history
            history_entry = f"{file_info.fileName()} - {time.strftime('%H:%M:%S')}"
            self.history_list.insertItem(0, QListWidgetItem(history_entry))

            self.show_loading_popup()
            threading.Thread(
                target=self.evaluate_and_show_result,
                args=(file_path, self.model_combo.currentText()),
                daemon=True
            ).start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process image: {str(e)}")

    def show_loading_popup(self):
        self.is_loading = True
        self.loading_phase = 0
        self.popup.close_button.hide()
        self.popup.show()
        self.animate_loading()

    def animate_loading(self):
        if self.is_loading:
            phases = [
                "Loading...",
                "Evaluating...",
                "Deciding..."
            ]
            self.popup.title_label.setText(phases[self.loading_phase])
            self.loading_phase = (self.loading_phase + 1) % 3
            QTimer.singleShot(800, self.animate_loading)

    def evaluate_and_show_result(self, file_path, model_type):
        real_probability, fake_probability = evaluate_image(file_path, model_type)
        self.is_loading = False
        self.popup.set_result(real_probability, fake_probability)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial"))
    window = ImageClassifierApp()
    window.show()
    sys.exit(app.exec_())