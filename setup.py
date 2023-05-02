from setuptools import setup, find_packages

dependencies = ["openai", "tiktoken", "geocoder", "requests", "termighty", "azure-cognitiveservices-speech", "spacy"]

url = "https://github.com/GabrielSCabrera/GPTBot"

with open("README.md", "r") as fs:
    long_description = fs.read()

setup(
    name="GPTBot",
    packages=find_packages(where="GPTBot"),
    package_dir={"": "GPTBot"},
    version="0.0.1",
    description="GPTX-Powered Interactive Assistant",
    long_description=long_description,
    author="Gabriel S. Cabrera",
    author_email="gabriel.sigurd.cabrera@gmail.com",
    url=url,
    download_url=url + "archive/v0.0.1.tar.gz",
    keywords=["terminal", "gpt", "gui", "windows", "linux"],
    install_requires=dependencies,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.11",
    ],
)
