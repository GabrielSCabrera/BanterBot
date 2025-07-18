# For running tests: python -m unittest discover -s tests
# For building: python setup.py sdist bdist_wheel
# For formatting: autoflake --remove-all-unused-imports -r -i . | isort . | black --preview --line-length 120 .
# For compiling protos: protoc --python_out=. memory.proto


import unittest

from setuptools import find_packages, setup

dependencies = [
    "azure-cognitiveservices-speech>=1.37.0",
    "numba>=0.59.1",
    "numpy>=1.26.2",
    "openai>=1.23.2",
    "protobuf==4.25.8",
    "requests>=2.31.0",
    "spacy>=3.7.4",
    "tiktoken>=0.7.0",
    "uuid6>=2024.1.12",
]

description = (
    "BanterBot: An OpenAI ChatGPT-powered chatbot with Azure Neural Voices. Supports speech-to-text and text-to-speech "
    "interactions with emotional tone selection. Features real-time monitoring and Tkinter frontend."
)

url = "https://github.com/GabrielSCabrera/BanterBot"

with open("README.md", "r") as fs:
    long_description = fs.read()


def run_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests", pattern="test_*.py")
    return test_suite


version = "0.0.16"
setup(
    author="Gabriel S. Cabrera",
    author_email="gabriel.sigurd.cabrera@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Utilities",
    ],
    description=description,
    download_url=url + f"/releases/download/v{version}-alpha/BanterBot-{version}.tar.gz",
    entry_points={"console_scripts": ["banterbot=banterbot.gui.cli:run"]},
    install_requires=dependencies,
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
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="BanterBot",
    packages=find_packages(),
    package_data={"banterbot.protos": ["*.py"], "banterbot.resources": ["*"]},
    python_requires=">=3.9",
    test_suite="setup.run_tests",
    url=url,
    version=version,
)
