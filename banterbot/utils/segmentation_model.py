import spacy

from banterbot.data.constants import EN_CORE_WEB_SM


class SegmentationModel:
    """
    A specialized configuration of SpaCy's `en_core_web_sm` model that is lightweight and only performs sentence
    segmentation. Automatically downloads the `en_core_web_sm` model if it is not found.
    """

    # Initialize the SpaCy NLP sentence splitting model only once as a class attribute to conserve resources.
    try:
        # Initialize the SpaCy model for English.
        _nlp = spacy.load(EN_CORE_WEB_SM, disable=["tagger", "attribute_ruler", "lemmatizer"])
    except OSError:
        # If the model isn't downloaded, download it.
        print(f'Downloading SpaCy language model: "{EN_CORE_WEB_SM}". This will only happen once.\n\n\n')
        spacy.cli.download(EN_CORE_WEB_SM)
        print(f'\n\n\nDownload of "{EN_CORE_WEB_SM}" Complete.')

        # Reattempt initialization of the SpaCy model.
        _nlp = spacy.load(EN_CORE_WEB_SM, disable=["tagger", "attribute_ruler", "lemmatizer"])

    # Since we only need SpaCy to split sentences, we disable the parser pipe to improve performance.
    _nlp.disable_pipe("parser")
    _nlp.enable_pipe("senter")

    @classmethod
    def split(cls, string: str) -> list[str, ...]:
        """
        Split a string into a list of sentences using the SpaCy NLP model.

        Args:
            string (str): The string of text to split.

        Returns:
            list[str, ...]: A list of individual sentences.
        """
        sentences = [str(sentence) for sentence in self.__class__._nlp(string).sents]
        return sentences
