from termighty import TextBox, Term, Listener, System
from termighty_input_box import InputBox
from termighty_output_box import OutputBox
from gptbot import GPTBot
from tts_synthesizer import TTSSynthesizer
import threading
import time


class Interface:
    def __init__(self, border_color: str = "Charcoal", background_color: str = "Black"):
        self._border_color = border_color
        self._background_color = background_color
        self._gptbot = GPTBot()
        self._tts_synthesizer = TTSSynthesizer()
        self._history = []
        self._current_entry = None
        self._shutdown = False
        self._user_name = "USER"
        self._init_gui()

    def _init_gui(self):
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
            wrap_subsequent_indent=" " * (2 + max(len(self._user_name), len(self._gptbot._name))),
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
    def input_history(self):
        return self._input_window._outputs

    def _thread_output_text(self):
        N = 0
        while not System.kill_all and not self._shutdown:
            length = self._tts_synthesizer._total_length
            if length > N:
                new_output = [f"{self._gptbot._name.upper()}: " + "".join(self._tts_synthesizer._output[-1])]
                output = self._process_history() + new_output
                self._output_window(output)
                N = length
            time.sleep(0.005)

    def _shutdown_output(self):
        output = self._process_history() + [self._gptbot._summarize_conversation()]
        self._output_window(output)

    def _thread_speak(self):
        N = 0
        while not System.kill_all:
            length = len(self._history)
            if length > N:
                entry = self._history[-1]
                self._tts_synthesizer.speak(entry["full_response"]["text"])
                entry["response"] = "".join(self._tts_synthesizer._output[-1])
                entry["completed"] = True
                N = length
                if "SHUTDOWN()" in entry["full_response"]["actions"]:
                    self._shutdown = True
                    self._shutdown_output()
                    break
            time.sleep(0.005)

    def _thread_gpt_response(self):
        N = 0
        while not System.kill_all:
            length = len(self._input_window._outputs)
            if length > N:
                entry = self._input_window._outputs[-1].strip()
                # interrupt_response = None
                # if self._tts_synthesizer._synthesis_completed = True and self._tts_synthesizer._synthesis_started = True:
                #     self._tts_synthesizer._interrupt = True
                #     interrupt_response = self._gptbot._get_interrupt_response()
                response = self._gptbot.get_response(entry)
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

    def _process_history(self):
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

    def start(self):
        self._term.clear(flush=True)

        self._title.start()
        self._output_window.start()
        self._input_prompt.start()

        for border in self._borders:
            border.start()

        Listener.start()
        self._input_window.start()

        startup_message = self._gptbot._startup_message()

        self._history.append(
            {
                "prompt": None,
                "full_response": startup_message,
                "response": None,
                "interrupted": False,
                "completed": False,
            })

        thread_speak = threading.Thread(target=self._thread_speak, daemon=True)
        thread_output_text = threading.Thread(target=self._thread_output_text, daemon=True)
        thread_gpt_response = threading.Thread(target=self._thread_gpt_response, daemon=True)

        thread_speak.start()
        thread_output_text.start()
        thread_gpt_response.start()

        # prompt = input("User: ")
        # response = self.get_response(prompt)
        # print(f"{self.name}: ", response["text"])
        # self._speak(response["text"])
        # if "SHUTDOWN()" in response["actions"]:
        #     break


if __name__ == "__main__":
    interface = Interface()
    interface.start()
