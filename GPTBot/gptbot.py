from collections.abc import Iterator
import datetime
import json
import os
import re
import string
import threading
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
    def __init__(
        self,
        model: Optional[str] = None,
        character: Optional[str] = None,
        random_character: bool = False,
        user_name: Optional[str] = None,
    ) -> None:

        openai.api_key = os.environ.get(config.openai_api_key_env_variable)

        self._geocoder = geocoder.ip("me")
        self._weather_update_frequency = datetime.timedelta(minutes=15)
        self._weather_last_updated = None

        if model is None:
            model = config.default_chat_gpt_model

        self._model = model
        self._user_name = user_name.capitalize() if user_name is not None else None
        self._tokenizer = tiktoken.encoding_for_model(self._model)
        self._max_len = 4096
        self._interrupt = False
        self._history = []
        self._history_lock = threading.Lock()

        action_response_pattern = "\$ *ACTIONS *\: *\[(.+),? *\] *\$ *ACTIONS"
        emotion_response_pattern = "\$ *EMOTION *\:(.+)\$ *EMOTION"
        text_response_pattern = "\$ *TEXT *\:(.+)\$ *TEXT"
        text_open_response_pattern = "\$ *TEXT *\:"
        text_close_response_pattern = "\$ *TEXT"
        sentence_split_pattern = "([\.\?\!][ \r\n\t]+)"

        self._action_response_pattern = re.compile(action_response_pattern, flags=re.DOTALL)
        self._emotion_response_pattern = re.compile(emotion_response_pattern, flags=re.DOTALL)
        self._text_response_pattern = re.compile(text_response_pattern, flags=re.DOTALL)
        self._text_open_response_pattern = re.compile(text_open_response_pattern)
        self._text_close_response_pattern = re.compile(text_close_response_pattern)
        self._sentence_split_pattern = re.compile(sentence_split_pattern)

        self._init_character(character=character, random_character=random_character)
        self._init_character_traits()
        self._init_system()
        self._init_startup_message()

    @property
    def name(self) -> str:
        return self._name

    @property
    def _context(self) -> str:

        now = datetime.datetime.now()
        timestamp = now.strftime("%I:%M %p on %A %B %d %Y")

        lat, lon = self._geocoder.latlng

        if self._weather_last_updated is None or self._weather_last_updated + self._weather_update_frequency <= now:
            self._weather_last_updated = now

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

        context = (
            f"It is currently {timestamp}. Position is: {self._geocoder.city}, {self._geocoder.country}{self._weather}."
        )

        return [{"role": "system", "content": context}]

    def _count_tokens(self, messages: list[messages_dict]) -> int:

        num_tokens = 3
        for message in messages:

            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(self._tokenizer.encode(value))
        return num_tokens

    def _init_character(self, character: str, random_character: bool = False) -> None:

        if random_character:
            character = self._select_random_character()

        elif character is None:
            character = config.default_character
        self._character = character

    def _init_character_traits(self) -> None:

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
        self._default_emotion = self._select_emotion(response)

    def _init_startup_message(self) -> None:

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
        with self._history_lock:
            self._history_append(role="assistant", content=content, name=self._name)
        self._startup_message, success = self._response_parse(content)

    def _init_system(self) -> None:

        emotions = list(config.emotions[:-2]) + [", or ".join(config.emotions[-2:])]
        emotions_str = ", ".join(emotions)

        self._init_text = (
            f"You are {self._character}. Your entire reality is that of {self._name}.\n"
            "Stay in character throughout the conversation, do not ever break the fourth wall.\n"
            "When interrupted, address the interrupting prompt first, then return to the previous topic if relevant.\n"
            "Structure your responses in this order: 1. an action, 2. an emotion, and 3. a verbal statement.\n"
            "1. Action: Choose from these available functions: MOVE_FORWARD(DISTANCE), MOVE_BACKWARD(DISTANCE), "
            "TURN(ANGLE), SHUTDOWN(), or NULL(). DISTANCE is in meters, and ANGLE is in degrees.\n"
            "2. Emotion: Considering the context of the conversation given your character's personality, select the "
            f"most suitable emotion from the options provided in this list: {emotions_str}.\n"
            "3. Verbal Statement: Provide spoken words without any action descriptions or vocal tones.\n"
            "Adhere to the order and format your response as follows:\n"
            "$ACTIONS:[<action_1>,<action_2>,...]$ACTIONS"
            "$EMOTION:<emotion>$EMOTION"
            "$TEXT:<verbal_statement>$TEXT"
        )

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
        example_assistant_response_3 = "$ACTIONS:[SHUTDOWN()]$ACTIONS$EMOTION:whispering$EMOTION$TEXT:Goodbye.$TEXT"

        self._history = [
            {"role": "system", "content": self._init_text},
            {"role": "system", "content": "Here is an example of correct output formatting:"},
            {"role": "system", "name": "example_user", "content": example_user_prompt_1},
            {"role": "system", "name": "example_assistant", "content": example_assistant_response_1},
            {"role": "system", "name": "example_user", "content": example_user_prompt_2},
            {"role": "system", "name": "example_assistant", "content": example_assistant_response_2},
            {"role": "system", "name": "example_user", "content": example_user_prompt_3},
            {"role": "system", "name": "example_assistant", "content": example_assistant_response_3},
            {"role": "system", "content": "Example finished.  Begin the conversation:"},
        ]

    def _get_error_response(self) -> str:

        prompt = (
            f"You are portraying the character of {self._character}. Offer a brief apology suggesting that you were "
            "not paying close attention to what the user just said."
        )
        messages = [{"role": "system", "content": prompt}]
        response = self._request(messages=messages)
        return response

    def _history_append(
        self, role: Literal["system", "user", "assistant"], content: str, name: Optional[str] = None
    ) -> None:
        history_entry = {"role": role, "content": content}
        if name is not None:
            history_entry["name"] = name
        self._history.append(history_entry)

    def _history_append_interruption(self) -> None:
        with self._history_lock:
            response = self._history_append(role="system", content=f"The user interrupted {self._name} mid-speech.")

    def _prompt_emotion_selection(self) -> None:
        emotions = list(config.emotions[:-2]) + [", or ".join(config.emotions[-2:])]
        emotions_str = ", ".join(emotions)
        prompt = (
            f"Choose a default emotional state for your character from the available options: {emotions_str}. Select "
            "the most appropriate emotion, even if it may not be a perfect fit. Provide your answer as a single word. "
            "Ensure that the chosen word is from the given list and not an emotion outside of the provided options."
        )
        return prompt

    def _prompt_name_selection(self) -> None:
        prompt = (
            "Please provide the first name of the character. Write only one name, with no extra text or punctuation."
        )
        return prompt

    def _prompt_voice_selection(self) -> str:
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

        action_search = re.findall(self._action_response_pattern, response)
        if len(action_search) != 1:
            actions = ["NULL()"]
        else:
            actions = [action.strip() for action in action_search[0].split(",")]

        emotion_search = re.findall(self._emotion_response_pattern, response)
        if len(emotion_search) != 1:
            emotion = self._default_emotion
        else:
            emotion = emotion_search[0].lower()

        text_search = re.findall(self._text_response_pattern, response)
        if len(text_search) != 1:
            success = False
            text = self._get_error_response()
        else:
            success = True
            text = text_search[0]

        return {"actions": actions, "emotion": emotion, "text": text}, success

    def _response_unparse(self, actions: list[str, ...], emotion: str, text: str) -> str:

        response_str = f"$ACTIONS:[{','.join(actions)}]$ACTIONS$EMOTION:{emotion}$EMOTION$TEXT:{text}$TEXT"
        return response_str

    def _request(self, messages: list[messages_dict], **kwargs) -> str:

        kwargs["messages"] = messages
        kwargs["model"] = self._model
        kwargs["n"] = 1
        kwargs["max_tokens"] = self._max_len - self._count_tokens(messages)
        kwargs["stream"] = False

        response = openai.ChatCompletion.create(**kwargs)
        return response.choices[0].message.content.strip()

    def _request_stream(self, messages: list[messages_dict], **kwargs) -> Iterator:

        kwargs["messages"] = messages
        kwargs["model"] = self._model
        kwargs["n"] = 1
        kwargs["max_tokens"] = self._max_len - self._count_tokens(messages)
        kwargs["stream"] = True

        self._latest_stream = []

        return openai.ChatCompletion.create(**kwargs)

    def _select_emotion(self, response: str) -> str:

        emotion = self._strip_punctuation(response).lower()
        if emotion in config.emotions:
            return emotion
        else:
            return config.default_emotion

    def _select_name(self, response: str) -> str:

        self._name = self._strip_punctuation(response).capitalize()

    def _select_random_character(self) -> str:

        prompt = (
            "You are helping a user choose a character for a chatbot personality. The character can be a renowned "
            "fictional figure from a book, film, television series, or video game, or a real person, either from "
            "history or currently alive. Provide the character's name along with a brief description of their identity "
            "and the suggested behavior for their chatbot persona. Please select only one character and ensure that "
            "the description and chatbot persona are clear and coherent."
        )

        messages = [
            {"role": "system", "content": prompt},
            {"role": "system", "content": "Expects format similar to the following: " + config.default_character},
        ]

        response = self._request(messages=messages, temperature=1.2, top_p=0.9)

        return response

    def _select_voice(self, response: str) -> None:
        name = self._strip_punctuation(response).capitalize()
        if name in config.neural_voices.keys():
            self._voice = config.neural_voice_formatter.format(name)
        else:
            self._voice = config.neural_voice_formatter.format(config.default_voice)

    def _stream_parser(self, response: Iterator) -> Iterator[str]:
        actions = ["NULL()"]
        emotion = self._default_emotion

        actions_complete = False
        emotion_complete = False

        text_detected = False

        response_text = ""

        self._interrupt = False

        for chunk in response:

            delta = chunk["choices"][0]["delta"]

            if self._interrupt or delta == {}:
                break

            elif "content" in delta.keys():
                response_text += delta["content"]

                if not actions_complete:
                    for match in re.finditer(self._action_response_pattern, response_text):
                        actions_str = response_text[match.start() : match.end()]
                        actions = re.findall(self._action_response_pattern, actions_str)[0].upper().split(",")
                        response_text = response_text[: match.start()] + response_text[match.end() :]
                        actions_complete = True
                        break

                if not emotion_complete:
                    for match in re.finditer(self._emotion_response_pattern, response_text):
                        emotion_str = response_text[match.start() : match.end()]
                        emotion = re.findall(self._emotion_response_pattern, emotion_str)[0]
                        emotion = self._select_emotion(response=emotion)
                        response_text = response_text[: match.start()] + response_text[match.end() :]
                        emotion_complete = True
                        break

                if not text_detected:
                    match = re.search(self._text_open_response_pattern, response_text)
                    if match:
                        response_text = response_text[match.end() :]
                        text_detected = True

                elif re.search(self._sentence_split_pattern, response_text):
                    split_response_text = re.split(self._sentence_split_pattern, response_text)
                    sentence = "".join(split_response_text[0:-1])
                    sentence = re.sub(self._text_close_response_pattern, "", sentence)
                    response_text = response_text[len(sentence) :]

                    yield {"actions": actions, "emotion": emotion, "text": sentence}

        if text_detected:
            sentence = re.sub(self._text_close_response_pattern, "", response_text)
            yield {"actions": actions, "emotion": emotion, "text": sentence}

    def _strip_punctuation(self, s: str) -> str:
        table = str.maketrans(dict.fromkeys(string.punctuation))
        return s.translate(table).strip()

    def _summarize_conversation(self) -> str:
        prompt = (
            "Break character and complete the following task as written: Summarize the conversation, focusing on key "
            "points and any specific user information that may be useful for future discussions, in the most succinct "
            "manner possible. Be objective, and write everything in third person."
        )
        messages = self._history + [{"role": "system", "content": prompt}]
        response = self._request(messages=messages, top_p=0.7)
        return response

    def _weather_data_parse(self, data: dict) -> str:
        properties = data["properties"]
        units = properties["meta"]["units"]
        data_now = properties["timeseries"][0]["data"]
        instant = data_now["instant"]["details"]
        next_hour = data_now["next_1_hours"]
        next_six_hours = data_now["next_6_hours"]
        next_twelve_hours = data_now["next_12_hours"]

        current_conditions = [f"{key}: {instant[key]} {units[key]}" for key in instant.keys()]

        forecast = (
            f"Next hour's weather: {next_hour['summary']['symbol_code']}, "
            f"next six hours' weather: {next_six_hours['summary']['symbol_code']}, "
            f"next twelve hours' weather: {next_twelve_hours['summary']['symbol_code']}."
        )

        summary = ". Current weather conditions: " + "; ".join(current_conditions) + ". " + forecast

        summary = summary.replace("_", " ")

        return summary

    def interrupt(self) -> None:
        self._interrupt = True

    def prompt(self, message: str) -> parsed_response:
        with self._history_lock:
            self._history_append(role="user", content=message, name=self._user_name)
        response = self._request(messages=self._context + self._history)
        response_parsed, success = self._response_parse(response=response)

        retry_attempts = 0
        while not success and retry_attempts < config.retry_attempt_limit:
            response_parsed, success = self._response_parse(response=response)
            retry_attempts += 1

        response_unparsed = self._response_unparse(**response_parsed)
        with self._history_lock:
            self._history_append(role="assistant", content=response_unparsed, name=self._name)
        return response_parsed

    def prompt_stream(self, message: str) -> Iterator:
        with self._history_lock:
            self._history_append(role="user", content=message, name=self._user_name)
        response = self._request_stream(messages=self._context + self._history)
        for block in self._stream_parser(response=response):
            yield block


if __name__ == "__main__":
    bot = GPTBot()
    print("Starting")
    stream = bot.prompt_stream("Tell me a long complex story")
    for i in stream:
        print(i)
