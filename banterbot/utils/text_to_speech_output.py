import time
from typing import Iterator

from banterbot.utils.text_to_speech_word import TextToSpeechWord


class TextToSpeechOutput:
    """
    Represents the output of a text-to-speech conversion.
    """

    def __init__(self, input_string: str) -> None:
        """
        Initializes the TextToSpeechOutput object.

        Args:
            input_string: The input string to be converted to speech.
        """
        self.input_string = input_string
        self.words = []
        self.is_active = False

    def __getitem__(self, idx: int) -> TextToSpeechWord:
        """
        Retrieves a TextToSpeechWord at the specified index.

        Args:
            idx: The index of the word to retrieve.

        Returns:
            The TextToSpeechWord at the specified index.
        """
        return self.words[idx]

    def __iter__(self) -> Iterator[TextToSpeechWord]:
        """
        Returns an iterator over the TextToSpeechWord objects in the output.

        Yields:
            TextToSpeechWord: The next TextToSpeechWord object in the output.
        """
        for word in self.words:
            yield word

    def __len__(self) -> int:
        """
        Returns the length of the word list.

        Returns:
            The length of the word list as an integer.
        """
        return len(self.words)

    def __setitem__(self, idx: int, value: TextToSpeechWord) -> None:
        """
        Sets the value of a TextToSpeechWord at the specified index.

        Args:
            idx: The index of the word to set.
            value: The new TextToSpeechWord value.
        """
        self.words[idx] = value

    def __str__(self) -> str:
        """
        Returns a string representation of the text-to-speech output.

        Returns:
            The concatenated string of all the words in the output.
        """
        return "".join([word.word for word in self.words])

    def append(self, entry: TextToSpeechWord) -> None:
        """
        Appends a TextToSpeechWord to the output.

        Args:
            entry: The TextToSpeechWord object to append.
        """
        self.words.append(entry)

    def stop(self) -> None:
        """
        Stops the TextToSpeechOutput process and indicates that it has ended. It is essential to call this method at the
        end of the output process; otherwise, the `fetch` method will run indefinitely.
        """
        self.is_active = False

    def stream(self) -> Iterator[TextToSpeechWord]:
        """
        Provides a stream of TextToSpeechWord objects from the output.

        Yields:
            TextToSpeechWord: The next TextToSpeechWord object in the output.
        """
        self.is_active = True
        N = 0
        while self.is_active:
            if self.__len__ > N:
                yield self.__getitem__(N)
                N += 1
            time.sleep(0.005)
