# ChatAI

A lightweight Windows desktop chat client for local Ollama models. ChatAI connects directly to Ollama's local API; it does not run a web server.

## Features

- Select from models installed in Ollama.
- Turn model thinking on or off for each request.
- Adjust the conversation context length.
- Render common Markdown formatting, including headings, lists, emphasis, and code blocks with a copy button.
- Keep chat history and app preferences between launches.
- Rename or delete chats from the conversation history.
- English, Italian, Spanish, and French interface translations.

## Requirements

- Windows 10 or later.
- [Ollama for Windows](https://ollama.com/download) with at least one model installed.
- Python 3 with Tkinter to run from source. The standard Windows Python installer includes Tkinter; enable the optional Tcl/Tk feature if it is not installed.

## Run from source

1. Start Ollama and confirm that a model is installed.
2. Double-click **Launch ChatAI.bat**.
3. Select a model from the composer at the bottom of the window.

The default Ollama API address is `http://localhost:11434`. Change it in **Settings** if your Ollama server uses another address. The Thinking switch sends `think: true` or `think: false` with requests; whether it has an effect depends on the selected model.

## Build a standalone executable

Double-click **Build ChatAI EXE.bat**. The script installs or updates PyInstaller and builds a windowed, single-file executable at `dist/ChatAI.exe`. The first build requires an Internet connection to install PyInstaller. Python is not required on computers that run the resulting executable.

## Local data

Conversations and preferences are stored in `%APPDATA%\ChatAI`. ChatAI sends prompts to the Ollama server configured in Settings. No ChatAI-hosted server is used.

## Project files

- `ChatAI.pyw` — desktop application source.
- `Launch ChatAI.bat` — launches the app with Python on Windows.
- `Build ChatAI EXE.bat` — builds the standalone executable.
- `icon.ico` — application and executable icon.
- `icon.png` — icon preview.
