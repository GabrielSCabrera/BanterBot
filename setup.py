import unittest

from setuptools import find_packages, setup

# # Cannot add specific URLs to dependencies in PyPi, so this is commented out, but it works otherwise.
# spacy_version = "3.5.0"
# spacy_models = ["en_core_web_lg", "en_core_web_md", "en_core_web_sm"]
# URL = "https://github.com/explosion/spacy-models/releases/download/"
# spacy_dependencies = [f"{model}@{URL}{model}-{spacy_version}/{model}-{spacy_version}.tar.gz" for model in spacy_models]

dependencies = [
    "openai",
    "tiktoken",
    "requests",
    "azure-cognitiveservices-speech",
    "numpy",
    "uuid6",
    "protobuf==3.20.2",
    "nltk",
    "spacy",
    # # Cannot add specific URLs to dependencies in PyPI, so this is commented out, but it works otherwise.
    # f"spacy=={spacy_version}",
    # *spacy_dependencies,
]

url = "https://github.com/GabrielSCabrera/BanterBot"

description = (
    "BanterBot: An OpenAI ChatGPT-powered chatbot with Azure Neural Voices. Supports speech-to-text and text-to-speech "
    "interactions with emotional tone selection. Features real-time monitoring and Tkinter frontend."
)

with open("README.md", "r") as fs:
    long_description = fs.read()

# For running tests: python -m unittest discover -s tests
# For building: python setup.py sdist bdist_wheel
# For formatting: autoflake -r -i . | isort . | black --line-length 120 .
# For compiling protos: protoc --python_out=. memory.proto


def run_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests", pattern="test_*.py")
    return test_suite


version = "0.0.7"
setup(
    name="BanterBot",
    packages=find_packages(),
    package_data={"banterbot.protos": ["*.py"]},
    test_suite="setup.run_tests",
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gabriel S. Cabrera",
    author_email="gabriel.sigurd.cabrera@gmail.com",
    url=url,
    download_url=url + f"/releases/download/v{version}-alpha/BanterBot-{version}.tar.gz",
    keywords=[
        "tkinter",
        "tk",
        "gpt",
        "gui",
        "windows",
        "linux",
        "cross-platform",
        "chatgpt",
        "text-to-speech",
        "speech-to-text",
        "tts",
        "stt",
        "chatbot",
        "openai",
        "interactive",
    ],
    install_requires=dependencies,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": ["banterbot=banterbot.gui.cli:run"],
    },
)
