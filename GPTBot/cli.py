import argparse
from gptbot.interface import Interface


def run():
    parser = argparse.ArgumentParser(
        prog="Persona Interface",
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
        "-m",
        "--mode",
        choices=["ChatCompletion", "Completion"],
        default="ChatCompletion",
        type=str,
        dest="mode",
        help="OpenAI API Selection. ChatCompletion is cheaper, but often not as good unless you have GPT-4 access.",
    )

    parser.add_argument(
        "-r",
        "--rand",
        "--random",
        action="store_true",
        dest="random",
        help='Override the "character" argument and have the program select a random character.',
    )

    parser.add_argument(
        "-n",
        "--no-thread",
        action="store_false",
        dest="nothread",
        help='Disable multithreading on initialization of Persona (can help with "Too Many Requests" exceptions).',
    )

    parser.add_argument(
        "-g",
        "--gpt4",
        action="store_true",
        dest="gpt4",
        help="Enable GPT-4; overrides --mode and --no-thread flag, and only works if you have GPT-4 API access.",
    )

    parser.add_argument(
        "-t",
        "--temp",
        "--temperature",
        type=float,
        dest="temperature",
        help="Set the model temperature.",
    )

    args = parser.parse_args()

    kwargs = {
        "username": args.username,
        "character": args.character,
        "mode": args.mode,
        "random_character": args.random,
        "thread_on_init": args.nothread,
        "gpt4": args.gpt4,
        "temperature": args.temperature,
    }

    print("Loading...")
    interface = Interface(**kwargs)
    interface.start()
