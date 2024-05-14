.. BanterBot documentation master file, created by
   sphinx-quickstart on Sun May 28 21:02:41 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to BanterBot's documentation!
=====================================

BanterBot is a user-friendly chatbot application that leverages OpenAI
models for generating context-aware responses, Azure Neural Voices for
text-to-speech synthesis, and Azure speech-to-text recognition. The
package offers a comprehensive toolkit for building chatbot applications
with an intuitive interface and a suite of utilities.

Features
--------

-  Utilizes OpenAI models to generate context-aware responses
-  Leverages Azure Neural Voices for premium text-to-speech
   synthesis
-  Offers a wide range of output formats, multilingual voices,
   and speaking styles
-  Allows real-time monitoring of the chatbot's responses
-  Supports asynchronous speech-to-text microphone input
-  Includes an abstract base class for creating custom frontends
   for the BanterBot application
-  Features a tkinter-based frontend implementation
-  Automatically selects an appropriate emotion or tone based on
   the conversation context

Requirements
------------

Three environment variables are required for full functionality:

-  ``OPENAI_API_KEY``: A valid OpenAI API key
-  ``AZURE_SPEECH_KEY``: A valid Azure Cognitive Services Speech API key
   for text-to-speech and speech-to-text functionality
-  ``AZURE_SPEECH_REGION``: The region associated with your Azure
   Cognitive Services Speech API key

Components
----------

TKInterface
~~~~~~~~~~~

A graphical user interface (GUI) establishes a multiplayer conversation
environment where up to nine users can interact with the chatbot
simultaneously. The GUI includes a conversation history area and user
panels with 'Listen' buttons to process user input. It also supports key
bindings for user convenience.

OpenAIService
~~~~~~~~~~~~~

A class responsible for managing interactions with the OpenAI
ChatCompletion API. It offers functionality to generate responses from
the API based on input messages. It supports generating responses in
their entirety or as a stream of response blocks.

SpeechSynthesisService
~~~~~~~~~~~~~~~~~~~~~~

A class that handles text-to-speech synthesis using Azure’s Cognitive
Services. It supports a wide range of output formats, voices, and
speaking styles. The synthesized speech can be interrupted, and the
progress can be monitored in real-time.

SpeechRecognitionService
~~~~~~~~~~~~~~~~~~~~~~~~

A class that provides an interface to convert spoken language into
written text using Azure Cognitive Services. It allows continuous speech
recognition and provides real-time results as sentences are recognized.

Interface
~~~~~~~~~

An abstract base class for designing frontends for the BanterBot
application. It provides a high-level interface for managing
conversations with the bot, including sending messages, receiving
responses, and updating the conversation area. Accepts both keyboard
inputs and microphone voice inputs.

Installation
------------

Important Note
~~~~~~~~~~~~~~

BanterBot requires several spaCy language models to run, and will
automatically download them on first-time initialization, if they
are missing or incompatible -- this process can sometimes take a while.

Pip (Recommended)
~~~~~~~~~~~~~~~~~

BanterBot can be installed or updated using the Python Package Index (PyPi):

.. code:: bash

   python -m pip install --upgrade banterbot


Manual
~~~~~~

To install BanterBot, simply clone the repository and install the
required dependencies:

.. code:: bash

   git clone https://github.com/gabrielscabrera/banterbot.git
   cd banterbot
   python -m pip install .

Usage
-----

Launch with Command Line
~~~~~~~~~~~~~~~~~~~~~~~~

Start BanterBot with an enhanced graphical user interface by running the command ``banterbot`` 
in your terminal. This GUI allows multiple users to interact with the bot, each with a dedicated 
button for speech input and a display for responses.

-  ``--prompt``: Set a system prompt at the beginning of
   the conversation (e.g., ``--prompt "You are Grendel the 
   Quiz Troll, a charismatic troll who loves to host quiz 
   shows."``).

-  ``--model``: Choose the OpenAI model for conversation
   generation. Defaults to GPT-4, but other versions can be
   selected if specified in the code.

-  ``--voice``: Select a Microsoft Azure Cognitive Services
   text-to-speech voice. The default is "Aria," but other voices
   can be specified if available.

-  ``--debug``: Enable debug mode to display additional
   information in the terminal for troubleshooting.

-  ``--greet``: Have the bot greet the user upon startup.

-  ``--name``: Assign a name to the assistant for aesthetic
   purposes. This does not inform the bot itself; to provide the bot
   with information, use the ``--prompt`` flag.

Here is an example:

.. code:: bash

   banterbot --greet --model gpt-4-turbo --voice davis --prompt "You are Grondle the Quiz Troll, a charismatic troll who loves to host quiz shows." --name Grondle

Additionally, you can use `banterbot character` to select a pre-loaded character to interact with. For example:

.. code:: bash

   banterbot character therapist

Will start a conversation with `Grendel the Therapy Troll`. To list all available characters, run:

.. code:: bash

   banterbot character -h

You can also use ``banterbot voice-search`` to search through all the available voices. For example:

.. code:: bash

   banterbot voice-search --language en fr

Will list all English (en) and French (fr) voice models. Run ``banterbot voice-search -h`` for more information.


Launch with a Python script
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use BanterBot in a script, create an instance of the ``TKInterface`` class and call its ``run`` method:

.. code:: python
   
   from banterbot import AzureNeuralVoiceManager, OpenAIModelManager, TKInterface

   model = OpenAIModelManager.load("gpt-4o")
   voice = AzureNeuralVoiceManager.load("Davis")
   assistant_name = "Grendel"

   # Optional system prompt to set up a custom character prior to initializing BanterBot.
   system = "You are Grendel the Quiz Troll, a charismatic troll who loves to host quiz shows."

   # The four arguments `model`, `voice`, `system`, and `assistant_name` are optional.
   interface = TKInterface(model=model, voice=voice, system=system, assistant_name=assistant_name)
   
   # Setting `greet` to True instructs BanterBot to initiate the conversation. Otherwise, the user must initiate.
   interface.run(greet=True)

Chat Logs
---------

Chat logs are saved in the ``$HOME/Documents/BanterBot/Conversations/``
directory as individual ``.txt`` files.


Documentation
=============

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
