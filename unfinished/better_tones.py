import time

from banterbot.data.azure_neural_voices import get_voice_by_name
from banterbot.data.openai_models import get_model_by_name
from banterbot.extensions.prosody_selector import ProsodySelector
from banterbot.utils.phrase import Phrase


def create_ssml(phrases: list[Phrase]) -> str:
    """
    Creates a more advanced SSML string from the given list of `Phrase` instances, that customizes the emphasis,
    style, pitch, and rate of speech on a sub-sentence level.

    Args:
        phrases (list[Phrase]): Instances of class `Phrase` that contain data that can be converted into speech.
        voice (AzureNeuralVoice): The voice to be used.

    Returns:
        str: The SSML string.
    """
    # Start the SSML string with the required header and voice tag
    ssml = (
        '<speak version="1.0" '
        'xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="https://www.w3.org/2001/mstts" '
        'xml:lang="en-US">'
    )

    # Loop through each text in the list
    for phrase in phrases:
        ssml += f'<voice name="{phrase.voice.voice}">'
        # Add the express-as tag with the style and styledegree
        ssml += f'<mstts:express-as style="{phrase.style}" styledegree="{phrase.styledegree}">'
        # Add the prosody tag with the pitch, rate, and emphasis
        ssml += f'<prosody pitch="{phrase.pitch}" rate="{phrase.rate}">'
        # Add the emphasis tag
        ssml += f'<emphasis level="{phrase.emphasis}">'
        # Add the text
        ssml += phrase.text
        # Close the emphasis, prosody, and express-as tags
        ssml += "</emphasis></prosody></mstts:express-as></voice>"

    # Close the voice and speak tags and return the SSML string
    ssml += "</speak>"
    return ssml


if __name__ == "__main__":
    voice = get_voice_by_name("Tony")
    model = get_model_by_name("gpt-3.5-turbo")

    selector = ProsodySelector(model=model, voice=voice)
    t0 = time.perf_counter_ns()
    output = selector.select(
        # ["Wait, don't shoot! Oh it's you, Bud!", "I thought I was a goner for sure!", "Fuck you, dude!"]
        # ["Oh my god, that is hilarious! I can't believe you said that. What did he say to his wife?"]
        ["So in conclusion, the most efficient way to tackle the problem is: head on. What do you think?"]
    )
    t1 = time.perf_counter_ns()
    print(1e-9 * (t1 - t0))

    ssml = create_ssml(output)
    ssml = ssml.replace("en-US-TonyNeural", "Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)")
    print(ssml)
