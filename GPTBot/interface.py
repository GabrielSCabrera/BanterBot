"""
This program defines an interface for a text-based conversational agent based on the GPTBot class. The program uses the
termighty library to create a graphical user interface for user interaction and handles input and output processing, as
well as text-to-speech synthesis.

The Interface class defines a number of methods for initializing the GUI, processing and formatting the history of
messages for output, scrolling the output window to the latest messages, preparing the output for shutdown by
summarizing the conversation and displaying it in the output window, and starting the Interface.

The program also defines several threads for handling the output of text to the output window, speaking the GPTBot's
responses using the TTSSynthesizer, and generating GPTBot responses based on user input.

The program takes command-line arguments for specifying the character to use for GPTBot, either by name or randomly. If
no argument is provided, the default is None.

Overall, this program provides a framework for creating a text-based conversational agent with a user-friendly graphical
interface, using the GPTBot class for generating responses and the termighty library for handling input and output
processing.
"""
import argparse
import re
import sys
import threading
import time
from typing import Literal, Optional

from termighty import Listener, System, Term, TextBox
from termighty_input_box import InputBox
from termighty_output_box import OutputBox

import config
from gptbot import GPTBot
from tts_synthesizer import TTSSynthesizer


class Interface:
    """
    A class representing a text-based conversational interface for a GPTBot. It provides a graphical user interface for
    user interaction and handles input and output processing, as well as text-to-speech synthesis.
    """

    def __init__(
        self,
        border_color: str = "Charcoal",
        background_color: str = "Black",
        character=None,
        random_character=False,
        username: Optional[str] = None,
        mode: Literal["ChatCompletion", "Completion"] = "ChatCompletion",
        thread_on_init: bool = True,
        gpt4: bool = False,
        temperature: float = 1.0,
    ) -> None:
        """
        Initializes the Interface class with specified border and background colors, and GPTBot character settings.

        Args:
            border_color (str): The color of the border, default is "Charcoal".
            background_color (str): The color of the background, default is "Black".
            character (str): The name of the character to use for GPTBot, default is None.
            random_character (bool): If True, chooses a random character, default is False.
            username (str): The name of the user.
        """
        # Set the colors for the border and background of the interface
        self._border_color = border_color
        self._background_color = background_color

        # Select the API temperature.
        self._temperature = temperature

        # Have the GPTBot use the GPT-4 API
        if gpt4:
            model = "gpt-4"
            mode = "ChatCompletion"
            thread_on_init = False
        else:
            model = None

        # Initialize a new instance of the GPTBot class with the specified character settings
        self._gptbot = GPTBot(
            model=model,
            character=character,
            random_character=random_character,
            username=username,
            mode=mode,
            thread_on_init=thread_on_init,
        )

        # Initialize a new instance of the TTSSynthesizer class for text-to-speech synthesis
        self._tts_synthesizer = TTSSynthesizer()

        # Initialize an empty history of messages
        self._history = []

        # Initialize variables for the current entry, shutdown status, user name, and interrupt status
        self._current_entry = None
        self._shutdown = False
        self._username = username.upper() if username is not None else "USER"
        self._interrupt = False

        # Init Action Patterns
        self._action_patterns = {}
        for action in config.actions:
            split_action = action.split("(")
            pattern = re.compile(f"({split_action[0]})\((.*)\)")
            self._action_patterns[action] = pattern

        # Initialize a lock for the history of messages to prevent race conditions
        self._history_lock = threading.Lock()

        # Initialize the graphical user interface for the Interface class
        self._init_gui()

        # Append the startup message for the GPTBot to the history of messages
        with self._history_lock:
            self._history.append(
                {
                    "prompt": None,
                    "username": self._gptbot.username.upper(),
                    "character_name": self._gptbot.character_name.upper(),
                    "emotion": self._gptbot._startup_message["emotion"],
                    "actions": self._gptbot._startup_message["actions"],
                    "text": [self._gptbot._startup_message["text"]],
                    "spoken_text": None,
                    "completed": True,
                }
            )

    def _init_gui(self) -> None:
        """
        Initializes the graphical user interface for the Interface class. It sets up text boxes, input and output
        windows, and borders.
        """
        # Initialize Terminal
        self._term = Term()

        # Set default sizes and edge lengths for the different elements of the interface
        size = 1
        w_size = 1 * size
        edge_B = -(size + 1)
        edge_R = -(w_size + 1)

        # Set the text to display at the input prompt
        input_prompt_text = " User Input > "

        # Initialize the different text boxes that make up the interface
        self._title = TextBox(0, 0, size, -1, background=self._border_color)
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

        # Center the title text
        self._title.alignment = "center"

        # Set up the border elements of the interface
        self._borders = [
            TextBox(edge_B, 0, -1, -1, background=self._border_color),
            TextBox(size, 0, edge_B, w_size, background=self._border_color),
            TextBox(size, edge_R, edge_B, -1, background=self._border_color),
            TextBox(2 * edge_B, w_size, edge_B - 1, -size, background=self._border_color),
        ]

        # Set the text for the title and input prompt text boxes
        self._title(["Conversation History"])
        self._input_prompt([input_prompt_text])

    @property
    def input_history(self) -> list[str, ...]:
        """
        Property that returns the input history of the interface, which contains user inputs.

        Returns:
            list[str, ...]: List of strings representing the input history.
        """
        return self._input_window._inputs

    def _history_process(self, include_latest_response: bool = True) -> list[str]:
        """
        Process and format the message history to display in the output window.

        Args:
            include_latest_response[bool]: A boolean that omits the latest historical output if set to False.

        Returns:
            list[str]: A list of formatted strings representing the message history.
        """
        # Initialize an empty list to store the formatted strings
        output = []

        # Select the final index of the message history through which this method will iterate
        N = len(self._history) if include_latest_response else len(self._history) - 1

        # Iterate through the message history
        for entry in self._history[:N]:
            if entry["prompt"] is not None:
                # If the current entry is a user message, format it and append it to the output list
                output.append(f"{entry['username']}: {entry['prompt'].strip()}")
            if entry["spoken_text"]:
                # If the current entry is a GPTBot message, format it and append it to the output list
                output.append(f"{entry['character_name']}: {entry['spoken_text'].strip()}")
                output.append("\n")  # Add a newline after the GPTBot message

        # If "include_latest_response" is False, print only the latest prompt if it is not None.
        if not include_latest_response:
            entry = self._history[-1]
            if entry["prompt"] is not None:
                output.append(f"{entry['username']}: {entry['prompt'].strip()}")
            current_output = f"{entry['character_name']}:"
            if entry["spoken_text"] is not None:
                current_output += entry["spoken_text"]  # .rstrip()
            output.append(current_output)

        return output

    def _scroll(self, force_scroll: bool = False) -> None:
        """
        Scrolls the output window to the latest messages, ensuring that the most recent conversation is visible.

        Args:
            force_scroll(bool): If set to True, forces the window to scroll regardless of the override.
        """
        # If scroll override is not set, scroll to the latest messages
        if not self._output_window._scroll_override or force_scroll:
            # Calculate the bottom of the output window
            bottom = max(0, len(self._output_window._new_line) - self._output_window._shape[0])
            # Set the origin of the output window to the bottom
            self._output_window._origin = (bottom, 0)

    def _shutdown(self) -> None:
        """
        Prepares the output for shutdown by summarizing the conversation and displaying it in the output window.
        """

        # Get the formatted conversation history and the summary message
        output = self._history_process(include_latest_response=True) + ["\n", self._gptbot._summarize_conversation()]

        # Display the conversation and summary in the output window
        self._output_window(output)

        # Scroll to the bottom of the output window to show the latest messages
        self._scroll(force_scroll=True)

    def _thread_output_text(self) -> None:
        """
        Thread that handles the output of text to the output window. It monitors changes in the message history
        and updates the output window accordingly.
        """
        # Initialize variables to keep track of the last processed TTS length and history length
        last_processed_tts_length = 0
        last_processed_history_length = 0

        # Loop until the program is being shut down
        while not System.kill_all and not self._shutdown:
            # Check if new text has been synthesized by the TTS synthesizer
            length = self._tts_synthesizer._total_length
            # Calculating history length in order to prevent inconsistent lengths over time
            len_history = len(self._history)
            if length > last_processed_tts_length:
                # If there is new synthesized text, add it to the output window
                output = self._history_process(include_latest_response=False)
                output[-1] += " " + "".join(self._tts_synthesizer._output[-1])
                self._output_window(output)
                self._scroll()

                # Update the last processed TTS length and history length
                last_processed_tts_length = length
                last_processed_history_length = len_history

            # Check if the message history has changed
            if last_processed_history_length < len_history:
                # If the history has changed, update the output window
                history = self._history_process(include_latest_response=True)
                self._output_window(history)

            # Sleep for a short time to avoid excessive CPU usage
            time.sleep(0.005)

    def _thread_speak(self) -> None:
        """
        Thread that handles speaking the GPTBot's responses using the TTSSynthesizer. It monitors the history
        and synthesizes speech for new responses.
        """

        # initialize variables to track changes in the history and to be used to check for new entries
        N = 0
        break_outer_loop = False

        # loop until the program is shut down or break_outer_loop is set to True
        while not System.kill_all and not break_outer_loop:
            len_history = len(self._history)
            self._interrupt = False

            # check if there are new entries in the history
            with self._gptbot._history_lock:
                if len_history > N:
                    # get the latest entry in the history
                    entry = self._history[len_history - 1]
                    idx = 0

                    # loop through each part of the response
                    while not self._interrupt and (not entry["completed"] or idx < len(entry["text"])):
                        if entry["text"] is not None and idx < len(entry["text"]):

                            # synthesize speech for the response
                            self._tts_synthesizer.speak(
                                entry["text"][idx],
                                voice_name=self._gptbot._voice,
                                style=entry["emotion"],
                            )

                            # append the synthesized speech to the history
                            with self._history_lock:
                                if entry["spoken_text"] is None:
                                    entry["spoken_text"] = ""
                                entry["spoken_text"] += " " + "".join(self._tts_synthesizer._output[-1])

                            idx += 1

                            # check if the response contains the "EXIT()" action
                            if "EXIT()" in entry["actions"]:
                                self._shutdown = True
                                break_outer_loop = True
                                break
                            else:
                                for action in entry["actions"]:
                                    if search := re.findall(self._action_patterns["SAVE_USER_NAME(NAME)"], action):
                                        new_name = search[0][1].strip().split(" ")[0].strip().title()
                                        self._gptbot.username = new_name

                        time.sleep(0.005)
                    N = len_history

                    # unparsed the response to a string and append it to GPTBot's message history
                    message_unparsed = self._gptbot._response_unparse(
                        actions=entry["actions"], emotion=entry["emotion"], text=entry["spoken_text"]
                    )
                    self._gptbot._history_append(role="assistant", content=message_unparsed)
                    if self._shutdown:
                        self._shutdown()

            time.sleep(0.005)

    def _thread_gpt_response(self) -> None:
        """
        Thread that handles generating GPTBot responses based on user input. It processes user input and generates
        appropriate responses using the GPTBot class.
        """

        # Tracks the last processed input
        N = 0

        # Continuously check for new inputs
        while not System.kill_all:
            # Get the current number of inputs
            len_inputs = len(self._input_window._inputs)

            # If there is a new input, process it
            if len_inputs > N:

                # Interrupt any ongoing TTS synthesis
                self.interrupt()

                # Process each input
                idx = len_inputs - 1
                entry = self._input_window._inputs[idx]

                # Add all unprocessed inputs to the message history
                with self._history_lock:
                    for i in self._input_window._inputs[N : idx - 1]:
                        self._history.append(
                            {
                                "prompt": i.strip(),
                                "username": self._gptbot.username.upper(),
                                "character_name": self._gptbot.character_name.upper(),
                                "emotion": None,
                                "actions": [],
                                "text": [],
                                "spoken_text": None,
                                "completed": True,
                            }
                        )

                    # Add the current input to the message history
                    self._history.append(
                        {
                            "prompt": entry,
                            "username": self._gptbot.username.upper(),
                            "character_name": self._gptbot.character_name.upper(),
                            "emotion": None,
                            "actions": [],
                            "text": [],
                            "spoken_text": None,
                            "completed": False,
                        }
                    )

                # Generate GPTBot responses based on the input
                for response in self._gptbot.prompt_stream(entry, temperature=self._temperature):
                    # If there is a new input before the response is finished, stop generating responses for this input
                    if idx < len(self._input_window._inputs) - 1:
                        break

                    # Update the message history with the generated response
                    with self._history_lock:
                        self._history[-1]["actions"] = response["actions"]
                        self._history[-1]["emotion"] = response["emotion"]
                        self._history[-1]["text"].append(response["text"])

                    # Check if the response contains a shutdown command
                    if "EXIT()" in response["actions"]:
                        # Clear the input prompt, hide the cursor, and freeze the input window
                        self._input_prompt([""])
                        self._term.cursor_hide(flush=True)
                        self._input_window.freeze()
                        break

                    time.sleep(0.005)

                # Mark the input as completed in the message history
                with self._history_lock:
                    self._history[-1]["completed"] = True

                # Update the last processed input
                N = len_inputs

            time.sleep(0.005)

    def interrupt(self):
        """
        Interrupts the current text-to-speech synthesis and GPTBot processing. It stops ongoing actions and
        updates the history to reflect the interruption.
        """
        # Stop TTS synthesis and GPTBot processing
        self._tts_synthesizer.interrupt()
        self._gptbot.interrupt()
        self._interrupt = True

        # Only mark as interruption if TTS synthesis is ongoing
        if not self._tts_synthesizer._synthesis_completed:
            self._gptbot._history_append_interruption()

    def start(self) -> None:
        """
        Starts the Interface, initializes the GUI elements and starts the threads for processing input and output.
        It sets up the environment and manages threading for seamless user interaction.
        """
        # clear terminal before initializing GUI elements
        self._term.clear(flush=True)

        # start GUI elements
        self._title.start()
        self._output_window.start()
        self._input_prompt.start()

        # start GUI borders
        for border in self._borders:
            border.start()

        # start input listener
        Listener.start()

        # start input box
        self._input_window.start()

        # start threads for output text, speaking GPTBot's responses, and generating GPTBot responses
        thread_output_text = threading.Thread(target=self._thread_output_text, daemon=True)
        thread_speak = threading.Thread(target=self._thread_speak, daemon=True)
        thread_gpt_response = threading.Thread(target=self._thread_gpt_response, daemon=True)

        thread_output_text.start()
        thread_speak.start()
        thread_gpt_response.start()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="GPTBot Interface",
        description=(
            "This program defines an interface for a text-based conversational agent based on the GPTBot class. The "
            "program uses the termighty library to create a graphical user interface for user interaction and handles "
            "input and output processing, as well as text-to-speech synthesis."
        ),
        epilog=(
            "Requires three environment variables for full functionality. "
            "1) OPENAI_API_KEY: A valid OpenAI API key, "
            "2) AZURE_SPEECH_KEY: A valid Azure Cognitive Services Speech API key for TTS functionality, and "
            "3) AZURE_SPEECH_REGION: The region associated with your Azure Cognitive Services Speech API key."
        ),
    )

    parser.add_argument(
        "-u",
        "--username",
        type=str,
        dest="username",
        help="The name of the program's user, only one word without spaces is allowed.",
    )

    parser.add_argument(
        "-c",
        "--character",
        type=str,
        dest="character",
        help=(
            "A name and/or short description of the character GPTBot should emulate. For best results, use the "
            'second-person singular to describe the character, in the form "<name> from <context>, <details>".'
        ),
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=["ChatCompletion", "Completion"],
        default="ChatCompletion",
        type=str,
        dest="mode",
        help="OpenAI API Selection. ChatCompletion is cheaper, but often not as good unless you have GPT-4 access.",
    )

    parser.add_argument(
        "-r",
        "--rand",
        "--random",
        action="store_true",
        dest="random",
        help='Override the "character" argument and have the program select a random character.',
    )

    parser.add_argument(
        "-n",
        "--no-thread",
        action="store_false",
        dest="nothread",
        help='Disable multithreading on initialization of GPTBot (can help with "Too Many Requests" exceptions).',
    )

    parser.add_argument(
        "-g",
        "--gpt4",
        action="store_true",
        dest="gpt4",
        help="Enable GPT-4; overrides --mode and --no-thread flag, and only works if you have GPT-4 API access.",
    )

    parser.add_argument(
        "-t",
        "--temp",
        "--temperature",
        type=float,
        dest="temperature",
        help="Set the model temperature.",
    )

    args = parser.parse_args()

    kwargs = {
        "username": args.username,
        "character": args.character,
        "mode": args.mode,
        "random_character": args.random,
        "thread_on_init": args.nothread,
        "gpt4": args.gpt4,
        "temperature": args.temperature,
    }

    print("Loading...")
    interface = Interface(**kwargs)
    interface.start()
