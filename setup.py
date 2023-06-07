import unittest

from setuptools import find_packages, setup

dependencies = ["openai", "tiktoken", "requests", "azure-cognitiveservices-speech", "spacy", "numpy"]

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


def run_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests", pattern="test_*.py")
    return test_suite


version = "0.0.5"
setup(
    name="BanterBot",
    packages=find_packages(),
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
