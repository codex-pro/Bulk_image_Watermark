
import os
import sys
import glob
import ntpath
from PIL import Image
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLineEdit, QPushButton, QLabel, QProgressBar
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QFileDialog, QListWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot


class OverlayThread(QThread):

    def __init__(self, overlay, folder, signal):
        QThread.__init__(self)
        self.overlay = overlay
        self.folder = folder
        self.signal = signal

    def run(self):
        image = Image.open(self.overlay)
        image = image.resize((50, 50), Image.ANTIALIAS)
        image.save(self.overlay)
        self.folder += "/*"
        files = glob.glob(self.folder)
        file_count = len(files)
        for index, file in enumerate(files):
            try:
                create_overlay(self.overlay, file)
            except Exception as e:
                print(e)
            count = index + 1
            self.signal.emit({"value": (count/file_count)*100, "text": "Processing: {}".format(file)})
        self.signal.emit({"value": 100, "text": "Completed!"})


class MainWidget(QWidget):

    signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.signal.connect(self.slot)
        self.t = None
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("<h1>Overlay Creator v0.1</h1>"))
        overlay_layout = QHBoxLayout()
        self.overlay = QLineEdit()
        overlay_layout.addWidget(QLabel("OVERLAY"))
        overlay_layout.addWidget(self.overlay)
        choose_overlay = QPushButton("CHOOSE OVERLAY")
        choose_overlay.clicked.connect(self.choose_overlay_clicked)
        overlay_layout.addWidget(choose_overlay)
        main_layout.addLayout(overlay_layout)
        image_folder_layout = QHBoxLayout()
        image_folder_layout.addWidget(QLabel("IMAGES"))
        self.image = QLineEdit()
        image_folder_layout.addWidget(self.image)
        choose_image = QPushButton("CHOOSE IMAGES FOLDER")
        choose_image.clicked.connect(self.choose_image_clicked)
        image_folder_layout.addWidget(choose_image)
        main_layout.addLayout(image_folder_layout)
        apply = QPushButton("APPLY")
        apply.clicked.connect(self.apply_clicked)
        main_layout.addWidget(apply)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)
        self.status = QListWidget()
        main_layout.addWidget(self.status)
        self.setLayout(main_layout)

    @pyqtSlot(dict)
    def slot(self, value):
        self.progress.setVisible(True)
        self.progress.setValue(value["value"])
        self.status.addItem(QListWidgetItem(value["text"]))

    def choose_overlay_clicked(self):
        file = QFileDialog.getOpenFileName(self, "Choose Overlay file")
        file = file[0]
        self.overlay.setText(file)

    def choose_image_clicked(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose images directory")
        self.image.setText(folder)

    def apply_clicked(self):
        folder = self.image.text()
        overlay = self.overlay.text()
        self.t = OverlayThread(overlay, folder, self.signal)
        self.t.start()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 600, 600)
        self.setWindowTitle("Overlay Creator v0.1")
        self.setCentralWidget(MainWidget())


def create_overlay(overlay_image, original_image_path):
    bg = Image.open(original_image_path)
    fg = Image.open(overlay_image)
    width, height = bg.size
    # fg = fg.resize((50, 50), Image.LANCZOS)
    # fg.putalpha(70)
    bg.paste(fg, (int(width/2), int(height/2)), fg)
    if not os.path.exists("output"):
        os.makedirs("output")
    file_name = ntpath.basename(original_image_path)
    try:
        bg.save("output/{}".format(file_name), optimized=True)
    except OSError:
        bg = bg.convert("RGB")
        bg.save("output/{}".format(file_name), optimized=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
