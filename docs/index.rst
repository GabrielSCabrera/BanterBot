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
``banterbot`` command.

Add the ``-g`` flag to enable GPT-4 for better quality conversations;
note that this will only work if you have GPT-4 API access, and is both
significantly more costly and slower than the default GPT-3.5-Turbo.

Add the ``-s`` flag followed by a string in quotes to set up a custom
character prior to initialization (e.g., ``-s "You are Grendel the Quiz
Troll, a charismatic troll who loves to host quiz shows."``).

Add the ``-m`` flag to activate the multiplayer interface.

Launch with a Python script
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use BanterBot in a script, create an instance of the `TKSimpleInterface`
class and call the `run` method:

.. code:: python

   from banterbot import TKSimpleInterface, get_voice_by_name, get_model_by_name

   model = get_model_by_name("gpt-3.5-turbo")
   voice = get_voice_by_name("Aria")
   style = "chat"

   # Optional system prompt to set up a custom character prior to initializing BanterBot.
   system = "You are Grendel the Quiz Troll, a charismatic troll who loves to host quiz shows."

   # The four arguments `model`, `voice`, `style`, and `system` are optional.
   interface = TKSimpleInterface(model=model, voice=voice, style=style, system=system)
   interface.run()


For multiplayer, you can modify the above code slightly:

.. code:: python

    from banterbot import TKMultiplayerInterface, get_voice_by_name, get_model_by_name

    model = get_model_by_name("gpt-3.5-turbo")
    voice = get_voice_by_name("Aria")
    style = "chat"

    # Optional system prompt to set up a custom character prior to initializing BanterBot.
    system = "You are Grendel the Quiz Troll, a charismatic troll who loves to host quiz shows."

    # The four arguments `model`, `voice`, `style`, and `system` are optional.
    interface = TKMultiplayerInterface(model=model, voice=voice, style=style, system=system)
    interface.run()

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
