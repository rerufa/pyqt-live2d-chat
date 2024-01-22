from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from dotenv import load_dotenv
load_dotenv(override=True)
import os
import common
import sys
import logging
import asyncio
from typing import Callable
import queue
import traceback
import llms
import io
import sounddevice as sd
import soundfile as sf
import ttss


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
        llm_row = common.IterCount(0)
        self.layout.addLayout(self.llm_layout)
        self.llm_checkbox = QCheckBox("Enable LLM")
        if os.environ.get("ENABLE_LLM") == 'true': self.llm_checkbox.setChecked(True)
        self.llm_layout.addWidget(self.llm_checkbox, llm_row.val, 0, 1, 1)
        # azure
        self.azure_checkbox = QCheckBox("Enable Azure")
        if os.environ.get("ENABLE_AZURE") == 'true': self.azure_checkbox.setChecked(True)
        self.llm_layout.addWidget(self.azure_checkbox, next(llm_row), 0, 1, 1)
        # gemini
        self.gemini_checkbox = QCheckBox("Enable Gemini")
        if os.environ.get("ENABLE_GEMINI") == 'true': self.gemini_checkbox.setChecked(True)
        self.llm_layout.addWidget(self.gemini_checkbox, llm_row.val, 1, 1, 1)
        # GPT
        self.gpt_checkbox = QCheckBox("Enable GPT")
        if os.environ.get("ENABLE_GPT") == 'true': self.gpt_checkbox.setChecked(True)
        self.llm_layout.addWidget(self.gpt_checkbox, llm_row.val, 2, 1, 1)
        # tts layout
        self.tts_layout = QGridLayout()
        self.layout.addLayout(self.tts_layout)
        self.tts_checkbox = QCheckBox("Enable TTS")
        if os.environ.get("ENABLE_TTS") == 'true': self.tts_checkbox.setChecked(True)
        tts_row = common.IterCount(0)
        self.tts_layout.addWidget(self.tts_checkbox, tts_row.val, 0, 1, 1)
        bert_vits_radio_button = QRadioButton("BERT_VITS")
        self.tts_layout.addWidget(bert_vits_radio_button, next(tts_row), 1, 1, 1)
        azure_radio_button = QRadioButton("AZURE")
        self.tts_layout.addWidget(azure_radio_button, tts_row.val, 0, 1, 1)
        if os.environ.get("TTS_TYPE") == "BERT_VITS":
            bert_vits_radio_button.setChecked(True)
        elif os.environ.get("TTS_TYPE") == "AZURE":
            azure_radio_button.setChecked(True)
        self.tts_radio_group = QButtonGroup()
        self.tts_radio_group.addButton(bert_vits_radio_button)
        self.tts_radio_group.addButton(azure_radio_button)
        # chatbox 
        self.chatbox_checkbox = QCheckBox("Show Chat Box")
        if os.environ.get("ENABLE_CHATBOX") == 'true': self.chatbox_checkbox.setChecked(True)
        else: self.chatbox_checkbox.setChecked(False)
        self.layout.addWidget(self.chatbox_checkbox)
        # jump button
        start_button = QPushButton("Start")
        start_button.setFixedSize(880, 100)
        start_button.clicked.connect(self.jump)
        self.layout.addWidget(start_button)
    
    def jump(self) -> None:
        os.environ["ENABLE_LLM"] = str(self.llm_checkbox.isChecked()).lower()
        os.environ["ENABLE_AZURE"] = str(self.azure_checkbox.isChecked()).lower()
        os.environ["ENABLE_GEMINI"] = str(self.gemini_checkbox.isChecked()).lower()
        os.environ["ENABLE_GPT"] = str(self.gpt_checkbox.isChecked()).lower()
        os.environ["ENABLE_TTS"] = str(self.tts_checkbox.isChecked()).lower()
        os.environ["ENABLE_CHATBOX"] = str(self.chatbox_checkbox.isChecked()).lower()
        os.environ["TTS_TYPE"] = str(self.tts_radio_group.checkedButton().text())
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
        self.back_q = queue.Queue()
        self.back_thread = BackThead(self.back_q)
        self.back_thread.start()
        self.back_thread.signal.sig.connect(self.back_callback)
        # chat box 
        if os.environ.get("ENABLE_CHATBOX") == 'true':
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
        self.list_widget_add_item(text, Qt.AlignmentFlag.AlignRight)
        # 清空输入框
        self.input_box.clear()
        # listwidget to bottom
        self.list_widget.scrollToBottom()
        self.input_box.setText("......")
        self.input_box.setEnabled(False)
        self.submit_button.setEnabled(False)
        # send 2 llm
        self.back_q.put(text)
    
    def list_widget_add_item(self, text: str, align: Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft) -> None:
        item = QListWidgetItem(self.list_widget)
        br_count = text.count("\n")
        height = 20 * (len(text) // 25 + br_count) + 50
        item.setSizeHint(QSize(400, height+10))
        self.list_widget.setItemWidget(item, MyChatBubble(text, height, align))
        self.lru_list_clean()
        self.list_widget.scrollToBottom()
    
    def lru_list_clean(self) -> None:
        while self.list_widget.count() > 30:
            self.list_widget.takeItem(0)
    
    def back_callback(self, text: str) -> None:
        self.input_box.setText("")
        self.input_box.setEnabled(True)
        self.submit_button.setEnabled(True)
        self.input_box.setFocus()
        if text in (None, ""): return
        self.list_widget_add_item(text)
        self.text_edit.setHtml(text[:120])
        self.list_widget.scrollToBottom()

    # close
    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        self.back_thread.terminate()


class MyChatBubble(QWidget):
    def __init__(self, message: str, height: int=50, align: Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, height)
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


def llm_clo() -> str:
    llm_list = []
    if os.environ.get("ENABLE_AZURE") == "true":
        llm_list.append(llms.azure_clo())
    if os.environ.get("ENABLE_GEMINI") == "true":
        llm_list.append(llms.gemini_clo())
    @common.wrap_log_ts_async
    async def llm_inner(text: str) -> str:
        tasks = []
        for llm in llm_list:
            task = asyncio.ensure_future(llm(text))
            tasks.append(task)
        dones, _ = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        for done in dones:
            if done.exception() is not None:
                logging.warning(f"llm error {done.exception()}")
                continue
            if done.result() is not None:
                return done.result()
        return None
    return llm_inner


class BackSignal(QObject):
    sig = Signal(str)


class BackThead(QThread):
    def __init__(self, q: queue.Queue, parent=None) -> None:
        super().__init__(parent)
        self.signal = BackSignal()
        self.q = q
        self.loop = asyncio.get_event_loop()
        self.tts_enable =  True if os.environ.get("ENABLE_TTS") == 'true' else False
        self.llm_enable =  True if os.environ.get("ENABLE_LLM") == 'true' else False
        if self.llm_enable:
            self.llm = llm_clo()
        if self.tts_enable:
            tts_type = os.environ.get("TTS_TYPE")
            if tts_type == "BERT_VITS":
                self.tts = ttss.bert_vits_tts_clo()
            elif tts_type == "AZURE":
                self.tts = ttss.azure_tts_clo()
            self.audio_queue = queue.Queue()
            self.audio_thread = AudioThread(self.audio_queue)
            self.audio_thread.start()
        
    def run(self) -> None:
        while True:
            temp = self.q.get()
            try:
                self.loop.run_until_complete(self.task_run(temp))
            except Exception as e: 
                traceback.print_exc()
                self.signal.sig.emit("哦呀, 出错了.")
    
    async def task_run(self, text: str) -> None:
        tasks = []
        tts_task = None
        llm_task = None
        re = None
        if self.tts_enable:
            tts_task = asyncio.ensure_future(self.tts(text))
            tasks.append(tts_task)
        if self.llm_enable:
            llm_task = asyncio.ensure_future(self.llm(text))
            tasks.append(llm_task)
        await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        if tts_task is not None:
            if tts_task.exception() is not None:
                logging.warning(f"tts error {tts_task.exception()}")
            elif tts_task.result() is not None:
                self.audio_queue.put(tts_task.result())
        if llm_task is not None:
            if llm_task.exception() is not None:
                logging.warning(f"llm error {llm_task.exception()}")
            elif llm_task.result() is not None:
                if self.tts_enable:
                    llm_tts = await asyncio.ensure_future(self.tts(llm_task.result()))
                    if llm_tts is not None: self.audio_queue.put(llm_tts)
                re = llm_task.result()
        self.signal.sig.emit(re)
    
    # close 
    def terminate(self) -> None:
        super().terminate()
        self.audio_thread.terminate()


class AudioSignal(QObject):
    sig = Signal(str)


class AudioThread(QThread):
    def __init__(self, q: queue.Queue ,parent=None) -> None:
        super().__init__(parent)
        # common.init_log("qt_audio_sub")
        logging.info("qt audio thread start")
        self.signal = AudioSignal()
        self.q = q
        self.volume = float(os.environ.get('TTS_VOLUME'))
    
    def run(self) -> None:
        while True:
            audio = self.q.get()
            try:
                temp_audio = io.BytesIO(audio)
                data, rate = sf.read(temp_audio)
                data = data * self.volume
                sd.play(data, rate, blocking=True)
            except Exception as e:
                traceback.print_exc()
                logging.error(f"play audio error {e}")
    
    # close
    def terminate(self) -> None:
        super().terminate()
        self.wait()


def main() -> None:
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    app.exec()


def test(*args, **kwargs) -> None:
    loop = asyncio.get_event_loop()
    tts = ttss.azure_tts_clo()
    audio = loop.run_until_complete(tts("你好~"))
    data, sample = sf.read(io.BytesIO(audio))
    sd.play(data, sample, blocking=True)


if __name__ == "__main__":
    common.init_log("main_")
    # test()
    main()