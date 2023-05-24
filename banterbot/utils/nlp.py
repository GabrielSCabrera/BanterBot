import spacy

from banterbot.data.constants import EN_CORE_WEB_SM, EN_CORE_WEB_MD


class NLP:
    """
    A comprehensive toolkit featuring a set of Natural Language Processing utilities, powered by the SpaCy package.

    The toolkit is designed to automatically download the necessary models, thus simplifying the initial setup for
    users. A unique feature of this toolkit is its intelligent model selection algorithm. This algorithm is programmed
    to automatically select the most lightweight and suitable model for each specific task, ensuring the perfect balance
    between speed and efficiency.

    With this automation, users are relieved from the task of manual model selection, allowing them to focus on
    achieving optimal operational efficiency with their NLP tasks.
    """

    @classmethod
    def _init_models(cls):
        cls._models = {}

        segmenter = cls._load_model(name=EN_CORE_WEB_SM, disable=["tagger", "attribute_ruler", "lemmatizer"])
        segmenter.disable_pipe("parser")
        segmenter.enable_pipe("senter")

        cls._models["segmenter"] = segmenter
        cls._models[EN_CORE_WEB_MD] = cls._load_model(name=EN_CORE_WEB_MD)

    @classmethod
    def _load_model(cls, *, name: str, **kwargs) -> spacy.language.Language:
        # Initialize the SpaCy NLP sentence splitting model only once as a class attribute to conserve resources.
        try:
            # Initialize the SpaCy model for English.
            model = spacy.load(name, **kwargs)
        except OSError:
            # If the model isn't downloaded, download it.
            cls._download_model(name)
            # Reattempt initialization of the SpaCy model.
            model = spacy.load(name, **kwargs)
        return model

    @classmethod
    def _download_model(cls, name: str) -> None:
        """
        Download the specified language model, and let the user know that the model is being downloaded.
        """
        print(f'Downloading SpaCy language model: "{name}". This will only happen once.\n\n\n')
        spacy.cli.download(EN_CORE_WEB_SM)
        print(f'\n\n\nFinished download of SpaCy language model: "{name}".')

    @classmethod
    def model(cls, name: str) -> spacy.language.Language:
        """
        Returns the specified SpaCy model directly.
        """
        return self._models[name]

    @classmethod
    def segment_sentences(cls, string: str) -> tuple[str, ...]:
        """
        Split a string into a list of sentences using a specialized configuration of SpaCy's `en_core_web_sm` model that
        is lightweight and exclusively performs sentence segmentation.

        Args:
            string (str): The string of text to split.

        Returns:
            tuple[str, ...]: A list of individual sentences.
        """
        return tuple([str(sentence) for sentence in cls._models["segmenter"](string).sents])

    @classmethod
    def extract_keywords(cls, string: str) -> tuple[str, ...]:
        """
        Extracts a set of relevant keywords from a string of text.
        """
        return cls._models[EN_CORE_WEB_MD](string).ents


# SpacyUtils should initialize (and if need be, download) all models *once* on import
SpacyUtils._init_models()
