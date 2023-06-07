import argparse

from banterbot.data.azure_neural_voices import _neural_voices, get_voice_by_name
from banterbot.data.openai_models import get_model_by_name
from banterbot.gui.tk_multiplayer_interface import TKMultiplayerInterface
from banterbot.gui.tk_simple_interface import TKSimpleInterface


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
            "Requires three environment variables for full functionality."
            "1) OPENAI_API_KEY: A valid OpenAI API key,"
            "2) AZURE_SPEECH_KEY: A valid Azure Cognitive Services Speech API key for text-to-speech and "
            "speech-to-text functionality,"
            "3) AZURE_SPEECH_REGION: The region associated with your Azure Cognitive Services Speech API key."
        ),
    )

    parser.add_argument(
        "-p",
        "--prompt",
        action="store",
        type=str,
        dest="prompt",
        help="Adds a system prompt to the beginning of the conversation; can help to set the scene.",
    )

    parser.add_argument(
        "-g",
        "--gpt4",
        action="store_true",
        dest="gpt4",
        help="Enable GPT-4; only works if you have GPT-4 API access.",
    )

    parser.add_argument(
        "-m",
        "--multiplayer",
        action="store_true",
        dest="multiplayer",
        help="Enables the pre-release multiplayer interface; multiplayer is not fully implemented and may be buggy.",
    )

    parser.add_argument(
        "-e",
        "--emotion",
        action="store_true",
        dest="tone",
        help="Enables emotional tone evaluation prior to the bot's responses.",
    )

    voices = ", ".join(f"`{voice}`" for voice in _neural_voices.keys())
    parser.add_argument(
        "-v",
        "--voice",
        action="store",
        type=str,
        default="Aria",
        dest="voice",
        help=f"Select a Microsoft Azure Cognitive Services text-to-speech voice. Options are: {voices}",
    )

    universal_styles = [
        "angry",
        "cheerful",
        "excited",
        "friendly",
        "hopeful",
        "sad",
        "shouting",
        "terrified",
        "unfriendly",
        "whispering",
    ]
    universal_styles = ", ".join(f"`{style}`" for style in universal_styles)
    parser.add_argument(
        "-s",
        "--style",
        action="store",
        type=str,
        default="friendly",
        dest="style",
        help=(
            "Select a Microsoft Azure Cognitive Services text-to-speech voice style. Universally available styles "
            f"across all available voices are: {universal_styles}. Some voices may have more available styles, see "
            "`/banterbot/data/azure_neural_voices.py` for more information."
        ),
    )
    args = parser.parse_args()

    kwargs = {
        "model": get_model_by_name("gpt-4") if args.gpt4 else get_model_by_name("gpt-3.5-turbo"),
        "voice": get_voice_by_name(args.voice),
        "style": args.style,
        "system": args.prompt,
        "tone": args.tone,
    }

    if args.multiplayer:
        interface = TKMultiplayerInterface(**kwargs)
    else:
        interface = TKSimpleInterface(**kwargs)

    interface.run()
