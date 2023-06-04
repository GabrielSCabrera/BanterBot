import tkinter as tk
from tkinter import ttk
from typing import Optional

from banterbot.data.azure_neural_voices import AzureNeuralVoice, get_voice_by_name
from banterbot.data.openai_models import OpenAIModel, get_model_by_name
from banterbot.gui.interface import Interface


class TKMultiplayerInterface(tk.Tk, Interface):
    def __init__(
        self,
        model: OpenAIModel = get_model_by_name("gpt-3.5-turbo"),
        voice: AzureNeuralVoice = get_voice_by_name("Aria"),
        style: str = "chat",
        system: Optional[str] = None,
    ) -> None:
        tk.Tk.__init__(self)
        Interface.__init__(self, model=model, voice=voice, style=style, system=system)

    def update_conversation_area(self, word: str) -> None:
        super().update_conversation_area(word)
        self.conversation_area["state"] = tk.NORMAL
        self.conversation_area.insert(tk.END, word)
        self.conversation_area.update_idletasks()
        self.conversation_area["state"] = tk.DISABLED
        self.conversation_area.see(tk.END)

    def select_all_on_focus(self, event) -> None:
        widget = event.widget
        if widget == self.name_entry:
            self._name_entry_focused = True
            widget.selection_range(0, tk.END)
            widget.icursor(tk.END)
        else:
            self._name_entry_focused = False

    def listener_activate(self, idx: int) -> None:
        user_name = self.name_entries[idx].get().split(" ")[0].strip()
        super().listener_activate(user_name)

    def listener_deactivate(self) -> None:
        super().listener_deactivate()

    def run(self) -> None:
        self.mainloop()

    def _init_gui(self) -> None:
        self.title(f"BanterBot {self._model.name}")
        self.configure(bg="black")
        self.geometry("1024x565")
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

        self.panel_frame = ttk.Frame(self)
        self.panel_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.name_entries = []
        self.listen_buttons = []

        for i in range(9):
            name_entry = tk.Entry(
                self.panel_frame, bg="black", fg="white", insertbackground="white", font=self._font, width=12
            )
            name_entry.grid(row=i, column=0, padx=(5, 0), pady=5, sticky="nsew")
            name_entry.insert(0, f"User {i+1}")
            self.name_entries.append(name_entry)

            listen_button = ttk.Button(self.panel_frame, text="Listen", width=7)
            listen_button.grid(row=i, column=1, padx=(0, 5), pady=5, sticky="nsew")
            listen_button.bind(f"<ButtonPress-1>", lambda event, i=i: self.listener_activate(i))
            listen_button.bind(f"<ButtonRelease-1>", lambda event: self.listener_deactivate())
            self.listen_buttons.append(listen_button)

            self.bind(f"<KeyPress-{i+1}>", lambda event, i=i: self.listener_activate(i))
            self.bind(f"<KeyRelease-{i+1}>", lambda event: self.listener_deactivate())

        self.request_btn = ttk.Button(self.panel_frame, text="Request", command=self.request_response, width=7)
        self.request_btn.grid(row=9, column=0, padx=(5, 0), pady=5, sticky="nsew")

        self.bind("<Return>", lambda event: self.request_response())

    def request_response(self) -> None:
        pass
