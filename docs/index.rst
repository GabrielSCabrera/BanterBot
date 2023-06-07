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
-  Offers a wide range of output formats, voices, and speaking
   styles
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

OpenAIManager
~~~~~~~~~~~~~

A class responsible for managing interactions with the OpenAI
ChatCompletion API. It offers functionality to generate responses from
the API based on input messages. It supports generating responses in
their entirety or as a stream of response blocks.

TextToSpeech
~~~~~~~~~~~~

A class that handles text-to-speech synthesis using Azure’s Cognitive
Services. It supports a wide range of output formats, voices, and
speaking styles. The synthesized speech can be interrupted, and the
progress can be monitored in real-time.

SpeechToText
~~~~~~~~~~~~

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

TKSimpleInterface
~~~~~~~~~~~~~~~~~

A graphical user interface (GUI) for a chatbot application that employs
OpenAI models for generating responses, Azure Neural Voices for
text-to-speech, and Azure speech-to-text. The class inherits from both
tkinter.Tk and Interface, offering a seamless integration of chatbot
functionality with an intuitive interface.

TKMultiplayerInterface (In Development)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This GUI establishes a multiplayer conversation environment where up to
nine users can interact with the chatbot simultaneously. The GUI
includes a conversation history area and user panels with ‘Listen’
buttons to process user input. It also supports key bindings for user
convenience.

Installation
------------

Pip (Recommended)
~~~~~~~~~~~~~~~~~

BanterBot is installable using the Python Package Index (PyPi):

.. code:: bash

   python -m pip install banterbot

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

Start BanterBot by running the ``banterbot`` command in your terminal.

-  Add the ``-g`` flag to enable GPT-4 for enhanced conversation
   quality. Please note that GPT-4 API access is required, and using
   GPT-4 is more costly and slower than the default GPT-3.5-Turbo.

-  Use the ``-p`` flag followed by a string in quotes to set up a custom
   character prior to initialization (e.g.,
   ``-p "You are Grendel the Quiz Troll, a charismatic troll who loves hosting quiz shows."``).

-  Include the ``-m`` flag to activate the multiplayer interface.

-  Apply the ``-e`` flag to enable emotional tone evaluation before the
   bot generates its responses.

-  To select a Microsoft Azure Cognitive Services text-to-speech voice,
   use the ``-v`` flag followed by one of the available voice options
   (e.g., ``-v jenny``).

-  Select a Microsoft Azure Cognitive Services text-to-speech voice
   style by using the ``-s`` flag followed by one of the available style
   options (e.g., ``-s friendly``).

Launch with a Python script
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use BanterBot in a script, create an instance of the
``TKSimpleInterface`` class and call the ``run`` method:

.. code:: python

   from banterbot import TKSimpleInterface, get_voice_by_name, get_model_by_name

   model = get_model_by_name("gpt-3.5-turbo")
   voice = get_voice_by_name("Davis")

   style = "excited"
   # Optional system prompt to set up a custom character prior to initializing BanterBot.
   system = "You are Grendel the Quiz Troll, a charismatic troll who loves to host quiz shows."

   # The four arguments `model`, `voice`, `style`, `system`, and `tone` are optional.
   # Setting `tone` to True enables voice tones and emotions.
   interface = TKSimpleInterface(model=model, voice=voice, style=style, system=system, tone=True)
   interface.run()

For multiplayer, you can swap out TKSimpleInterface in the above code
with TKMultiplayerInterface.

Chat Logs
---------

Chat logs are saved in the ``$HOME/Documents/BanterBot/Conversations/``
directory as individual ``.txt`` files.

Components
----------

OpenAIManager
~~~~~~~~~~~~~

.. autoclass:: banterbot.api_managers.openai_manager.OpenAIManager
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

TextToSpeech
~~~~~~~~~~~~

.. autoclass:: banterbot.api_managers.text_to_speech.TextToSpeech
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

SpeechToText
~~~~~~~~~~~~

.. autoclass:: banterbot.api_managers.speech_to_text.SpeechToText
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

Interface
~~~~~~~~~

.. autoclass:: banterbot.gui.interface.Interface
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

TKSimpleInterface
~~~~~~~~~~~~~~~~~

.. autoclass:: banterbot.gui.tk_simple_interface.TKSimpleInterface
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

TKMultiplayerInterface
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: banterbot.gui.tk_multiplayer_interface.TKMultiplayerInterface
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

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
