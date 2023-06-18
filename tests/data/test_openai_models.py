import unittest
from unittest.mock import patch

from banterbot.data.openai_models import OpenAIModel, get_model_by_name


class TestOpenAIModel(unittest.TestCase):
    """
    This test suite includes tests for the `OpenAIModel` class and the `get_model_by_name` function. The
    `TestOpenAIModel` class tests the creation of an `OpenAIModel` instance and the post-initialization method that sets
    the tokenizer attribute. The `TestGetModelByName` class tests the retrieval of a valid model by name and the
    handling of an invalid model name.
    """

    def test_openai_model_creation(self):
        model = OpenAIModel(name="gpt-3.5-turbo", max_tokens=4097, version=3, rank=2)
        self.assertEqual(model.name, "gpt-3.5-turbo")
        self.assertEqual(model.max_tokens, 4097)
        self.assertEqual(model.version, 3)
        self.assertEqual(model.rank, 2)
        self.assertIsNotNone(model.tokenizer)

    def test_openai_model_post_init(self):
        with patch("tiktoken.encoding_for_model") as mock_encoding_for_model:
            model = OpenAIModel(name="gpt-3.5-turbo", max_tokens=4097, version=3, rank=2)
            mock_encoding_for_model.assert_called_once_with("gpt-3.5-turbo")


class TestGetModelByName(unittest.TestCase):
    def test_get_model_by_name_valid(self):
        model = get_model_by_name("gpt-3.5-turbo")
        self.assertIsInstance(model, OpenAIModel)
        self.assertEqual(model.name, "gpt-3.5-turbo")

    def test_get_model_by_name_invalid(self):
        with self.assertRaises(KeyError):
            get_model_by_name("invalid-model-name")


if __name__ == "__main__":
    unittest.main()
