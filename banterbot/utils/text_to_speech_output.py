from typing import Iterator

from banterbot.utils.text_to_speech_word import TextToSpeechWord


class TextToSpeechOutput:
    """
    This class encapsulates the output of a text-to-speech conversion, providing
    a convenient interface for working with and manipulating the converted data.
    """

    def __init__(self, input_string: str) -> None:
        """
        Initializes a new TextToSpeechOutput instance, setting up the input string and preparing the words list for the
        converted words.

        Args:
            input_string (str): The input string that is to be converted into speech.
        """
        self.input_string = input_string

        # A list to store the converted TextToSpeechWord objects
        self.words = []

        # Tracks the active state of the TextToSpeechOutput object
        self.is_active = False

    def __getitem__(self, idx: int) -> TextToSpeechWord:
        """
        Allows for indexing into the TextToSpeechOutput object to retrieve words at specific positions.

        Args:
            idx (int): The index of the word to retrieve.

        Returns:
            TextToSpeechWord: The word at the specified index.
        """
        return self.words[idx]

    def __iter__(self) -> Iterator[TextToSpeechWord]:
        """
        Provides an iterator to iterate over the TextToSpeechWord objects in the output.

        Yields:
            TextToSpeechWord: The next TextToSpeechWord object in the output.
        """
        for word in self.words:
            yield word

    def __len__(self) -> int:
        """
        Allows for the use of len() on a TextToSpeechOutput instance, returning
        the number of words in the output.

        Returns:
            int: The number of words in the output.
        """
        return len(self.words)

    def __setitem__(self, idx: int, value: TextToSpeechWord) -> None:
        """
        Allows for setting the value of a word at a specific index in the output.

        Args:
            idx (int): The index of the word to be replaced.
            value (TextToSpeechWord): The new word to be placed at the specified index.
        """
        self.words[idx] = value

    def __str__(self) -> str:
        """
        Converts the TextToSpeechOutput instance into a string, concatenating all the words in the output.

        Returns:
            str: The string representation of the text-to-speech output.
        """
        return "".join(word.word for word in self.words)

    def append(self, entry: TextToSpeechWord) -> None:
        """
        Appends a TextToSpeechWord object to the words list in the output.

        Args:
            entry (TextToSpeechWord): The word to be appended to the output.
        """
        self.words.append(entry)
