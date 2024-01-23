# pyqt-live2d-chat
![pyqt-live2d-chat](https://github.com/JhonSmith0x7b/pyqt-live2d-chat/actions/workflows/ci.yaml/badge.svg)

## 概述

本项目是一个基于 PySide6 和 Live2D 的聊天应用。它提供了一个图形界面，用户可以与 Live2D 模型进行实时对话。

## 文件结构

- `main.py`: 应用的入口文件，包含了应用的主要逻辑。
- `live2d.py`: 封装了与 Live2D 模型交互的功能。
- `chat_widget.py`: 实现了聊天界面的窗口部件。
- `resources/`: 存放了应用所需的资源文件，如 Live2D 模型和背景图片。

## 安装和运行

1. 克隆项目到本地：`git clone https://github.com/username/repo.git`
2. 进入项目目录：`cd pyqt-live2d-chat`
3. 安装依赖：`pip install -r requirements.txt`
4. 运行应用：`python main.py`

## 功能特性

- 实时对话：用户可以与 Live2D 模型进行实时对话。
- 自定义界面：用户可以选择不同的背景图片和 Live2D 模型。
- 多语言支持：应用支持多种语言，用户可以切换界面语言。

## 技术栈

- Python: 用于编写应用的主要逻辑。
- PyQt: 用于创建图形界面。
- Live2D: 用于加载和渲染 Live2D 模型。

## 示例代码

以下是 `main.py` 中的示例代码：
