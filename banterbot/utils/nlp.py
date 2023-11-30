import logging
from typing import Generator

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

    _models = {
        "senter": None,
        "splitter": None,
        SpaCyLangModel.EN_CORE_WEB_SM: None,
        SpaCyLangModel.EN_CORE_WEB_MD: None,
        SpaCyLangModel.EN_CORE_WEB_LG: None,
    }

    @classmethod
    def install_all_models(cls) -> None:
        """
        Lazily checks if models are already installed, and installs any that are missing.
        """
        installed = spacy.util.get_installed_models()
        for model in SpaCyLangModel:
            if model.value not in installed:
                cls._download_model(model.value)

    @classmethod
    def load_all_models(cls) -> None:
        """
        Preloads all available models.
        """
        for model in cls._models:
            cls.model(model)

    @classmethod
    def model(cls, name: str) -> spacy.language.Language:
        """
        Returns the specified SpaCy model lazily by loading models the first time they are called, then storing them in
        the `cls._models` dictionary.

        Args:
            name (str): The name of the SpaCy model to return.

        Returns:
            spacy.language.Language: The requested SpaCy model.
        """
        if name == "senter" and cls._models["senter"] is None:
            # Define a set of pipeline components to disable for the sentence senter.
            senter_disable = ["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"]
            senter = cls._load_model(name=SpaCyLangModel.EN_CORE_WEB_SM.value, disable=senter_disable)
            # Enable the sentence segmentation pipeline component for the senter model.
            senter.enable_pipe("senter")

            logging.debug("NLP initializing model: `senter`")
            cls._models["senter"] = senter

        elif name == "splitter" and cls._models["splitter"] is None:
            rules = {}
            splitter = cls._load_model(name=SpaCyLangModel.EN_CORE_WEB_MD.value)
            # Customize the tokenization rules for the word splitter in order to prevent splitting of contractions.
            ignore = ("'", "’", "‘")
            for key, value in splitter.tokenizer.rules.items():
                if all(i not in key for i in ignore):
                    rules[key] = value
            splitter.tokenizer.rules = rules
            logging.debug("NLP initializing model: `splitter`")
            cls._models["splitter"] = splitter

        elif name == SpaCyLangModel.EN_CORE_WEB_SM and cls._models[SpaCyLangModel.EN_CORE_WEB_SM] is None:
            logging.debug(f"NLP initializing model: `{SpaCyLangModel.EN_CORE_WEB_SM.value}`")
            cls._models[SpaCyLangModel.EN_CORE_WEB_SM] = cls._load_model(name=SpaCyLangModel.EN_CORE_WEB_SM.value)

        elif name == SpaCyLangModel.EN_CORE_WEB_MD and cls._models[SpaCyLangModel.EN_CORE_WEB_MD] is None:
            logging.debug(f"NLP initializing model: `{SpaCyLangModel.EN_CORE_WEB_MD.value}`")
            cls._models[SpaCyLangModel.EN_CORE_WEB_MD] = cls._load_model(name=SpaCyLangModel.EN_CORE_WEB_MD.value)

        elif name == SpaCyLangModel.EN_CORE_WEB_LG and cls._models[SpaCyLangModel.EN_CORE_WEB_LG] is None:
            logging.debug(f"NLP initializing model: `{SpaCyLangModel.EN_CORE_WEB_LG.value}`")
            cls._models[SpaCyLangModel.EN_CORE_WEB_LG] = cls._load_model(name=SpaCyLangModel.EN_CORE_WEB_LG.value)

        return cls._models[name]

    @classmethod
    def segment_sentences(cls, string: str, whitespace: bool = True) -> tuple[str, ...]:
        """
        Splits a text string into individual sentences using a specialized SpaCy model. The model is a lightweight
        version of `en_core_web_sm` designed specifically for sentence segmentation.

        Args:
            string (str): The input text string.
            whitespace (str): If True, keep whitespace at the beginning/end of sentences; if False, strip it.

        Returns:
            tuple[str, ...]: A tuple of individual sentences as strings.
        """
        return tuple(
            sentence.text_with_ws if whitespace else sentence.text for sentence in cls.model("senter")(string).sents
        )

    @classmethod
    def segment_words(cls, string: str, whitespace: bool = True) -> tuple[str, ...]:
        """
        Splits a text string into individual words using a specialized SpaCy model. The model is customized version of
        `en_core_web_md` in which words are not split on apostrophes, in order to preserve contractions.

        Args:
            string (str): The input text string.
            whitespace (str): If True, include whitespace characters between words; if False, omit it.

        Returns:
            tuple[str, ...]: A tuple of individual words as strings.
        """
        words = []
        for word in cls.model("splitter")(string):
            words.append(word.text)
            if whitespace and word.whitespace_:
                words.append(word.whitespace_)

        return tuple(words)

    @classmethod
    def extract_keywords(cls, strings: list[str]) -> tuple[tuple[str, ...]]:
        """
        Extracts keywords from a list of text strings using the `en_core_web_md` SpaCy model.

        Args:
            strings (list[str]): A list of strings.

        Returns:
            tuple[str, ...]: A tuple of extracted keywords as strings.
        """
        docs = cls.model(SpaCyLangModel.EN_CORE_WEB_MD).pipe(strings)
        return tuple(tuple(str(entity) for entity in doc.ents) for doc in docs)

    @classmethod
    def tokenize(cls, strings: list[str]) -> Generator[spacy.tokens.doc.Doc, None, None]:
        """
        Given a string or list of strings, returns tokenized versions of the strings as a generator.

        Args:
            strings (list[str]): A list of strings.

        Returns:
            Generator[spacy.tokens.doc.Doc, None, None]: A stream of `spacy.tokens.doc.Doc` instances.
        """
        return cls.model(SpaCyLangModel.EN_CORE_WEB_LG).pipe(strings)

    @classmethod
    def _download_model(cls, name: str) -> None:
        """
        Downloads a SpaCy model by its name. It also provides information about the download process to the user.

        Args:
            name (str): The name of the SpaCy model to download.
        """
        logging.info(f'Downloading SpaCy language model: "{name}". This will only happen once.\n\n\n')
        spacy.cli.download(name)
        logging.info(f'\n\n\nFinished download of SpaCy language model: "{name}".')

    @classmethod
    def _load_model(cls, *, name: str, **kwargs) -> spacy.language.Language:
        """
        Loads a SpaCy model by its name. If the model is not available, it is downloaded automatically.

        Args:
            name (str): The name of the SpaCy model to load.
            **kwargs: Additional keyword arguments for the spacy.load function.

        Returns:
            spacy.language.Language: The loaded SpaCy model.
        """
        try:
            model = spacy.load(name, **kwargs)
        except OSError:
            cls._download_model(name)
            model = spacy.load(name, **kwargs)
        return model


# Upon import, NLP downloads any missing required models.
NLP.install_all_models()
