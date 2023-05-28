import unittest

from setuptools import find_packages, setup

dependencies = ["openai", "tiktoken", "requests", "azure-cognitiveservices-speech", "spacy"]

url = "https://github.com/GabrielSCabrera/BanterBot"

with open("README.md", "r") as fs:
    long_description = fs.read()

# For running tests: python -m unittest discover -s tests
# For building: python setup.py sdist bdist_wheel


def run_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests", pattern="test_*.py")
    return test_suite


setup(
    name="BanterBot",
    packages=find_packages(),
    test_suite="setup.run_tests",
    version="0.0.1",
    description="ChatGPT-Powered Text-To-Speech Interaction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gabriel S. Cabrera",
    author_email="gabriel.sigurd.cabrera@gmail.com",
    url=url,
    download_url=url + "archive/v0.0.1.tar.gz",
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
        "tts",
        "chatbot",
    ],
    install_requires=dependencies,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": ["banterbot=banterbot.gui.cli:run"],
    },
)
