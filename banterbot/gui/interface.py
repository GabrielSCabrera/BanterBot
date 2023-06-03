import datetime
import threading
from abc import ABC, abstractmethod
from typing import List, Optional

from banterbot.core.openai_manager import OpenAIManager
from banterbot.core.speech_to_text import SpeechToText
from banterbot.core.text_to_speech import TextToSpeech
from banterbot.data.azure_neural_voices import AzureNeuralVoice
from banterbot.data.config import chat_logs
from banterbot.data.openai_models import OpenAIModel
from banterbot.utils.message import Message
from banterbot.utils.thread_queue import ThreadQueue


class Interface(ABC):
    """
    Interface is an abstract base class for creating frontends for the BanterBot application. It provides a high-level
    interface for managing conversation with the bot, including sending messages, receiving responses, and updating the
    conversation area. The interface supports both text and speech-to-text input for user messages.
    """

    def __init__(self, model: OpenAIModel, voice: AzureNeuralVoice, style: str) -> None:
        """
        Initialize the BanterBotInterface with the given model, voice, and style.

        Args:
            model (OpenAIModel): The OpenAI model to use for generating responses.
            voice (AzureNeuralVoice): The voice to use for text-to-speech synthesis.
            style (str): The speaking style to use for text-to-speech synthesis.
        """
        # Initialize OpenAI ChatCompletion, Azure Speech-to-Text, and Azure Text-to-Speech components
        self._openai_manager = OpenAIManager(model=model)
        self._speech_to_text = SpeechToText()
        self._text_to_speech = TextToSpeech()

        # Initialize message handling and conversation attributes
        self._messages: List[Message] = []
        self._output_lock = threading.Lock()
        self._log_lock = threading.Lock()
        self._log_path = chat_logs / f"chat_{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}.txt"
        self._response_thread = None
        self._listening_toggle = False

        # Initialize thread management components
        self._thread_queue = ThreadQueue()

        # Initialize voice and style attributes
        self._voice = voice
        self._style = style

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

    def send_message(self, user_message: str, name: Optional[str] = None) -> None:
        """
        Send a message from the user to the conversation.

        Args:
            user_message (str): The message content from the user.
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        message = Message(role="user", name=name, content=user_message)
        text = f"{message.name.title() if message.name is not None else 'User'}: {user_message}\n\n"
        self._messages.append(message)
        self.update_conversation_area(word=text)

    def prompt(self, user_message: str, name: Optional[str] = None) -> None:
        """
        Prompt the bot with the given user message.

        Args:
            user_message (str): The message content from the user.
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        # Do not send the message if it is empty.
        if user_message.strip():
            message_thread = threading.Thread(
                target=self.send_message,
                args=(
                    user_message,
                    name,
                ),
                daemon=True,
            )
            self._thread_queue.add_task(message_thread, unskippable=True)

            self._response_thread = threading.Thread(target=self.get_response, daemon=True)
            self._thread_queue.add_task(self._response_thread)

            # Interrupt any currently active ChatCompletion or Text-to-Speech streams
            if self._thread_queue.is_alive():
                self._openai_manager.interrupt()
                self._text_to_speech.interrupt()

    def toggle_listen(self, name: Optional[str] = None) -> None:
        """
        Toggle the listening state of the bot. If the bot is currently listening, it will stop listening for user input
        using speech-to-text. If the bot is not currently listening, it will start listening for user input using
        speech-to-text.

        Args:
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        if self._listening_toggle:
            self._speech_to_text.interrupt()
        else:
            self._listen_thread = threading.Thread(target=self._listen, args=(name,), daemon=True)
            self._listen_thread.start()

        self._listening_toggle = not self._listening_toggle

    def get_response(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIManager and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        prefixed = False
        content = []
        for block in self._openai_manager.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area("Assistant: ")
                prefixed = True

            sentences = " ".join(block)
            for word in self._text_to_speech.speak(sentences, voice=self._voice, style=self._style):
                self.update_conversation_area(word.word)
                content.append(word.word)

            self.update_conversation_area(" ")
            content.append(" ")

        content = "".join(content)
        self._messages.append(Message(role="assistant", content=content.strip()))
        self.end_response()

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
        # Listen for user input using speech-to-text
        for sentence in self._speech_to_text.listen():

            # Do not send the message if it is empty.
            if sentence.strip():

                # Send the transcribed message to the bot
                message_thread = threading.Thread(
                    target=self.send_message,
                    args=(
                        sentence,
                        name,
                    ),
                    daemon=True,
                )
                self._thread_queue.add_task(message_thread, unskippable=True)

                self._response_thread = threading.Thread(target=self.get_response, daemon=True)
                self._thread_queue.add_task(self._response_thread)

                # Interrupt any currently active ChatCompletion or Text-to-Speech streams
                if self._thread_queue.is_alive():
                    self._openai_manager.interrupt()
                    self._text_to_speech.interrupt()

    def _append_to_chat_log(self, word: str) -> None:
        """
        Updates the chat log with the latest output.

        Args:
            word (str): The word to be added to the conversation area.
        """
        with self._log_lock:
            with open(self._log_path, "a+") as fs:
                fs.write(word)
