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
import requests
import json
import time


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
        #elif os.environ.get("TTS_TYPE") == "AZURE":
        #    azure_radio_button.setChecked(True)
        azure_radio_button.setChecked(True)
        self.tts_radio_group = QButtonGroup()
        self.tts_radio_group.addButton(bert_vits_radio_button)
        self.tts_radio_group.addButton(azure_radio_button)
        # chatbox 
        self.chatbox_checkbox = QCheckBox("Show Chat Box")
        if os.environ.get("ENABLE_CHATBOX") == 'true': self.chatbox_checkbox.setChecked(True)
        else: self.chatbox_checkbox.setChecked(False)
        self.layout.addWidget(self.chatbox_checkbox)
        # bili live bullet
        self.bili_checkbox = QCheckBox("Enable Bili Live Bullet")
        if os.environ.get("ENABLE_BILI") == 'true': self.bili_checkbox.setChecked(True)
        self.layout.addWidget(self.bili_checkbox)
        # local live2d 
        self.local_live2d_checkbox = QCheckBox("Enable Local Live2D")
        if os.environ.get("ENABLE_LOCAL_LIVE2D") == 'true': self.local_live2d_checkbox.setChecked(True)
        self.layout.addWidget(self.local_live2d_checkbox)
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
        os.environ["ENABLE_BILI"] = str(self.bili_checkbox.isChecked()).lower()
        os.environ["ENABLE_LOCAL_LIVE2D"] = str(self.local_live2d_checkbox.isChecked()).lower()
        self.hide()
        self.next_window = MainWindow()
        self.next_window.show()
        self.destroy()
    
    # close
    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)


