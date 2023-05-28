import spacy

from banterbot.data.constants import EN_CORE_WEB_MD, EN_CORE_WEB_SM


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
    def _init_models(cls):
        """
        Initializes and configures the required SpaCy models for sentence segmentation and keyword extraction.
        """
        cls._models = {}

        # Define a set of pipeline components to disable for the sentence segmenter.
        segmenter_disable = ["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"]
        segmenter = cls._load_model(name=EN_CORE_WEB_SM, disable=segmenter_disable)
        # Enable the sentence segmentation pipeline component for the segmenter model.
        segmenter.enable_pipe("senter")

        cls._models["segmenter"] = segmenter
        cls._models[EN_CORE_WEB_MD] = cls._load_model(name=EN_CORE_WEB_MD)

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

    @classmethod
    def _download_model(cls, name: str) -> None:
        """
        Downloads a SpaCy model by its name. It also provides information about the download process to the user.

        Args:
            name (str): The name of the SpaCy model to download.
        """
        print(f'Downloading SpaCy language model: "{name}". This will only happen once.\n\n\n')
        spacy.cli.download(name)
        print(f'\n\n\nFinished download of SpaCy language model: "{name}".')

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
    def segment_sentences(cls, string: str) -> tuple[spacy.tokens.span.Span, ...]:
        """
        Splits a text string into individual sentences using a specialized SpaCy model. The model is a lightweight version
        of `en_core_web_sm` designed specifically for sentence segmentation.

        Args:
            string (str): The input text string.

        Yields:
            tuple[spacy.tokens.span.Span, ...]: A tuple of individual sentences in the form of SpaCy Span objects.
        """
        return tuple(sentence.text_with_ws for sentence in cls._models["segmenter"](string).sents)

    @classmethod
    def extract_keywords(cls, string: str) -> tuple[str, ...]:
        """
        Extracts keywords from a text string using the `en_core_web_md` SpaCy model.

        Args:
            string (str): The input text string.

        Returns:
            tuple[str, ...]: A tuple of extracted keywords as strings.
        """
        return tuple([str(entity) for entity in cls._models[EN_CORE_WEB_MD](string).ents])


# Upon import, NLP initializes and downloads (if necessary) all models.
NLP._init_models()
