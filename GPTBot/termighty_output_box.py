from termighty.utils.listener import Listener
from termighty.widgets.text_editor import TextEditor


class OutputBox(TextEditor):
    """
    A widget that allows users to input text and display a list of outputs.

    Inherits from the TextEditor class.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize an OutputBox object.

        Args:
        *args: positional arguments to be passed to the TextEditor class
        **kwargs: keyword arguments to be passed to the TextEditor class
        """
        super().__init__(*args, **kwargs)
        self._outputs = []
        self._scroll_override = False

    def _run_getch_thread(self) -> None:
        """
        Override the _run_getch_thread method of the TextEditor class.

        This method is run in a separate thread and waits for user input. It processes user input
        and updates the text and cursor position accordingly.
        """
        self._raw_text = self._text
        getch_iterator = Listener.getch_iterator()

        ignore_keys = [
            "Left",
            "Keypad-Left",
            "Right",
            "Keypad-Right",
            "Alt-Left",
            "Alt-Right",
            "Alt-Up",
            "Alt-Down",
            "Ctrl-Left",
            "Ctrl-Keypad-Left",
            "Ctrl-Right",
            "Ctrl-Keypad-Right",
            "Ctrl-Up",
            "Ctrl-Keypad-Up",
            "Ctrl-Down",
            "Ctrl-Keypad-Down",
            "Backspace",
            "Ctrl-Backspace",
            "Ctrl-Keypad-Backspace",
            "Ctrl-Delete",
            "Ctrl-Keypad-Delete",
            "Delete",
            "Keypad-Delete",
            "Enter",
            "Space",
            "Tab",
            "End",
            "Keypad-End",
            "Home",
            "Keypad-Home",
            "Alt-End",
            "Alt-Home",
            "Alt-PgDn",
            "Alt-PgUp",
            "\n",
            "\r",
            "\t",
        ]

        self._term.cursor_show(flush=True)
        for key in getch_iterator:
            if not self._frozen:
                new_row = None
                bottom = max(0, len(self._new_line) - self._shape[0])

                if key == "Up":
                    new_row = max(0, self._origin[0] - 1)
                elif key == "Down":
                    new_row = min(bottom, self._origin[0] + 1)
                elif key == "PgUp":
                    new_row = 0
                elif key == "PgDn":
                    new_row = bottom

                if new_row is not None and self._origin[0] != new_row:
                    self._origin = (new_row, 0)
                    if new_row == bottom:
                        self._scroll_override = False
                    else:
                        self._scroll_override = True
                    super(TextEditor, self)._set_view()

    def _set_view(self) -> None:
        """
        Override the _set_view method of the TextEditor class.

        This method updates the view of the text and cursor position based on the current state
        of the widget.
        """

        row, col = self._cursor_position
        row_prev, col_prev = self._prev_cursor_position

        if row_prev != row:
            self._origin = (self._origin[0], 0)

        cursor_position = (
            row + self._ref_row_start - self._origin[0],
            col + self._ref_col_start - self._origin[1],
        )

        cursor_position = (
            row + self._row_start - self._origin[0],
            col + self._col_start - self._origin[1],
        )

        self._selected_processed = [
            (position[0] + self._row_start - self._origin[0], position[1] + self._col_start - self._origin[1])
            for position in self._selected
        ]
        self._prev_cursor_position = self._cursor_position

        super(TextEditor, self)._set_view()
