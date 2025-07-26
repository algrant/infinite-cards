import sys
import os
from pathlib import Path
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QScrollArea,
    QGridLayout, QMessageBox
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer

class ImageChangeHandler(FileSystemEventHandler):
    def __init__(self, notify_callback):
        super().__init__()
        self.notify_callback = notify_callback

    def notify_wrapper(self, path):
        self.notify_callback(path)

    def is_interesting(self, path):
        return path.is_file() and path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']

    def on_modified(self, event):
        path = Path(event.src_path)
        if self.is_interesting(path):
            self.notify_wrapper(path)

    def on_created(self, event):
        path = Path(event.src_path)
        if self.is_interesting(path):
            self.notify_wrapper(path)

    def on_moved(self, event):
        path = Path(event.dest_path)
        if self.is_interesting(path):
            self.notify_wrapper(path)

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.setGeometry(200, 200, 1000, 700)

        self.current_folder = None
        self.image_paths = []
        self.thumbnail_labels = {}
        self.modified_images = set()

        # Layouts
        main_layout = QVBoxLayout(self)
        top_bar = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.status_label = QLabel("")
        self.reload_button = QPushButton("Reload Image")
        self.reload_button.setVisible(False)
        self.reload_button.clicked.connect(self.reload_current_image)

        select_btn = QPushButton("Select Folder")
        select_btn.clicked.connect(self.select_folder)
        top_bar.addWidget(select_btn)
        top_bar.addWidget(self.folder_label)
        top_bar.addWidget(self.status_label)
        top_bar.addStretch()
        top_bar.addWidget(self.reload_button)

        main_layout.addLayout(top_bar)

        # Thumbnails area
        thumbs_area = QScrollArea()
        thumbs_area.setWidgetResizable(True)
        thumbs_container = QWidget()
        self.thumbs_layout = QGridLayout(thumbs_container)
        thumbs_area.setWidget(thumbs_container)

        # Large image area
        self.large_image_label = QLabel("Select an image")
        self.large_image_label.setAlignment(Qt.AlignCenter)
        self.large_image_label.setMinimumSize(512, 512)

        content_layout = QHBoxLayout()
        content_layout.addWidget(thumbs_area, 1)
        content_layout.addWidget(self.large_image_label, 2)

        main_layout.addLayout(content_layout)

        self.observer = None
        self.current_large_image_path = None

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = Path(folder)
            self.folder_label.setText(f"Folder: {folder}")
            self.load_images()
            self.start_watching(folder)

    def load_images(self):
        self.clear_thumbnails()
        self.image_paths = [p for p in self.current_folder.iterdir() if p.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']]
        for i, img_path in enumerate(self.image_paths):
            thumbnail = self.make_thumbnail(img_path)
            label = QLabel()
            label.setPixmap(thumbnail)
            label.mousePressEvent = lambda e, p=img_path: self.show_large_image(p)
            self.thumbnail_labels[str(img_path)] = label
            self.thumbs_layout.addWidget(label, i // 2, i % 2)

    def clear_thumbnails(self):
        for i in reversed(range(self.thumbs_layout.count())):
            widget = self.thumbs_layout.itemAt(i).widget()
            self.thumbs_layout.removeWidget(widget)
            widget.deleteLater()
        self.thumbnail_labels.clear()

    def make_thumbnail(self, path):
        with Image.open(path) as im:
            im.thumbnail((128, 128))
            im = im.convert("RGBA")
            data = im.tobytes("raw", "RGBA")
            qimg = QImage(data, im.width, im.height, QImage.Format_RGBA8888)
            return QPixmap.fromImage(qimg)

    def show_large_image(self, path):
        self.current_large_image_path = path
        pixmap = QPixmap(str(path)).scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.large_image_label.setPixmap(pixmap)
        self.status_label.setText(f"Selected: {path.name}")
        self.reload_button.setVisible(False)

    def reload_current_image(self):
        if self.current_large_image_path:
            self.show_large_image(self.current_large_image_path)
            self.status_label.setText(f"Reloaded: {self.current_large_image_path.name}")
            self.reload_button.setVisible(False)

    def notify_file_modified(self, path):
        if self.current_large_image_path and str(path) == str(self.current_large_image_path):
            self.status_label.setText(f"Modified: {path.name}")
            self.reload_button.setVisible(True)

    def start_watching(self, folder):
        if self.observer:
            self.observer.stop()
            self.observer.join()

        handler = ImageChangeHandler(self.notify_file_modified)
        self.observer = Observer()
        self.observer.schedule(handler, folder, recursive=True)
        self.observer.start()

    def closeEvent(self, event):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())
