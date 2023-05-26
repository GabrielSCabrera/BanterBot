import threading
import tkinter as tk
from tkinter import ttk
from typing import List

from banterbot.core.openai_manager import Message, OpenAIManager
from banterbot.core.text_to_speech import TextToSpeech
from banterbot.data.openai_models import openai_models
from banterbot.utils.text_to_speech_word import TextToSpeechWord

# Choose model to use
MODEL = openai_models["gpt-3.5-turbo"]


class BanterBotApplication(tk.Tk):
    """
    This class is the main application for the Chatbot. It utilizes the OpenAI model to interact with the user. The
    interactions occur through a graphical user interface that displays the chat history and provides an entry box for
    user input.
    """

    def __init__(self) -> None:
        super().__init__()

        # OpenAI and Text-to-Speech setup for managing AI interactions and text-to-speech functionalities
        self._openai_manager = OpenAIManager(model=MODEL)
        self._text_to_speech = TextToSpeech()

        # Threading lock for synchronizing output operations in multithreading environment
        self._output_lock = threading.Lock()

        # List for storing Message objects and threading setup for response handling
        self._messages: List[Message] = []
        self._response_thread = None

        # Initialize the GUI
        self._init_gui()

    def _init_gui(self):
        """
        Initializes the TKinter GUI.
        """
        # Basic tkinter setup for window title, background color, window size, and font
        self.title("BanterBot")
        self.configure(bg="black")
        self.geometry("1024x768")
        self._font = ("Cascadia Code", 16)

        # GUI component setup to create frames, conversation area, scrollbar, message entry box, and send button
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

        self.send_btn = ttk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_btn.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.entry_frame.columnconfigure(1, weight=1)

        self.message_entry.bind("<Return>", lambda event: self.send_message())

    def update_conversation_area(self, word: TextToSpeechWord) -> None:
        """
        Updates the conversation text area by adding a new word. The category of the word determines whether a space
        should be added before the word or not.

        Args:
            word (TextToSpeechWord): The word to add to the conversation.
        """
        self.conversation_area["state"] = tk.NORMAL
        if word.category == "Word":
            self.conversation_area.insert(tk.END, " ")
        self.conversation_area.insert(tk.END, word.word)
        self.conversation_area.update_idletasks()
        self.conversation_area["state"] = tk.DISABLED
        self.conversation_area.see(tk.END)

    def send_message(self) -> None:
        """
        Sends a user message. The message is displayed in the GUI and triggers the process to get a response. If a
        previous response is still being processed, it is interrupted before the new message is sent.
        """
        user_message = self.message_entry.get()

        if not user_message:
            return
        else:
            if self._response_thread and self._response_thread.is_alive():
                self._openai_manager.interrupt()
                self._text_to_speech.interrupt()
                with self._output_lock:
                    self.end_response()

        with self._output_lock:
            user_message_obj = Message(role="user", content=user_message)
            self._messages.append(user_message_obj)
            self.message_entry.delete(0, tk.END)
            self.conversation_area["state"] = tk.NORMAL
            self.conversation_area.insert(tk.END, f"User: {user_message}\n\n")
            self.conversation_area["state"] = tk.DISABLED
            self.conversation_area.see(tk.END)

        with self._output_lock:
            self._response_thread = threading.Thread(target=self.get_response, daemon=True)
            self._response_thread.start()

    def get_response(self) -> None:
        """
        Gets a response from the chatbot. The response is then displayed in the GUI and spoken by the text-to-speech
        system.
        """
        response_messages = self._openai_manager.prompt(messages=self._messages)
        response = " ".join(response_messages)

        if response:
            response_message_obj = Message(role="assistant", content=response)
            self._messages.append(response_message_obj)

            text, voice, style = response_message_obj.content, "en-US-AriaNeural", "general"
            self.conversation_area["state"] = tk.NORMAL
            self.conversation_area.insert(tk.END, "Assistant: ")
            self.conversation_area["state"] = tk.DISABLED
            for word in self._text_to_speech.speak(text, voice, style):
                self.update_conversation_area(word)

        self.end_response()

    def end_response(self) -> None:
        """
        Ends the response. This method adds two newlines to the conversation area to visually separate the response from
        the next message.
        """
        self.conversation_area["state"] = tk.NORMAL
        self.conversation_area.insert(tk.END, "\n\n")
        self.conversation_area["state"] = tk.DISABLED
        self.conversation_area.see(tk.END)

    def run(self) -> None:
        """
        Starts the tkinter main loop to run the application. This method must be called for the application to start.
        """
        self.mainloop()


if __name__ == "__main__":
    # Instantiate and run the application
    app = BanterBotApplication()
    app.run()
