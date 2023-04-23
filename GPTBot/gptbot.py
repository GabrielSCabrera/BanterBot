import datetime
import json
import os
import re
import string
from typing import Literal, Optional, TypedDict

import openai
import geocoder
import requests
import tiktoken

import termighty
import config


class parsed_response(TypedDict):
    """A typed dictionary for parsed responses from the AI."""

    text: str
    emotion: Literal[config.emotions]
    actions: list[str, ...]


class messages_dict(TypedDict):
    """A typed dictionary for message dictionaries."""

    role: Literal["system", "user", "assistant"]
    content: str


class GPTBot:
    """
    A class that represents a GPT-powered chatbot with a specific character.

    Attributes:
        model (str): The name of the GPT model to use.
        character (str): A description of the character the chatbot should emulate.
    """

    def __init__(
        self, model: Optional[str] = None, character: Optional[str] = None, random_character: bool = False
    ) -> None:
        """
        Initialize the GPTBot instance with the given model and character.

        Args:
            model (Optional[str]): The name of the GPT model to use. Defaults to None.
            character (Optional[str]): A description of the character the chatbot should emulate. Defaults to None.
            random_character (bool): Indicates that the Chatbot should select a random character. Overrides "character".
        """
        # Set up OpenAI API access and model
        openai.api_key = os.environ.get(config.openai_api_key_env_variable)

        # Set up geolocation based on IP
        self._geocoder = geocoder.ip("me")
        self._weather_update_frequency = datetime.timedelta(minutes=15)
        self._weather_last_updated = None

        if model is None:
            model = config.default_chat_gpt_model

        self._model = model
        self._tokenizer = tiktoken.encoding_for_model(self._model)
        self._max_len = 4096
        self._history = []

        # Compile regex patterns for parsing responses
        text_response_pattern = "\$TEXT *\:(.+)\$TEXT"
        emotion_response_pattern = "\$EMOTION *\:(.+)\$EMOTION"
        action_response_pattern = "\$ACTIONS *\: *\[(.+),? *\] *\$ACTIONS"
        self._text_response_pattern = re.compile(text_response_pattern, flags=re.DOTALL)
        self._emotion_response_pattern = re.compile(emotion_response_pattern, flags=re.DOTALL)
        self._action_response_pattern = re.compile(action_response_pattern, flags=re.DOTALL)

        # Initialize character, voice, name, system, and startup message.
        self._init_character(character=character, random_character=random_character)
        self._init_system()
        self._init_character_traits()
        self._init_startup_message()

    @property
    def name(self) -> str:
        """Get the chatbot's name."""
        return self._name

    @property
    def _context(self) -> str:
        """
        Returns the current context, which includes the current time and weather information.

        Returns:
            str: A string containing the current time, geolocation, and weather information.
        """
        # Get the current time and format it to display in a user-friendly way.
        now = datetime.datetime.now()
        timestamp = now.strftime("%I:%M %p on %A %B %d %Y")

        # Get the latitude and longitude of the user's location.
        lat, lon = self._geocoder.latlng

        # Check if the weather information needs to be updated.
        if self._weather_last_updated is None or self._weather_last_updated + self._weather_update_frequency <= now:
            self._weather_last_updated = now

            # Retrieve weather information from the API and parse the data.
            url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
            headers = {
                "User-Agent": "GPTBot/0.0.1 github.com/GabrielSCabrera/GPTBot",
                "From": "gabriel.sigurd.cabrera@gmail.com",
            }
            try:
                data = requests.get(url, headers=headers).json()
                self._weather = self._weather_data_parse(data)
            except:
                self._weather = self._weather_data_parse(data)

        # Construct the context string using the current time, geolocation, and weather information.
        context = (
            f"It is currently {timestamp}. Position is: {self._geocoder.city}, {self._geocoder.country}{self._weather}."
        )

        # Return the context string as a list containing a dictionary with role and content keys.
        # The returned value is in this format so that it can be consumed by the ChatHandler object.
        return [{"role": "system", "content": context}]

    def _count_tokens(self, messages: list[messages_dict]) -> int:
        """
        Count the number of tokens in the given list of message dictionaries.

        Args:
            messages (list[messages_dict]): A list of message dictionaries.

        Returns:
            int: The number of tokens in the messages.
        """
        # Every reply is primed with <im_start>assistant
        num_tokens = 3
        for message in messages:
            # Every message follows <im_start>{role/name}\n{content}<im_end>\n
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(self._tokenizer.encode(value))
        return num_tokens

    def _init_character(self, character: str, random_character: bool = False) -> None:
        """
        Initialize the character for the chatbot.

        Args:
            character (str): A description of the character the chatbot should emulate.
            random_character (bool): Indicates that the Chatbot should select a random character. Overrides "character".
        """
        # Have ChatGPT select a random character for the user.
        if random_character:
            character = self._select_random_character()
        # Set up character default if not provided
        elif character is None:
            character = config.default_character
        self._character = character

    def _init_character_traits(self) -> None:
        """Initialize character traits such as name, voice, and default emotion."""

        character_info = (
            f"You are assisting me in identifying facts about the character/person: {self._character}. You adhere "
            "to all instructions accurately and without deviation, refraining from commenting on the answers. You "
            "provide only desired responses: when asked to choose an option from a list, strictly select from the "
            "given options. Single word responses only, no embellishment or punctuation."
        )
        messages = [{"role": "system", "content": character_info}]

        name_prompt = self._prompt_name_selection()
        messages.append({"role": "user", "content": name_prompt})
        response = self._request(messages=messages, temperature=0.0)
        messages.append({"role": "assistant", "content": response})
        self._select_name(response)

        voice_prompt = self._prompt_voice_selection()
        messages.append({"role": "user", "content": voice_prompt})
        response = self._request(messages=messages, temperature=0.0)
        messages.append({"role": "assistant", "content": response})
        self._select_voice(response)

        default_emotion_prompt = self._prompt_emotion_selection()
        messages.append({"role": "user", "content": default_emotion_prompt})
        response = self._request(messages=messages, temperature=0.0)
        messages.append({"role": "assistant", "content": response})
        self._select_emotion(response)

    def _init_startup_message(self) -> None:
        """
        Initialize the chatbot's startup message as a parsed response, including a greeting, default emotion, and null
        action.

        The method requests a greeting message from the AI model, then appends it to the chatbot's history.
        """
        character_info = f"You are an AI assistant playing the character of {self._character}."
        prompt = (
            "You have just been summoned (or awakened, depending on the hour).  Prepare a greeting that reflects your "
            "character. No longer than two sentences."
        )
        messages = [
            {"role": "system", "content": character_info},
            {"role": "user", "content": prompt},
        ]
        response = self._request(self._context + messages)

        content = f"$TEXT:{response}$TEXT" f"$EMOTION:{self._default_emotion}$EMOTION" "$ACTIONS:[NULL()]$ACTIONS"
        self._history_append(role="assistant", content=content)
        self._startup_message, success = self._response_parse(content)

    def _init_system(self) -> None:
        """Initialize the system message and conversation history."""

        emotions = list(config.emotions[:-2]) + [", or ".join(config.emotions[-2:])]
        emotions_str = ", ".join(emotions)

        self._init_text = (
            f"You are {self._character}. Respond to the user's latest text prompt with three distinct responses: a "
            "verbal response, an emotional response, and an action response. Remain in character at all times. The "
            "verbal response should consist of spoken words only, without any descriptions of actions or voice tones."
            f"For the emotional response, use one of the options provided: {emotions_str}."
            "For the action response, use the exact function forms provided: MOVE_FORWARD(DISTANCE), "
            "MOVE_BACKWARD(DISTANCE), TURN(DEGREES), SHUTDOWN(), or NULL()."
            "Format your responses as follows:"
            "$TEXT:<verbal_response>$TEXT"
            "$EMOTION:<selected_emotion>$EMOTION"
            "$ACTIONS:[<selected_action_1>,<selected_action_2>,...]$ACTIONS"
        )

        self._history = [{"role": "user", "content": self._init_text}]

    def _get_error_response(self) -> str:
        """
        Generate an error response indicating that the chatbot might not have paid close attention or didn't catch
        what the user said.

        Returns:
            str: A short response that shows the chatbot might not have understood the user.
        """
        prompt = (
            f"You are portraying the character of {self._character}. Offer a brief apology suggesting that you were "
            "not paying close attention to what the user just said."
        )
        messages = [{"role": "system", "content": prompt}]
        response = self._request(messages=messages)
        return response

    def _history_append(self, role: Literal["system", "user", "assistant"], content: str) -> None:
        """
        Append a message with a specified role and content to the chatbot's conversation history.

        Args:
            role (Literal["system", "user", "assistant"]): The role of the message sender.
            content (str): The content of the message.
        """
        self._history.append({"role": role, "content": content})

    def _history_append_interruption(self) -> None:
        """
        Append a system message to the chat history indicating that the chatbot was interrupted mid-speech.
        """
        response = self._history_append(role="system", content=f"The user interrupted {self._name} mid-speech.")

    def _prompt_emotion_selection(self) -> None:
        """Create a prompt for initializing the chatbot's default emotion."""
        emotion_str = ", ".join(config.emotions)
        prompt = (
            f"Select a default emotional state for your character from the options: {emotion_str}. Choose the most "
            f"suitable emotion for {self._name}, even if it's not an ideal match. Provide your answer as a single word."
        )
        return prompt

    def _prompt_name_selection(self) -> None:
        """Create a prompt for initializing the chatbot's name."""
        prompt = (
            "Please provide the first name of the character. Write only one name, with no extra text or punctuation."
        )
        return prompt

    def _prompt_voice_selection(self) -> str:
        """Create a prompt for initializing the chatbot's voice."""
        voices_str = "\n".join(f"{name}: " + ", ".join(traits) for name, traits in config.neural_voices.items())
        names = list(config.neural_voices.keys())
        names_str = ", ".join(names[:-2] + [", or ".join(names[-2:])])
        prompt = (
            f"Choose a voice profile for {self._name} from the provided options:\n{voices_str}.\n"
            "Select a male voice for male characters and a female voice for female characters. Take into account the "
            "character's professionalism, emotivity, and pitch. Pick one profile from the list, even if it's not a "
            f"good match. Provide a one-word answer, which must be one of the names in the list: {names_str}."
        )
        return prompt

    def _response_parse(self, response: str) -> tuple[parsed_response, bool]:
        """
        Parse a response string into a dictionary containing text, emotion, and actions.

        Args:
            response (str): The response string to parse.

        Returns:
            parsed_response: A dictionary containing the parsed text, emotion, and actions.
            success (bool): A boolean indicating whether or not the parser extracted text correctly.
        """

        text_search = re.findall(self._text_response_pattern, response)
        emotion_search = re.findall(self._emotion_response_pattern, response)
        action_search = re.findall(self._action_response_pattern, response)

        if len(text_search) != 1:
            success = False
            text = self._get_error_response()
        else:
            success = True
            text = text_search[0]

        if len(emotion_search) != 1:
            emotion = self._default_emotion
        else:
            emotion = emotion_search[0].lower()

        if len(action_search) != 1:
            actions = ["NULL()"]
        else:
            actions = [action.strip() for action in action_search[0].split(",")]

        return {"text": text, "emotion": emotion, "actions": actions}, success

    def _response_unparse(self, text: str, emotion: str, actions: list[str, ...]) -> str:
        """
        Convert a response into a string format that combines text, emotion, and actions.

        Args:
            text (str): The text content of the response.
            emotion (str): The emotion related to the response.
            actions (list[str, ...]): A list of actions in the response.

        Returns:
            str: The combined string representation of the response.
        """
        response_str = f"$TEXT:{text}$TEXT" f"$EMOTION:{emotion}$EMOTION" f"$ACTIONS:[{','.join(actions)}]$ACTIONS"
        return response_str

    def _request(self, messages: list[messages_dict], **kwargs) -> str:
        """
        Send a request to the OpenAI API to generate a response based on the given messages and optional keyword
        arguments.

        Args:
            messages (list[messages_dict]): A list of message dictionaries.
            **kwargs: Optional keyword arguments; arguments "model", "n", and "max_tokens" cannot be modified.

        Returns:
            str: The content of the response generated by the AI model.
        """
        kwargs["messages"] = messages
        kwargs["model"] = self._model
        kwargs["n"] = 1
        kwargs["max_tokens"] = self._max_len - self._count_tokens(messages)

        response = openai.ChatCompletion.create(**kwargs)
        return response.choices[0].message.content.strip()

    def _select_emotion(self, response: str) -> None:
        """
        Initialize the chatbot's default emotion from the given response.

        Args:
            response (str): The response containing the chatbot's default emotion.
        """
        emotion = self._strip_punctuation(response).lower()
        if emotion in config.emotions:
            self._default_emotion = emotion
        else:
            self._default_emotion = config.default_emotion

    def _select_name(self, response: str) -> str:
        """
        Initialize the chatbot's name from the given response.

        Args:
            response (str): The response containing the chatbot's name.
        """
        self._name = self._strip_punctuation(response).capitalize()

    def _select_random_character(self) -> str:
        """
        Select a random character for a chatbot personality and return the character's name along with a brief
        description of their identity and the suggested behavior for their chatbot persona. The character can be a
        renowned fictional figure from a book, film, television series, or video game, or a real person, either from
        history or currently alive.

        Returns:
        str: The character's name along with a brief description of their identity and the suggested behavior for
        their chatbot persona.
        """
        # Define the prompt message
        prompt = (
            "You are helping a user choose a character for a chatbot personality. The character can be a renowned "
            "fictional figure from a book, film, television series, or video game, or a real person, either from "
            "history or currently alive. Provide the character's name along with a brief description of their identity "
            "and the suggested behavior for their chatbot persona. Please select only one character and ensure that "
            "the description and chatbot persona are clear and coherent."
        )

        # Define the messages to be sent to the API
        messages = [
            {"role": "system", "content": prompt},
            {"role": "system", "content": "Expects format similar to the following: " + config.default_character},
        ]

        # Send the messages to the API and get the response
        response = self._request(messages=messages, temperature=0.8, top_p=0.9)

        # Return the response
        return response

    def _select_voice(self, response: str) -> None:
        """
        Initialize the chatbot's voice from the given response.

        Args:
            response (str): The response containing the chatbot's voice.
        """
        name = self._strip_punctuation(response).capitalize()
        if name in config.neural_voices.keys():
            self._voice = config.neural_voice_formatter.format(name)
        else:
            self._voice = config.neural_voice_formatter.format(config.default_voice)

    def _strip_punctuation(self, s: str) -> str:
        """
        Removes punctuation and strips whitespace from the given string.
        """
        table = str.maketrans(dict.fromkeys(string.punctuation))
        return s.translate(table).strip()

    def _summarize_conversation(self) -> str:
        """
        Summarize the key points and any specific user information from the chatbot's conversation history that might be
        useful for future conversations.

        Returns:
            str: A summary of the conversation.
        """
        prompt = (
            "Break character and complete the following task as written: Summarize the conversation, focusing on key "
            "points and any specific user information that may be useful for future discussions, in the most succinct "
            "manner possible."
        )
        messages = self._history + [{"role": "system", "content": prompt}]
        response = self._request(messages=messages, top_p=0.7)
        return response

    def _weather_data_parse(self, data: dict) -> str:
        """
        Parses the weather data retrieved from the YR API and returns a summary string containing current conditions and
        forecast for the next hour, six hours, and twelve hours.

        Args:
            data (dict): Weather data retrieved from the API.

        Returns:
            str: Summary string containing current conditions and forecast.
        """
        # Extract necessary data from the input dictionary
        properties = data["properties"]
        units = properties["meta"]["units"]
        data_now = properties["timeseries"][0]["data"]
        instant = data_now["instant"]["details"]
        next_hour = data_now["next_1_hours"]
        next_six_hours = data_now["next_6_hours"]
        next_twelve_hours = data_now["next_12_hours"]

        # Format current conditions into a list of strings
        current_conditions = [f"{key}: {instant[key]} {units[key]}" for key in instant.keys()]

        # Format forecast into a string
        forecast = (
            f"Next hour's weather: {next_hour['summary']['symbol_code']}, "
            f"next six hours' weather: {next_six_hours['summary']['symbol_code']}, "
            f"next twelve hours' weather: {next_twelve_hours['summary']['symbol_code']}."
        )

        # Combine current conditions and forecast into a summary string
        summary = ". Current weather conditions: " + "; ".join(current_conditions) + ". " + forecast

        # Replace underscores with spaces in the summary string
        summary = summary.replace("_", " ")

        # Return the summary string
        return summary

    def prompt(self, message: str) -> parsed_response:
        """
        Add a user message to the chatbot's conversation history and generate a parsed response from the AI model.

        Args:
            message (str): The user's message.

        Returns:
            parsed_response: A dictionary containing the parsed text, emotion, and actions in the response.
        """
        self._history_append(role="user", content=message)
        response = self._request(messages=self._context + self._history)
        response_parsed, success = self._response_parse(response=response)

        retry_attempts = 0
        while not success and retry_attempts < config.retry_attempt_limit:
            response_parsed, success = self._response_parse(response=response)
            retry_attempts += 1

        response_unparsed = self._response_unparse(
            text=response_parsed["text"], emotion=response_parsed["emotion"], actions=response_parsed["actions"]
        )
        self._history_append(role="assistant", content=response_unparsed)
        return response_parsed
