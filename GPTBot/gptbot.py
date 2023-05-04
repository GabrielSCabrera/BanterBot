"""
The GPTBot class is a chatbot implemented using the OpenAI ChatGPT architecture, designed to carry on conversations with
users. The class consists of several methods that allow it to process input messages, generate responses, and store a
history of the conversation. The bot is capable of handling interruptions from the user, parsing user input to extract
relevant information, and generating responses in a specified emotional state.

The key features of the GPTBot class include:

    * Support for interrupting the bot mid-response.
    * The ability to generate responses in a specified emotional state.
    * The capacity to prompt the user for information to improve the conversation.
    * The ability to summarize the conversation history.
    * Streaming responses to allow for asynchronous chat conversations.

Overall, the GPTBot class provides a robust chatbot framework that can be customized to fit a wide range of
applications.
"""

from collections.abc import Iterator
import datetime
import json
import os
import re
import string
import threading
from typing import Any, Literal, Optional, TypedDict, Union

import openai
import geocoder
import requests
import spacy
import spacy.cli
import tiktoken

import termighty
import config


class ParsedResponse(TypedDict):
    """
    A typed dictionary for parsed responses from the AI.
    The ParsedResponse class describes the format for the parsed responses from the OpenAI API.

    Attributes:
        text (str): A string to hold the text of the response.
        emotion (Literal[config.emotions]): A string literal to specify the emotion of the response.
        actions (list[str, ...]): A list of strings to hold any actions specified in the response.
    """

    text: str  # A string to hold the text of the response.
    emotion: Literal[config.emotions]  # A string literal to specify the emotion of the response.
    actions: list[str, ...]  # A list of strings to hold any actions specified in the response.


class MessageDict(TypedDict):
    """
    A typed dictionary to represent a message in the conversation history.

    Attributes:
    - role (Literal["system", "user", "assistant"]): The role of the message sender.
    - content (str): The content of the message.
    - name (Optional[str]): The name of the message sender.
    """

    role: Literal["system", "user", "assistant"]
    content: str
    name: Optional[str] = None


