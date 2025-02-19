import argparse
import logging
import textwrap

from banterbot import characters
from banterbot.gui.tk_interface import TKInterface
from banterbot.managers.azure_neural_voice_manager import AzureNeuralVoiceManager
from banterbot.managers.openai_model_manager import OpenAIModelManager

character_choices = {
    "android": (characters.android, "Marvin the Paranoid Android"),
    "bartender": (characters.bartender, "Sagehoof the Centaur Mixologist"),
    "chef": (characters.chef, "Boyardine the Angry Chef"),
    "historian": (characters.historian, "Blabberlore the Gnome Historian"),
    "quiz": (characters.quiz, "Grondle the Quiz Troll"),
    "teacher-french": (characters.teacher_french, "Henri the French Teacher"),
    "teacher-mandarin": (characters.teacher_mandarin, "Chen Lao Shi the Mandarin Chinese Teacher"),
    "therapist": (characters.therapist, "Grendel the Therapy Troll"),
}


class CustomHelpFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        text = textwrap.dedent(text)
        text = textwrap.indent(text, indent)
        text = text.splitlines()
        text = [textwrap.fill(line, width) for line in text]
        text = "\n".join(text)
        return text


class ModelChoice(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, OpenAIModelManager.load(values.lower()))


class VoiceChoice(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, AzureNeuralVoiceManager.load(values.lower()))


def init_parser(subparser) -> None:
    subparser.add_argument(
        "--prompt",
        action="store",
        type=str.lower,
        dest="prompt",
        help="Adds a system prompt to the beginning of the conversation; can help to set the scene.",
    )

    subparser.add_argument(
        "--model",
        choices=OpenAIModelManager.list(),
        action=ModelChoice,
        default=OpenAIModelManager.load("gpt-4o-mini"),
        dest="model",
        help="Select the OpenAI model the bot should use.",
    )

    subparser.add_argument(
        "--voice",
        action=VoiceChoice,
        default=AzureNeuralVoiceManager.load("aria"),
        dest="voice",
        help="Select a Microsoft Azure Cognitive Services text-to-speech voice.",
    )

    subparser.add_argument(
        "--debug",
        action="store_true",
        dest="debug",
        help="Enable debug mode, which will echo a number of hidden processes to the terminal.",
    )

    subparser.add_argument(
        "--greet",
        action="store_true",
        dest="greet",
        help="Greet the user on initialization.",
    )

    subparser.add_argument(
        "--name",
        action="store",
        type=str.lower,
        dest="name",
        help=(
            "Give the assistant a name; only for aesthetic purposes, the bot is not informed. Instead, use `--prompt` "
            "if you wish to provide it with information."
        ),
    )


def init_subparser_character(subparser) -> None:
    character_descriptions = [i[1] for i in character_choices.values()]
    if len(character_descriptions) > 1:
        character_descriptions[-1] = f"or {character_descriptions[-1]}"

    character_descriptions = ", ".join(character_descriptions)
    subparser.add_argument(
        "character",
        action="store",
        choices=character_choices,
        help=f"Choose one of the available characters to interact with them: {character_descriptions}",
        type=str.lower,
    )


def init_subparser_voice_search(subparser) -> None:
    subparser.add_argument(
        "--country",
        action="store",
        choices=AzureNeuralVoiceManager.list_countries(),
        dest="country",
        help="Filter by country code.",
        nargs="*",
        type=str.lower,
    )

    subparser.add_argument(
        "--gender",
        action="store",
        choices=AzureNeuralVoiceManager.list_genders(),
        dest="gender",
        help="Filter by gender.",
        nargs="*",
        type=str.lower,
    )

    subparser.add_argument(
        "--language",
        action="store",
        choices=AzureNeuralVoiceManager.list_languages(),
        dest="language",
        help="Filter by language code.",
        nargs="*",
        type=str.lower,
    )

    subparser.add_argument(
        "--region",
        action="store",
        choices=AzureNeuralVoiceManager.list_regions(),
        dest="region",
        help="Filter by region name.",
        nargs="*",
        type=str.lower,
    )

    subparser.add_argument(
        "--style",
        action="store",
        choices=AzureNeuralVoiceManager.list_styles(),
        dest="style",
        help="Filter by voice style.",
        nargs="*",
        type=str.lower,
    )


def exec_main(args) -> None:
    kwargs = {
        "model": args.model,
        "voice": args.voice,
        "system": args.prompt,
        "assistant_name": args.name,
    }

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    interface = TKInterface(**kwargs)
    interface.run(greet=args.greet)


def exec_character(args) -> None:
    character = args.character.lower().strip()
    character_choices[character][0]()


def exec_voice_search(args) -> None:
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
        prog="BanterBot",
        usage="%(prog)s [options]",
        description=(
            "BanterBot is an OpenAI ChatGPT-powered chatbot with Azure Neural Voices. Supports speech-to-text and"
            " text-to-speech interactions. Create a custom BanterBot with the provided options, or use the"
            " `character` command to select a pre-loaded character. For custom BanterBots, use the `voice-search`"
            " command to see which voices are available."
        ),
        epilog=(
            "Requires three environment variables for full functionality.\n"
            "\n 1) OPENAI_API_KEY: A valid OpenAI API key,"
            "\n 2) AZURE_SPEECH_KEY: A valid Azure Cognitive Services Speech API key for text-to-speech and "
            "speech-to-text functionality,"
            "\n 3) AZURE_SPEECH_REGION: The region associated with your Azure Cognitive Services Speech API key."
        ),
        formatter_class=CustomHelpFormatter,
    )
    init_parser(parser)

    subparsers = parser.add_subparsers(required=False, dest="command")

    subparser_character = subparsers.add_parser(
        "character",
        prog="BanterBot Character Loader",
        usage="%(prog)s [options]",
        description="Select one of the pre-loaded BanterBot characters to begin a conversation.",
        formatter_class=CustomHelpFormatter,
        epilog=(
            "Requires three environment variables for full functionality.\n"
            "\n 1) OPENAI_API_KEY: A valid OpenAI API key,"
            "\n 2) AZURE_SPEECH_KEY: A valid Azure Cognitive Services Speech API key for text-to-speech and "
            "speech-to-text functionality,"
            "\n 3) AZURE_SPEECH_REGION: The region associated with your Azure Cognitive Services Speech API key."
        ),
    )

    init_subparser_character(subparser_character)

    subparser_voice_search = subparsers.add_parser(
        "voice-search",
        prog="BanterBot Voice Search",
        usage="%(prog)s [options]",
        description=(
            "Use this tool to search through available Azure Cognitive Services Neural Voices using the provided "
            "search parameters (country, gender, language, region). For more information visit:\n"
            "https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts"
        ),
        epilog=(
            "Requires two environment variables for voice search:\n"
            "\n 1) AZURE_SPEECH_KEY: A valid Azure Cognitive Services Speech API key for text-to-speech and "
            "speech-to-text functionality,"
            "\n 2) AZURE_SPEECH_REGION: The region associated with your Azure Cognitive Services Speech API key."
        ),
        formatter_class=CustomHelpFormatter,
    )

    init_subparser_voice_search(subparser_voice_search)

    args = parser.parse_args()

    if args.command == "character":
        exec_character(args)
    elif args.command == "voice-search":
        exec_voice_search(args)
    else:
        exec_main(args)


if __name__ == "__main__":
    run()
