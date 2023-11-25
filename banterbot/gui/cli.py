import argparse
import logging
import textwrap

from banterbot.data.enums import Prosody, ToneMode
from banterbot.gui.tk_multiplayer_interface import TKMultiplayerInterface
from banterbot.managers.azure_neural_voice_manager import AzureNeuralVoiceManager
from banterbot.managers.openai_model_manager import OpenAIModelManager


class CustomHelpFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        text = textwrap.dedent(text)
        text = textwrap.indent(text, indent)
        text = text.splitlines()
        text = [textwrap.fill(line, width) for line in text]
        text = "\n".join(text)
        return text


def voice_search() -> None:
    """
    An extra tool that can be used to search through the available Azure Cognitive Services Neural Voices.
    """
    parser = argparse.ArgumentParser(
        prog="BanterBot Voice Search",
        usage="%(prog)s [options]",
        description=(
            "Use this tool to search through available Azure Cognitive Services Neural Voices using the provided "
            "search parameters (country, gender, language, region). For more information visit:\n"
            "https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts"
        ),
        epilog=(
            "Requires two environment variables for voice search:\n"
            "\n1) AZURE_SPEECH_KEY: A valid Azure Cognitive Services Speech API key for text-to-speech and "
            "speech-to-text functionality,"
            "\n2) AZURE_SPEECH_REGION: The region associated with your Azure Cognitive Services Speech API key."
        ),
        formatter_class=CustomHelpFormatter,
    )

    parser.add_argument(
        "--country",
        action="store",
        choices=AzureNeuralVoiceManager.list_countries(),
        dest="country",
        help="Filter by country code.",
        nargs="*",
        type=str,
    )

    parser.add_argument(
        "--gender",
        action="store",
        choices=AzureNeuralVoiceManager.list_genders(),
        dest="gender",
        help="Filter by country code.",
        nargs="*",
        type=str,
    )

    parser.add_argument(
        "--language",
        action="store",
        choices=AzureNeuralVoiceManager.list_languages(),
        dest="language",
        help="Filter by language code.",
        nargs="*",
        type=str,
    )

    parser.add_argument(
        "--region",
        action="store",
        choices=AzureNeuralVoiceManager.list_regions(),
        dest="region",
        help="Filter by region name.",
        nargs="*",
        type=str,
    )

    parser.add_argument(
        "--style",
        action="store",
        choices=AzureNeuralVoiceManager.list_styles(),
        dest="style",
        help="Filter by voice style.",
        nargs="*",
        type=str,
    )

    args = parser.parse_args()
    kwargs = {
        "gender": args.gender,
        "language": args.language,
        "country": args.country,
        "region": args.region,
        "style": args.style,
    }

    search_results = sorted(AzureNeuralVoiceManager.search(**kwargs), key=lambda x: x.name)
    for voice in search_results:
        print(voice, end="\n\n")


def run() -> None:
    """
    The main function to run the BanterBot Command Line Interface.

    This function parses command line arguments, sets up the necessary configurations, and initializes the BanterBotTK
    graphical user interface for user interaction.
    """
    parser = argparse.ArgumentParser(
        prog="BanterBot GUI",
        usage="%(prog)s [options]",
        description=(
            "This program initializes a GUI that allows users to interact with a chatbot. The user can enter multiple "
            "names, each with a dedicated button on its right. When holding down the button associated with a given "
            "name, the user can speak into their microphone and their prompt will be sent to the bot for a response. "
            "If this does not work, keep the button down until your text is visualized in the scrollable text area."
            "The chatbot's responses are generated using the specified OpenAI model and will be played back using the "
            "specified Azure Neural Voice."
        ),
        epilog=(
            "Requires three environment variables for full functionality.\n"
            "\n1) OPENAI_API_KEY: A valid OpenAI API key,"
            "\n2) AZURE_SPEECH_KEY: A valid Azure Cognitive Services Speech API key for text-to-speech and "
            "speech-to-text functionality,"
            "\n3) AZURE_SPEECH_REGION: The region associated with your Azure Cognitive Services Speech API key."
        ),
        formatter_class=CustomHelpFormatter,
    )

    parser.add_argument(
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
        "--voice",
        action=VoiceChoice,
        default=AzureNeuralVoiceManager.load("aria"),
        dest="voice",
        help=(
            "Select a Microsoft Azure Cognitive Services text-to-speech voice. Use the included console script "
            "`banterbot-voice-search` to find a suitable voice for your BanterBot."
        ),
    )

    parser.add_argument(
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
        "--debug",
        action="store_true",
        dest="debug",
        help="Enable debug mode, which will echo a number of hidden processes to the terminal.",
    )

    parser.add_argument(
        "--greet",
        action="store_true",
        dest="greet",
        help="Greet the user on initialization.",
    )

    parser.add_argument(
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
