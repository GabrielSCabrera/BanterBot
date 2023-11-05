import datetime
import logging
import threading
from abc import ABC, abstractmethod
from typing import List, Optional, Union

from banterbot.config import chat_logs
from banterbot.data.azure_neural_voices import AzureNeuralVoice
from banterbot.data.enums import ChatCompletionRoles, ToneMode
from banterbot.data.openai_models import OpenAIModel, get_model_by_name
from banterbot.data.prompts import ToneSelection
from banterbot.extensions.option_selector import OptionSelector
from banterbot.extensions.prosody_selector import ProsodySelector
from banterbot.managers.openai_manager import OpenAIManager
from banterbot.managers.speech_to_text import SpeechToText
from banterbot.managers.text_to_speech import TextToSpeech
from banterbot.utils.message import Message
from banterbot.utils.thread_queue import ThreadQueue


class Interface(ABC):
    """
    Interface is an abstract base class for creating frontends for the BanterBot application. It provides a high-level
    interface for managing conversation with the bot, including sending messages, receiving responses, and updating a
    conversation area. The interface supports both text and speech-to-text input for user messages.
    """

    def __init__(
        self,
        model: OpenAIModel,
        voice: AzureNeuralVoice,
        style: str,
        languages: Optional[Union[str, list[str]]] = None,
        system: Optional[str] = None,
        tone_mode: Optional[ToneMode] = None,
        phrase_list: Optional[list[str]] = None,
    ) -> None:
        """
        Initialize the BanterBotInterface with the given model, voice, and style.

        Args:
            model (OpenAIModel): The OpenAI model to use for generating responses.
            voice (AzureNeuralVoice): The voice to use for text-to-speech synthesis.
            style (str): The speaking style to use for text-to-speech synthesis.
            languages (Optional[Union[str, list[str]]]): The languages supported by the speech-to-text recognizer.
            system (Optional[str]): An initialization prompt that can be used to set the scene.
            tone_mode (bool): Which tone evaluation mode to use.
            phrase_list(list[str], optional): Optionally provide the recognizer with context to improve recognition.
        """
        logging.debug(f"Interface initialized")

        # Initialize OpenAI ChatCompletion, Azure Speech-to-Text, and Azure text-to-speech components
        self._openai_manager = OpenAIManager(model=model)
        self._speech_to_text = SpeechToText(languages=languages, phrase_list=phrase_list)
        self._text_to_speech = TextToSpeech()

        # Initialize message handling and conversation attributes
        self._messages: List[Message] = []
        self._messages_token_count: List[int] = []
        self._log_lock = threading.Lock()
        self._log_path = chat_logs / f"chat_{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}.txt"
        self._listening_toggle = False

        # Initialize thread management components
        self._thread_queue = ThreadQueue()

        # Initialize model, voice, and style attributes
        self._model = model
        self._voice = voice
        self._style = style

        # Initialize the OptionSelector for tone selection
        self._tone = tone_mode
        self._tone_selector = OptionSelector(
            model=get_model_by_name("gpt-3.5-turbo"),
            options=self._voice.styles,
            system=ToneSelection.SYSTEM.value,
            prompt=ToneSelection.PROMPT.value.format(self._style),
        )
        self._prosody_selector = ProsodySelector(model=get_model_by_name("gpt-4"), voice=self._voice)

        # Initialize the system message, if provided
        self._system = system
        if self._system is not None:
            message = Message(role=ChatCompletionRoles.SYSTEM, content=system)
            self._messages.append(message)
            self._messages_token_count.append(message.count_tokens(model=self._model))

        # Initialize the subclass GUI
        self._init_gui()

    @property
    def listening(self) -> bool:
        """
        If the current instance of SpeechToText is in the process of listening, returns True. Otherwise, returns False.

        Args:
            bool: The listening state of the current instance.
        """
        return self._speech_to_text._listening

    @property
    def speaking(self) -> bool:
        """
        If the current instance of TextToSpeech is in the process of speaking, returns True. Otherwise, returns False.

        Args:
            bool: The speaking state of the current instance.
        """
        return self._text_to_speech.speaking

    @property
    def streaming(self) -> bool:
        """
        If the current instance of OpenAIManager is in the process of streaming, returns True. Otherwise, returns False.

        Args:
            bool: The streaming state of the current instance.
        """
        return self._openai_manager.streaming

    def send_message(
        self,
        content: str,
        role: ChatCompletionRoles = ChatCompletionRoles.USER,
        name: Optional[str] = None,
        hidden: bool = False,
    ) -> None:
        """
        Send a message from the user to the conversation.

        Args:
            message (str): The message content from the user.
            role (ChatCompletionRoles): The role (USER, ASSISTANT, SYSTEM) associated with the content.
            name (Optional[str]): The name of the user sending the message. Defaults to None.
            hidden (bool): If True, does not display the message in the interface.
        """
        message = Message(role=role, name=name, content=content)
        name = message.name.title() if message.name is not None else ChatCompletionRoles.USER.value.title()
        text = f"{name}: {content}\n\n"
        self._messages.append(message)
        self._messages_token_count.append(message.count_tokens(model=self._model))
        if not hidden:
            self.update_conversation_area(word=text)

    def system_prompt(self, message: str, name: Optional[str] = None) -> None:
        """
        Prompt the bot with the given message, issuing a command which is not displayed in the conversation area.

        Args:
            message (str): The message content from the user.
        """
        # Do not send the message if it is empty.
        if message.strip():

            # Interrupt any currently active ChatCompletion, text-to-speech, or speech-to-text streams
            if self._thread_queue.is_alive():
                self._openai_manager.interrupt()
                self._text_to_speech.interrupt()
                self._speech_to_text.interrupt()

            message_thread = threading.Thread(
                target=self.send_message,
                args=(
                    message,
                    ChatCompletionRoles.SYSTEM,
                    None,
                    True,
                ),
                daemon=True,
            )
            self._thread_queue.add_task(message_thread, unskippable=True)
            self._thread_queue.add_task(threading.Thread(target=self.get_response, daemon=True))

    def prompt(self, message: str, name: Optional[str] = None) -> None:
        """
        Prompt the bot with the given user message.

        Args:
            message (str): The message content from the user.
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        # Do not send the message if it is empty.
        if message.strip():

            # Interrupt any currently active ChatCompletion, text-to-speech, or speech-to-text streams
            if self._thread_queue.is_alive():
                self._openai_manager.interrupt()
                self._text_to_speech.interrupt()
                self._speech_to_text.interrupt()

            message_thread = threading.Thread(
                target=self.send_message,
                args=(
                    message,
                    ChatCompletionRoles.USER,
                    name,
                ),
                daemon=True,
            )
            self._thread_queue.add_task(message_thread, unskippable=True)
            self._thread_queue.add_task(threading.Thread(target=self.get_response, daemon=True))

    def listener_toggle(self, name: Optional[str] = None) -> None:
        """
        Toggle the listening state of the bot. If the bot is currently listening, it will stop listening for user input
        using speech-to-text. If the bot is not currently listening, it will start listening for user input using
        speech-to-text.

        Args:
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        if self._listening_toggle:
            self.listener_deactivate()
        else:
            self.listener_activate(name=name)

    def listener_activate(self, name: Optional[str] = None) -> None:
        """
        Activate the speech-to-text listener.

        Args:
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        if not self._listening_toggle:
            self._listening_toggle = True
            self._listen_thread = threading.Thread(target=self._listen, args=(name,), daemon=True)
            self._listen_thread.start()

    def listener_deactivate(self, soft: bool = True) -> None:
        """
        Deactivate the speech-to-text listener.
        """
        if self._listening_toggle:
            self._listening_toggle = False
            self._speech_to_text.interrupt(soft=soft)

    def get_response(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIManager and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        if self._tone is None:
            self._get_response_no_tone()
        elif self._tone == ToneMode.BASIC:
            self._get_response_basic_tone()
        elif self._tone == ToneMode.ADVANCED:
            self._get_response_advanced_tone()

    def _get_response_advanced_tone(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIManager and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        prefixed = False
        content = []

        # Initialize the generator for asynchronous yielding of sentence blocks
        for block in self._openai_manager.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area(f"{ChatCompletionRoles.ASSISTANT.value.title()}: ")
                prefixed = True

            messages = self._messages
            messages_token_count = self._messages_token_count
            system = ""

            if self._system:
                messages = messages[1:]
                messages_token_count = messages_token_count[1:]
                system = self._system

            phrases = self._prosody_selector.select(block, messages, messages_token_count, content, system)

            for word in self._text_to_speech.speak_phrases(phrases):
                self.update_conversation_area(word.word)
                content.append(word.word)

            self.update_conversation_area(" ")
            content.append(" ")

        content = "".join(content)
        message = Message(role=ChatCompletionRoles.ASSISTANT, content=content.strip())
        self._messages.append(message)
        self._messages_token_count.append(message.count_tokens(model=self._model))

        self.end_response()

    def _get_response_basic_tone(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIManager and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        prefixed = False
        content = []

        style = self._get_next_tone()
        tone_content = f"Tone: {style}\n"
        # Add an intermediate message (not visualized in the conversation area) noting the assistant's tone.
        self._append_to_chat_log(tone_content)
        message = Message(role=ChatCompletionRoles.ASSISTANT, content=tone_content)
        self._messages.append(message)
        self._messages_token_count.append(message.count_tokens(model=self._model))

        # Initialize the generator for asynchronous yielding of sentence blocks
        for block in self._openai_manager.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area(f"{ChatCompletionRoles.ASSISTANT.value.title()}: ")
                prefixed = True

            sentences = " ".join(block)
            for word in self._text_to_speech.speak(sentences, voice=self._voice, style=style):
                self.update_conversation_area(word.word)
                content.append(word.word)

            self.update_conversation_area(" ")
            content.append(" ")

        content = "".join(content)
        message = Message(role=ChatCompletionRoles.ASSISTANT, content=content.strip())
        self._messages.append(message)
        self._messages_token_count.append(message.count_tokens(model=self._model))
        self.end_response()

    def _get_response_no_tone(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIManager and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        prefixed = False
        content = []

        # Initialize the generator for asynchronous yielding of sentence blocks
        for block in self._openai_manager.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area(f"{ChatCompletionRoles.ASSISTANT.value.title()}: ")
                prefixed = True

            sentences = " ".join(block)
            for word in self._text_to_speech.speak(sentences, voice=self._voice, style=self._style):
                self.update_conversation_area(word.word)
                content.append(word.word)

            self.update_conversation_area(" ")
            content.append(" ")

        content = "".join(content)
        message = Message(role=ChatCompletionRoles.ASSISTANT, content=content.strip())
        self._messages.append(message)
        self._messages_token_count.append(message.count_tokens(model=self._model))
        self.end_response()

    def get_response_advanced(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIManager and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        prefixed = False
        content = []
        style = self._style

        # If the tone is to be evaluated, evaluate it once before yielding the blocks
        if self._tone:
            style = self._get_next_tone()
            tone_content = f"Tone: {style}\n"
            # Add an intermediate message (not visualized in the conversation area) noting the assistant's tone.
            self._append_to_chat_log(tone_content)
            message = Message(role=ChatCompletionRoles.ASSISTANT, content=tone_content)
            self._messages.append(message)
            self._messages_token_count.append(message.count_tokens(model=self._model))

        # Initialize the generator for asynchronous yielding of sentence blocks
        for block in self._openai_manager.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area(f"{ChatCompletionRoles.ASSISTANT.value.title()}: ")
                prefixed = True

            sentences = " ".join(block)
            for word in self._text_to_speech.speak(sentences, voice=self._voice, style=style):
                self.update_conversation_area(word.word)
                content.append(word.word)

            self.update_conversation_area(" ")
            content.append(" ")

        content = "".join(content)
        message = Message(role=ChatCompletionRoles.ASSISTANT, content=content.strip())
        self._messages.append(message)
        self._messages_token_count.append(message.count_tokens(model=self._model))
        self.end_response()
        speak_phrases

    def end_response(self) -> None:
        """
        End the bot's response and update the conversation area accordingly. This method should be called after the
        bot's response has been fully generated and added to the conversation area.
        """
        self.update_conversation_area("\n\n")

    @abstractmethod
    def _init_gui(self) -> None:
        """
        Initialize the graphical user interface for the frontend.
        This method should be implemented by subclasses to create the specific GUI components.
        """

    @abstractmethod
    def update_conversation_area(self, word: str) -> None:
        """
        Update the conversation area with the given word, and add the word to the chat log.
        This method should be implemented by subclasses to handle updating the specific GUI components.

        Args:
            word (str): The word to add to the conversation area.
        """
        self._append_to_chat_log(word)

    @abstractmethod
    def run(self) -> None:
        """
        Run the frontend application.
        This method should be implemented by subclasses to handle the main event loop of the specific GUI framework.
        """

    def _listen(self, name: Optional[str] = None) -> None:
        """
        Listen for user input using speech-to-text and prompt the bot with the transcribed message.

        Args:
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        # Interrupt any currently active ChatCompletion, text-to-speech, or speech-to-text streams
        self._speech_to_text.interrupt()
        self._text_to_speech.interrupt()
        self._openai_manager.interrupt()

        # Flag is set to True if a new user input is detected.
        input_detected = False

        # Listen for user input using speech-to-text
        for sentence in self._speech_to_text.listen():

            # Do not send the message if it is empty.
            if sentence.strip():

                # Set the flag to True since a new user input was detected.
                input_detected = True

                # Send the transcribed message to the bot
                message_thread = threading.Thread(
                    target=self.send_message,
                    args=(
                        sentence.strip(),
                        ChatCompletionRoles.USER,
                        name,
                    ),
                    daemon=True,
                )
                self._thread_queue.add_task(message_thread, unskippable=True)

        if input_detected:
            self._thread_queue.add_task(threading.Thread(target=self.get_response, daemon=True))

    def _append_to_chat_log(self, word: str) -> None:
        """
        Updates the chat log with the latest output.

        Args:
            word (str): The word to be added to the conversation area.
        """
        with self._log_lock:
            logging.debug(f"Interface appended new data to the chat log")
            with open(self._log_path, "a+") as fs:
                fs.write(word)

    def _get_next_tone(self):
        """
        Sends the message history as an input to the tone selector to semi-randomly select a fitting tone for the
        assistant's next response. If the tone selection fails, returns the default style.

        Returns:
            str: A voice tone compatible with the active AzureNeuralVoice instance.
        """
        tone = self._tone_selector.select(self._messages)
        return tone if tone is not None else self._style
