from banterbot.data.azure_neural_voices import AzureNeuralVoice, get_voice_by_name
from banterbot.data.openai_models import get_model_by_name
from banterbot.extensions.prosody_selector import ProsodySelector


def create_ssml(
    texts: list, voice: AzureNeuralVoice, styles: list, styledegrees: list, pitches: list, rates: list, emphases: list
) -> str:
    """
    Creates an SSML string from the given list of texts, voice, styles, styledegrees, pitches, rates, and emphases.

    Args:
        texts (list): The list of input strings that are to be converted into speech.
        voice (AzureNeuralVoice): The voice to be used.
        styles (list): The list of speaking styles to be applied.
        styledegrees (list): The list of style degrees to be applied.
        pitches (list): The list of pitches to be applied.
        rates (list): The list of rates to be applied.
        emphases (list): The list of emphases to be applied.

    Returns:
        str: The SSML string.
    """
    # Start the SSML string with the required header and voice tag
    ssml = (
        '<speak version="1.0" '
        'xmlns="http://www.w3.org/2001/10/synthesis" '
        'xmlns:mstts="https://www.w3.org/2001/mstts" '
        'xml:lang="en-US">'
        f'<voice name="{voice.voice}">'
    )

    # Loop through each text in the list
    for n, (text, style, styledegree, pitch, rate, emphasis) in enumerate(
        zip(texts, styles, styledegrees, pitches, rates, emphases)
    ):
        # Add the express-as tag with the style and styledegree
        ssml += f'<mstts:express-as style="{style}" styledegree="{styledegree}">'
        # Add the prosody tag with the pitch, rate, and emphasis
        ssml += f'<prosody pitch="{pitches[i]}" rate="{rates[i]}">'
        # Add the emphasis tag
        ssml += f'<emphasis level="{emphases[i]}">'
        # Add the text
        ssml += texts[i]
        # Close the emphasis, prosody, and express-as tags
        ssml += "</emphasis></prosody></mstts:express-as>"

    # Close the voice and speak tags and return the SSML string
    ssml += "</voice></speak>"
    return ssml


if __name__ == "__main__":
    voice = get_voice_by_name("Tony")
    model = get_model_by_name("gpt-4")
    selector = ProsodySelector(model=model, voice=voice)
