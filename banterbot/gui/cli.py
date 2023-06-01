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
        prog="BanterBot GUI",
        description=(
            "This program initializes a GUI that allows users to interact with a chatbot by entering a name and a "
            "message, and it displays the conversation history in a scrollable text area. Users can send messages by "
            "pressing the `Send` button or the `Enter` key. The chatbot's responses are generated using the specified "
            "OpenAI model and can be played back using the specified Azure Neural Voice. Additionally, users can "
            "toggle speech-to-text input by pressing the `Listen` button."
        ),
        epilog=(
            "Requires three environment variables for full functionality. "
            "1) OPENAI_API_KEY: A valid OpenAI API key,\n"
            "2) AZURE_SPEECH_KEY: A valid Azure Cognitive Services Speech API key for text-to-speech and "
            "speech-to-text functionality,\n"
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

    args=parser.parse_args()

    kwargs = {
        "model": get_model_by_name("gpt-4") if args.gpt4 else get_model_by_name("gpt-3.5-turbo"),
    }

    gui = BanterBotTK(**kwargs)
    gui.run()
