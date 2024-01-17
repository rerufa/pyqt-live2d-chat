from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from dotenv import load_dotenv
load_dotenv()
import os
import common
import sys


def set_layout_visibility(layout: QLayout, visible: bool) -> None:
    for i in range(layout.count()):
        layout.itemAt(i).widget().setVisible(visible)


class SettingsWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Settings Window")
        # layout settings
        self.layout = QVBoxLayout(self)
        self.resize(900, 600)
        self.setLayout(self.layout)
        # llm box layout
        self.llm_layout = QGridLayout()
        self.layout.addLayout(self.llm_layout)
        # azure
        self.azure_inputs = self.set_llm_config_widget(self.layout, "AZURE")
        # gemini
        self.gemini_inputs = self.set_llm_config_widget(self.layout, "GEMINI")
        # GPT
        self.gpt_inputs = self.set_llm_config_widget(self.layout, "GPT", checked=False)
        # live2d layout
        self.live2d_layout = QGridLayout()
        live2d_endpoint = QLineEdit(os.environ.get("LIVE2D_ENDPOINT"))
        self.live2d_layout.addWidget(QLabel("Live2D Endpoint"), 0, 0, 1, 1)
        self.live2d_layout.addWidget(live2d_endpoint, 0, 1, 1, 1)
        self.layout.addLayout(self.live2d_layout)
        # tts layout
        self.tts_layout = QGridLayout()
        tts_endpoint = QLineEdit(os.environ.get("TTS_ENDPOINT"))
        self.tts_checkbox = QCheckBox("TTS")
        self.tts_checkbox.setChecked(True)
        self.tts_layout.addWidget(self.tts_checkbox, 0, 0, 1, 1)
        self.tts_layout.addWidget(QLabel("TTS Endpoint"), 0, 1, 1, 1)
        self.tts_layout.addWidget(tts_endpoint, 0, 2, 1, 1)
        self.layout.addLayout(self.tts_layout)
        self.dialog_checkbox = QCheckBox("Show Dialog Box")
        self.dialog_checkbox.setChecked(True)
        self.layout.addWidget(self.dialog_checkbox)
        # jump button
        start_button = QPushButton("Start")
        start_button.setFixedSize(880, 100)
        start_button.clicked.connect(self.jump)
        self.layout.addWidget(start_button)
    
    def set_llm_config_widget(self, layout: QLayout,llm_name: str, checked: bool=True) -> tuple[QCheckBox, QLineEdit, QLineEdit, QLineEdit, QLineEdit]:
        checkbox = QCheckBox(llm_name)
        checkbox.setChecked(checked)
        model = os.environ.get(f"{llm_name}_MODEL")
        endpoint = QLineEdit(os.environ.get(f"{llm_name}_ENDPOINT"))
        api_key = QLineEdit(f"{llm_name}_API_KEY")
        model = QLineEdit(os.environ.get(f"{llm_name}_MODEL"))
        prefix = QLineEdit(os.environ.get(f"{llm_name}_PREFIX"))
        inputs = (checkbox, endpoint, api_key, model, prefix)
        layout.addWidget(checkbox)
        llm_layout = QGridLayout()
        layout.addLayout(llm_layout)
        row = common.IterCount(0)
        llm_layout.addWidget(QLabel("Endpoint"), next(row), 0, 1, 1)
        llm_layout.addWidget(endpoint, row.val, 1, 1, 1)
        llm_layout.addWidget(QLabel("Api Key"), next(row), 0, 1, 1)
        llm_layout.addWidget(api_key, row.val, 1, 1, 1)
        llm_layout.addWidget(QLabel("Model"), next(row), 0, 1, 1)
        llm_layout.addWidget(model, row.val, 1, 1, 1)
        llm_layout.addWidget(QLabel("Prefix"), next(row), 0, 1, 1)
        llm_layout.addWidget(prefix, row.val, 1, 1, 1)
        checkbox.stateChanged.connect(lambda: set_layout_visibility(llm_layout, checkbox.isChecked()))
        if not checked: set_layout_visibility(llm_layout, False)
        return inputs
    
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
        os.environ["USE_TTS"] = str(self.tts_checkbox.isChecked())
        os.environ["SHOW_DIALOG"] = str(self.dialog_checkbox.isChecked())
        self.hide()
        self.next_window = MainWindow()
        self.next_window.show()


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Main Window")
        self.resize(500, 800)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setWindowFlags(
        #     # Qt.WindowType.WindowStaysOnTopHint
        #     Qt.WindowType.FramelessWindowHint 
        #     # Qt.WindowType.WindowTransparentForInput
        # )
        # layout setting
        self.layout = QGridLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.live2d_layout = QVBoxLayout()
        self.layout.addLayout(self.live2d_layout, 0, 0, 1, 1)
        # web window setting
        self.web_window = QWebEngineView(self)
        self.web_window.page().setBackgroundColor(Qt.GlobalColor.transparent)
        self.web_window.load(QUrl(os.environ.get("LIVE2D_ENDPOINT")))
        # text edit setting
        self.text_edit = QTextEdit(self)
        self.text_edit.setFixedSize(500, 200)
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
        self.live2d_layout.addWidget(self.text_edit)
        self.live2d_layout.addWidget(self.web_window)
        # chat box 
        self.chat_layout = QVBoxLayout()
        self.layout.addLayout(self.chat_layout, 0, 1, 1, 1)
        self.list_widget = QListWidget()
        self.list_widget.setFixedSize(500, 750)
        self.chat_layout.addWidget(self.list_widget)
        # 创建输入框
        self.input_box = QLineEdit()
        self.input_box.setFixedSize(500, 50)
        # 添加控件到窗口
        self.chat_layout.addWidget(self.input_box)
        self.submit_button = QPushButton("Submit")
        self.chat_layout.addWidget(self.submit_button)
        # 连接信号
        self.submit_button.clicked.connect(self.on_submit_pressed)
        self.input_box.returnPressed.connect(self.on_submit_pressed)

    def on_submit_pressed(self) -> None:
        # 获取输入文本
        text = self.input_box.text()
        if text.strip() == "":return
        # 将文本添加到列表控件
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(QSize(400, 60))
        self.list_widget.setItemWidget(item, MyChatBubble(text, Qt.AlignmentFlag.AlignRight))
        # 清空输入框
        self.input_box.clear()
        self.lru_list_clean()
        # listwidget to bottom
        self.list_widget.scrollToBottom()
    
    def lru_list_clean(self) -> None:
        while self.list_widget.count() > 30:
            self.list_widget.takeItem(0)


class MyChatBubble(QWidget):
    def __init__(self, message: str, align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 50)
        self.message = message
        self.align = align
        self.width_fix = 100
        if self.align == Qt.AlignmentFlag.AlignLeft:
            self.delta = 0
        else: self.delta = self.width_fix - 5

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont("Microsoft YaHei", 15))

        # 绘制背景
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRoundedRect(self.delta, 0, self.width() - self.width_fix, self.height(), 10, 10)

        # 绘制气泡边框
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawRoundedRect(1 + self.delta, 1, self.width() - 2 - self.width_fix, self.height() - 2, 10, 10)

        # 绘制气泡阴影
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawLine(1 + self.delta, self.height() - 1, self.width() - 1 - self.width_fix, self.height() - 1)
        painter.drawLine(self.width() - 1, self.height() - 1, self.width() - 1, 1)

        # 绘制文本
        painter.setPen(QPen(QColor(0, 0, 0), 10))
        painter.drawText(QRect(abs(self.delta - 10), 0, self.width() - self.width_fix, self.height()), self.message, self.align)


def main() -> None:
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    app.exec()


def test(*args, **kwargs) -> None:
    pass



if __name__ == "__main__":
    # test()
    main()