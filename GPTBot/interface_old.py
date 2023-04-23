import threading
import time
import sys

from termighty import TextBox, Term, Listener, System
from termighty_input_box import InputBox
from termighty_output_box import OutputBox

from gptbot import GPTBot
from tts_synthesizer import TTSSynthesizer


class Interface:
    def __init__(
        self, border_color: str = "Charcoal", background_color: str = "Black", character=None, random_character=False
    ) -> None:
        """
        Initializes the interface by setting up the graphical elements and creating instances of the GPTBot and
        TTSSynthesizer classes for processing user input and synthesizing speech, respectively.

        Args:
            border_color (str): The color of the interface's border (default "Charcoal").
            background_color (str): The color of the interface's background (default "Black").
            character (str): The character to use as the GPTBot's icon (default None).
            random_character (bool): Whether to choose a random character for the GPTBot's icon (default False).
        """
        self._border_color = border_color
        self._background_color = background_color
        self._gptbot = GPTBot(character=character, random_character=random_character)
        self._tts_synthesizer = TTSSynthesizer()
        self._history = []
        self._current_entry = None
        self._shutdown = False
        self._user_name = "USER"
        self._init_gui()

        self._history.append(
            {
                "prompt": None,
                "full_response": self._gptbot._startup_message,
                "response": None,
                "interrupted": False,
                "completed": False,
            }
        )

    def _init_gui(self) -> None:
        """
        Initializes the graphical interface by creating instances of the TextBox and InputBox classes from the Termighty
        library and setting their properties.
        """
        self._term = Term()

        size = 1
        w_size = 1 * size
        edge_B = -(size + 1)
        edge_R = -(w_size + 1)

        input_prompt_text = " User Input > "

        self._title = TextBox(0, 0, size, -1, background=self._border_color)  # Top Border
        self._output_window = OutputBox(
            size,
            size,
            2 * edge_B,
            edge_R,
            background=self._background_color,
            wrap_text=True,
        )
        self._input_prompt = TextBox(
            edge_B - 1, w_size, edge_B, w_size + len(input_prompt_text), background=self._background_color
        )
        self._input_window = InputBox(
            edge_B - 1,
            w_size + len(input_prompt_text),
            edge_B,
            edge_R,
            line_numbers=False,
            background=self._background_color,
            horizontal_scroll_buffer=0,
        )

        self._title.alignment = "center"

        self._borders = [
            TextBox(edge_B, 0, -1, -1, background=self._border_color),  # Bottom Border
            TextBox(size, 0, edge_B, w_size, background=self._border_color),  # Left Border
            TextBox(size, edge_R, edge_B, -1, background=self._border_color),  # Right Border
            TextBox(2 * edge_B, w_size, edge_B - 1, -size, background=self._border_color),  # Separator
        ]

        self._title(["Conversation History"])
        self._input_prompt([input_prompt_text])

    @property
    def input_history(self) -> list[str, ...]:
        """
        Returns a list of strings representing the user's input history. Each string in the list corresponds to a single
        line of input entered by the user.

        Return:
        self._input_window._outputs (list[str,...]): a list of strings representing the user's input history
        """
        return self._input_window._outputs

    def _thread_output_text(self) -> None:
        """
        Runs in an independent thread to continuously check for new output from the text-to-speech synthesizer and
        update the graphical interface accordingly.
        """
        N = 0
        while not System.kill_all and not self._shutdown:
            length = self._tts_synthesizer._total_length
            if length > N:
                new_output = [f"{self._gptbot._name.upper()}: " + "".join(self._tts_synthesizer._output[-1])]
                output = self._process_history() + new_output
                self._output_window(output)
                if not self._output_window._scroll_override:
                    bottom = max(0, len(self._output_window._new_line) - self._output_window._shape[0])
                    self._output_window._origin = (bottom, 0)
                N = length
            time.sleep(0.005)

    def _shutdown_output(self) -> None:
        """
        Displays the final output from the chat session, including a summary message from the GPTBot, when the user
        initiates a shutdown of the program.
        """
        output = self._process_history() + [self._gptbot._summarize_conversation()]
        self._output_window(output)

    def _thread_speak(self) -> None:
        """
        Runs in an independent thread to continuously check for new prompts in the chat history and synthesize speech
        for the ChatGPT model's responses.
        """
        N = 0
        while not System.kill_all:
            length = len(self._history)
            if length > N:
                entry = self._history[-1]
                self._tts_synthesizer.speak(
                    entry["full_response"]["text"],
                    voice_name=self._gptbot._voice,
                    style=entry["full_response"]["emotion"],
                )
                entry["response"] = "".join(self._tts_synthesizer._output[-1])
                entry["completed"] = True
                N = length
                if "SHUTDOWN()" in entry["full_response"]["actions"]:
                    self._shutdown = True
                    self._shutdown_output()
                    break
            time.sleep(0.005)

    def _thread_gpt_response(self) -> None:
        """
        Runs in an independent thread to continuously check for new user input in the graphical interface, send the
        input to the ChatGPT model for processing, and update the chat history with the model's response.
        """
        N = 0
        while not System.kill_all:
            length = len(self._input_window._outputs)
            if length > N:
                entry = self._input_window._outputs[-1].strip()
                interrupt_response = None
                if not self._tts_synthesizer._synthesis_completed and self._tts_synthesizer._synthesis_started:
                    self._tts_synthesizer._interrupt = True
                    interrupt_response = self._gptbot._history_append_interruption()
                response = self._gptbot.prompt(entry)

                self._history.append(
                    {
                        "prompt": entry,
                        "full_response": response,
                        "response": None,
                        "interrupted": False,
                        "completed": False,
                    }
                )
                N = length
                if "SHUTDOWN()" in response["actions"]:
                    self._input_prompt([""])
                    self._input_window.freeze()
                    self._term.cursor_hide(flush=True)
                    break
            time.sleep(0.005)

    def _process_history(self) -> None:
        """
        Returns a formatted list of strings representing the chat history, including both user input and GPT-3 model
        responses.
        """
        output = []
        max_name_len = max(len(self._user_name), len(self._gptbot._name))
        for entry in self._history:
            if entry["completed"]:
                if entry["prompt"] is not None:
                    output.append(f"{self._user_name:>{max_name_len}s}: {entry['prompt']}")
                output.append(f"{self._gptbot._name.upper():>{max_name_len}s}: {entry['response']}")
                output.append("\n")

        if not self._history[-1]["completed"] and entry["prompt"] is not None:
            output.append(f"{self._user_name:>{max_name_len}s}: {self._history[-1]['prompt']}")

        return output

    def start(self) -> None:
        """
        Starts the graphical interface and all the independent threads for processing speech synthesis and ChatGPT model
        responses.
        """
        self._term.clear(flush=True)

        self._title.start()
        self._output_window.start()
        self._input_prompt.start()

        for border in self._borders:
            border.start()

        Listener.start()
        self._input_window.start()

        thread_speak = threading.Thread(target=self._thread_speak, daemon=True)
        thread_output_text = threading.Thread(target=self._thread_output_text, daemon=True)
        thread_gpt_response = threading.Thread(target=self._thread_gpt_response, daemon=True)

        thread_speak.start()
        thread_output_text.start()
        thread_gpt_response.start()


if __name__ == "__main__":
    kwargs = {}
    if len(sys.argv) > 1:
        character = " ".join(sys.argv[1:])
        if character.lower().strip() in ("random", "rand"):
            kwargs = {"random_character": True}
        else:
            kwargs = {"character": character}

    interface = Interface(**kwargs)
    interface.start()
