

import backend as bk  # Import your backend module
import sounddevice as sd

import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QFileDialog, QComboBox, QLabel 


#  reqiurements of the app

# take input from user for speaker id, severity, type, condition as text
# select input device from the list of available devices
# start recording 
# select dataset path
# display the phrase to be spoken in a separate window

class audioWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio")
        self.setFixedSize(QSize(400, 200))
        self.layout = QVBoxLayout() 
        self.combo = QComboBox() 
        self.combo.addItem("Select Device")
        self.populate_input_devices()
        self.layout.addWidget(self.combo)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.deviceIndex = self.select_input_device()  # Moved this line to after self.combo is defined
        self.combo.setCurrentIndex(self.deviceIndex)
    def populate_input_devices(self):
        devices = sd.query_devices()
        input_devices = [f"{idx}: {device['name']}" for idx, device in enumerate(devices) if device['max_input_channels'] > 0]
        self.combo.addItems(input_devices)

    def select_input_device(self):
        device_index = self.combo.currentIndex()
        print(f"Selected input device: {bk.select_input_device(device_index)}")
        return device_index
class phraseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.take_count = 0
        self.phrase_index = 0
        self.setWindowTitle("Phrase")
        self.setFixedSize(QSize(400, 200))
        self.csv_path = bk.PhrasecsvPath
        print(self.csv_path)
        self.layout = QVBoxLayout() 
        self.phrases = QLabel()
        self.layout.addWidget(self.phrases) 
        self.status = QLabel()
        self.layout.addWidget(self.status)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.main = MainWindow()
        self.severeity = self.main.severity
        self.type_ = self.main.type_
        self.condition = self.main.condition
        self.deviceId = self.main.deviceId
        self.update_phrase()
        self.record()
    def record(self): 
            bk.run(self.severeity, self.type_, self.condition, self.deviceId) 
            self.status.setText(bk.status)
    def update_phrase(self):
        try:
            next_phrase = next(bk.get_phrase(self.csv_path))
            self.phrases.setText(next_phrase)
        except StopIteration:
            pass  # Handle the end of the phrases here, if necessary
class metadataWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metadata")
        self.setFixedSize(QSize(400, 200))
        self.layout = QVBoxLayout()
        self.severity = QLineEdit()
        self.type_ = QLineEdit()
        self.condition = QLineEdit() 
        self.severity.setPlaceholderText("Severity")
        self.type_.setPlaceholderText("Type")
        self.condition.setPlaceholderText("Condition")
        self.saveButton = QPushButton("Save", self)
        self.saveButton.setGeometry(100, 150, 200, 50)
        self.saveButton.clicked.connect(self.save_metadata)  
        self.layout.addWidget(self.saveButton)
        self.layout.addWidget(self.severity)
        self.layout.addWidget(self.type_)
        self.layout.addWidget(self.condition) 
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
    def save_metadata(self):
        self.severity = self.severity.text()
        self.type_ = self.type_.text()
        self.condition = self.condition.text()
        self.close()
     
            
class settingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(QSize(400, 200))
        self.metadata = metadataWindow() 
        self.audiosettings = audioWindow()
        self.deviceId = self.audiosettings.deviceIndex 
        self.severity = self.metadata.severity
        self.type_ = self.metadata.type_
        self.condition =  self.metadata.condition
        listButton = QPushButton("Input Devices", self)
        listButton.setGeometry(100, 100, 200, 50) 
        listButton.clicked.connect(self.audiosettings.show)
        setmetadataButton = QPushButton("Set Metadata", self)
        setmetadataButton.setGeometry(100, 150, 200, 50)
        setmetadataButton.clicked.connect(self.metadata.show)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dysscribe")
        self.setFixedSize(QSize(400, 200))
        recButton = QPushButton("Start Recording", self)
        recButton.setGeometry(100, 100, 200, 50)
        recButton.clicked.connect(self.start_recording)
        settingsButton = QPushButton("Settings", self)
        settingsButton.setGeometry(100, 150, 200, 50)
        settingsButton.clicked.connect(self.open_settings)
        self.settings = settingsWindow()
        self.type_ = self.settings.type_
        self.severity = self.settings.severity
        self.condition = self.settings.condition
        self.deviceId = self.settings.deviceId
        self.speaker_id = bk.get_next_id(bk.DataCsvPath, bk.recsdir)
    def start_recording(self):
        # Get speaker ID, severity, type, condit
        # ion 

        self.phrase = phraseWindow()
        self.phrase.show()
         
        
    def open_settings(self):
        self.settings = settingsWindow()
        self.settings.show()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()