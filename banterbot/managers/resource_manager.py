import importlib.resources
import json
from io import StringIO
from typing import Any

import banterbot
import banterbot.resources


class ResourceManager:

    """
    An interface to simplify loading resources from the `/banterbot/resources/` data directory. In addition to
    syntactically simplifying the process, this class gives the option to cache the loaded files to reduce overhead on
    future calls.
    """

    _raw_data: dict[str] = {}
    _csv_data: dict[list[list[str]]] = {}
    _json_data: dict[dict[Any]] = {}

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear the entire cache by deleting the contents of the `ResourceLoader._raw_data`, `ResourceLoader._csv_data`,
        and `ResourceLoader._json_data` dicts.
        """
        cls.clear_raw_cache()
        cls.clear_csv_cache()
        cls.clear_json_cache()

    @classmethod
    def clear_raw_cache(cls) -> None:
        """
        Clear the raw data cache by deleting the contents of the `ResourceLoader._raw_data` dict.
        """
        cls._raw_data.clear()

    @classmethod
    def clear_csv_cache(cls) -> None:
        """
        Clear the CSV data cache by deleting the contents of the `ResourceLoader._csv_data` dict.
        """
        cls._csv_data.clear()

    @classmethod
    def clear_json_cache(cls) -> None:
        """
        Clear the JSON data cache by deleting the contents of the `ResourceLoader._json_data` dict.
        """
        cls._json_data.clear()

    @classmethod
    def load_raw(cls, filename: str, cache: bool = True, encoding: str = "utf-8") -> str:
        """
        Load a specified file by filename and return its contents as a string.

        Args:
            filename (str): The name of the resource file — should including its suffix.
            cache (bool): If True, cache the loaded data to reduce overhead the next time its loaded.
            encoding (str): The type of encoding to use when loading the resource.

        Returns:
            str: The resource file's contents as a string.
        """
        if filename not in cls._raw_data:
            path = importlib.resources.files(banterbot.resources).joinpath(filename)
            try:
                with open(file=path, mode="r", encoding=encoding) as fs:
                    data = fs.read()
            except FileNotFoundError:
                message = f"Class `ResourceLoader` found no such resource: `{filename}`"
                raise FileNotFoundError(message)

            if cache:
                cls._raw_data[filename] = data
        else:
            data = cls._raw_data[filename]

        return data

    @classmethod
    def load_json(cls, filename: str, cache: bool = True, encoding: str = "utf-8") -> dict[Any]:
        """
        Load a specified JSON file by filename and return its contents as a dictionary.

        Args:
            filename (str): The name of the resource file — should be a JSON file.
            cache (bool): If True, cache the loaded data to reduce overhead the next time its loaded.
            encoding (str): The type of encoding to use when loading the resource.

        Returns:
            dict[Any]: The JSON data formatted as a dictionary.
        """
        if filename not in cls._json_data:
            raw_data = cls.load_raw(filename=filename, cache=False, encoding=encoding)
            try:
                data = json.loads(raw_data)
            except json.decoder.JSONDecodeError as e:
                message = f"Class `ResourceLoader` unable to interpret resource as JSON: `{filename}`. {e.args[0]}"
                raise json.decoder.JSONDecodeError(message)

            if cache:
                cls._json_data[filename] = data
        else:
            data = cls._json_data[filename]

        return data

    @classmethod
    def load_csv(
        cls,
        filename: str,
        cache: bool = True,
        encoding: str = "utf-8",
        delimiter: str = ",",
        quotechar: str = '"',
        dialect: str = "excel",
        strict: bool = True,
    ) -> list[list[str]]:
        """
        Load a specified CSV file by filename and return its contents as a nested list of strings.

        Args:
            filename (str): The name of the resource file — should be a CSV file.
            cache (bool): If True, cache the loaded data to reduce overhead the next time its loaded.
            encoding (str): The type of encoding to use when loading the resource.
            delimiter (str): The CSV delimiter character.
            quotechar (str): The CSV quote character.
            dialect (str): The CSV dialect.
            strict (bool): If True, raises an exception when the file is not correctly formatted.

        Returns:
            list[list[str]]: The CSV data formatted as a nested list of strings.
        """
        if filename not in cls._csv_data:
            raw_data = cls.load_raw(filename=filename, cache=False, encoding=encoding)
            try:
                data = []
                with StringIO(raw_data, newline="") as fs:
                    reader = csv.reader(fs, delimiter=delimiter, quotechar=quotechar, dialect=dialect, strict=strict)
                    for row in reader:
                        data.append(row)
            except csv.Error as e:
                message = f"Class `ResourceLoader` unable to interpret resource as CSV: `{filename}`, {e.args[0]}"
                raise csv.Error(message)

            if cache:
                cls._csv_data[filename] = data
        else:
            data = cls._csv_data[filename]

        return data
