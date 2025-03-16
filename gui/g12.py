import sys
import threading
import time
import os
import predict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QMessageBox, QVBoxLayout, QWidget, QDialog, QHBoxLayout,
    QListWidget, QListWidgetItem, QShortcut, QComboBox, QMenu
)
from PyQt5.QtGui import QPixmap, QFont, QKeySequence, QColor, QLinearGradient, QPainter, QIcon, QMovie
from PyQt5.QtCore import Qt, QTimer, QFileInfo, QPoint

def evaluate_image(image_path, model_type):
    time.sleep(15)
    if model_type == "Large Model":
        return predict.predict_large(image_path)
    elif model_type == "Mobile Model":
        return predict.predict_mobile(image_path)
    else:  # Small Model
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
        
        self.title_label = QLabel("Analysis Result", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font: bold 24px Arial;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        self.layout.addWidget(self.title_label)

        self.animation_label = QLabel(self)
        self.movie = QMovie("animation.gif")
        self.animation_label.setMovie(self.movie)
        self.animation_label.setAlignment(Qt.AlignCenter)
        self.animation_label.setStyleSheet("background: transparent;")
        self.layout.addWidget(self.animation_label)

        self.result_content = QWidget()
        self.result_content.setStyleSheet("background: transparent;")
        result_layout = QVBoxLayout(self.result_content)
        result_layout.setSpacing(20)
        
        self.real_label = QLabel("Real:", self)
        self.real_label.setStyleSheet("""
            font: 20px Arial; 
            color: #4CAF50;
            background: transparent;
        """)
        self.fake_label = QLabel("Fake:", self)
        self.fake_label.setStyleSheet("""
            font: 20px Arial;
            color: #F44336;
            background: transparent;
        """)
        
        result_layout.addWidget(self.real_label, 0, Qt.AlignCenter)
        result_layout.addWidget(self.fake_label, 0, Qt.AlignCenter)
        self.layout.addWidget(self.result_content)
        self.result_content.hide()

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

    def start_animation(self):
        self.movie.start()
        self.animation_label.show()
        self.result_content.hide()
        self.close_button.hide()

    def set_result(self, real_probability, fake_probability):
        QTimer.singleShot(0, lambda: self.movie.stop())
        self.animation_label.hide()
        self.title_label.setText("Result:")
        self.real_label.setText(f"Real: {real_probability:.2f}%")
        self.fake_label.setText(f"Fake: {fake_probability:.2f}%")
        self.result_content.show()
        self.close_button.show()

    def reset_results(self):
        self.title_label.setText("Analysis Result")
        self.real_label.setText("Real:")
        self.fake_label.setText("Fake:")
        self.close_button.hide()

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
        self.setWindowIcon(QIcon('logo1.png'))
        self.setWindowTitle("Image Real/Fake Classifier")
        self.setGeometry(100, 100, 1200, 800)
        self.current_theme = "dark"
        self.popup = ResultPopup(self)
        self.set_theme()
        self.history = []
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.main_layout.addWidget(left_panel, stretch=2)

        # Fine Tune Button
        self.fine_tune_btn = QPushButton("🔧 Fine Tune", self)
        self.fine_tune_btn.setStyleSheet("""
            QPushButton {
                font: bold 16px Arial;
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
                color: white;
                border-radius: 20px;
                border: 2px solid #FFFFFF;
                margin-bottom: 10px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #357a38; }
        """)
        self.fine_tune_btn.clicked.connect(self.open_fine_tune_file)
        left_layout.addWidget(self.fine_tune_btn, alignment=Qt.AlignCenter)

        # Model Selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Small Model", "Large Model", "Mobile Model"])
        self.model_combo.setStyleSheet("""
            QComboBox {
                font: 16px Arial;
                padding: 8px 12px;
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #E91E63);
                color: white;
                border: 2px solid #FFFFFF;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 2px solid rgba(255, 255, 255, 100);
            }
        """)
        left_layout.addWidget(self.model_combo, alignment=Qt.AlignCenter)

        # Image Canvas
        self.canvas = QLabel(self)
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setFixedSize(700, 500)
        left_layout.addWidget(self.canvas, alignment=Qt.AlignCenter)
        self.add_image_text()

        # Metadata
        self.meta_label = QLabel("", self)
        self.meta_label.setStyleSheet("color: rgb(255, 255, 255); font: 12px Arial;")
        self.meta_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.meta_label)

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
        left_layout.addWidget(self.load_button, alignment=Qt.AlignCenter)

        # Theme Toggle
        bottom_left = QWidget()
        bottom_left_layout = QHBoxLayout(bottom_left)
        bottom_left_layout.setContentsMargins(0, 10, 0, 0)
        
        self.theme_button = QPushButton("🌓", self)
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.setStyleSheet("""
            QPushButton {
                background-color: #6A6B6E;
                color: white;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 150);
                font-size: 24px;
            }
            QPushButton:hover { background-color: #2196F3; }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)
        bottom_left_layout.addWidget(self.theme_button)
        bottom_left_layout.addStretch()
        
        left_layout.addWidget(bottom_left)

        # Right Section
        right_container = QWidget()
        right_container.setLayout(QVBoxLayout())
        right_container.layout().setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(right_container, stretch=1)

        # History Toggle
        self.toggle_history_btn = QPushButton("▼ Hide History", self)
        self.toggle_history_btn.setStyleSheet("""
            QPushButton {
                font: bold 14px Arial;
                padding: 5px 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #E91E63);
                color: white;
                border-radius: 15px;
                border: 1px solid #FFFFFF;
                margin-bottom: 5px;
            }
            QPushButton:hover { background-color: #eb6143; }
        """)
        self.toggle_history_btn.clicked.connect(self.toggle_history_visibility)
        right_container.layout().addWidget(self.toggle_history_btn, 0, Qt.AlignCenter)

        # History List
        self.right_panel = QWidget()
        self.right_panel.setVisible(True)
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
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
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_context_menu)
        self.history_list.itemClicked.connect(self.re_evaluate_image)
        right_layout.addWidget(QLabel("📚 History:", self))
        right_layout.addWidget(self.history_list)
        
        right_container.layout().addWidget(self.right_panel)

        # Shortcuts
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
        else:
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
        self.canvas.setText("Drag/upload image")
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
            self.popup.reset_results()

            file_info = QFileInfo(file_path)
            meta_text = f"""
                📐 Dimensions: {pixmap.width()}x{pixmap.height()}
                💾 Size: {file_info.size()/1024:.1f} KB
                📅 Modified: {file_info.lastModified().toString('yyyy-MM-dd HH:mm')}
            """
            self.meta_label.setText(meta_text)

            self.temp_history_entry = f"{file_info.filePath()} - {time.strftime('%D %H:%M:%S')}"
            
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
        self.popup.start_animation()
        self.popup.show()
        self.animate_loading()

    def animate_loading(self):
        if self.is_loading:
            phases = ["Loading...", "Evaluating...", "Deciding..."]
            self.popup.title_label.setText(phases[self.loading_phase])
            self.loading_phase = (self.loading_phase + 1) % 3
            QTimer.singleShot(9000, self.animate_loading)

    def evaluate_and_show_result(self, file_path, model_type):
        real_probability, fake_probability = evaluate_image(file_path, model_type)
        self.is_loading = False
        
        result_text = (f"{self.temp_history_entry}\n"
                      f"Model: {model_type} | "
                      f"Real: {real_probability:.2f} | "
                      f"Fake: {fake_probability:.2f}")
        
        self.history_list.insertItem(0, QListWidgetItem(result_text))
        self.popup.set_result(real_probability, fake_probability)

    def toggle_history_visibility(self):
        if self.right_panel.isVisible():
            self.right_panel.hide()
            self.toggle_history_btn.setText("▲ Show History")
        else:
            self.right_panel.show()
            self.toggle_history_btn.setText("▼ Hide History")
            self.main_layout.setStretch(0, 2)

    def show_context_menu(self, pos):
        item = self.history_list.itemAt(pos)
        if item:
            menu = QMenu(self)
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self.delete_history_item(item))
            menu.exec_(self.history_list.mapToGlobal(pos))

    def delete_history_item(self, item):
        row = self.history_list.row(item)
        self.history_list.takeItem(row)

    def re_evaluate_image(self, item):
        first_line = item.text().split('\n')[0]
        file_path = first_line.split(' - ')[0]
        if os.path.exists(file_path):
            self.process_image(file_path)
        else:
            QMessageBox.warning(self, "Error", "The image file no longer exists.")

    def open_fine_tune_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select CSV File for Fine Tuning",
            "",
            "CSV Files (*.csv)"
        )
        if file_path:
            self.fineTune(file_path)

    def fineTune(self, csv_path):
        """Placeholder for fine tuning functionality"""
        print(f"Fine tuning initiated with: {csv_path}")
        # Add your fine tuning implementation here

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial"))
    window = ImageClassifierApp()
    window.show()
    sys.exit(app.exec_())