from gptbot import GPTBot


class Character(GPTBot):
    def __init__(
        self,
        model: Optional[str] = None,
        character: Optional[str] = None,
        random_character: bool = False,
        user_name: Optional[str] = None,
    ):
        """ """
        super().__init__()
