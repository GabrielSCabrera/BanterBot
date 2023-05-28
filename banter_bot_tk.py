import tkinter as tk
from tkinter import ttk

from banterbot.data.openai_models import openai_models
from banterbot.gui.banter_bot_frontend import BanterBotFrontend

# Choose model to use
MODEL = openai_models["gpt-3.5-turbo"]


class BanterBotFrontendTK(tk.Tk, BanterBotFrontend):
    def __init__(self) -> None:
        """
        Initialize the BanterBotFrontendTK class, which inherits from both tkinter.Tk and BanterBotFrontend.
        """
        tk.Tk.__init__(self)
        BanterBotFrontend.__init__(self, model=MODEL, voice="en-US-AriaNeural", style="general")

    def _init_gui(self) -> None:
        """
        Initialize the graphical user interface for the BanterBot application.
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

        self.message_entry = tk.Entry(self.entry_frame, bg="black", fg="white", font=self._font)
        self.message_entry.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.entry_frame.columnconfigure(0, weight=3)

        self.send_btn = ttk.Button(self.entry_frame, text="Send", command=self.prompt)
        self.send_btn.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.entry_frame.columnconfigure(1, weight=1)

        self.message_entry.bind("<Return>", lambda event: self.prompt())

    def update_conversation_area(self, word: str) -> None:
        """
        Update the conversation area with the given word.

        Args:
            word (str): The word to be added to the conversation area.
        """
        self.conversation_area["state"] = tk.NORMAL
        self.conversation_area.insert(tk.END, word)
        self.conversation_area.update_idletasks()
        self.conversation_area["state"] = tk.DISABLED
        self.conversation_area.see(tk.END)

    def prompt(self) -> None:
        """
        Prompt the user for input and process the message.
        """
        user_message = self.message_entry.get()
        if not user_message:
            return
        else:
            super().prompt(user_message)
            self.message_entry.delete(0, tk.END)

    def run(self) -> None:
        """
        Run the BanterBot application.
        """
        self.mainloop()


if __name__ == "__main__":
    app = BanterBotFrontendTK()
    app.run()
