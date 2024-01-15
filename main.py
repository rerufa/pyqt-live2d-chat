from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from dotenv import load_dotenv
load_dotenv()
import os
import common


class SettingsWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Settings Window")
        # layout settings
        layout = QVBoxLayout()
        self.resize(900, 600)
        self.layout = layout
        self.setLayout(layout)
        # llm box layout
        self.llm_layout = QGridLayout()
        self.layout.addLayout(self.llm_layout)
        # azure
        azure_checkbox = QCheckBox("Azure")
        azure_checkbox.setChecked(True)
        azure_model = os.environ.get("AZURE_MODEL")
        azure_endpoint = QLineEdit(os.environ.get("AZURE_ENDPOINT"))
        azure_api_key = QLineEdit("AZURE_API_KEY")
        azure_model = QLineEdit(os.environ.get("AZURE_MODEL"))
        azure_prefix = QLineEdit(os.environ.get("AZURE_PREFIX"))
        self.azure_inputs = (azure_checkbox, azure_endpoint, azure_api_key, azure_model, azure_prefix)
        row = common.IterCount(0)
        self.llm_layout.addWidget(azure_checkbox, row.val, 0, 1, 1)
        self.llm_layout.addWidget(QLabel("Endpoint"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(azure_endpoint, row.val, 1, 1, 1)
        self.llm_layout.addWidget(QLabel("Api Key"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(azure_api_key, row.val, 1, 1, 1)
        self.llm_layout.addWidget(QLabel("Model"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(azure_model, row.val, 1, 1, 1)
        self.llm_layout.addWidget(QLabel("Prefix"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(azure_prefix, row.val, 1, 1, 1)
        # gemini
        gemini_checkox = QCheckBox("Gemini")
        gemini_checkox.setChecked(True)
        gemini_endpoint = QLineEdit(os.environ.get("GEMINI_ENDPOINT"))
        gemini_api_key = QLineEdit("GEMINI_API_KEY")
        gemini_model = QLineEdit(os.environ.get("GEMINI_MODEL"))
        gemini_prefix = QLineEdit(os.environ.get("GEMINI_PREFIX"))
        self.gemini_inputs = (gemini_checkox, gemini_endpoint, gemini_api_key, gemini_model, gemini_prefix)
        self.llm_layout.addWidget(gemini_checkox, next(row), 0, 1, 1)
        self.llm_layout.addWidget(QLabel("Endpoint"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(gemini_endpoint, row.val, 1, 1, 1)
        self.llm_layout.addWidget(QLabel("Api Key"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(gemini_api_key, row.val, 1, 1, 1)
        self.llm_layout.addWidget(QLabel("Model"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(gemini_model, row.val, 1, 1, 1)
        self.llm_layout.addWidget(QLabel("Prefix"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(gemini_prefix, row.val, 1, 1, 1)
        # GPT
        gpt_checkox = QCheckBox("GPT")
        gpt_checkox.setChecked(False)
        gpt_endpoint = QLineEdit(os.environ.get("GPT_ENDPOINT"))
        gpt_api_key = QLineEdit("GPT_API_KEY")
        gpt_model = QLineEdit(os.environ.get("GPT_MODEL"))
        gpt_prefix = QLineEdit(os.environ.get("gpt_PREFIX"))
        self.gpt_inputs = (gpt_checkox, gpt_endpoint, gpt_api_key, gpt_model, gpt_prefix)
        self.llm_layout.addWidget(gpt_checkox, next(row), 0, 1, 1)
        self.llm_layout.addWidget(QLabel("Endpoint"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(gpt_endpoint, row.val, 1, 1, 1)
        self.llm_layout.addWidget(QLabel("Api Key"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(gpt_api_key, row.val, 1, 1, 1)
        self.llm_layout.addWidget(QLabel("Model"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(gpt_model, row.val, 1, 1, 1)
        self.llm_layout.addWidget(QLabel("Prefix"), next(row), 0, 1, 1)
        self.llm_layout.addWidget(gpt_prefix, row.val, 1, 1, 1)
        # tts layout
        self.tts_layout = QGridLayout()
        tts_endpoint = QLineEdit(os.environ.get("TTS_ENDPOINT"))
        self.tts_layout.addWidget(QLabel("TTS Endpoint"), 0, 0, 1, 1)
        self.tts_layout.addWidget(tts_endpoint, 0, 1, 1, 1)
        self.layout.addLayout(self.tts_layout)
        # live2d layout
        self.live2d_layout = QGridLayout()
        live2d_endpoint = QLineEdit(os.environ.get("LIVE2D_ENDPOINT"))
        self.live2d_layout.addWidget(QLabel("Live2D Endpoint"), 0, 0, 1, 1)
        self.live2d_layout.addWidget(live2d_endpoint, 0, 1, 1, 1)
        self.layout.addLayout(self.live2d_layout)
        # jump button
        start_button = QPushButton("Start")
        start_button.setFixedSize(880, 100)
        start_button.clicked.connect(self.jump)
        self.layout.addWidget(start_button)

    
    def jump(self) -> None:
        if self.azure_inputs[0].isChecked():
            os.environ["IS_AZURE"] = "True"
            os.environ["AZURE_ENDPOINT"] = self.azure_inputs[1].text()
            os.environ["AZURE_API_KEY"] = self.azure_inputs[2].text()
            os.environ["AZURE_MODEL"] = self.azure_inputs[3].text()
            os.environ["AZURE_PREFIX"] = self.azure_inputs[4].text()
        elif self.gemini_inputs[0].isChecked():
            os.environ["IS_GEMINI"] = "True"
            os.environ["GEMINI_ENDPOINT"] = self.gemini_inputs[1].text()
            os.environ["GEMINI_API_KEY"] = self.gemini_inputs[2].text()
            os.environ["GEMINI_MODEL"] = self.gemini_inputs[3].text()
            os.environ["GEMINI_PREFIX"] = self.gemini_inputs[4].text()
        elif self.gpt_inputs[0].isChecked():
            os.environ["IS_GPT"] = "True"
            os.environ["GPT_ENDPOINT"] = self.gpt_inputs[1].text()
            os.environ["GPT_API_KEY"] = self.gpt_inputs[2].text()
            os.environ["GPT_MODEL"] = self.gpt_inputs[3].text()
            os.environ["GPT_PREFIX"] = self.gpt_inputs[4].text()
        os.environ["TTS_ENDPOINT"] = self.tts_layout.itemAt(1).widget().text()
        os.environ["LIVE2D_ENDPOINT"] = self.live2d_layout.itemAt(1).widget().text()
        self.hide()
        self.next_window = MainWindow()
        self.next_window.show()


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Main Window")
        self.resize(500, 800)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            # Qt.WindowType.WindowStaysOnTopHint
            Qt.WindowType.FramelessWindowHint 
            # Qt.WindowType.WindowTransparentForInput
        )
        # layout setting
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # web window setting
        self.web_window = QWebEngineView(self)
        self.web_window.page().setBackgroundColor(Qt.GlobalColor.transparent)
        self.web_window.load(QUrl(os.environ.get("LIVE2D_ENDPOINT")))
        # text edit setting
        self.text_edit = QTextEdit(self)
        self.text_edit.setFixedSize(QSize(500, 200))
        self.text_edit.setHtml("小鸣也爱无所事事哟~")
        self.text_edit.setStyleSheet(
            "background-image: url(resources/chat.png);\
            background-position: top left;\
            background-repeat: repeat-xy;\
            color: black;\
            font-size: 15px;\
            font-family: 'Microsoft YaHei';\
            padding: 8px 28px 5px;"
            )
        self.text_edit.setFrameStyle(0) # 0 is invisible
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.web_window)


if __name__ == "__main__":
    app = QApplication([])
    window = SettingsWindow()
    window.show()
    app.exec()