class QWebEngineViewDrag(QWebEngineView):
    def contextMenuEvent(self, event):
        self.menu = QMenu()
        
        self.menu_action_settings = self.menu.addAction('Settings')
        self.menu_action_settings.triggered.connect(self.parentWidget().openSettings)
        
        self.menu_action_exit = self.menu.addAction("Exit") # = QAction
        #self.menu_action_exit.setText("Exit")
        self.menu_action_exit.triggered.connect(self.parentWidget().close) # self.close
        #self.menu.addAction(self.menu_action_exit)
        
        self.menu.popup(event.globalPos())
        
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.clicked = False
        self.setWindowTitle("Main Window")
        self.resize(500, 800)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint 
            # Qt.WindowType.WindowTransparentForInput
        )
        # layout setting
        self.layout = QGridLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.live2d_layout = QVBoxLayout()
        self.layout.addLayout(self.live2d_layout, 0, 0, 1, 1)
        # web window setting
        self.web_window = QWebEngineViewDrag(self)
        #self.web_window.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.web_window.page().setBackgroundColor(Qt.GlobalColor.transparent)
        self.local_live2d_enable = True if os.environ.get("ENABLE_LOCAL_LIVE2D") == 'true' else False
        if self.local_live2d_enable:
            # QProcess invoke a npm server
            self.live2d_process = QProcess(self)
            self.live2d_process.setWorkingDirectory("./live2d/Samples/TypeScript/Demo")
            self.live2d_process.start("npm", ["run", "serve"])
            self.live2d_process.waitForStarted()
            self.live2d_process.readyReadStandardOutput.connect(self.on_ready_read_standard_output)
            self.live2d_process.readyReadStandardError.connect(self.on_ready_read_standard_error)
            url = QUrl("http://127.0.0.1:12303/Samples/TypeScript/Demo/")
        else: url = QUrl(os.environ.get("LIVE2D_ENDPOINT"))
        self.web_window.load(url)
        # text edit setting
        self.text_edit = QTextEdit(self)
        self.text_edit.setFixedSize(500, 200)
        self.text_edit.setHtml("Xiaoming also loves to do nothing~")
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
        
        self.web_window.focusProxy().installEventFilter(self)
        
        self.back_q = queue.Queue()
        self.back_thread = BackThead(self.back_q)
        self.back_thread.start()
        self.back_thread.signal.sig.connect(self.back_callback)
        # chat box 
        self.chatbox_enable = True if os.environ.get("ENABLE_CHATBOX") == 'true' else False
        if self.chatbox_enable:
            self.chatbox_enable = True
            self.chat_layout = QVBoxLayout()
            self.layout.addLayout(self.chat_layout, 0, 1, 1, 1)
            self.list_widget = QListWidget()
            self.list_widget.setFixedSize(500, 750)
            self.chat_layout.addWidget(self.list_widget)
            # 创建输入框 / Create an input box
            self.input_box = QLineEdit()
            self.input_box.setFixedSize(500, 50)
            # 添加控件到窗口 / Add the controls to the window
            self.chat_layout.addWidget(self.input_box)
            self.submit_button = QPushButton("Submit")
            self.chat_layout.addWidget(self.submit_button)

            # 连接信号 / Connect the signals
            self.submit_button.clicked.connect(self.on_submit_pressed)
            self.input_box.returnPressed.connect(self.on_submit_pressed)
 
    def eventFilter(self, obj, event):
        import PySide6.QtCore
        if obj is self.web_window.focusProxy() and event.type() == PySide6.QtCore.QEvent.MouseMove and self.clicked:
            #print("MouseMove")
            delta = QPoint (event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()
            
        if obj is self.web_window.focusProxy() and event.type() == PySide6.QtCore.QEvent.MouseButtonPress:
            #print("Widget click")
            self.oldPos = event.globalPosition().toPoint()
            self.clicked = True
            
        if obj is self.web_window.focusProxy() and event.type() == PySide6.QtCore.QEvent.MouseButtonRelease:
            #print("Widget unclick")
            self.clicked = False
            
        return super(MainWindow, self).eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPosition().toPoint() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()
         
    def openSettings(self) -> None:
        #print(self)
        self.hide()
        self.next_window = SettingsWindow()
        self.next_window.show()
        self.destroy()    
           
    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
                  
    def on_submit_pressed(self) -> None:
        # 获取输入文本 / Get the input text
        text = self.input_box.text()
        if text.strip() == "":return
        # 将文本添加到列表控件 / Add the text to the list widget
        self.list_widget_add_item(text, Qt.AlignmentFlag.AlignRight)
        # 清空输入框 / Clear input box
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
        if self.chatbox_enable:
            self.input_box.setEnabled(True)
            self.submit_button.setEnabled(True)
            self.input_box.setText("")
            self.input_box.setFocus()
        if text not in (None, ""):
            if self.chatbox_enable:
                self.list_widget_add_item(text)
                self.list_widget.scrollToBottom()
            self.text_edit.setHtml(text[:120])
    
    def on_ready_read_standard_output(self) -> None:
        data = self.live2d_process.readAllStandardOutput()
        logging.info(data)
    
    def on_ready_read_standard_error(self) -> None:
        data = self.live2d_process.readAllStandardError()
        logging.error(data)

    # close
    def closeEvent(self, event: QCloseEvent) -> None:
        logging.info("in close event")
        if self.local_live2d_enable:
            self.live2d_process.close()
            self.live2d_process.kill()
            self.live2d_process.waitForFinished()
        self.back_thread.terminate()
        super().closeEvent(event)


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
        # 绘制背景 / Draw background
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRoundedRect(self.delta, 0, self.width() - self.width_fix, self.height(), 10, 10)
        # 绘制气泡边框 / Draw a bubble frame
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawRoundedRect(1 + self.delta, 1, self.width() - 2 - self.width_fix, self.height() - 2, 10, 10)
        # 绘制气泡阴影 / Draw the shadow of bubble
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawLine(1 + self.delta, self.height() - 1, self.width() - 1 - self.width_fix, self.height() - 1)
        painter.drawLine(self.width() - 1, self.height() - 1, self.width() - 1, 1)
        # 绘制文本 / Draw text
        painter.setPen(QPen(QColor(0, 0, 0), 10))
        painter.drawText(QRect(abs(self.delta - 10), 0, self.width() - self.width_fix, self.height()), self.message, self.align)


def llm_clo() -> str:
    llm_list = []
    if os.environ.get("ENABLE_AZURE") == "true":
        llm_list.append(llms.azure_clo())
    if os.environ.get("ENABLE_GEMINI") == "true":
        llm_list.append(llms.gemini_clo())
    if os.environ.get("ENABLE_GPT") == "true":
        llm_list.append(llms.gpt_clo())
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
        self.bili_enable =  True if os.environ.get("ENABLE_BILI") == 'true' else False
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
        if self.bili_enable:
            self.bili_thread = BiliThread(self.q)
            self.bili_thread.start()
        
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
            tts_task = asyncio.ensure_future(self.tts(text[:300]))
            tasks.append(tts_task)
        if self.llm_enable:
            llm_task = asyncio.ensure_future(self.llm(text[:300]))
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
        if self.tts_enable: self.audio_thread.terminate()
        if self.bili_enable: self.bili_thread.terminate()
        super().terminate()


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


class BiliThread(QThread):
    def __init__(self, q: queue.Queue ,parent=None) -> None:
        super().__init__(parent)
        logging.info("bili thread start")
        self.q = q
        self.room_id = os.environ.get("BILI_ROOM_ID")
    
    def get_bullets(self) -> list[tuple[str, str]]:
        url = f"https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid={self.room_id}&room_type=0"
        # api return ten bullets
        headers = {
            "authority": "api.live.bilibili.com",
            "accept": "application/json",
            "accept-language": "zh-CN",
            "origin": "https://live.bilibili.com",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers)
        data = json.loads(resp.text)
        re = []
        room = data['data']['room']
        for line in room:
            re.append((line['nickname'], line['text']))
        return re
    
    def run(self) -> None:
        simple_bk = []
        while True:
            try:
                re = self.get_bullets()
                start = 0 if len(re)-5<0 else len(re)-5
                for i in range(start, len(re)):
                    text = re[i][1]
                    if text in simple_bk: continue
                    simple_bk.append(text)
                    self.q.put(text)
                simple_bk = simple_bk[-100:]
                time.sleep(5)
            except Exception as e:
                traceback.print_exc()
                logging.error(f"loop bullet error {e}")
    
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