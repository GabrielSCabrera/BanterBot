import datetime
import logging
import threading
import time
from abc import ABC, abstractmethod
from typing import Optional, Union

from banterbot.config import chat_logs
from banterbot.data.enums import ChatCompletionRoles, ToneMode
from banterbot.data.prompts import ToneSelection
from banterbot.exceptions.format_mismatch_error import FormatMismatchError
from banterbot.extensions.option_selector import OptionSelector
from banterbot.extensions.prosody_selector import ProsodySelector
from banterbot.managers.openai_model_manager import OpenAIModelManager
from banterbot.models.azure_neural_voice import AzureNeuralVoice
from banterbot.models.message import Message
from banterbot.models.openai_model import OpenAIModel
from banterbot.services.openai_service import OpenAIService
from banterbot.services.speech_recognition_service import SpeechRecognitionService
from banterbot.services.speech_synthesis_service import SpeechSynthesisService
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
        tone_mode_model: OpenAIModel = None,
        phrase_list: Optional[list[str]] = None,
        assistant_name: Optional[str] = None,
    ) -> None:
        """
        Initialize the Interface with the specified model, voice, and style.

        Args:
            model (OpenAIModel): The OpenAI model to use for generating responses.
            voice (AzureNeuralVoice): The voice to use for text-to-speech synthesis.
            style (str): The speaking style to use for text-to-speech synthesis.
            languages (Optional[Union[str, list[str]]]): The languages supported by the speech-to-text recognizer.
            system (Optional[str]): An initialization prompt that can be used to set the scene.
            tone_mode (bool): Which tone evaluation mode to use.
            tone_mode_model (OpenAIModel): The OpenAI ChatCompletion model to use for tone evaluation.
            phrase_list (list[str], optional): Optionally provide the recognizer with context to improve recognition.
        """
        logging.debug(f"Interface initialized")
        # Select the OpenAI ChatCompletion model for tone evaluation.
        tone_mode_model = OpenAIModelManager.load("gpt-3.5-turbo") if tone_mode_model is None else tone_mode_model

        # Initialize OpenAI ChatCompletion, Azure Speech-to-Text, and Azure Text-to-Speech components
        self._openai_service = OpenAIService(model=model)
        self._openai_service_tone = OpenAIService(model=tone_mode_model)
        self._speech_recognition_service = SpeechRecognitionService(languages=languages, phrase_list=phrase_list)
        self._speech_synthesis_service = SpeechSynthesisService()

        # Initialize message handling and conversation attributes
        self._messages: list[Message] = []
        self._log_lock = threading.Lock()
        self._log_path = chat_logs / f"chat_{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}.txt"
        self._listening_toggle = False

        # Initialize thread management components
        self._thread_queue = ThreadQueue()

        # Initialize model, voice, style, and assistant name attributes
        self._model = model
        self._voice = voice
        self._style = style
        self._assistant_name = ChatCompletionRoles.ASSISTANT.value.title() if assistant_name is None else assistant_name

        # Initialize the OptionSelector for tone selection
        self._tone = tone_mode
        self._tone_selector = OptionSelector(
            model=self._openai_service_tone,
            options=self._voice.styles,
            system=ToneSelection.SYSTEM.value,
            prompt=ToneSelection.PROMPT.value.format(self._style),
        )
        self._prosody_selector = ProsodySelector(
            manager=self._openai_service_tone,
            voice=self._voice,
        )

        # Initialize the interruption flag, set to zero.
        self._interrupt = 0

        # Initialize the system message, if provided
        self._system = system
        if self._system is not None:
            message = Message(role=ChatCompletionRoles.SYSTEM, content=system)
            self._messages.append(message)

        # Initialize the subclass GUI
        self._init_gui()

    @property
    def listening(self) -> bool:
        """
        If the current instance of `SpeechSynthesisService` is in the process of listening, returns True. Otherwise,
        returns False.

        Args:
            bool: The listening state of the current instance.
        """
        return self._speech_recognition_service._listening

    @property
    def speaking(self) -> bool:
        """
        If the current instance of `SpeechRecognitionService` is in the process of speaking, returns True. Otherwise,
        returns False.

        Args:
            bool: The speaking state of the current instance.
        """
        return self._speech_synthesis_service.speaking

    @property
    def streaming(self) -> bool:
        """
        If the current instance of OpenAIService is in the process of streaming, returns True. Otherwise, returns False.

        Args:
            bool: The streaming state of the current instance.
        """
        return self._openai_service.streaming

    def interrupt(self, soft: bool = False, shutdown_time: Optional[int] = None) -> None:
        """
        Interrupts all speech-to-text recognition, text-to-speech synthesis, and OpenAI API streams.

        Args:
            soft (bool): If True, allows the recognizer to keep processing data that was recorded prior to interruption.
            shutdown_time (Optional[int]): The time at which the listener was deactivated.
        """
        self._speech_recognition_service.interrupt(soft=soft, shutdown_time=shutdown_time)
        self._speech_synthesis_service.interrupt()
        self._openai_service.interrupt()
        self._interrupt = time.perf_counter_ns() if not shutdown_time else shutdown_time

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
            # Interrupt any currently active ChatCompletion, text-to-speech, or speech-to-text streams
            self.interrupt()
            init_time = time.perf_counter_ns()
            self._listen_thread = threading.Thread(
                target=self._listen,
                kwargs={"name": name, "init_time": init_time},
                daemon=True,
            )
            self._listen_thread.start()

    def listener_deactivate(self) -> None:
        """
        Deactivate the speech-to-text listener.
        """
        if self._listening_toggle:
            self._listening_toggle = False
            shutdown_time = time.perf_counter_ns()
            self._speech_recognition_service.interrupt(soft=True, shutdown_time=shutdown_time)

    def prompt(self, message: str, name: Optional[str] = None) -> None:
        """
        Prompt the bot with the specified user message.

        Args:
            message (str): The message content from the user.
            name (Optional[str]): The name of the user sending the message. Defaults to None.
        """
        # Do not send the message if it is empty.
        if message.strip():
            # Interrupt any currently active ChatCompletion, text-to-speech, or speech-to-text streams
            self.interrupt()

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
            self._thread_queue.add_task(threading.Thread(target=self.respond, daemon=True))

    def respond(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIService and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        if self._tone is None:
            self._respond_no_tone()
        elif self._tone == ToneMode.BASIC:
            self._respond_basic_tone()
        elif self._tone == ToneMode.ADVANCED:
            self._respond_advanced_tone()

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
        if not hidden:
            self.update_conversation_area(word=text)

    def system_prompt(self, message: str, name: Optional[str] = None) -> None:
        """
        Prompt the bot with the specified message, issuing a command which is not displayed in the conversation area.

        Args:
            message (str): The message content from the user.
        """
        # Do not send the message if it is empty.
        if message.strip():
            # Interrupt any currently active ChatCompletion, text-to-speech, or speech-to-text streams
            self.interrupt()

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
            self._thread_queue.add_task(threading.Thread(target=self.respond, daemon=True))

    @abstractmethod
    def update_conversation_area(self, word: str) -> None:
        """
        Update the conversation area with the specified word, and add the word to the chat log.
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

    @abstractmethod
    def _init_gui(self) -> None:
        """
        Initialize the graphical user interface for the frontend.
        This method should be implemented by subclasses to create the specific GUI components.
        """

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

    def _respond_advanced_tone(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIService and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        prefixed = False
        content = []
        context = []

        # Initialize the generator for asynchronous yielding of sentence blocks
        for block in self._openai_service.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area(f"{self._assistant_name}: ")
                prefixed = True

            phrases, context = self._prosody_selector.select(sentences=block, context=content, system=self._system)

            if phrases is None:
                raise FormatMismatchError()

            for word in self._speech_synthesis_service.speak_phrases(phrases):
                self.update_conversation_area(word.word)
                content.append(word.word)

            self.update_conversation_area(" ")
            content.append(" ")

        content = "".join(content)
        message = Message(role=ChatCompletionRoles.ASSISTANT, content=content.strip())
        self._messages.append(message)

        self._response_end()

    def _respond_basic_tone(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIService and updating the conversation area with the response text using
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

        # Initialize the generator for asynchronous yielding of sentence blocks
        for block in self._openai_service.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area(f"{self._assistant_name}: ")
                prefixed = True
            sentences = " ".join(block)
            for word in self._speech_synthesis_service.speak(sentences, voice=self._voice, style=style):
                self.update_conversation_area(word.word)
                content.append(word.word)
            self.update_conversation_area(" ")
            content.append(" ")
        content = "".join(content)
        message = Message(role=ChatCompletionRoles.ASSISTANT, content=content.strip())
        self._messages.append(message)
        self._response_end()

    def _respond_no_tone(self) -> None:
        """
        Get a response from the bot and update the conversation area with the response. This method handles generating
        the bot's response using the OpenAIService and updating the conversation area with the response text using
        text-to-speech synthesis.
        """
        prefixed = False
        content = []

        # Initialize the generator for asynchronous yielding of sentence blocks
        for block in self._openai_service.prompt_stream(messages=self._messages):
            if not prefixed:
                self.update_conversation_area(f"{self._assistant_name}: ")
                prefixed = True
            sentences = " ".join(block)
            for word in self._speech_synthesis_service.speak(sentences, voice=self._voice, style=self._style):
                self.update_conversation_area(word.word)
                content.append(word.word)
            self.update_conversation_area(" ")
            content.append(" ")
        content = "".join(content)
        message = Message(role=ChatCompletionRoles.ASSISTANT, content=content.strip())
        self._messages.append(message)
        self._response_end()

    def _response_end(self) -> None:
        """
        End the bot's response and update the conversation area accordingly. This method should be called after the
        bot's response has been fully generated and added to the conversation area.
        """
        self.update_conversation_area("\n\n")

    def _listen(self, name: Optional[str] = None, init_time: Optional[int] = None) -> None:
        """
        Listen for user input using speech-to-text and prompt the bot with the transcribed message.

        Args:
            name (Optional[str]): The name of the user sending the message. Defaults to None.
            init_time (Optional[int]): The time at which the listener was activated.
        """
        # Flag is set to True if a new user input is detected.
        input_detected = False

        # Listen for user input using speech-to-text
        for sentence in self._speech_recognition_service.listen(init_time=init_time):
            # Break the loop if interrupted
            if init_time < self._interrupt:
                break
            # Do not send the message if it is empty.
            elif sentence.strip():
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
        # Respond if the listening loop is not broken.
        else:
            if input_detected:
                self._thread_queue.add_task(threading.Thread(target=self.respond, daemon=True))
