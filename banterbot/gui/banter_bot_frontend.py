import threading
from abc import ABC, abstractmethod
from typing import List

from banterbot.core.openai_manager import OpenAIManager
from banterbot.core.text_to_speech import TextToSpeech
from banterbot.utils.message import Message
from banterbot.utils.thread_queue import ThreadQueue


class BanterBotFrontend(ABC):
    def __init__(self, model: str, voice: str, style: str) -> None:
        """
        Initialize the BanterBotFrontend with the given model, voice, and style.

        Args:
            model (str): The name of the OpenAI model to use.
            voice (str): The name of the voice to use for text-to-speech.
            style (str): The speaking style to use for text-to-speech.
        """
        self._openai_manager = OpenAIManager(model=model)
        self._text_to_speech = TextToSpeech()
        self._messages: List[Message] = []
        self._output_lock = threading.Lock()
        self._response_thread = None
        self._thread_queue = ThreadQueue()
        self._voice = voice
        self._style = style
        self._init_gui()

    @abstractmethod
    def _init_gui(self) -> None:
        """
        Initialize the graphical user interface for the frontend.
        This method should be implemented by subclasses.
        """

    @abstractmethod
    def update_conversation_area(self, word: str) -> None:
        """
        Update the conversation area with the given word.
        This method should be implemented by subclasses.

        Args:
            word (str): The word to add to the conversation area.
        """

    def send_message(self, user_message: str) -> None:
        """
        Send a message from the user to the conversation.

        Args:
            user_message (str): The message content from the user.
        """
        user_message_obj = Message(role="user", content=user_message)
        self._messages.append(user_message_obj)
        self.update_conversation_area(word=f"User: {user_message}")
        self.update_conversation_area(word="\n\n")

    def prompt(self, user_message: str) -> None:
        """
        Prompt the bot with the given user message.

        Args:
            user_message (str): The message content from the user.
        """
        if self._thread_queue.is_alive():
            self._openai_manager.interrupt()
            self._text_to_speech.interrupt()

        self._message_thread = threading.Thread(target=self.send_message, args=(user_message,), daemon=True)
        self._thread_queue.add_task(self._message_thread, unskippable=True)

        self._response_thread = threading.Thread(target=self.get_response, daemon=True)
        self._thread_queue.add_task(self._response_thread)

    def get_response(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response.
        """
        prefixed = False
        content = []
        for block in self._openai_manager.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area("Assistant: ")
                prefixed = True

            sentences = " ".join(block)
            for word in self._text_to_speech.speak(sentences, voice_name=self._voice, style=self._style):
                self.update_conversation_area(word.word)
                content.append(word.word)

            self.update_conversation_area(" ")
            content.append(" ")

        content = "".join(content)
        self._messages.append(Message(role="assistant", content=content.strip()))
        self.end_response()

    def end_response(self) -> None:
        """
        End the bot's response and update the conversation area accordingly.
        """
        self.update_conversation_area("\n\n")

    @abstractmethod
    def run(self) -> None:
        """
        Run the frontend application.
        This method should be implemented by subclasses.
        """
