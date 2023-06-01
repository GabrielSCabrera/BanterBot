# BanterBot

BanterBot is a user-friendly chatbot application that leverages OpenAI models for generating context-aware responses, Azure Neural Voices for text-to-speech synthesis, and Azure speech-to-text recognition. The package offers a comprehensive toolkit for building chatbot applications with an intuitive interface and a suite of utilities.

## Features

* Employs OpenAI models for generating context-sensitive responses
* Utilizes Azure Neural Voices for high-quality text-to-speech synthesis
* Supports a variety of output formats, voices, and speaking styles
* Enables real-time monitoring of the chatbot's responses
* Features asynchronous speech-to-text microphone input
* Provides an abstract base class for crafting frontends for the BanterBot application
* Includes a tkinter-based frontend implementation

## Requirements

Three environment variables are required for full functionality:

* `OPENAI_API_KEY`: A valid OpenAI API key
* `AZURE_SPEECH_KEY`: A valid Azure Cognitive Services Speech API key for text-to-speech and speech-to-text functionality
* `AZURE_SPEECH_REGION`: The region associated with your Azure Cognitive Services Speech API key

## Components

### OpenAIManager

A class responsible for managing interactions with the OpenAI ChatCompletion API. It offers functionality to generate responses from the API based on input messages. It supports generating responses in their entirety or as a stream of response blocks.

### TextToSpeech

A class that handles text-to-speech synthesis using Azure's Cognitive Services. It supports a wide range of output formats, voices, and speaking styles. The synthesized speech can be interrupted, and the progress can be monitored in real-time.

### SpeechToText
A class that provides an interface to convert spoken language into written text using Azure Cognitive Services. It allows continuous speech recognition and provides real-time results as sentences are recognized.

### BanterBotInterface

An abstract base class for designing frontends for the BanterBot application. It provides a high-level interface for managing conversations with the bot, including sending messages, receiving responses, and updating the conversation area. Accepts both keyboard inputs and microphone voice inputs.

### BanterBotTK

A graphical user interface (GUI) for a chatbot application that employs OpenAI models for generating responses, Azure Neural Voices for text-to-speech, and Azure speech-to-text. The class inherits from both tkinter.Tk and BanterBotInterface, offering a seamless integration of chatbot functionality with an intuitive interface.

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

Start BanterBot by running the `banterbot` command in your terminal. Add the `-g` flag to enable GPT-4 for better quality conversations; note that this will only work if you have GPT-4 API access, and is both significantly more costly and slower than the default GPT-3.5-Turbo.

### Launch with a Python script

To use BanterBot in a script, create an instance of the `BanterBotTK` class and call the `run` method:

```python
from banterbot import BanterBotTK, get_voice_by_name, get_model_by_name

model = get_model_by_name("gpt-3.5-turbo")
voice = get_voice_by_name("Aria")
style = "chat"

# The three arguments `model`, `voice`, and `style` are optional.
BBTK = BanterBotTK(model=model, voice=voice, style=style)
BBTK.run()
```

## Chat Logs

Chat logs are saved in the `$HOME/Documents/BanterBot/Conversations/` directory as individual `.txt` files.

## Documentation

For a complete set of documentation, please refer to the [BanterBot Documentation](https://gabrielscabrera.github.io/BanterBot/).
