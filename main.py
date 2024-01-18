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
import functools
import requests
import asyncio
from typing import Callable
import queue
import traceback


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
        self.gpt_inputs = self.set_llm_config_widget(self.layout, "GPT")
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
        self.chatbox_checkbox = QCheckBox("Show Chat Box")
        enable_chatbox = os.environ.get("ENABLE_CHATBOX")
        if enable_chatbox == 'true': self.chatbox_checkbox.setChecked(True)
        else: self.chatbox_checkbox.setChecked(False)
        self.layout.addWidget(self.chatbox_checkbox)
        # jump button
        start_button = QPushButton("Start")
        start_button.setFixedSize(880, 100)
        start_button.clicked.connect(self.jump)
        self.layout.addWidget(start_button)
    
    def set_llm_config_widget(self, layout: QLayout,llm_name: str) -> tuple[QCheckBox, QLineEdit, QLineEdit, QLineEdit, QLineEdit]:
        checkbox = QCheckBox(llm_name)
        if os.environ.get(f"ENABLE_{llm_name}") == 'true': checked=True
        else: checked = False
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
            os.environ["ENABLE_AZURE"] = "true"
            os.environ["AZURE_ENDPOINT"] = self.azure_inputs[1].text()
            # os.environ["AZURE_API_KEY"] = self.azure_inputs[2].text()
            os.environ["AZURE_MODEL"] = self.azure_inputs[3].text()
            os.environ["AZURE_PREFIX"] = self.azure_inputs[4].text()
        elif self.gemini_inputs[0].isChecked():
            os.environ["ENABLE_GEMINI"] = "true"
            os.environ["GEMINI_ENDPOINT"] = self.gemini_inputs[1].text()
            # os.environ["GEMINI_API_KEY"] = self.gemini_inputs[2].text()
            os.environ["GEMINI_MODEL"] = self.gemini_inputs[3].text()
            os.environ["GEMINI_PREFIX"] = self.gemini_inputs[4].text()
        elif self.gpt_inputs[0].isChecked():
            os.environ["ENABLE_GPT"] = "true"
            os.environ["GPT_ENDPOINT"] = self.gpt_inputs[1].text()
            # os.environ["GPT_API_KEY"] = self.gpt_inputs[2].text()
            os.environ["GPT_MODEL"] = self.gpt_inputs[3].text()
            os.environ["GPT_PREFIX"] = self.gpt_inputs[4].text()
        os.environ["TTS_ENDPOINT"] = self.tts_layout.itemAt(1).widget().text()
        os.environ["LIVE2D_ENDPOINT"] = self.live2d_layout.itemAt(1).widget().text()
        os.environ["USE_TTS"] = str(self.tts_checkbox.isChecked()).lower()
        os.environ["ENABLE_CHATBOX"] = str(self.chatbox_checkbox.isChecked()).lower()
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
        if os.environ.get("ENABLE_CHATBOX") == 'true':
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

            self.q =  queue.Queue()
            self.llm_thread = LlmThead(self.q)
            self.llm_thread.start()
            # 连接信号
            self.submit_button.clicked.connect(self.on_submit_pressed)
            self.input_box.returnPressed.connect(self.on_submit_pressed)
            self.llm_thread.signal.sig.connect(self.llm_callback)

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
        self.q.put(text)
    
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
    
    def llm_callback(self, text: str) -> None:
        self.input_box.setText("")
        self.input_box.setEnabled(True)
        self.submit_button.setEnabled(True)
        self.input_box.setFocus()
        if text in (None, ""): return
        self.list_widget_add_item(text)
        self.text_edit.setHtml(text[:120])
        self.list_widget.scrollToBottom()


class LlmSignal(QObject):
    sig = Signal(str)


class LlmThead(QThread):
    def __init__(self, q: queue.Queue, parent=None) -> None:
        super().__init__(parent)
        self.signal = LlmSignal()
        self.q = q
        self.loop = asyncio.get_event_loop()
        self.llm = llm_clo(self.loop)
    
    def run(self) -> None:
        while True:
            tmp = self.q.get()
            try:
                self.signal.sig.emit(self.loop.run_until_complete(self.llm(tmp)))
            except Exception as e: 
                traceback.print_exc()
                self.signal.sig.emit("哦呀, 出错了.")


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


