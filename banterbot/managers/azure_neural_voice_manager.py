import logging
import os
import re
from itertools import chain
from typing import Optional, Union

import azure.cognitiveservices.speech as speechsdk

from banterbot.data.enums import EnvVar
from banterbot.models.azure_neural_voice_profile import AzureNeuralVoiceProfile


class AzureNeuralVoiceManager:
    """
    Management utility for loading Microsoft Azure Cognitive Services Neural Voice models from the Speech SDK. Only one
    instance per name is permitted to exist at a time, and loading occurs lazily, meaning that when the voices are
    downloaded, they are subsequently stored in cache as instances of class `AzureNeuralVoice`, and all future calls
    refer to these same cached instances.
    """

    _data = {}

    @classmethod
    def _download(cls) -> None:
        """
        Download all the Neural Voices to cache as instances of class `AzureNeuralVoice` using the `get_voices_async`
        method from the Microsoft Azure Cognitive Services Speech SDK class `SpeechSynthesizer`.
        """
        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get(EnvVar.AZURE_SPEECH_KEY.value),
            region=os.environ.get(EnvVar.AZURE_SPEECH_REGION.value),
        )
        result_future = speechsdk.SpeechSynthesizer(speech_config=speech_config).get_voices_async()
        synthesis_voices_result = result_future.get()

        # Regex pattern that extracts language, country, region, and a key from each voice's `short_name` attribute,
        pattern = re.compile(r"([a-z]+)\-([A-Z]+)\-(?:(\w+)\-)?(\w+?)Neural")

        for voice in synthesis_voices_result.voices:
            # Specify that we only want to store Neural Voices.
            if voice.voice_type == speechsdk.SynthesisVoiceType.OnlineNeural:
                match = re.fullmatch(pattern=pattern, string=voice.short_name)

                if not match:
                    logging.debug(f"Unable to parse Azure Cognitive Services Neural Voice: {voice.short_name}.")
                else:
                    language = match[1]
                    country = match[2]
                    region = match[3]
                    name = match[4]

                    if name in cls._data:
                        key = name + "-" + region
                    else:
                        key = name

                    cls._data[key.lower()] = AzureNeuralVoiceProfile(
                        country=country,
                        description=voice.name,
                        gender=voice.gender,
                        language=language,
                        locale=voice.locale,
                        name=name,
                        short_name=voice.short_name.lower(),
                        style_list=voice.style_list if voice.style_list else None,
                        region=region,
                    )

    @classmethod
    def data(cls) -> dict[str, AzureNeuralVoiceProfile]:
        """
        Access the data dictionary, downloading it first using the `_download` classmethod if necessary.

        Returns:
            dict[str, AzureNeuralVoiceProfile]: A dict containing the downloaded `AzureNeuralVoiceProfile` instances.
        """
        if not cls._data:
            cls._download()

        return cls._data

    @classmethod
    def _preprocess_search_arg(cls, arg: Optional[Union[list[str], str]] = None) -> Optional[Union[list[str], str]]:
        """
        Prepare an arbitrary argument given to the `search` method by lowering its value(s).

        Args:
            arg (Optional[Union[list[str], str]]): A string, list of strings, or None value.

        Returns:
            Optional[Union[list[str], str]]: The same input but lowered, if applicable.
        """
        if not arg:
            return None
        elif isinstance(arg, str):
            return [arg.lower()]
        elif isinstance(arg, (list, tuple, set)):
            return sorted([i.lower() for i in arg])

    @classmethod
    def search(
        cls,
        gender: Optional[Union[list[str], str]] = None,
        language: Optional[Union[list[str], str]] = None,
        country: Optional[Union[list[str], str]] = None,
        region: Optional[Union[list[str], str]] = None,
        style: Optional[Union[list[str], str]] = None,
    ) -> list[AzureNeuralVoiceProfile]:
        """
        Search through all the available Microsoft Azure Cognitive Services Neural Voice models using any combination
        of the provided arguments to get a list of relevant `AzureNeuralVoiceProfile` instances. For information on
        searchable languages, countries, and regions, visit:

        https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts#supported-languages

        Args:
            gender (Optional[Union[list[str], str]]): Can take the values MALE, FEMALE, and/or UNKNOWN.
            language (Optional[Union[list[str], str]]): Can take any language abbreviations (e.g., en, fr, etc.)
            country (Optional[Union[list[str], str]]): Can take any country abbreviations (e.g., US, FR, etc.)
            region (Optional[Union[list[str], str]]): Can take any region names (e.g., shaanxi, sichuan, etc.)

        Returns:
            list[AzureNeuralVoiceProfile]: A list of `AzureNeuralVoiceProfile` instances.
        """
        search_results = []

        # Convert any provided string values to lowercase if applicable.
        gender = cls._preprocess_search_arg(arg=gender)
        language = cls._preprocess_search_arg(arg=language)
        country = cls._preprocess_search_arg(arg=country)
        region = cls._preprocess_search_arg(arg=region)
        style = cls._preprocess_search_arg(arg=style)

        for voice in cls.data().values():
            # Convert the voice attributes to lowercase if applicable.
            voice_gender = voice.gender.name.lower() if voice.gender.name else None
            voice_language = voice.language.lower() if voice.language else None
            voice_country = voice.country.lower() if voice.country else None
            voice_region = voice.region.lower() if voice.region else None
            voice_styles = sorted([s.lower() for s in voice.style_list]) if voice.style_list else []

            # Prepare a set of search conditions.
            condition_gender = gender is None or voice_gender in gender
            condition_language = language is None or voice_language in language
            condition_country = country is None or voice_country in country
            condition_region = region is None or voice_region in region
            condition_styles = style is None or all(s in voice_styles for s in style)

            # If all conditions are met, add the voice to the search results.
            if all([condition_gender, condition_language, condition_country, condition_region, condition_styles]):
                search_results.append(voice)

        return search_results

    @classmethod
    def list_countries(cls) -> list[str]:
        """
        Returns a list of two-character country codes (e.g., us, fr, etc.)

        Returns:
            list[str]: A list of country codes.
        """
        voices = cls.data()
        return sorted(list(set(voice.country for voice in voices.values() if voice.country)))

    @classmethod
    def list_genders(cls) -> list[str]:
        """
        Returns a list of available voice genders

        Returns:
            list[str]: A list of genders.
        """
        voices = cls.data()
        return sorted(list(set(voice.gender.name for voice in voices.values() if voice.gender.name)))

    @classmethod
    def list_languages(cls) -> list[str]:
        """
        Returns a list of two-character language codes (e.g., en, fr, etc.)

        Returns:
            list[str]: A list of language codes.
        """
        voices = cls.data()
        return sorted(list(set(voice.language for voice in voices.values() if voice.language)))

    @classmethod
    def list_locales(cls) -> list[str]:
        """
        Returns a list of locales, which are language codes followed by countries, in some cases followed by a region,
        (e.g., en-US fr-FR, etc.).

        Returns:
            list[str]: A list of locales.
        """
        voices = cls.data()
        return sorted(list(set(voice.locale for voice in voices.values() if voice.locale)))

    @classmethod
    def list_regions(cls) -> list[str]:
        """
        Returns a list of regions (e.g., sichuan, shandong, etc.)

        Returns:
            list[str]: A list of regions.
        """
        voices = cls.data()
        return sorted(list(set(voice.region for voice in voices.values() if voice.region)))

    @classmethod
    def list_styles(cls) -> list[str]:
        """
        Returns a list of styles (e.g., sichuan, shandong, etc.)

        Returns:
            list[str]: A list of styles.
        """
        voices = cls.data()
        return sorted(list(set(chain.from_iterable(voice.style_list for voice in voices.values() if voice.style_list))))

    @classmethod
    def load(cls, name: str) -> AzureNeuralVoiceProfile:
        """
        Retrieve or initialize an `AzureNeuralVoice` instance by a name in the Neural Voices resource JSON.

        Args:
            name (str): The name of the voice profile.

        Returns:
            AzureNeuralVoice: An `AzureNeuralVoice` instance loaded with data from the specified name.

        Raises:
            KeyError: If the specified name is not found in the resource file defined by `config.azure_neural_voices`.
        """
        voices = cls.data()
        if (name := name.lower()) not in voices:
            message = (
                "BanterBot was unable to locate a Microsoft Azure Cognitive Services Neural Voice model named: "
                f"`{name}`. Use AzureNeuralVoiceManager.search(gender, language, country, region) to search for a "
                "specified gender, language, country, and/or region. These arguments can be strings, lists of strings, "
                "or None."
            )
            raise KeyError(message)

        return voices[name]
