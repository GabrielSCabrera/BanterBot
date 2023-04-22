# GPTBot
## A Conversational AI Chatbot

GPTBot is an interactive command-line-based chatbot that utilizes the ChatGPT architecture to engage users in natural language conversations. The program is designed to provide an immersive and visually appealing experience by leveraging the termighty library to create a terminal interface with rich text formatting and colors. In addition to text-based interactions, GPTBot also supports text-to-speech synthesis, enabling the chatbot to speak its responses with a variety of voices and emotional styles.
Features

* Interactive command-line interface with rich text formatting and colors using the termighty library
* Text-based conversation with a chatbot powered by ChatGPT
* Text-to-speech synthesis for spoken responses using Azure Speech TTS
* Customizable chatbot character for personalized experiences
* Real-time response display and updates
* Input history tracking and conversation summarization
* Threading for efficient and smooth operation

## Usage

To start the GPTBot interface, run the following command in your terminal:

python interface.py [character]

Replace [character] with the desired character for the chatbot (optional). If no character is provided, GPTBot will use a default character.

Once the interface is started, you can type your messages in the input box, and GPTBot will provide its responses in the output window. You can also listen to the synthesized speech of GPTBot's responses.

## Requirements

Requires three environment variables for full functionality:

1. `OPENAI_API_KEY` must be a valid OpenAI API key, 
2. `AZURE_SPEECH_KEY` must be a valid Azure Speech Service API key, for TTS functionality,
3. `AZURE_SPEECH_REGION` must be the region associated with the Azure Speech Service API key.
