.. BanterBot documentation master file, created by
   sphinx-quickstart on Sun May 28 21:02:41 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to BanterBot's documentation!
=====================================

BanterBot is a user-friendly chatbot application that leverages OpenAI
models for generating context-aware responses, Azure Neural Voices for
text-to-speech synthesis, and Azure speech-to-text recognition. The
package offers a comprehensive toolkit for building chatbot
applications with an intuitive interface and a suite of utilities.

Features
--------

-  Employs OpenAI models for generating context-sensitive responses
-  Utilizes Azure Neural Voices for high-quality text-to-speech
   synthesis
-  Supports a variety of output formats, voices, and speaking styles
-  Enables real-time monitoring of the chatbot’s responses
-  Features asynchronous speech-to-text microphone input
-  Provides an abstract base class for crafting frontends for the
   BanterBot application
-  Includes a tkinter-based frontend implementation

Requirements
------------

Three environment variables are required for full functionality:

-  ``OPENAI_API_KEY``: A valid OpenAI API key
-  ``AZURE_SPEECH_KEY``: A valid Azure Cognitive Services Speech
   API key for text-to-speech and speech-to-text functionality
-  ``AZURE_SPEECH_REGION``: The region associated with your Azure
   Cognitive Services Speech API key

Components
----------

OpenAIManager
~~~~~~~~~~~~~

.. autoclass:: banterbot.core.openai_manager.OpenAIManager
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

TextToSpeech
~~~~~~~~~~~~

.. autoclass:: banterbot.core.text_to_speech.TextToSpeech
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

SpeechToText
~~~~~~~~~~~~

.. autoclass:: banterbot.core.speech_to_text.SpeechToText
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

BanterBotInterface
~~~~~~~~~~~~~~~~~~

.. autoclass:: banterbot.gui.banter_bot_interface.BanterBotInterface
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

BanterBotTK
~~~~~~~~~~~

.. autoclass:: banterbot.gui.banter_bot_tk.BanterBotTK
   :members:
   :undoc-members:
   :special-members:
   :show-inheritance:

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

Start the BanterBot Command Line Interface (CLI) by executing the
``banterbot`` command. Use the ``-g`` or ``--gpt4`` flags to enable
GPT-4; this only works if you have GPT-4 API access.

Launch with a Python script
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use BanterBot in a script, create an instance of the `BanterBotTK`
class and call the `run` method:

.. code:: python

   from banterbot import BanterBotTK, get_voice_by_name, get_model_by_name

   model = get_model_by_name("gpt-3.5-turbo")
   voice = get_voice_by_name("Aria")
   style = "chat"

   # The three arguments `model`, `voice`, and `style` are optional.
   BBTK = BanterBotTK(model=model, voice=voice, style=style)
   BBTK.run()

Chat Logs
---------

Chat logs are saved in the ``$HOME/Documents/BanterBot/Conversations/``
directory as individual ``.txt`` files.

Documentation
=====================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
