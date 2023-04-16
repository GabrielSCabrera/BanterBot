from termighty.utils.listener import Listener
from termighty.utils import KeyProcessor
from termighty.widgets.text_editor import TextEditor

import textwrap


class InputBox(TextEditor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._outputs = []

    def _run_getch_thread(self) -> None:
        """
        Keeps updating the window every set number of seconds (given by `dt`) and accounts for changes in the terminal
        size (useful when dealing with relative coordinates on initialization).
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
                    self._outputs.append(self._raw_text[0])
                    self._raw_text = [""]
                    self._cursor_position = (0, 0)
                    self._selected = []
                    call = True
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
                    if self._wrap_text:
                        self.__call__([i for i in self._raw_text for j in textwrap.wrap(i, self._shape[1])])
                    else:
                        self.__call__(self._raw_text)
