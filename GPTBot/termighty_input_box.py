from termighty.utils.listener import Listener
from termighty.utils import KeyProcessor
from termighty.widgets.text_editor import TextEditor


class InputBox(TextEditor):
    """
    A widget that allows users to input text and store it in a list of outputs.

    Inherits from the TextEditor class.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize an InputBox object.

        Args:
        *args: positional arguments to be passed to the TextEditor class
        **kwargs: keyword arguments to be passed to the TextEditor class
        """
        super().__init__(*args, **kwargs)
        self._inputs = []
        self._deactivate = False

    def _run_getch_thread(self) -> None:
        """
        Override the _run_getch_thread method of the TextEditor class.

        This method is run in a separate thread and waits for user input. It processes user input
        and updates the text and cursor position accordingly.
        """
        self._raw_text = self._text
        getch_iterator = Listener.getch_iterator()

        ignore_keys = [
            "Enter",
            "Up",
            "Keypad-Up",
            "Down",
            "Keypad-Down",
            "Alt-Up",
            "Alt-Down",
            "Ctrl-Up",
            "Ctrl-Keypad-Up",
            "Ctrl-Down",
            "Ctrl-Keypad-Down",
            "PgDn",
            "PgUp",
            "Alt-PgDn",
            "Alt-PgUp",
            "\n",
            "\r",
        ]

        self._term.cursor_show(flush=True)
        for key in getch_iterator:
            if not self._frozen:
                if key == "Enter":
                    if self._raw_text[0] != "":
                        self._inputs.append(self._raw_text[0])
                        self._raw_text = [""]
                        self._cursor_position = (0, 0)
                        self._origin = (0, 0)
                        self._selected = []
                        self.__call__(self._raw_text)
                else:
                    call, self._raw_text, self._cursor_position, self._selected = KeyProcessor.process_key(
                        raw_text=self._raw_text,
                        cursor_position=self._cursor_position,
                        selected=self._selected,
                        shape=self._shape,
                        key=key,
                        ignore_keys=ignore_keys,
                    )
                    if call:
                        self.__call__(self._raw_text)
