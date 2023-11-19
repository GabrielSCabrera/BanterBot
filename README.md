# BanterBot

BanterBot is a user-friendly chatbot application that leverages OpenAI models for generating context-aware responses, Azure Neural Voices for text-to-speech synthesis, and Azure speech-to-text recognition. The package offers a comprehensive toolkit for building chatbot applications with an intuitive interface and a suite of utilities.

## Features

* Utilizes OpenAI models to generate context-aware responses
* Leverages Azure Neural Voices for premium text-to-speech synthesis
* Offers a wide range of output formats, voices, and speaking styles
* Allows real-time monitoring of the chatbot's responses
* Supports asynchronous speech-to-text microphone input
* Includes an abstract base class for creating custom frontends for the BanterBot application
* Features a tkinter-based frontend implementation
* Automatically selects an appropriate emotion or tone based on the conversation context

## Requirements

Three environment variables are required for full functionality:

* `OPENAI_API_KEY`: A valid OpenAI API key
* `AZURE_SPEECH_KEY`: A valid Azure Cognitive Services Speech API key for text-to-speech and speech-to-text functionality
* `AZURE_SPEECH_REGION`: The region associated with your Azure Cognitive Services Speech API key

## Components

### TKMultiplayerInterface

A graphical user interface (GUI) establishes a multiplayer conversation environment where up to nine users can interact with the chatbot simultaneously. The GUI includes a conversation history area and user panels with 'Listen' buttons to process user input. It also supports key bindings for user convenience.

### OpenAIService

A class responsible for managing interactions with the OpenAI ChatCompletion API. It offers functionality to generate responses from the API based on input messages. It supports generating responses in their entirety or as a stream of response blocks.

### SpeechSynthesisService

A class that handles text-to-speech synthesis using Azure's Cognitive Services. It supports a wide range of output formats, voices, and speaking styles. The synthesized speech can be interrupted, and the progress can be monitored in real-time.

### SpeechToText
A class that provides an interface to convert spoken language into written text using Azure Cognitive Services. It allows continuous speech recognition and provides real-time results as sentences are recognized.

## Installation

### Important Note

BanterBot requires several SpaCy language models to run, and will automatically download them on first-time initialization, if they are missing -- this process can sometimes take a while.

### Pip (Recommended)

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

Start BanterBot with an enhanced graphical user interface by running the command `banterbot` in your terminal. This GUI allows multiple users to interact with the bot, each with a dedicated button for speech input and a display for responses.

`-p`, `--prompt`: Set a system prompt at the beginning of the conversation (e.g., `-p "You are Grendel the Quiz Troll, a charismatic troll who loves to host quiz shows."`).

`-m`, `--model`: Choose the OpenAI model for conversation generation. Defaults to GPT-4, but other versions can be selected if specified in the code.

`-t`, `--tone-mode`: Configure the emotional tone evaluation mode. Options are NONE, BASIC, or ADVANCED. By default, it is set to ADVANCED.

`-v`, `--voice`: Select a Microsoft Azure Cognitive Services text-to-speech voice. The default is "Aria," but other voices can be specified if available.

`-s`, `--style`: Choose a voice style. This only works if `--tone-mode=NONE`. It defaults to a "friendly" style, with other styles available as per the Azure Cognitive Services specifications.

`-d`, `--debug`: Enable debug mode to display additional information in the terminal for troubleshooting.

`-g`, `--greet`: Have the bot greet the user upon startup.

`-n`, `--name`: Assign a name to the assistant for aesthetic purposes. This does not inform the bot itself; to provide the bot with information, use the `--prompt` flag.

Here is an example:

```bash
banterbot -g --model gpt-4-turbo --voice davis --prompt "You are Grendel the Quiz Troll, a charismatic troll who loves to host quiz shows." --tone-mode ADVANCED --name Grendel
```

### Launch with a Python script

To use BanterBot in a script, create an instance of the `TKSimpleInterface` class and call the `run` method:

```python
from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, ToneMode, TKMultiplayerInterface

model = OpenAIModelManager.load("gpt-4-turbo")
voice = AzureNeuralVoiceManager.load("Davis")
assistant_name = "Grendel"

# Set the tone_mode -- other options are ToneMode.NONE, ToneMode.BASIC.
tone_mode = ToneMode.ADVANCED

# Optional system prompt to set up a custom character prior to initializing BanterBot.
system = "You are Grendel the Quiz Troll, a charismatic troll who loves to host quiz shows."

# The five arguments `model`, `voice`, `system`, `tone_mode`, and `assistant_name` are optional.
interface = TKMultiplayerInterface(model=model, voice=voice, system=system, tone_mode=tone_mode, assistant_name=assistant_name)
interface.run()
```

There are several ready-to-go characters in the `characters` directory.

## Chat Logs

Chat logs are saved in the `$HOME/Documents/BanterBot/Conversations/` directory as individual `.txt` files.

## Documentation

For more complete documentation, please refer to the [BanterBot Docs](https://gabrielscabrera.github.io/BanterBot/).
