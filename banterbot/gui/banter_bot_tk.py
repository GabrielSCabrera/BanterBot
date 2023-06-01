import tkinter as tk
from tkinter import ttk
import threading

from banterbot.data.azure_neural_voices import AzureNeuralVoice, get_voice_by_name
from banterbot.data.openai_models import OpenAIModel, get_model_by_name
from banterbot.gui.banter_bot_interface import BanterBotInterface


class BanterBotTK(tk.Tk, BanterBotInterface):
    """
    BanterBotTK is a graphical user interface (GUI) for a chatbot application that uses OpenAI models for generating
    responses, Azure Neural Voices for text-to-speech, and Azure speech-to-text recognition. The class inherits from
    both tkinter.Tk and BanterBotInterface, providing a seamless integration of the chatbot functionality with a
    user-friendly interface.

    The GUI allows users to interact with the chatbot by entering their name and message, and it displays the
    conversation history in a scrollable text area. Users can send messages by pressing the "Send" button or the "Enter"
    key. The chatbot's responses are generated using the specified OpenAI model and can be played back using the
    specified Azure Neural Voice. Additionally, users can toggle speech-to-text input by pressing the "Listen" button.
    """

    def __init__(
        self,
        model: OpenAIModel = get_model_by_name("gpt-3.5-turbo"),
        voice: AzureNeuralVoice = get_voice_by_name("Aria"),
        style: str = "chat",
    ) -> None:
        """
        Initialize the BanterBotTK class, which inherits from both tkinter.Tk and BanterBotInterface.

        Args:
            model (OpenAIModel, optional): The OpenAI model to be used for generating responses.
            voice (AzureNeuralVoice, optional): The Azure Neural Voice to be used for text-to-speech.
            style (str, optional): The style of the conversation (e.g., "cheerful", "sad", "chat").
        """
        tk.Tk.__init__(self)
        BanterBotInterface.__init__(self, model=model, voice=voice, style=style)
        self._listening = False

    def _init_gui(self) -> None:
        """
        Initialize the graphical user interface for the BanterBot application.
        This method sets up the main window, conversation area, input fields, and buttons.
        """
        self.title("BanterBot")
        self.configure(bg="black")
        self.geometry("1024x768")
        self._font = ("Cascadia Code", 16)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", font=self._font, bg="black", fg="white")
        self.style.configure("Vertical.TScrollbar", background="black", bordercolor="black", arrowcolor="black")

        self.history_frame = ttk.Frame(self)
        self.conversation_area = tk.Text(
            self.history_frame, wrap=tk.WORD, state=tk.DISABLED, bg="black", fg="white", font=self._font
        )
        self.conversation_area.grid(row=0, column=0, ipadx=5, padx=5, pady=5, sticky="nsew")
        self.history_frame.rowconfigure(0, weight=1)
        self.history_frame.columnconfigure(0, weight=1)

        self.scrollbar = ttk.Scrollbar(self.history_frame, command=self.conversation_area.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.conversation_area["yscrollcommand"] = self.scrollbar.set

        self.history_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.entry_frame = ttk.Frame(self)
        self.entry_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.name_entry = tk.Entry(
            self.entry_frame, bg="black", fg="white", insertbackground="white", font=self._font, width=12
        )
        self.name_entry.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="nsew")
        self.name_entry.insert(0, "User")
        self.name_entry.bind("<FocusIn>", self.select_all_on_focus)
        self._name_entry_focused = False

        self.message_entry = tk.Entry(
            self.entry_frame, bg="black", fg="white", insertbackground="white", font=self._font
        )
        self.message_entry.grid(row=0, column=1, padx=(5, 5), pady=5, sticky="nsew")
        self.message_entry.focus_set()
        self.entry_frame.columnconfigure(1, weight=1)

        self.send_btn = ttk.Button(self.entry_frame, text="Send", command=self.prompt, width=7)
        self.send_btn.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="nsew")

        self.listen_btn = ttk.Button(self.entry_frame, text="Listen", command=self.toggle_listen, width=7)
        self.listen_btn.grid(row=0, column=3, padx=(0, 5), pady=5, sticky="nsew")

        self.message_entry.bind("<Return>", lambda event: self.prompt())

    def update_conversation_area(self, word: str) -> None:
        """
        Update the conversation area with the given word.

        Args:
            word (str): The word to be added to the conversation area.
        """
        super().update_conversation_area(word)
        self.conversation_area["state"] = tk.NORMAL
        self.conversation_area.insert(tk.END, word)
        self.conversation_area.update_idletasks()
        self.conversation_area["state"] = tk.DISABLED
        self.conversation_area.see(tk.END)

    def select_all_on_focus(self, event) -> None:
        """
        Select all text in the widget when it receives focus.

        Args:
            event: The event object containing information about the focus event.
        """
        widget = event.widget
        if widget == self.name_entry:
            self._name_entry_focused = True
            widget.selection_range(0, tk.END)
            widget.icursor(tk.END)
        else:
            self._name_entry_focused = False

    def reset_on_send(self) -> None:
        """
        Reset the focus state of the name entry field after sending a message.
        """
        self._name_entry_focused = False

    def toggle_listen(self) -> None:
        """
        Toggle the speech-to-text functionality.
        """
        if self.listening:
            self.listen_btn["text"] = "Listen"
        else:
            self.listen_btn["text"] = "Stop"

        user_name = self.name_entry.get().split(" ")[0].strip()
        super().toggle_listen(user_name)

    def prompt(self) -> None:
        """
        Prompt the user for input and process the message.
        This method retrieves the user's name and message, and then calls the superclass's prompt method.
        """
        user_name = self.name_entry.get().split(" ")[0].strip()
        user_message = self.message_entry.get()
        if not user_message:
            return
        else:
            super().prompt(user_message, user_name)
            self.message_entry.delete(0, tk.END)

    def run(self) -> None:
        """
        Run the BanterBot application.
        This method starts the main event loop of the tkinter application.
        """
        self.mainloop()
