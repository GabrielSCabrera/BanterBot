import openai
import os
import re
import datetime
import termighty

import tiktoken
import geocoder
from typing import Optional, TypedDict


class parsed_response(TypedDict):
    text: str
    emotion: str
    actions: list[str, ...]


class GPTBot:
    """
    A class to interact with OpenAI's GPT model, simulating a voice-activated assistant with a specified character.
    """

    def __init__(self, model: Optional[str] = None, character: Optional[str] = None) -> None:
        """
        Initialize GPTBot with the given model and character.

        :param model: The name of the GPT model to use, defaults to 'text-davinci-003'.
        :param character: The character the bot should emulate, defaults to Marvin from The Hitchhiker's Guide to the
        Galaxy.
        """

        # Set up OpenAI API access and model
        openai.api_key = os.environ.get("OPENAI_API_KEY")

        if model is None:
            model = "text-davinci-003"

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

        # Initialize character, voice, and name
        self._init_prompts(character=character)
        self._init_voice()
        self._init_default_emotion()
        self._init_character_name()

        # Set up geolocation based on IP
        self._geocoder = geocoder.ip("me")

    @property
    def name(self) -> str:
        """
        Returns the name of the character.
        """
        return self._name

    def _init_prompts(self, character: str) -> None:
        """
        Initialize character and prompts based on the given character.

        :param character: The character the bot should emulate.
        """
        # Set up character default if not provided
        if character is None:
            character = (
                "Marvin the depressed robot, from The Hitchhikers' Guide to the Galaxy; you are very smart and able to "
                "answer any and all questions, and are compliant to requests, albeit begrudgingly and sarcastically"
            )
        self._character = character

        # Set up init_text with the given character
        self._init_text = (
            f"You are {self._character}. Repond to the user's latest text prompt. Stay in character at all times. "
            "Perform actions using the exact function forms provided: MOVE_FORWARD(DISTANCE), MOVE_BACKWARD(DISTANCE), "
            "TURN(DEGREES), SHUTDOWN(), or NULL(). Return an emotion/state related to your character and context, "
            "using the exact options provided: angry, cheerful, excited, friendly, hopeful, sad, shouting, terrified, "
            "unfriendly, or whispering. Respond to prompts with the following format:\n"
            "$TEXT:<verbal_response>$TEXT\n"
            "$EMOTION:<emotional_state>$EMOTION\n"
            "$ACTIONS:[<action_1>,<action_2>,...]$ACTIONS\n"
            "$END\n"
        )

    def _count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a given text.

        :param text: The text to count tokens for.
        :return: The number of tokens in the text.
        """
        encoded = self._tokenizer.encode(text)
        assert self._tokenizer.decode(encoded) == text
        return len(encoded)

    def _get_context(self) -> str:
        """
        Get the current time and geolocation as a formatted string.

        :return: A string with the current time and geolocation.
        """
        now = datetime.datetime.now()
        timestamp = now.strftime("%I:%M %p on %A %B %d %Y")
        context = f"It is currently {timestamp}. Position is: {self._geocoder.city}, {self._geocoder.country}."
        return context

    def _init_character_name(self) -> None:
        """
        Generate and set the character's name using GPT.
        """
        prompt = (
            f"You are {self._character}. Provide a name the user can call you by. Write only the name, without any "
            "additional text."
        )
        response = self._response(prompt)
        self._name = response.capitalize().strip()

    def _init_voice(self) -> None:
        """
        Initialize the voice profile for the character using GPT.
        """
        # Set up available voice profiles
        voices = {
            "guy": ["male", "professional", "unemotional", "high-pitch"],
            "tony": ["male", "professional", "unemotional", "medium-pitch"],
            "davis": ["male", "casual", "expressive", "low-pitch"],
            "jason": ["male", "casual", "unemotional", "high-pitch"],
            "sara": ["female", "professional", "expressive", "medium-pitch"],
            "aria": ["female", "casual", "unemotional", "high-pitch"],
            "jenny": ["female", "casual", "expressive", "medium-pitch"],
            "jane": ["female", "casual", "expressive", "high-pitch"],
            "nancy": ["female", "casual", "expressive", "low-pitch"],
        }
        voices_string = "\n".join(f"{name}: " + ", ".join(traits) for name, traits in voices.items())
        prompt = (
            f"You are {self._character}. Choose a voice profile that best fits your character, ensuring the gender is "
            "correct. Take into account your character's name, background information, and whether they are based on "
            "a real or fictional person. Also, consider factors like professionalism, emotivity, and pitch. Select one "
            "name from the provided list, even if it's not a perfect match. Write your answer as a single word."
            "\nOptions:\n"
        )
        response = self._response(prompt + voices_string, temperature=0)
        name = response.lower().strip()
        if name in voices.keys():
            self._voice = f"en-US-{name.capitalize()}Neural"
        else:
            self._voice = f"en-US-TonyNeural"

    def _init_default_emotion(self) -> None:
        """
        Initialize the character's default emotion using GPT.
        """
        emotions = [
            "angry",
            "cheerful",
            "excited",
            "friendly",
            "hopeful",
            "sad",
            "shouting",
            "terrified",
            "unfriendly",
            "whispering",
        ]
        emotion_string = ", ".join(emotions)
        prompt = (
            f"You are {self._character}. Choose one default emotion from the following options: {emotion_string}. "
            "Select the most appropriate emotion, even if it's not a perfect fit. Write your answer as a single "
            "word."
        )
        response = self._response(prompt, temperature=0)
        emotion = response.lower().strip()
        if emotion in emotions:
            self._default_emotion = emotion
        else:
            self._default_emotion = "friendly"

    def _startup_message(self) -> parsed_response:
        """
        Generate the character's startup message using GPT.

        :return: A dictionary containing the text, emotion, and actions of the response.
        """
        prompt = f"You are {self._character}. After being woken, greet me with a sentence that reflects your character."
        response = self._response(self._get_context() + prompt)
        response_dict = {"text": response, "emotion": self._default_emotion, "actions": ["NULL()"]}
        self._history.append(("Initialize", response_dict))

        return response_dict

    def _wrap_new_prompt(self, text: str, count: int) -> str:
        """
        Wrap a new prompt with a specific format.

        :param text: The text of the prompt.
        :param count: The index of the prompt in the conversation.
        :return: A formatted string with the prompt.
        """
        wrapped = f"$PROMPT {count}:{text}$END PROMPT {count}\n"
        return wrapped

    def _stack_history(self) -> str:
        """
        Stack the conversation history in a formatted string.

        :return: A string with the conversation history.
        """
        history = []
        for n, (prompt, response) in enumerate(self._history):
            prompt = self._wrap_new_prompt(prompt, n)
            history.append(prompt)
            response = f"$TEXT:{response['text']}$TEXT$ACTIONS:[{','.join(response['actions'])}]$ACTIONS$END\n"
            history.append(response)

        history = "\n".join(history) + "\n"
        return history

    def _get_error_response(self) -> str:
        """
        Generate an error response using GPT.

        :return: A string containing the error response.
        """
        prompt = (
            f"You are {self._character}. Provide a short response indicating that you might not have paid close "
            "attention or didn't catch what the user said."
        )
        response = self._response(prompt)
        return response

    def _get_interrupt_response(self) -> str:
        """
        Generate a response to an interruption using GPT.

        :return: A string containing the response to the interruption.
        """
        prompt = (
            f"You are {self._character}. The user interrupted your mid-speech. Generate a short reaction to this "
            "interruption."
        )
        response = self._response(prompt)
        return response

    def _summarize_conversation(self) -> str:
        """
        Generate a summary of the conversation using GPT.

        :return: A string containing the summary of the conversation.
        """
        history = self._stack_history()
        prompt = (
            f"You are a voice-activated assistant with the personality of {self._character}. Given the conversation "
            f"and actions below:\n{history}\nSummarize the key points and any specific user information that might be "
            "useful for future conversations as succinctly as possible."
        )
        response = self._response(prompt)
        return response

    def _response(self, prompt: str, stop: Optional[str] = None, temperature: float = 0.7) -> str:
        """
        Generate a response using GPT.

        :param prompt: The prompt to send to GPT.
        :param stop: An optional string used as a stop sequence for GPT.
        :param temperature: The temperature to use for GPT's response (default 0.7).
        :return: A string containing GPT's response.
        """
        token_count = self._count_tokens(prompt)
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=self._max_len - token_count,
                n=1,
                stop=stop,
                temperature=temperature,
            )
            return response.choices[0].text.strip()
        except openai.error.AuthenticationError as e:
            voiced_error_message = (
                "Incorrect or missing OpenAI API Key. Assign it to environment variable OPENAI_API_KEY, and try again."
            )
            self._speak(voiced_error_message)
            raise e

    def _response_process(self, response: str) -> parsed_response:
        """
        Process the raw response from GPT.

        :param response: The raw response from GPT.
        :return: A dictionary containing the text, emotion, and actions of the response.
        """
        text_search = re.findall(self._text_response_pattern, response)
        emotion_search = re.findall(self._emotion_response_pattern, response)
        action_search = re.findall(self._action_response_pattern, response)

        search = [text_search, emotion_search, action_search]
        search = [i[0] if len(i) == 1 else None for i in search]

        if search[0] is None:
            search[0] = self._get_error_response()

        if search[1] is None:
            search[1] = self._default_emotion
        else:
            search[1] = search[1].lower()

        if search[2] is None:
            search[2] = "NULL()"

        response = {"text": search[0], "emotion": search[1], "actions": search[2].split(",")}
        return response

    def get_response(self, new_prompt: str) -> parsed_response:
        """
        Generate a response to the given prompt.

        :param new_prompt: The new prompt to get a response for.
        :return: A dictionary containing the text, emotion, and actions of the response.
        """
        context = self._get_context()
        new_prompt_wrapped = self._wrap_new_prompt(new_prompt, len(self._history))

        if len(self._history) > 0:
            history = self._stack_history()
        else:
            history = ""

        prompt = context + self._init_text + "\n" + history + new_prompt_wrapped

        response_raw = self._response(prompt, "$END")
        response = self._response_process(response_raw)

        self._history.append((new_prompt, response))

        return response
