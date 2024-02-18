# pyqt-live2d-chat

![pyqt-live2d-chat](https://github.com/JhonSmith0x7b/pyqt-live2d-chat/actions/workflows/ci.yaml/badge.svg)

## 1. 概述 / Overview

本项目是一个基于 `PySide6`和 `Live2D` 的聊天应用。它提供了一个图形界面，用户可以与 `Live2D` 模型进行实时对话, `LLM` 模型支持 `Gemini`, `Azure GPT`, `Openai GPT`。

核心是使用`Qt`的`Webview`展示`live2d`的`Web SDK`模型.

######---------------------------------------------------------------------------

This project is a chat application based on `PySide6` and `Live2D`. It provides a graphical interface for users to interact with `Live2D` models in real time, and supports `Gemini`, `Azure GPT`, `Openai GPT` models.

The idea is to use `Qt`'s `Webview` to display `live2d` `Web SDK` models.

## 2. 页面展示 / Page Display

### 2.1 基础设置页面 / Settings Window:

![settings window](./asserts/settings_window.png)

### 2.2 对话页面 / Chat Window:

![chat window](./asserts/chat_window.png)

## 3. 安装和运行 / Installation and Running

### 3.1 配置文件 / Configuration

本项目配置通过环境变量实现
首先复制 `.env.sample` 为 `.env`
配置具体参考代码与配置文件的注释.

######---------------------------------------------------------------------------

1. Copy `.env.sample` to `.env`
2. Configure the specific code and configuration file according to the code and configuration file comments.

### 3.2 依赖框架 / Dependencies

- Python3
- Node

### 3.3 本地运行 / Local Run

1. 克隆项目到本地：`git@github.com:JhonSmith0x7b/pyqt-live2d-chat.git`
2. 进入项目目录：`cd pyqt-live2d-chat`
3. 初始化子模块: `git submodule update --init`
4. 安装依赖：`pip install -r requirements.txt`
5. 运行应用：`python main.py`
6. 如果使用本地 live2d, 需要运行 `cd ./live2d/Samples/TypeScript/Demo/ && npm run build && npm run serve`

######---------------------------------------------------------------------------

1. Clone the project to local: `git@github.com:JhonSmith0x7b/pyqt-live2d-chat.git`
2. Enter the project directory: `cd pyqt-live2d-chat`
3. Initialize submodules: `git submodule update --init`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python main.py`
6. If you use local live2d, you need to run `cd./live2d/Samples/TypeScript/Demo/ && npm run build && npm run serve` (`npm install -g webpack`)

### 3.4 打包运行 / Packaging and Running

1. windows 使用 `build_main.ps1` 进行 pyinstaller 打包 exe 程序.

######---------------------------------------------------------------------------

1. On windows use `build_main.ps1` to package the exe program.
   question: what's .ps1?

## 4. 文件结构 / File Structure

- `main.py`: 应用的入口文件，包含了应用的主要逻辑。
- `./live2d/`: Live2D 代码, 从 Web SDK Demo 修改而来.
- `./llms/`: llm 代码
- `./ttss/`: tts 代码
- `./prompts/`: llm 指示文件
- `./resources/`: 存放了应用所需的资源文件，如 Live2D 模型和背景图片。

######---------------------------------------------------------------------------

- `main.py`: The entry file of the application, which contains the main logic.
- `./live2d/`: Live2D code, modified from Web SDK Demo.
- `./llms/`: llm code
- `./ttss/`: tts code
- `./prompts/`: llm indication files
- `./resources/`: Contains the resources required for the application, such as Live2D models and background images.

## 5. 支持项目 / Credits

- Live2D https://github.com/Live2D/CubismWebSamples
- 免费模型 https://koiyume233.booth.pm/

######---------------------------------------------------------------------------

- Live2D https://github.com/Live2D/CubismWebSamples
- Free model https://koiyume233.booth.pm/

## 6. Q&A

### 6.1 如何添加 live2D 模型 / How to add Live2D model

复制模型文件夹到 `./live2d/Resources/`, 修改 `./live2d/Samples/TypeScript/Demo/src/lappdefine.ts` 的 `ModelDir`, 将模型文件夹名称加入里面, npm 重新打包.

######---------------------------------------------------------------------------

Copy the model folder to `./live2d/Resources/`, modify the `./live2d/Samples/TypeScript/Demo/src/lappdefine.ts` of `ModelDir`, add the name folder name to it, NPM reinsert.
