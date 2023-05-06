# GPTBot
## A Conversational AI Chatbot

GPTBot is an interactive command-line-based chatbot that utilizes the ChatGPT architecture to engage users in natural language conversations. The program is designed to provide an immersive and visually appealing experience by leveraging the `termighty` library to create a terminal interface with rich text formatting and colors. In addition to text-based interactions, GPTBot also supports text-to-speech synthesis, enabling the chatbot to speak its responses with a variety of voices and emotional styles.
Features

* Interactive command-line interface with rich text formatting and colors using the termighty library
* Text-based conversation with a chatbot powered by ChatGPT
* Text-to-speech synthesis for spoken responses using Azure Speech TTS
* Customizable chatbot character for personalized experiences
* Real-time response display and updates
* Input history tracking and conversation summarization
* Threading for efficient and smooth operation

## Requirements

Requires three environment variables for full functionality:

* `OPENAI_API_KEY`: A valid OpenAI API key,
* `AZURE_SPEECH_KEY`: A valid Azure Cognitive Services Speech API key for TTS functionality,
* `AZURE_SPEECH_REGION`: The region associated with your Azure Cognitive Services Speech API key.

## Usage

### Manual Installation

To install and initiate the GPTBot interface, follow these steps:

1. Clone the GPTBot repository and navigate to the cloned directory.
2. Install the necessary package by running `python -m pip install .` in your terminal.
3. Launch the GPTBot Command Line Interface (CLI) by executing the `gptbot` command.

### Basics

For character customization, utilize the optional `--character` argument as follows:

`gptbot --character [character]`

Replace `[character]` with your desired chatbot character. It is advised to use second-person singular in the format "<name> from <context>, <additional details>". For example, "Marvin the Paranoid Android. You are a sad robot with a brain the size of a planet."

If no character is specified, `GPTBot` will default to Marvin the Paranoid Android.

For a randomly selected character, simply use:

`gptbot --random`

Once the interface is launched, type your messages in the input box, and GPTBot will generate responses in the output window. Additionally, you can listen to GPTBot's responses through synthesized speech.

### Available Command-Line Arguments

The program accepts the following command-line arguments:

* `-u` or `--username`: Specify the name of the program's user (one word, no spaces),
* `-c` or `--character`: Provide a name and/or short description of the persona GPTBot should emulate. It is recommended to use second-person singular in the format "<name> from <context>, <additional details>",
* `-m` or `--mode`: Select an OpenAI API mode, either "ChatCompletion" or "Completion"; defaults to "ChatCompletion",
* `-r`, `--rand`, or `--random`: Override the "character" argument and select a random character.
* `-n`, `--no-thread`: Disable multithreading on initialization of GPTBot (can help with "Too Many Requests" exceptions).
* `-g`, `--gpt4`: Enable GPT-4; overrides --mode and --no-thread flag, and only works if you have GPT-4 API access.
* `-t`, `--temp` or `--temperature`: Set the model temperature.

## Dependencies
1. `openai`: The OpenAI library is a Python package that provides a convenient and user-friendly way to interact with the OpenAI API. It allows developers to access various AI models, such as GPT-3, for tasks like natural language processing, translation, and text generation.

2. `tiktoken`: Tiktoken is a lightweight Python library for tokenizing text data. It is particularly useful when working with APIs that have token-based usage limits, as it enables developers to count the number of tokens in a text string without making an actual API call.

3. `geocoder`: Geocoder is a Python library that simplifies the process of geocoding and reverse geocoding. It allows developers to obtain geographic coordinates (latitude and longitude) for a given address or location, or retrieve the address for a given set of coordinates, by accessing various geocoding providers like Google Maps, OpenStreetMap, and more.

4. `requests`: The Requests library is a popular Python package for making HTTP requests in a simple and user-friendly manner. It streamlines the process of sending and receiving data from web services, handling tasks like URL encoding, handling query parameters, and managing cookies.

5. `termighty`: Termighty is a Python package that offers a toolkit for creating interactive terminal-based applications. It provides developers with functionalities like handling user input, managing terminal colors and styles, and organizing content on the screen.

6. `azure-cognitiveservices-speech`: The Azure Cognitive Services Speech SDK is a Python package that enables developers to integrate Microsoft's speech recognition, text-to-speech, and speech translation services into their applications. It provides a simple interface for working with speech data and supports various languages and dialects.

7. `spacy`: SpaCy is an efficient Python library for natural language processing (NLP) tasks, offering features like tokenization, part-of-speech tagging, named entity recognition, and dependency parsing. Its architecture is optimized for speed and scalability, suitable for various text processing applications. It supports pre-trained models for multiple languages and allows customization with custom datasets.
