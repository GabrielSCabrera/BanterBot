import argparse

from banterbot.data.openai_models import get_model_by_name
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
        "-g",
        "--gpt4",
        action="store_true",
        dest="gpt4",
        help="Enable GPT-4; only works if you have GPT-4 API access.",
    )

    kwargs = {
        "model": get_model_by_name("gpt-4") if args.gpt4 else get_model_by_name("gpt-3.5-turbo"),
    }

    gui = BanterBotTK(**kwargs)
    gui.run()
