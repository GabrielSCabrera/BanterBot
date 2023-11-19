import argparse
import logging

from banterbot.data.enums import Prosody, ToneMode
from banterbot.gui.tk_multiplayer_interface import TKMultiplayerInterface
from banterbot.managers.azure_neural_voice_manager import AzureNeuralVoiceManager
from banterbot.managers.openai_model_manager import OpenAIModelManager


def run() -> None:
    """
    The main function to run the BanterBot Command Line Interface.

    This function parses command line arguments, sets up the necessary configurations, and initializes the BanterBotTK
    graphical user interface for user interaction.
    """
    parser = argparse.ArgumentParser(
        prog="BanterBot GUI",
        description=(
            "This program initializes a GUI that allows users to interact with a chatbot. The user can enter multiple "
            "names, each with a dedicated button on its right. When holding down the button associated with a given "
            "name, the user can speak into their microphone and their prompt will be sent to the bot for a response. "
            "If this does not work, keep the button down until your text is visualized in the scrollable text area."
            "The chatbot's responses are generated using the specified OpenAI model and will be played back using the "
            "specified Azure Neural Voice."
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

    class ModelChoice(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, OpenAIModelManager.load(values.lower()))

    parser.add_argument(
        "-m",
        "--model",
        choices=OpenAIModelManager.list(),
        action=ModelChoice,
        default=OpenAIModelManager.load("gpt-4-turbo"),
        dest="model",
        help="Select the OpenAI model the bot should use.",
    )

    class ToneModeChoice(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            conversion_table = {
                "NONE": ToneMode.NONE,
                "BASIC": ToneMode.BASIC,
                "ADVANCED": ToneMode.ADVANCED,
            }
            setattr(namespace, self.dest, conversion_table[values.upper()])

    parser.add_argument(
        "-t",
        "--tone-mode",
        choices=["NONE", "BASIC", "ADVANCED"],
        action=ToneModeChoice,
        default=ToneMode.ADVANCED,
        dest="tone_mode",
        help="Set the emotional tone evaluation mode for the bot's responses.",
    )

    class VoiceChoice(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, AzureNeuralVoiceManager.load(values.lower()))

    parser.add_argument(
        "-v",
        "--voice",
        choices=AzureNeuralVoiceManager.list(),
        action=VoiceChoice,
        default=AzureNeuralVoiceManager.load("aria"),
        dest="voice",
        help=f"Select a Microsoft Azure Cognitive Services text-to-speech voice.",
    )

    parser.add_argument(
        "-s",
        "--style",
        choices=Prosody.STYLES,
        action="store",
        default="friendly",
        dest="style",
        help=(
            "ONLY WORKS IF --tone-mode=NONE. Select a Microsoft Azure Cognitive Services text-to-speech voice style. "
            f"Universally available styles across all available voices are: {Prosody.STYLES}. Some voices may have "
            "more available styles, see `/banterbot/data/azure_neural_voices.py` for more options."
        ),
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        help="Enable debug mode, which will echo a number of hidden processes to the terminal.",
    )

    parser.add_argument(
        "-g",
        "--greet",
        action="store_true",
        dest="greet",
        help="Greet the user on initialization.",
    )

    parser.add_argument(
        "-n",
        "--name",
        action="store",
        type=str,
        dest="name",
        help=(
            "Give the assistant a name; only for aesthetic purposes, the bot is not informed. Instead, use `--prompt` "
            "if you wish to provide it with information."
        ),
    )

    args = parser.parse_args()

    kwargs = {
        "model": args.model,
        "voice": args.voice,
        "style": args.style,
        "system": args.prompt,
        "tone_mode": args.tone_mode,
        "assistant_name": args.name,
    }

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    interface = TKMultiplayerInterface(**kwargs)
    interface.run(greet=args.greet)
