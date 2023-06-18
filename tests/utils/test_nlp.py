import unittest

from banterbot.utils.nlp import NLP


class TestNLP(unittest.TestCase):
    """
    This test suite includes four test cases for the NLP class:

        1. `test_segment_sentences`: Tests the `segment_sentences` method by checking if the input text is correctly
            split into individual sentences.
        2. `test_segment_words`: Tests the `segment_words` method by checking if the input text is correctly split into
            individual words.
        3. `test_extract_keywords`: Tests the `extract_keywords` method by checking if the correct keywords are
            extracted from the input text.
        4. `test_tokenize`: Tests the `tokenize` method by checking if the input list of strings is correctly tokenized.

    The `setUp` method is used to define a sample text that can be used in multiple test cases for conciseness.
    """

    def setUp(self):
        self.text = "This is a test sentence. It's a beautiful day! Let's go for a walk."

    def test_segment_sentences(self):
        sentences = NLP.segment_sentences(self.text)
        expected_sentences = ("This is a test sentence. ", "It's a beautiful day! ", "Let's go for a walk.")
        self.assertEqual(sentences, expected_sentences)

    def test_segment_words(self):
        words = NLP.segment_words(self.text, whitespace=False)
        expected_words = (
            "This",
            "is",
            "a",
            "test",
            "sentence",
            ".",
            "It",
            "'s",
            "a",
            "beautiful",
            "day",
            "!",
            "Let",
            "'s",
            "go",
            "for",
            "a",
            "walk",
            ".",
        )
        self.assertEqual(words, expected_words)

    def test_extract_keywords(self):
        text = ["Apple Inc. is an American multinational technology company headquartered in Cupertino, California."]
        keywords = NLP.extract_keywords(text)
        expected_keywords = (("Apple Inc.", "American", "Cupertino", "California"),)
        self.assertEqual(keywords, expected_keywords)

    def test_tokenize(self):
        strings = ["This is a test.", "Another test sentence."]
        tokens = list(NLP.tokenize(strings))
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].text, "This is a test.")
        self.assertEqual(tokens[1].text, "Another test sentence.")


if __name__ == "__main__":
    unittest.main()