def llm_clo(loop: asyncio.BaseEventLoop) -> str:
    bks = []
    llms = []
    if os.environ.get("ENABLE_AZURE") == "true":
        simple_azure_bk = []
        bks.append(simple_azure_bk)
        llms.append(azure_clo(loop, simple_azure_bk))
    if os.environ.get("ENABLE_GEMINI") == "true":
        simple_gemini_bk = []
        bks.append(simple_gemini_bk)
        llms.append(gemini_clo(loop, simple_gemini_bk))
    @common.wrap_log_ts_async
    async def llm_inner(text: str) -> str:
        common.lru_pop(*bks)
        tasks = []
        for llm in llms:
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


def azure_clo(loop: asyncio.BaseEventLoop, bk: list[dict[str, str]]) -> Callable:
    endpoint = os.environ.get("AZURE_ENDPOINT")
    api_key = os.environ.get("AZURE_API_KEY")
    model = os.environ.get("AZURE_MODEL")
    prefixs = os.environ.get("AZURE_PREFIX").split(",")
    url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version=2023-03-15-preview"
    init_prompt = open("./prompts/bullet_init.txt").read()
    error_prompt = open("./prompts/bullet_error.txt").read()
    async def azure_inner(text: str) -> str:
        for prefix in prefixs:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        else:
            return None
        messages = [
            {
                "role": "system",
                "content": init_prompt
            },
            {
                "role": "user",
                "content": text
            }
        ]
        messages.extend(bk)
        new_message = {
            "role": "user",
            "content": text
        }
        messages.append(new_message)
        resp = await loop.run_in_executor(
            None, 
            functools.partial(requests.post, 
            url=url,
            headers={"Content-Type": "application/json", "api-key": api_key},
            json={
                "messages": messages
            }
            )
        )
        if resp.json()['choices'][0]['finish_reason'] == "content_filter":
            return error_prompt
        re_message = resp.json()['choices'][0]['message']
        bk.append(new_message)
        bk.append(
            {
                "role": re_message['role'],
                "content": re_message['content']
            }
        )
        return resp.json()['choices'][0]['message']['content']
    return azure_inner


def gemini_clo(loop: asyncio.BaseEventLoop, bk: list[dict[str, str]]) -> Callable:
    endpoint = os.environ.get("GEMINI_ENDPOINT")
    model = os.environ.get("GEMINI_MODEL")
    api_key = os.environ.get("GEMINI_API_KEY")
    prefixs = os.environ.get("GEMINI_PREFIX").split(",")
    url = f"{endpoint}/v1/models/{model}?key={api_key}"
    init_prompt = open("./prompts/bullet_init.txt").read()
    error_prompt = open("./prompts/bullet_error.txt").read()
    async def gemini_inner(text: str) -> str:
        for prefix in prefixs:
            if text.startswith(prefix):
                text = text[len(prefix):]
                break
        else:
            return None
        contents = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": init_prompt
                    }
                ]
            },
            {
                "role": "model",
                "parts": [
                    {
                        "text": "我一定遵守."
                    }
                ]
            },
        ]
        contents.extend(bk)
        new_message = {
            "role": "user",
            "parts": [
                    {
                        "text": text
                    }
            ]
        }
        contents.append(new_message)
        resp = await loop.run_in_executor(
            None,
            functools.partial(
                requests.post,
                url=url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": contents
                }
            )
        )
        try:
            re_message = resp.json()['candidates'][0]['content']
        except Exception as e:
            logging.error(f"gemini error, response is {resp.text}")
            return error_prompt
        bk.append(new_message)
        bk.append(re_message)
        return re_message['parts'][0]['text']
    return gemini_inner



def main() -> None:
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    app.exec()


def test(*args, **kwargs) -> None:
    print(":")
    print(chr(ord(":") + 65248))
    pass


if __name__ == "__main__":
    common.init_log("main_")
    # test()
    main()