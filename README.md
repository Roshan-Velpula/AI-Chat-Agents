# AI Chat Agents

Welcome to the AI Chat Agents project! This project leverages OpenAI tools and function calling to enable automatic event and task creation within a chat interface.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Introduction

AI Chat Agents is a chat interface project that integrates OpenAI tools to provide intelligent responses and automate event and task creation. This project uses a chat UI implemented with NiceGUI and includes functionality to interact with Google Calendar for event management.

## Features

- Chat interface with dynamic message updates.
- User selection for personalized interactions.
- Automatic response generation using OpenAI.
- Integration with Google Calendar for event creation.
- Task management and execution.

## Installation

To get started with the AI Chat Agents project, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/aichatagents.git
    cd aichatagents
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    Create a `.env` file in the project root and add your OpenAI API key and Google API credentials.
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

To run the application, execute the following command:

```bash
python chat_ui.py
