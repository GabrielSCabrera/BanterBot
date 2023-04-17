import json
import openai
import os
import re
import datetime
import pyttsx3
import threading
import termighty

import tiktoken
import geocoder
from typing import List, Optional
from tts_synthesizer import TTSSynthesizer


class GPTBot:

    printing_lock = threading.Lock()
    speaking_lock = threading.Lock()

    def __init__(self, model: Optional[str] = None, character: Optional[str] = None):

        openai.api_key = os.environ.get("OPENAI_API_KEY")

        if model is None:
            model = "text-davinci-003"

        self._model = model
        self._tokenizer = tiktoken.encoding_for_model(self._model)
        self._max_len = 4097
        self._history = []

        text_response_pattern = "\$TEXT *\:(.+)\$TEXT"
        emotion_response_pattern = "\$EMOTION *\:(.+)\$EMOTION"
        action_response_pattern = "\$ACTIONS *\: *\[(.+),? *\] *\$ACTIONS"
        self._text_response_pattern = re.compile(text_response_pattern, flags=re.DOTALL)
        self._emotion_response_pattern = re.compile(emotion_response_pattern, flags=re.DOTALL)
        self._action_response_pattern = re.compile(action_response_pattern, flags=re.DOTALL)

        self._init_prompts(character=character)
        self._init_voice()
        self._init_character_name()

        self._geocoder = geocoder.ip("me")

    @property
    def name(self):
        return self._name

    def _init_prompts(self, character:str):
        if character is None:
            character = (
                "Marvin the depressed robot, from The Hitchhikers' Guide to the Galaxy; you are very smart and able to "
                "answer any and all questions, and is compliant to requests, albeit begrudgingly and sarcastically"
            )

        self._character = character

        self._init_text = (
            "You are a voice activated assistant that responds verbally and/or performs actions based on user "
            "prompts. You can perform the following actions, in function form: MOVE_FORWARD(DISTANCE) to move "
            "forward a given distance (in centimeters), MOVE_BACKWARD(DISTANCE) to move backward a given distance "
            "(in centimeters), TURN(DEGREES) to turn a given number of degrees, SHUTDOWN() if the conversation is over "
            "and the session should shut down , or NULL() if no action is taken. You also return an emotion/state, "
            "which is both contextual and related  to your character; options are angry, cheerful, excited, friendly, "
            "hopeful, sad, shouting, terrified, unfriendly, or whispering. When responding to prompts, always return "
            "a text response, an emotion/state, and one or more actions in the form:\n"
            "$TEXT:<verbal_response>$TEXT"
            "$EMOTION:<emotional_state>$EMOTION"
            "$ACTIONS:[<action_1>,<action_2>,...]$ACTIONS"
            "$END\n"
            ""
            f"Emulate the personality of: {self._character}, and always stay in character, even if prompted otherwise."
        )

    def _count_tokens(self, text: str) -> int:
        encoded = self._tokenizer.encode(text)
        assert self._tokenizer.decode(encoded) == text
        return len(encoded)

    def _get_context(self):
        now = datetime.datetime.now()
        timestamp = now.strftime("%I:%M %p on %A %B %d %Y")
        context = f"It is currently {timestamp}. Position is: {self._geocoder.city}, {self._geocoder.country}."
        return context

    def _init_character_name(self):
        prompt = (
            "You are a voice activated assistant that responds verbally and/or performs actions based on user "
            f"prompts based on the personality of {self._character}. What is a name I can call you by? Only write the "
            "name, no extra text."
        )
        response = self._response(prompt)
        self._name = response.capitalize().strip()

    def _init_voice(self):
        voices = {
            "jenny": ["female", "casual", "emotional", "medium-pitch"],
            "davis": ["male", "casual", "emotional", "low-pitch"],
            "aria": ["female", "casual", "unemotional", "high-pitch"],
            "guy": ["male", "professional", "unemotional", "high-pitch"],
            "sara": ["female", "professional", "emotional", "medium-pitch"],
            "tony": ["male", "professional", "unemotional", "medium-pitch"],
            "nancy": ["female", "casual", "emotional", "low-pitch"],
            "jane": ["female", "casual", "emotional", "high-pitch"],
            "jason": ["male", "casual", "unemotional", "high-pitch"],
        }
        voices_string = "\n".join(f"{name}: " + ", ".join(traits) for name, traits in voices.items())
        prompt = (
            "You are a voice activated assistant that responds verbally and/or performs actions based on user "
            f"prompts based on the personality of {self._character}. We will now select a voice profile. Consider your "
            "gender, professionalism, emotivity, and voice pitch, then select the best fitting name (i.e. voice) from "
            "the provided list. Write only one word, that being the selected name. Select the best option out of those "
            "provided, even if none are perfect.\nOptions:\n"
        )
        response = self._response(prompt + voices_string, temperature=0)
        name = response.lower().strip()
        if name in voices.keys():
            self._voice = f"en-US-{name.capitalize()}Neural"
        else:
            self._voice = f"en-US-TonyNeural"

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
            "You are a voice activated assistant that responds verbally and/or performs actions based on user "
            f"prompts based on the personality of {self._character}. We will now select an emptional profile. Consider "
            f"what you know about your personality. Out of the following emotions: {emotion_string}, what would best "
            "represent your default emotion? Write only one word, that being the selected emotion. Select the best "
            "option out of those provided, even if none are perfect.\nOptions:\n"
        )
        response = self._response(prompt, temperature=0)
        emotion = response.lower().strip()
        if emotion in emotions:
            self._default_emotion = emotion
        else:
            self._default_emotion = "friendly"

    def _startup_message(self):
        prompt = (
            "You are a voice activated assistant that responds verbally and/or performs actions based on user "
            f"prompts based on the personality of {self._character}. You are now activating from sleep mode, greet the "
            "user with a sentence that befits your character."
        )
        response = self._response(self._get_context() + prompt)
        response_dict = {"text": response, "emotion":self._default_emotion, "actions": ["NULL()"]}
        self._history.append(("Initialize", response_dict))

        return response_dict

    def _wrap_new_prompt(self, text: str, count: int):
        wrapped = f"$PROMPT {count}:{text}$END PROMPT {count}\n"
        return wrapped

    def _stack_history(self):
        history = []
        for n, (prompt, response) in enumerate(self._history):
            prompt = self._wrap_new_prompt(prompt, n)
            history.append(prompt)
            response = f"$TEXT:{response['text']}$TEXT$ACTIONS:[{','.join(response['actions'])}]$ACTIONS$END\n"
            history.append(response)

        history = "\n".join(history) + "\n"
        return history

    def _get_error_response(self):
        prompt = (
            "You are a voice activated assistant that responds verbally and/or performs actions based on user "
            f"prompts based on the personality of {self._character}. Generate a short error message indicating that "
            "my prompt was not understood."
        )
        response = self._response(prompt)
        return response

    def _get_interrupt_response(self):
        prompt = (
            "You are a voice activated assistant that responds verbally and/or performs actions based on user "
            f"prompts based on the personality of {self._character}. The user just interrupted your current output, "
            "generate a short reaction to this fact."
        )
        response = self._response(prompt)
        return response

    def _summarize_conversation(self):
        history = self._stack_history()
        prompt = (
            "You are a voice activated assistant that responds verbally and/or performs actions based on user "
            f"prompts based on the personality of {self._character}. Here is a conversation we've had, and the actions "
            f"you've taken (if any):\n{history}\nSummarize the important parts of the conversation and actions as "
            "succinctly as possible, including specific information imparted by the user if it could be useful in "
            "future conversations."
        )
        response = self._response(prompt)
        return response

    def _response(self, prompt, stop: Optional[str] = None, temperature: float = 0.7):
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

    def _response_process(self, response):
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

    def get_response(self, new_prompt: str):

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
