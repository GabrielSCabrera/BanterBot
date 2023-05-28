# BanterBot

BanterBot is a user-friendly chatbot application that leverages OpenAI models for generating context-aware responses and Azure Neural Voices for text-to-speech synthesis. The package offers a comprehensive toolkit for building chatbot applications with an intuitive interface and a suite of utilities.

## Features

* Employs OpenAI models for generating context-sensitive responses
* Utilizes Azure Neural Voices for high-quality text-to-speech synthesis
* Supports a variety of output formats, voices, and speaking styles
* Enables real-time monitoring of the chatbot's responses
* Provides an abstract base class for crafting frontends for the BanterBot application
* Includes a tkinter-based frontend implementation

## Requirements

Three environment variables are required for full functionality:

* `OPENAI_API_KEY`: A valid OpenAI API key
* `AZURE_SPEECH_KEY`: A valid Azure Cognitive Services Speech API key for TTS functionality
* `AZURE_SPEECH_REGION`: The region associated with your Azure Cognitive Services Speech API key

## Components

### OpenAIManager

A class responsible for managing interactions with the OpenAI ChatCompletion API. It offers functionality to generate responses from the API based on input messages. It supports generating responses in their entirety or as a stream of response blocks.

### TextToSpeech

A class that handles text-to-speech synthesis using Azure's Cognitive Services. It supports a wide range of output formats, voices, and speaking styles. The synthesized speech can be interrupted, and the progress can be monitored in real-time.

### BanterBotInterface

An abstract base class for designing frontends for the BanterBot application. It provides a high-level interface for managing conversations with the bot, including sending messages, receiving responses, and updating the conversation area.

### BanterBotTK

A graphical user interface (GUI) for a chatbot application that employs OpenAI models for generating responses and Azure Neural Voices for text-to-speech. The class inherits from both tkinter.Tk and BanterBotInterface, offering a seamless integration of chatbot functionality with an intuitive interface.

## Installation

### Pip

BanterBot is installable using the Python Package Index (PyPi):

```bash
python -m pip install banterbot
```

### Manual

To install BanterBot, simply clone the repository and install the required dependencies:

```bash
git clone https://github.com/gabrielscabrera/banterbot.git
cd banterbot
python -m pip install .
```

## Usage

### Launch with Command Line

Start the BanterBot Command Line Interface (CLI) by executing the `banterbot` command. Use the `-g` or `--gpt4` flags to enable GPT-4; this only works if you have GPT-4 API access.

### Launch with a Python script

To use BanterBot, just import the necessary components and create an instance of the BanterBotTK class:

```python
from banterbot import BanterBotTK
from banterbot.data.azure_neural_voices import get_voice_by_name
from banterbot.data.openai_models import openai_models

model = openai_models["gpt-3.5-turbo"]
voice = get_voice_by_name("Aria")
style = "chat"

app = BanterBotTK(model=model, voice=voice, style=style)
app.run()
```

## Chat Logs

Chat logs are saved in the `$HOME/Documents/BanterBot/Conversations/` directory as individual `.txt` files.

## Documentation

For a complete set of documentation, please refer to the [BanterBot Documentation](https://gabrielscabrera.github.io/BanterBot/).