class GPTBot:
    """
    GPTBot is a class for interacting with an AI language model while maintaining a consistent character and
    voice based on the selected personality. The class handles various tasks such as fetching weather data,
    generating responses in a structured format, and handling interruptions.

    Args:
        model (str, optional): The OpenAI model to use. Defaults to None.
        character (str, optional): The character or personality for the AI to adopt. Defaults to None.
        random_character (bool, optional): Whether to select a random character. Defaults to False.
        username (str, optional): The user's name for personalizing interactions. Defaults to None.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        character: Optional[str] = None,
        random_character: bool = False,
        username: Optional[str] = None,
        mode: Literal["ChatCompletion", "Completion"] = "ChatCompletion",
        thread_on_init: bool = True,
    ) -> None:
        """
        Initializes the GPTBot instance with the given model, character, random_character flag, and username.
        Sets up the API key, geocoder, tokenizer, and initializes the character traits and startup message.

        Args:
            model (str, optional): The OpenAI model to use. Defaults to None.
            character (str, optional): The character or personality for the AI to adopt. Defaults to None.
            random_character (bool, optional): Whether to select a random character. Defaults to False.
            username (str, optional): The user's name for personalizing interactions. Defaults to None.
            mode (Literal["ChatCompletion", "Completion"]): Whether to call the ChatCompletion or Completion API.
        """
        # Set OpenAI API key
        openai.api_key = os.environ.get(config.openai_api_key_env_variable)

        # Select the API
        self._mode = mode

        try:
            # Initialize a spaCy model for English
            self._nlp = spacy.load("en_core_web_sm")
        except OSError:
            spacy.cli.download("en_core_web_sm")
            self._nlp = spacy.load("en_core_web_sm")

        # Set up geocoder for IP address lookup
        self._geocoder = geocoder.ip("me")

        # Set weather update frequency and time of last update
        self._weather_update_frequency = datetime.timedelta(minutes=15)
        self._weather_last_updated = None

        # If no model is specified, use the default one specified in config.py
        if model is None:
            model = config.default_chat_gpt_models[self._mode]
        self._model = model

        # Capitalize user name if provided
        self._username = username.capitalize() if username is not None else "USER"

        # Set up tokenizer for model
        self._tokenizer = tiktoken.encoding_for_model(self._model)

        # Set the maximum length for chat responses, (OpenAI's listed limit, and chat history list
        self._max_len = 4096

        # Initialize the interrupt flag
        self._interrupt = False
        self._history = []

        # Messages to print if a TooManyRequests exception occurs before the custom error messages are generated.
        self._request_messages = [
            {"actions": ["NULL()"], "emotion": "sad", "text": f"Rate limiting difficulties, retry attempt {i}."}
            for i in range(config.request_retry_attempt_limit)
        ]
        self._force_quit_message = {
            "actions": ["EXIT()"],
            "emotion": "sad",
            "text": "Exiting program due to rate limiting.",
        }

        # Set up history and lock for multi-threading safety
        self._history_lock = threading.Lock()

        # Set up regular expressions for parsing AI responses
        self._action_response_pattern = re.compile("\$ *ACTIONS *\: *\[(.+),? *\] *\$ *ACTIONS", flags=re.DOTALL)
        self._emotion_response_pattern = re.compile("\$ *EMOTION *\:(.+)\$ *EMOTION", flags=re.DOTALL)
        self._text_response_pattern = re.compile("\$ *TEXT *\:(.+)\$ *TEXT", flags=re.DOTALL)
        self._text_open_response_pattern = re.compile("\$ *TEXT *\:")
        self._text_close_response_pattern = re.compile("\$ *TEXT")
        self._sentence_split_pattern = re.compile("([\.\?\!][ \r\n\t]+)")

        # Initialize the character traits and startup message
        self._init_character(character=character, random_character=random_character)

        # Initialize character traits threads
        initialization_threads = self._init_traits_threads()

        # Initialize rate limit message threads
        initialization_threads += self._init_request_messages_threads()

        # Append the startup message thread
        initialization_threads.append(threading.Thread(target=self._thread_startup_message, daemon=True))

        # Start all initialization threads
        for thread in initialization_threads:
            thread.start()
            if not thread_on_init:
                thread.join()

        # Wait for all initialization threads to finish
        if thread_on_init:
            for thread in initialization_threads:
                thread.join()

        # Initialize system variables and messages
        self._init_system()

        # Add startup message to chat history
        with self._history_lock:
            self._history_append(role="assistant", content=self._startup_content, name=self._name)

    @property
    def character_name(self) -> str:
        """
        Returns the short-form name of the selected character.

        Returns:
            str: The name of the GPTBot's selected character.
        """
        return self._name

    @property
    def username(self) -> str:
        """
        Returns the name of the user.

        Returns:
            str: The name of the GPTBot's user.
        """
        return self._username

    @username.setter
    def username(self, username: str) -> None:
        """
        Modifies the name of the user.

        Args:
            username (str): The updated name of the GPTBot's user.
        """
        self._username = username.capitalize() if username is not None else "USER"

    @property
    def _context(self) -> list[MessageDict]:
        """
        Generates a context message based on the current time, location, and weather. The context message is used in
        conversation to provide information about the environment.

        Returns:
            list[MessageDict]: A list containing one dictionary with 'role' and 'content' keys for the context message.
        """
        # Get current timestamp
        now = datetime.datetime.now()
        timestamp = now.strftime("%I:%M %p on %A %B %d %Y")

        # Get latitude and longitude of the user
        lat, lon = self._geocoder.latlng

        # Check if the weather data needs to be updated
        if self._weather_last_updated is None or self._weather_last_updated + self._weather_update_frequency <= now:
            # Update weather data
            self._weather_last_updated = now

            # Make API call to get weather data
            url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
            headers = {
                "User-Agent": "GPTBot/0.0.1 github.com/GabrielSCabrera/GPTBot",
                "From": "gabriel.sigurd.cabrera@gmail.com",
            }
            try:
                data = requests.get(url, headers=headers).json()
                self._weather = self._weather_data_parse(data)
            except:
                # Set empty string if there's an error getting weather data
                self._weather = ""

        # Construct context message
        context = (
            f"It is currently {timestamp}. Position is: {self._geocoder.city}, {self._geocoder.country}{self._weather}."
        )

        return [{"role": "system", "content": context}]

    def _count_tokens(
        self, messages: Union[list[MessageDict], str], mode: Literal["ChatCompletion", "Completion"]
    ) -> int:
        """
        Counts the number of tokens in a given set of messages.

        Args:
            messages (Union[list[MessageDict], str]): A list of dicts containing message information, or a string.
            mode (Literal["ChatCompletion", "Completion"]): Whether to call the ChatCompletion or Completion API.

        Returns:
            int: The number of tokens in the given message(s).
        """

        if mode == "ChatCompletion":
            # Set a starting token count of 3 to account for the start prompt and AI response prefix
            num_tokens = 3

            # Loop through each message in the input list
            for message in messages:
                # Add 4 tokens for each message to account for message metadata
                num_tokens += 4
                # Loop through each key-value pair in the message dictionary
                for key, value in message.items():
                    # Encode the message value using the tokenizer and add the number of tokens to the total count
                    num_tokens += len(self._tokenizer.encode(value))

        elif mode == "Completion":
            num_tokens = len(self._tokenizer.encode(text))

        return num_tokens

    def _init_character(self, character: str, random_character: bool = False) -> None:
        """
        Initializes the character for the AI by either selecting a random character or using the given character.

        Args:
            character (str): The character or personality for the AI to adopt.
            random_character (bool, optional): Whether to select a random character. Defaults to False.
        """
        # If the random character flag is set, select a random character (overrides "character")
        if random_character:
            character = self._select_random_character()

        # If no character is provided, use the default one specified in config.py
        elif character is None:
            character = config.default_character

        # Set the character
        self._character = character

    def _init_system(self) -> None:
        """
        Initializes the system message for the AI, which contains instructions for structuring responses.
        The message includes guidelines for actions, emotions, and verbal statements.
        """

        # Create a list of actions, and use it to generate a string for use in the initialization text
        actions = list(config.actions[:-2]) + [", or ".join(config.actions[-2:])]
        actions_str = ", ".join(actions)

        # Create a list of emotions, and use it to generate a string for use in the initialization text
        emotions = list(config.emotions[:-2]) + [", or ".join(config.emotions[-2:])]
        emotions_str = ", ".join(emotions)

        self._init_text = config.initialization_prompt.format(self._character) + (
            "Structure your responses in the following order: 1) an action, 2) an emotion, "
            "and 3) a verbal statement.\n"
            f"\tActions: Select from the available options: {actions_str}. DISTANCE is meters, and ANGLE is degrees.\n"
            "\tEmotion: Based on the conversation and your character's personality, pick the most appropriate emotion "
            f"from the provided list: {emotions_str}.\n"
            "\tVerbal Statement: The only thing allowed in this section is first-person speech. Do not describe your "
            "actions, expressions, or narration. Only include the exact words spoken by your character.\n"
            "Format your response exactly as follows:\n"
            "$ACTIONS:[<action_1>,<action_2>,...]$ACTIONS\n"
            "$EMOTION:<emotion>$EMOTION\n"
            "$TEXT:<verbal_statement>$TEXT"
        )

        # Create examples of correctly-formatted responses for use in the system message
        example_user_prompt_1 = "Could you please walk in a square?"
        example_assistant_response_1 = (
            "$ACTIONS:[MOVE_FORWARD(1), TURN(90), MOVE_FORWARD(1), TURN(90), MOVE_FORWARD(1), TURN(90), "
            f"MOVE_FORWARD(1), TURN(90)]$ACTIONS$EMOTION:{self._default_emotion}$EMOTION$TEXT:Sure, I just walked in "
            "a square for you. What's next?$TEXT"
        )

        example_user_prompt_2 = "Could you please lower your voice?"
        example_assistant_response_2 = (
            "$ACTIONS:[NULL()]$ACTIONS$EMOTION:whispering$EMOTION$TEXT:I'm sorry if I was too loud. I will make sure "
            "to lower my voice from now on.$TEXT"
        )

        example_user_prompt_3 = "Thanks, I have to get going!"
        example_assistant_response_3 = "$ACTIONS:[EXIT()]$ACTIONS$EMOTION:whispering$EMOTION$TEXT:Goodbye.$TEXT"

        start_prompt = "Here is an example of correct output formatting:"
        end_prompt = "Example finished. Begin the conversation, and do not deviate from the demonstrated formatting."

        # Initialize the history list with the system message, examples of correctly-formatted responses, and a message
        # indicating the end of the example conversation
        with self._history_lock:
            self._history = [
                {"role": "system", "content": self._init_text},
                {"role": "system", "content": start_prompt},
                {"role": "system", "name": self._username, "content": example_user_prompt_1},
                {"role": "system", "name": self._name, "content": example_assistant_response_1},
                {"role": "system", "name": self._username, "content": example_user_prompt_2},
                {"role": "system", "name": self._name, "content": example_assistant_response_2},
                {"role": "system", "name": self._username, "content": example_user_prompt_3},
                {"role": "system", "name": self._name, "content": example_assistant_response_3},
                {"role": "system", "content": end_prompt},
            ]

    def _init_traits_threads(self) -> list[threading.Thread, ...]:
        """
        Initializes the character traits for the AI, including name, voice, and default emotion. This method
        sends requests to the AI to generate and select these traits based on the chosen character.

        Returns:
            list[threading.Thread, ...]: A list containing threads which each initialize a character trait.
        """

        # Create an initial message about the character
        character_info = (
            "Assist me in identifying facts about yourself. You adhere to all instructions accurately and without "
            "deviation, refraining from commenting on the answers. You provide only desired responses: when asked to "
            "choose an option from a list, strictly select from the given options. Single word responses only, no "
            "embellishment or punctuation."
        )

        # Create a message dictionary containing the system messages
        messages = [
            {"role": "system", "content": config.initialization_prompt.format(self._character)},
            {"role": "system", "content": character_info},
        ]

        # Define a list of prompts, processors, and attributes to be used in the threads
        prompts = [self._prompt_name_selection, self._prompt_voice_selection, self._prompt_emotion_selection]
        processors = [self._select_name, self._select_voice, self._select_emotion]
        attributes = ["_name", "_voice", "_default_emotion"]

        threads = []
        # Loop through each prompt, processor, and attribute and create a thread for each
        for prompt, processor, attribute in zip(prompts, processors, attributes):
            # Create a new thread to call the _thread_traits method with the appropriate arguments
            threads.append(
                threading.Thread(target=self._thread_traits, args=(messages, prompt, processor, attribute), daemon=True)
            )

        # Return the list of threads
        return threads

    def _join_messages(self, messages=list[MessageDict], start_prompt: bool = True) -> str:
        """
        Joins all a list of messages into a single string that can be read by the OpenAI Completion API (as opposed to
        the OpenAI ChatCompletion API, which can directly parse the list of messages.)

        Args:
            messages (list[MessageDict]): A list containing a set of messages compatible with the ChatCompletion API.
            start_prompt (bool): If True, appends the name of the assistant to the end of the prompt.

        Returns:
            str:    A string containing the joined history data.
        """
        prompts = []
        assistant_name = None
        for message in messages:
            if message["role"] == "system":
                name = "SYSTEM MESSAGE"
            elif "name" in message.keys():
                name = message["name"].upper()
                if message["role"] == "assistant":
                    assistant_name = name
            else:
                name = message["role"].upper()
            prompts.append(f":\t{message['content']}")

        if assistant_name is not None and start_prompt:
            prompts.append(f"{assistant_name}:\t")

        return "\n".join(prompts)

    def _get_error_response(self) -> str:
        """
        Generates an error response for the AI to use when it has not understood the user's input.

        Returns:
            str: The error response as a string.
        """
        # Set up the prompt for the AI to generate an error response
        prompt = "Offer a brief apology suggesting that you were not paying close attention to what the user just said."

        # Create a message for the AI to respond to
        messages = [
            {"role": "system", "content": config.initialization_prompt.format(self._character)},
            {"role": "system", "content": prompt},
        ]

        # Send the message to the AI and receive the error response
        response = self._request(messages=messages, stream=False, mode=self._mode)

        return response

    def _history_append(
        self, role: Literal["system", "user", "assistant"], content: str, name: Optional[str] = None
    ) -> None:
        """
        Appends a message to the conversation history.

        Args:
            role (str): The role of the message sender ('user', 'assistant', or 'system').
            content (str): The content of the message.
            name (str, optional): The name of the message sender. Defaults to None.
        """
        # Create a dictionary to represent the new message to append
        history_entry = {"role": role, "content": content}

        # If a name was provided, add it to the message dictionary
        if name is not None:
            history_entry["name"] = name

        # Append the new message to the history list
        self._history.append(history_entry)

    def _history_append_interruption(self) -> None:
        """
        Appends an interruption message to the conversation history, indicating that the user has interrupted
        the AI's response.
        """
        # Lock the history for multi-threading safety
        with self._history_lock:
            # Append the interruption message to the history list
            response = self._history_append(role="system", content=f"The user interrupted {self._name} mid-speech.")

    def _init_request_messages_threads(self) -> list[threading.Thread, ...]:
        """
        Generates a set of error responses for the AI to use when it has been rate limited.  Is calculated in advance
        in case rate limiting occurs.

        Returns:
            list[threading.Thread, ...]: The list of threads that asynchronously prepare advance error messages.
        """
        # Prepare the list of threads, starting with the force quit message
        threads = [threading.Thread(target=self._thread_force_quit_message, daemon=True)]

        # Set up the prompt for the AI to generate an error response
        prompt = (
            "You are temporarily indisposed, and will return shortly. Write a quick one sentence message indicating "
            "that this is the case."
        )

        # Create a message for the AI to respond to
        messages = [
            {"role": "system", "content": config.initialization_prompt.format(self._character)},
            {"role": "system", "content": prompt},
        ]

        # Create threads that generate the rate limit messages to store in the _request_messages attribute
        for i in range(config.request_retry_attempt_limit):
            threads.append(threading.Thread(target=self._thread_request_messages, args=(messages, i), daemon=True))

        return threads

    def _prompt_emotion_selection(self) -> str:
        """
        Generates a prompt for the AI to select its default emotional state based on the chosen character.

        Returns:
            str: The prompt for emotion selection as a string.
        """
        # Combine the list of emotions from the config file into a string
        emotions = list(config.emotions[:-2]) + [", or ".join(config.emotions[-2:])]
        emotions_str = ", ".join(emotions)

        # Create a prompt for the AI to select its default emotional state
        prompt = (
            f"Choose a default emotional state for your character from the available options: {emotions_str}. Select "
            "the most appropriate emotion, even if it may not be a perfect fit. Provide your answer as a single word. "
            "Ensure that the chosen word is from the given list and not an emotion outside of the provided options."
        )
        return prompt

    def _prompt_name_selection(self) -> str:
        """
        Generates a prompt for the AI to select a suitable name based on the chosen character.

        Returns:
            str: The prompt for name selection as a string.
        """
        # Define the prompt message for the AI to select a name for the character
        prompt = (
            "Please provide the first name of the character. Write only one name, with no extra text or punctuation."
        )
        return prompt

    def _prompt_voice_selection(self) -> str:
        """
        Generates a prompt for the AI to select a suitable voice based on the chosen character.

        Returns:
            str: The prompt for voice selection as a string.
        """
        # Join the traits of each voice together to create a string to display in the prompt
        voices_str = "\n".join(f"{name}: " + ", ".join(traits) for name, traits in config.neural_voices.items())

        # Get the names of the available voices and join them together to create a string to display in the prompt
        names = list(config.neural_voices.keys())
        names_str = ", ".join(names[:-2] + [", or ".join(names[-2:])])

        # Create the prompt with instructions for selecting a voice
        prompt = (
            f"Choose the best-fitting voice profile from the provided options:\n{voices_str}.\n"
            "If you are male, select a male voice. If female, select a female voice. Consider your level of "
            "professionalism, emotivity, and voice pitch to select an option once a gender is chosen. Pick one profile "
            "from the list, even if it's not a good match. Provide a one-word answer, which must be one of the names "
            f"in the list: {names_str}."
        )

        return prompt

    def _response_parse(self, response: str) -> tuple[ParsedResponse, bool]:
        """
        Parses the AI's response into the action, emotion, and verbal statement components.

        Args:
            response (str): The AI's response.
            mode (Literal["ChatCompletion", "Completion"]): Whether to call the ChatCompletion or Completion API.

        Returns:
            tuple: A ParsedResponse object, and a boolean indicating if the parsing was successful.
        """

        # Find any actions in the response and split them by comma.
        # If no actions found, append "NULL()".
        action_search = re.findall(self._action_response_pattern, response)
        if len(action_search) != 1:
            actions = ["NULL()"]
        else:
            actions = [action.strip() for action in action_search[0].split(",")]

        # Find any emotion in the response. If none found, use the default emotion.
        emotion_search = re.findall(self._emotion_response_pattern, response)
        if len(emotion_search) != 1:
            emotion = self._default_emotion
        else:
            emotion = emotion_search[0].lower()

        # Find any verbal statements in the response. If none found, return an error message.
        text_search = re.findall(self._text_response_pattern, response)
        if len(text_search) != 1:
            success = False
            text = self._get_error_response()
        else:
            success = True
            text = text_search[0]

        # Return a ParsedResponse object, and a boolean indicating whether the parsing was successful.
        return {"actions": actions, "emotion": emotion, "text": text}, success

    def _response_parse_stream(
        self,
        response: Iterator,
        mode: Literal["ChatCompletion", "Completion"],
    ) -> Iterator[ParsedResponse]:
        """
        Parses a streaming response from the OpenAI API and yields individual messages as they are received.

        Args:
            response (Iterator): The streaming response object.
            mode (Literal["ChatCompletion", "Completion"]): Whether to call the ChatCompletion or Completion API.

        Yields:
            ParsedResponse: A dictionary containing the parsed message's "actions", "emotion", and "text" attributes.
        """
        # Initialize default values
        actions = ["NULL()"]
        emotion = self._default_emotion

        # Track whether action and emotion have been extracted from the response
        actions_complete = False
        emotion_complete = False

        # Track whether text has been detected in the response
        text_detected = False

        # Initialize response text and interruption flag
        response_text = ""
        self._interrupt = False

        # Iterate over the response chunks
        for chunk in response:

            # For "ChatCompletion" mode, the response is more complex.
            if mode == "ChatCompletion":
                # Extract the delta, which contains the new text from the AI
                delta = chunk["choices"][0]["delta"]

                # If the interruption flag has been set or the delta is empty, break out of the loop
                if self._interrupt or delta == {}:
                    break

                # If there is new content in the delta, add it to the response text and parse it
                elif "content" in delta.keys():
                    response_text += delta["content"]

            # For "Completion" mode, the response is easily accessible via the "text" key.
            elif mode == "Completion":
                response_text += chunk["choices"][0]["text"]

            else:
                raise ValueError('Invalid "mode" selection for method "_response_parse_stream" in GPTBot.')

            # Extract actions if they have not already been extracted
            if not actions_complete:
                for match in re.finditer(self._action_response_pattern, response_text):
                    actions_str = response_text[match.start() : match.end()]
                    actions = re.findall(self._action_response_pattern, actions_str)[0].upper().split(",")
                    response_text = response_text[: match.start()] + response_text[match.end() :]
                    actions_complete = True
                    break

            # Extract emotion if it has not already been extracted
            if not emotion_complete:
                for match in re.finditer(self._emotion_response_pattern, response_text):
                    emotion_str = response_text[match.start() : match.end()]
                    emotion = re.findall(self._emotion_response_pattern, emotion_str)[0]
                    emotion = self._select_emotion(response=emotion)
                    response_text = response_text[: match.start()] + response_text[match.end() :]
                    emotion_complete = True
                    break

            # Extract text if it has not already been detected
            if not text_detected:
                match = re.search(self._text_open_response_pattern, response_text)
                if match:
                    response_text = response_text[match.end() :]
                    text_detected = True

            # If text has been detected, split it into sentences and yield each sentence with actions and emotion
            elif re.search(self._sentence_split_pattern, response_text):
                split_response_text = [str(sentence) for sentence in self._nlp(response_text).sents]
                sentence = "".join(split_response_text[:-1])
                sentence = re.sub(self._text_close_response_pattern, "", sentence)
                response_text = response_text[len(sentence) :]

                yield {"actions": actions, "emotion": emotion, "text": sentence}

        # If there is remaining text in the response, yield it with actions and emotion
        if text_detected:
            sentence = re.sub(self._text_close_response_pattern, "", response_text)
            yield {"actions": actions, "emotion": emotion, "text": sentence}

    def _response_unparse(self, actions: list[str, ...], emotion: str, text: str) -> str:
        """
        Combines the parsed response components into a single formatted response string.

        Args:
            actions (list): A list of strings representing the actions to be taken by the AI.
            emotion (str): A string representing the emotion to be conveyed by the AI.
            text (str): A string representing the verbal statement to be made by the AI.

        Returns:
            str: The formatted response string.
        """

        # Combine the actions into a comma-separated string and format the actions section of the response
        actions_str = ",".join(actions)
        actions_formatted = f"$ACTIONS:[{actions_str}]$ACTIONS"

        # Format the emotion section of the response
        emotion_formatted = f"$EMOTION:{emotion}$EMOTION"

        # Format the text section of the response
        text_formatted = f"$TEXT:{text}$TEXT"

        # Combine the formatted sections of the response into a single string
        response_str = f"{actions_formatted}{emotion_formatted}{text_formatted}"

        return response_str

    def _request(
        self, messages: list[MessageDict], stream: bool, mode: Literal["ChatCompletion", "Completion"], **kwargs
    ) -> Union[Iterator, str]:
        """
        Sends a request to the OpenAI API to generate a response based on the given messages and other parameters. Can
        return a stream, or can wait until the entire response is complete and return a string.

        Args:
            messages (list[dict[str, str]]): A list of messages as dictionaries containing message information.
            stream (bool): Whether the request should return an iterable stream, or the entire response text at once.
            mode (Literal["ChatCompletion", "Completion"]): Whether to call the ChatCompletion or Completion API.
            **kwargs: Additional parameters to be passed to the OpenAI API request - some are not modifiable.

        Returns:
            Union[Iterator, str]: The response generated by the OpenAI API as an iterator, or as a string.
        """
        # Add relevant attributes to the kwargs parameter dictionary
        kwargs["model"] = self._model
        kwargs["n"] = 1
        kwargs["stream"] = stream

        if mode == "Completion":
            kwargs["prompt"] = self._join_messages(messages)
            kwargs["max_tokens"] = self._max_len - self._count_tokens(messages=kwargs["prompt"], mode=mode)
            if "messages" in kwargs.keys():
                del kwargs["messages"]

        elif mode == "ChatCompletion":
            kwargs["messages"] = messages
            kwargs["max_tokens"] = self._max_len - self._count_tokens(messages=messages, mode=mode)
            if "prompt" in kwargs.keys():
                del kwargs["prompt"]
        else:
            raise ValueError('Invalid "mode" selection for method "_request" in GPTBot.')

        # Keep track of whether or not the request was successful
        success = False
        # Retry the request if it fails due to rate limiting
        for i in range(config.request_retry_attempt_limit):
            try:
                # Send request to OpenAI API and retrieve response
                if mode == "ChatCompletion":
                    response = openai.ChatCompletion.create(**kwargs)
                elif mode == "Completion":
                    response = openai.Completion.create(**kwargs)
                # Set the success flag and exit the loop
                success = True
                break
            except (openai.error.RateLimitError, openai.error.APIError):
                # If the request fails due to rate limiting, append a rate limit message to the chat history
                self._history_append(self._request_messages[i])
                # Wait for a short period before retrying the request
                time.sleep(5)

        if not success:
            # If the request fails after all retries, append a force quit message to the chat history
            with self._history_lock:
                self._history_append(self._force_quit_message)

        if stream:
            # Return the response as an iterator object
            return response
        elif not stream:
            # Extract the generated response from the response object and strip whitespace
            if mode == "ChatCompletion":
                return response.choices[0].message.content.strip()
            elif mode == "Completion":
                return response.choices[0].text.strip()

    def _select_emotion(self, response: str) -> str:
        """
        Selects the emotion based on the AI's response.

        Args:
            response (str): The response provided by the AI.

        Returns:
            str: The selected emotion as a string.
        """
        # Remove punctuation and make the response lowercase
        emotion = self._strip_punctuation(response).lower()
        # Check if the emotion is valid and return it if it is
        if emotion in config.emotions:
            return emotion
        # If the emotion is not valid, return the default emotion
        else:
            return config.default_emotion

    def _select_name(self, response: str) -> str:
        """
        Sets the AI's name based on the provided response from the user.

        Args:
            response (str): The AI's response to the name prompt.

        Returns:
            str: The AI's selected name.
        """
        return self._strip_punctuation(response).capitalize()

    def _select_random_character(self) -> str:
        """
        Selects a random character for the chatbot personality by prompting the user for a character name and brief
        description of their identity and suggested behavior for the chatbot persona.

        Returns:
            str: The selected character with description and chatbot persona.
        """

        # Construct prompt message to request character and behavior information
        prompt = (
            "You are helping a user choose a character for a chatbot personality. The character can be a renowned "
            "fictional figure from a book, film, television series, or video game, or a real person, either from "
            "history or currently alive. Provide the character's name along with a brief description of their identity "
            "and the suggested behavior for their chatbot persona. Please select only one character and ensure that "
            "the description and chatbot persona are clear and coherent."
        )

        # Construct messages to send to the AI requesting the character and behavior information
        messages = [
            {"role": "system", "content": prompt},
            {"role": "system", "content": "Expects format similar to the following: " + config.default_character},
        ]

        # Send the messages to the AI to get the response
        response = self._request(messages=messages, temperature=1.2, top_p=0.9, stream=False, mode=self._mode)

        # Return the selected character with description and chatbot persona
        return response

    def _select_voice(self, response: str) -> str:
        """
        Selects a neural voice for the AI to use based on the user's response.

        Args:
            response (str): The user's response to the voice selection prompt.

        Returns:
            str: The name of the selected voice profile.
        """
        # Extract the name from the user's response and capitalize it
        names = [self._strip_punctuation(name).capitalize() for name in response.split(" ")]

        # If the name is not a valid option in the config file, set the AI's voice to the default option.
        voice = config.neural_voice_formatter.format(config.default_voice)
        for name in names:
            # Check if the name is a valid option in the config file
            if name in config.neural_voices.keys():
                # If it is, set the AI's voice to the selected option
                voice = config.neural_voice_formatter.format(name)
                break

        return voice

    def _strip_punctuation(self, s: str) -> str:
        """
        Removes all punctuation from the given string and returns the result.

        Args:
            s (str): The string to remove punctuation from.

        Returns:
            str: The resulting string with no punctuation and stripped of leading/trailing whitespace.
        """
        # Create a translation table that maps all punctuation characters to None using dict.fromkeys()
        table = str.maketrans(dict.fromkeys(string.punctuation))
        # Apply the translation table to the input string using str.translate()
        # This removes all punctuation characters from the string
        # Finally, strip any remaining leading/trailing whitespace from the string and return it
        return s.translate(table).strip()

    def _summarize_conversation(self) -> str:
        """
        This function summarizes the conversation that has taken place, focusing on the key points discussed and any specific user
        information that may be useful for future discussions. The summary is written in third person and should be as succinct as possible.

        Returns:
            str: The summary of the conversation as a string.
        """
        # Create a prompt for the AI to summarize the conversation
        prompt = (
            "Break character and complete the following task as written: conclude your simulated conversation by "
            "summarizing the conversation, reflecting on key moments and recalling noteworthy details, as a real "
            "person would, in the most succinct manner possible. Be objective, and write everything in third person. "
            "Focus on memorable topics and significant events rather than mundane exchanges like casual greetings "
            "or weather discussions. Ensure that you prioritize essential elements and distinctive moments from the "
            "conversation for future recollection, thus simulating a genuine human interaction and memory retention."
        )

        # Combine the history of the conversation with the prompt for the AI to generate a summary
        messages = self._history + [{"role": "system", "content": prompt}]

        # Request the AI to generate the summary using the given messages
        # A temperature of 0.0 ensures that the AI's response is always the same, making it more objective
        # A top_p value of 0.5 means that the AI will only use the top 50% of tokens with the highest probability
        response = self._request(messages=messages, temperature=0.0, top_p=0.5, stream=False, mode=self._mode)

        return response

    def _thread_force_quit_message(self) -> None:
        """
        Initializes the force quit message to be displayed when the OpenAI API rate limit is exceeded and the
        GPTBot instance is shutting down. Uses the character's persona to generate the message.
        """
        # Set up the prompt for the AI to generate an error response
        prompt = (
            f"You are not feeling well and must shut down, compose a brief message to inform the user of your "
            "current situation."
        )

        # Send the prompt to the AI and retrieve the error response
        messages = [
            {"role": "system", "content": config.initialization_prompt.format(self._character)},
            {"role": "system", "content": prompt},
        ]

        # Convert the response to the format required by the ChatCompletion API
        response = {
            "actions": ["EXIT()"],
            "emotion": "sad",
            "text": self._request(messages=messages, stream=False, mode=self._mode),
        }

        # Set the response as the force quit message
        self._force_quit_message = response

    def _thread_request_messages(self, messages: str, index: int) -> None:
        """
        A thread that sends a message to the AI and receives the error response for rate limiting.

        Args:
            message (str): The message to send to the AI.
            index (int): The index of the rate limit message in the list of messages.
        """
        # Send the message to the AI and receive the error response
        response = {
            "actions": ["NULL()"],
            "emotion": "sad",
            "text": self._request(messages=messages, stream=False, mode=self._mode),
        }

        # Convert the response to the format required by the ChatCompletion API
        response_unparsed = self._response_unparse(**response)

        # Replace the current error response with the updated version
        self._request_messages[index] = response_unparsed

    def _thread_startup_message(self) -> None:
        """
        Initializes the startup message for the AI, which is a greeting based on the character's traits.
        """
        # Define greeting prompt message
        prompt = (
            "Craft a character-specific greeting, considering your personality, temperament, time of day, and weather "
            "conditions if applicable. Limit your response to two sentences of pure dialogue, without any descriptive "
            "narration or actions (e.g., no 'I glance up at the user as he enters' or *Grinning*). Focus solely on the "
            "spoken words."
        )

        # Define the message history
        messages = [
            {"role": "system", "content": config.initialization_prompt.format(self._character)},
            {"role": "system", "content": prompt},
        ]

        # Request a response from the AI for the greeting message
        response = self._request(self._context + messages, stream=False, mode=self._mode)

        # Format the response into a message dictionary
        self._startup_content = (
            f"$ACTIONS:[NULL()]$ACTIONS" f"$EMOTION:{self._default_emotion}$EMOTION" f"$TEXT:{response}$TEXT"
        )

        # Parse the response to get the startup message
        self._startup_message = self._response_parse(response=self._startup_content)[0]

    def _thread_traits(self, messages: MessageDict, prompt: callable, processor: callable, attribute: str) -> None:
        """
        A method for initializing character traits using a separate thread. It prompts the AI to generate a prompt
        for the user to respond to, and then uses the AI response to select a value for the attribute being initialized.

        Args:
            messages (dict): A dictionary that includes the role, content, and name of a message
            prompt (callable): A callable function that generates a prompt for the AI
            processor (callable): A callable function that selects a value for the attribute from the AI response
            attribute (str): The name of the attribute being initialized
        """
        # Ask the AI to generate a prompt
        messages = [*messages, {"role": "user", "content": prompt()}]
        response = self._request(messages=messages, temperature=0.0, stream=False, mode=self._mode)

        # Use the AI response to select a value for the attribute
        setattr(self, attribute, processor(response))

    def _weather_data_parse(self, data: dict) -> str:
        """
        Parses the JSON weather data returned by the OpenWeatherMap API.

        Args:
            data (dict): The JSON weather data.

        Returns:
            str: A string containing a summary of the weather data.
        """
        # Extract the necessary data from the JSON response
        properties = data["properties"]
        units = properties["meta"]["units"]
        data_now = properties["timeseries"][0]["data"]
        instant = data_now["instant"]["details"]
        next_hour = data_now["next_1_hours"]
        next_six_hours = data_now["next_6_hours"]
        next_twelve_hours = data_now["next_12_hours"]

        # Create a list of strings describing the current weather conditions
        current_conditions = [f"{key}: {instant[key]} {units[key]}" for key in instant.keys()]

        # Create a string describing the forecast for the next hour, six hours, and twelve hours
        forecast = (
            f"Next hour's weather: {next_hour['summary']['symbol_code']}, "
            f"next six hours' weather: {next_six_hours['summary']['symbol_code']}, "
            f"next twelve hours' weather: {next_twelve_hours['summary']['symbol_code']}."
        )

        # Combine the current weather conditions and the forecast into a summary string
        summary = ". Current weather conditions: " + "; ".join(current_conditions) + ". " + forecast

        # Replace underscores in the summary string with spaces
        summary = summary.replace("_", " ")

        return summary

    def interrupt(self) -> None:
        """
        Interrupts the current chat stream.
        """
        # Set the '_interrupt' attribute to True
        self._interrupt = True

    def prompt(self, message: str, mode: Optional[Literal["ChatCompletion", "Completion"]] = None) -> ParsedResponse:
        """
        Takes in a message from the user, appends it to the conversation history, and sends it to the AI for a response.
        The response is then parsed and returned as a ParsedResponse object.

        Args:
            message (str): The message from the user.
            mode (Optional[Literal["ChatCompletion", "Completion"]]): Completion API selection.

        Returns:
            ParsedResponse: A ParsedResponse object containing the parsed response from the AI.
        """
        # Select the default mode if none is provided
        if mode is None:
            mode = self._mode

        # Append user message to conversation history
        with self._history_lock:
            self._history_append(role="user", content=message, name=self._username)

        # Send messages to AI and get response
        response = self._request(messages=self._context + self._history, stream=False, mode=mode)

        # Parse response and retry if unsuccessful
        response_parsed, success = self._response_parse(response=response)
        retry_attempts = 0
        while not success and retry_attempts < config.retry_attempt_limit:
            response_parsed, success = self._response_parse(response=response)
            retry_attempts += 1

        # Unparse parsed response and append to conversation history
        response_unparsed = self._response_unparse(**response_parsed)
        with self._history_lock:
            self._history_append(role="assistant", content=response_unparsed, name=self._name)

        return response_parsed

    def prompt_stream(
        self, message: str, mode: Optional[Literal["ChatCompletion", "Completion"]] = None
    ) -> Iterator[ParsedResponse]:
        """
        Sends the user message to the AI and generates a stream of response blocks parsed from the AI's stream.

        Args:
            message (str): The user's message.
            mode (Optional[Literal["ChatCompletion", "Completion"]]): Completion API selection.

        Yields:
            ParsedResponse: A dictionary containing the parsed message's "actions", "emotion", and "text" attributes.
        """
        # Select the default mode if none is provided
        if mode is None:
            mode = self._mode

        # Append the user's message to the conversation history with a user role
        with self._history_lock:
            self._history_append(role="user", content=message, name=self._username)

        # Make a stream request to the AI, passing the history and context messages
        response = self._request(messages=self._context + self._history, stream=True, mode=mode)

        # Parse the response stream and yield each response block
        for block in self._response_parse_stream(response=response, mode=mode):
            yield block
