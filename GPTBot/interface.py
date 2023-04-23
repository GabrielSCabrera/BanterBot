import threading
import time
import sys

from termighty import TextBox, Term, Listener, System
from termighty_input_box import InputBox
from termighty_output_box import OutputBox

from gptbot import GPTBot
from tts_synthesizer import TTSSynthesizer


class Interface:
    """
    A graphical user interface for GPTBot and TTSSynthesizer.

    It utilizes the GPTBot class to generate responses to user inputs, and the TTSSynthesizer class to generate speech
    for the chatbot's responses.
    """

    def __init__(
        self, border_color: str = "Charcoal", background_color: str = "Black", character=None, random_character=False
    ) -> None:
        """
        Initialize the interface.

        This method initializes the interface by creating the necessary GUI elements and starting the various threads
        required to run the program.

        Args:
            border_color (str): The color of the border for the GUI.
            background_color (str): The color of the background for the GUI.
            character (str): The name of the chatbot's character.
            random_character (bool): Whether to use a random character for the chatbot.
        """
        self._border_color = border_color
        self._background_color = background_color
        self._gptbot = GPTBot(character=character, random_character=random_character)
        self._tts_synthesizer = TTSSynthesizer()
        self._history = []
        self._current_entry = None
        self._shutdown = False
        self._user_name = "USER"

        self._history_lock = threading.Lock()

        self._init_gui()

        with self._history_lock:
            self._history.append(
                {
                    "prompt": None,
                    "full_response": self._gptbot._startup_message,
                    "spoken_text": None,
                }
            )

    def _init_gui(self) -> None:
        """
        Initializes the graphical user interface (GUI) of the chatbot by creating various TextBoxes and InputBox and
        setting their properties such as size, position, color, and alignment. It sets up the borders of the GUI using
        TextBoxes and adds the required text to the title TextBox and the input prompt TextBox.
        """
        self._term = Term()

        # Calculate the sizes of various parts of the GUI
        size = 1
        w_size = 1 * size
        edge_B = -(size + 1)
        edge_R = -(w_size + 1)

        input_prompt_text = " User Input > "

        # Initialize the various TextBoxes and InputBox for the GUI
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

        # Set the title TextBox's alignment
        self._title.alignment = "center"

        # Set up the border TextBoxes for the GUI
        self._borders = [
            TextBox(edge_B, 0, -1, -1, background=self._border_color),  # Bottom Border
            TextBox(size, 0, edge_B, w_size, background=self._border_color),  # Left Border
            TextBox(size, edge_R, edge_B, -1, background=self._border_color),  # Right Border
            TextBox(2 * edge_B, w_size, edge_B - 1, -size, background=self._border_color),  # Separator
        ]

        # Set the title TextBox's text and the input prompt TextBox's text
        self._title(["Conversation History"])
        self._input_prompt([input_prompt_text])

    @property
    def input_history(self) -> list[str, ...]:
        """
        Returns the list of user inputs that have been processed by the chatbot.

        Returns:
            list[str, ...]: The list of user inputs.

        """
        return self._input_window._inputs

    def _history_process(self) -> list[str, ...]:
        """
        This method processes the chat history and returns a formatted list of the chat messages.

        Returns:
            list[str]: The formatted list of chat messages.
        """
        output = []
        max_name_len = max(len(self._user_name), len(self._gptbot._name))
        N = len(self._history)
        for entry in self._history[: N - 1]:
            if entry["prompt"] is not None:
                output.append(f"{self._user_name:>{max_name_len}s}: {entry['prompt']}")
            if entry["spoken_text"] is not None:
                output.append(f"{self._gptbot._name.upper():>{max_name_len}s}: {entry['spoken_text']}")
                output.append("\n")

        if self._history[N - 1]["prompt"] is not None:
            output.append(f"{self._user_name:>{max_name_len}s}: {self._history[N-1]['prompt']}")

        return output

    def _scroll(self) -> None:
        """
        Scroll the output window to the bottom, assuming the scrolling position hasn't been overriden by the user.
        """
        if not self._output_window._scroll_override:
            bottom = max(0, len(self._output_window._new_line) - self._output_window._shape[0])
            self._output_window._origin = (bottom, 0)

    def _thread_output_text(self) -> None:
        """
        Continuously checks the output generated by the text-to-speech synthesizer and adds it to the chat history if it
        has not been added already. It also adds any new entries in the chat history since the last update to the
        output. It then updates the output window with the new output and scrolls the output window to the bottom to
        show the latest messages.
        """
        # Initialize counters for the length of the text-to-speech output and the length of the chat history
        N_TTS = 0
        N_history = 0

        # Continuously check the text-to-speech output and chat history and update the output window accordingly
        while not System.kill_all and not self._shutdown:
            length = self._tts_synthesizer._total_length
            len_history = len(self._history)

            # If there is new text-to-speech output, add it to the chat history and update the output window
            if length > N_TTS:
                new_output = [f"{self._gptbot._name.upper()}: " + "".join(self._tts_synthesizer._output[-1])]
                output = self._history_process() + new_output
                self._output_window(output)
                self._scroll()

                # Update the counters for the text-to-speech output and the chat history
                N_TTS = length
                N_history = len_history

            # If there are new entries in the chat history since the last update, update the output window
            elif N_history < len_history:
                history = self._history_process()
                self._output_window(history)

            # Wait for a small amount of time before checking again
            time.sleep(0.005)

    def _shutdown_output(self) -> None:
        """
        Outputs the final chat message on shutdown, summarizing the conversation.
        """
        output = self._history_process() + [self._gptbot._summarize_conversation()]
        self._output_window(output)
        self._scroll()

    def _thread_speak(self) -> None:
        """
        Thread function that generates text-to-speech output for the chatbot responses.

        This method continuously checks the chat history for new entries and generates text-to-speech output for any new
        chatbot responses. It then updates the chat history with the spoken text for the response. If the response
        includes the "SHUTDOWN()" action, it sets the shutdown flag to True and calls the shutdown output method.
        """

        # Initialize a counter for the number of entries in the chat history
        N = 0

        # Continuously check the chat history for new chatbot responses and generate text-to-speech output for them
        while not System.kill_all:
            len_history = len(self._history)

            # If there is a new chatbot response in the chat history, generate TTS output for it and update chat history
            if len_history > N:
                idx = len_history - 1
                self._tts_synthesizer.speak(
                    self._history[idx]["full_response"]["text"],
                    voice_name=self._gptbot._voice,
                    style=self._history[idx]["full_response"]["emotion"],
                )

                with self._history_lock:
                    self._history[idx]["spoken_text"] = "".join(self._tts_synthesizer._output[-1])

                N = len_history

                # If the response includes "SHUTDOWN()" action, set shutdown flag to True and call "_shutdown_output()"
                if "SHUTDOWN()" in self._history[idx]["full_response"]["actions"]:
                    self._shutdown = True
                    self._shutdown_output()
                    break

            # Wait for a small amount of time before checking again
            time.sleep(0.005)

    def _thread_gpt_response(self) -> None:
        """
        Continuously monitors user input and generates GPT responses for them. Records each prompt and full response,
        and updates the GUI accordingly.
        """
        N = 0
        while not System.kill_all:
            len_inputs = len(self._input_window._inputs)
            if len_inputs > N:
                idx = len_inputs - 1
                entry = self._input_window._inputs[idx].strip()

                # Interrupt current TTS synthesis if not completed
                if not self._tts_synthesizer._synthesis_completed:
                    self._tts_synthesizer.interrupt()
                    self._gptbot._history_append_interruption()

                # Generate a response to the user's input
                response = self._gptbot.prompt(entry)

                with self._history_lock:
                    # Append any intermediate inputs to the history
                    for i in self._input_window._inputs[N:idx]:
                        self._history.append(
                            {
                                "prompt": i.strip(),
                                "full_response": None,
                                "spoken_text": None,
                            }
                        )

                    # Append the latest prompt and response to the history
                    self._history.append(
                        {
                            "prompt": entry,
                            "full_response": response,
                            "spoken_text": None,
                        }
                    )

                # Update the index of the latest input
                N = len_inputs

                # Shutdown if the response indicates so
                if "SHUTDOWN()" in response["actions"]:
                    self._input_prompt([""])
                    self._term.cursor_hide(flush=True)
                    self._input_window.freeze()
                    break

            # Wait for a small amount of time before checking again
            time.sleep(0.005)

    def start(self) -> None:
        """
        Starts the interface.

        The method first clears the terminal, and then initializes and starts the graphical user interface.
        It also starts three separate threads that manage the user's interaction with the chatbot and the display
        of its responses.

        The threads are started as daemon threads, which means they will not prevent the Python interpreter
        from exiting if the main thread finishes execution.
        """
        # Clear the terminal screen.
        self._term.clear(flush=True)

        # Start the GUI elements and listener.
        self._title.start()
        self._output_window.start()
        self._input_prompt.start()

        for border in self._borders:
            border.start()

        Listener.start()
        self._input_window.start()

        # Start threads that manage chatbot interaction and response display.
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
