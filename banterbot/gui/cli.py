import argparse

from banterbot.data.openai_models import openai_models
from banterbot.gui.banter_bot_tk import BanterBotTK


def run() -> None:
    """
    The main function to run the BanterBot Command Line Interface.

    This function parses command line arguments, sets up the necessary configurations, and initializes the BanterBotTK
    graphical user interface for user interaction.
    """
    parser = argparse.ArgumentParser(
        prog="BanterBot Command Line Interface",
        description=(
            "This program defines an interface for a text-based conversational agent based on the Persona class. The "
            "program uses the termighty library to create a graphical user interface for user interaction and handles "
            "input and output processing, as well as text-to-speech synthesis."
        ),
        epilog=(
            "Requires three environment variables for full functionality. "
            "1) OPENAI_API_KEY: A valid OpenAI API key, "
            "2) AZURE_SPEECH_KEY: A valid Azure Cognitive Services Speech API key for TTS functionality, and "
            "3) AZURE_SPEECH_REGION: The region associated with your Azure Cognitive Services Speech API key."
        ),
    )

    parser.add_argument(
        "-u",
        "--username",
        type=str,
        dest="username",
        help="The name of the program's user, only one word without spaces is allowed.",
    )

    parser.add_argument(
        "-c",
        "--character",
        type=str,
        dest="character",
        help=(
            "A name and/or short description of the character Persona should emulate. For best results, use the "
            'second-person singular to describe the character, in the form "<name> from <context>, <details>".'
        ),
    )

    parser.add_argument(
        "-g",
        "--gpt4",
        action="store_true",
        dest="gpt4",
        help="Enable GPT-4; only works if you have GPT-4 API access.",
    )

    args = parser.parse_args()

    kwargs = {
        # "username": args.username,
        # "character": args.character,
        "model": openai_models["gpt-4"]
        if args.gpt4
        else openai_models["gpt-3.5-turbo"],
    }

    print("Loading...")
    gui = BanterBotTK(**kwargs)
    gui.run()
