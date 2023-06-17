import logging
from typing import Generator, List, Tuple

import spacy

from banterbot.data.enums import SpaCyLangModel


class NLP:
    """
    A comprehensive toolkit that provides a set of Natural Language Processing utilities. It leverages the capabilities
    of the SpaCy package. The toolkit is designed to automatically download the necessary models if they are not
    available.

    One of the main features of this toolkit is the intelligent model selection mechanism. It is designed to select the
    most appropriate and lightweight model for each specific task, balancing between computational efficiency and task
    performance.
    """

    @classmethod
    def _init_models(cls) -> None:
        """
        Initializes and configures the required SpaCy models for sentence segmentation and keyword extraction.
        This method is called upon import to ensure that the necessary models are available and configured.
        """
        cls._models = {}

        # Define a set of pipeline components to disable for the sentence senter.
        senter_disable = ["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"]
        senter = cls._load_model(name=SpaCyLangModel.EN_CORE_WEB_SM.value, disable=senter_disable)
        # Enable the sentence segmentation pipeline component for the senter model.
        senter.enable_pipe("senter")

        rules = {}
        splitter = cls._load_model(name=SpaCyLangModel.EN_CORE_WEB_MD.value)
        # Customize the tokenization rules for the word splitter in order to prevent splitting of contractions.
        ignore = ("'", "’", "‘")
        for key, value in splitter.tokenizer.rules.items():
            if all(i not in key for i in ignore):
                rules[key] = value
        splitter.tokenizer.rules = rules

        logging.debug("NLP initializing model: `senter`")
        cls._models["senter"] = senter
        logging.debug("NLP initializing model: `splitter`")
        cls._models["splitter"] = splitter
        logging.debug(f"NLP initializing model: `{SpaCyLangModel.EN_CORE_WEB_MD.value}`")
        cls._models[SpaCyLangModel.EN_CORE_WEB_MD.value] = cls._load_model(name=SpaCyLangModel.EN_CORE_WEB_MD.value)
        logging.debug(f"NLP initializing model: `{SpaCyLangModel.EN_CORE_WEB_LG.value}`")
        cls._models[SpaCyLangModel.EN_CORE_WEB_LG.value] = cls._load_model(name=SpaCyLangModel.EN_CORE_WEB_LG.value)

    @classmethod
    def _load_model(cls, *, name: str, **kwargs) -> spacy.language.Language:
        """
        Loads a SpaCy model by its name.

        Args:
            name (str): The name of the SpaCy model to load.
            **kwargs: Additional keyword arguments for the spacy.load function.

        Returns:
            spacy.language.Language: The loaded SpaCy model.
        """
        model = spacy.load(name, **kwargs)
        return model

    @classmethod
    def model(cls, name: str) -> spacy.language.Language:
        """
        Returns the specified SpaCy model.

        Args:
            name (str): The name of the SpaCy model to return.

        Returns:
            spacy.language.Language: The requested SpaCy model.
        """
        return cls._models[name]

    @classmethod
    def segment_sentences(cls, string: str, whitespace: bool = True) -> Tuple[str, ...]:
        """
        Splits a text string into individual sentences using a specialized SpaCy model. The model is a lightweight
        version of `en_core_web_sm` designed specifically for sentence segmentation.

        Args:
            string (str): The input text string.
            whitespace (str): If True, keep whitespace at the beginning/end of sentences; if False, strip it.

        Returns:
            Tuple[str, ...]: A tuple of individual sentences as strings.
        """
        return tuple(
            sentence.text_with_ws if whitespace else sentence.text for sentence in cls._models["senter"](string).sents
        )

    @classmethod
    def segment_words(cls, string: str, whitespace: bool = True) -> Tuple[str, ...]:
        """
        Splits a text string into individual words using a specialized SpaCy model. The model is customized version of
        `en_core_web_md` in which words are not split on apostrophes, in order to preserve contractions.

        Args:
            string (str): The input text string.
            whitespace (str): If True, include whitespace characters between words; if False, omit it.

        Returns:
            Tuple[str, ...]: A tuple of individual words as strings.
        """
        words = []
        for word in cls._models["splitter"](string):
            words.append(word.text)
            if whitespace and word.whitespace_:
                words.append(word.whitespace_)

        return tuple(words)

    @classmethod
    def extract_keywords(cls, string: str) -> Tuple[str, ...]:
        """
        Extracts keywords from a text string using the `en_core_web_md` SpaCy model.

        Args:
            string (str): The input text string.

        Returns:
            Tuple[str, ...]: A tuple of extracted keywords as strings.
        """
        return tuple([str(entity) for entity in cls._models[SpaCyLangModel.EN_CORE_WEB_MD.value](string).ents])

    @classmethod
    def tokenize(cls, strings: List[str]) -> Generator[spacy.tokens.doc.Doc, None, None]:
        """
        Given a string or list of strings, returns tokenized versions of the strings as a generator.

        Args:
            strings (List[str]): A list of strings.

        Returns:
            Generator[spacy.tokens.doc.Doc, None, None]: A stream of `spacy.tokens.doc.Doc` instances.
        """
        return cls._models[SpaCyLangModel.EN_CORE_WEB_LG.value].pipe(strings)


NLP._init_models()
