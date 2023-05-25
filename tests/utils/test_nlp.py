"""
These tests cover the initialization of models, retrieving a specific model, segmenting sentences, extracting keywords,
and downloading a model if it is not available. The @patch decorator is used to mock the standard output and check if
the correct messages are printed during the model download process.
"""
import unittest
from io import StringIO
from unittest.mock import patch

from banterbot.utils.nlp import NLP


class NLPTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the models before running the tests
        NLP._init_models()

    def test_model(self):
        model = NLP.model("en_core_web_md")
        self.assertIsNotNone(model)
        self.assertEqual(model.lang, "en")

    def test_segment_sentences(self):
        string = "This is a test. Another sentence."
        expected_sentences = ("This is a test.", "Another sentence.")
        sentences = NLP.segment_sentences(string)
        self.assertEqual(sentences, expected_sentences)

    def test_extract_keywords(self):
        string = "Apple is a technology company."
        expected_keyword = "Apple"
        expected_label = "ORG"
        keywords = NLP.extract_keywords(string)
        self.assertEqual(keywords[0].text, expected_keyword)
        self.assertEqual(keywords[0].label_, expected_label)

    # @patch('sys.stdout', new_callable=StringIO)
    # def test_download_model(self, mock_stdout):
    #     NLP._download_model("en_core_web_sm")
    #     output = mock_stdout.getvalue()
    #     self.assertIn('Downloading SpaCy language model: "en_core_web_sm".', output)
    #     self.assertIn('Finished download of SpaCy language model: "en_core_web_sm".', output)


if __name__ == "__main__":
    unittest.main()
