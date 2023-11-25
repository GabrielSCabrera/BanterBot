from typing import Optional


class FormatMismatchError(ValueError):
    """
    Exception raised when the output format from an external API does not match the expected format.
    This can be used to signal a mismatch in the expected structure or content type of the data returned from an API
    call.

    Args:

        expression (Optional[str]): The input expression or API response that caused the error. This is optional and
        used for providing context in the error message.

        message (Optional[str]): An explanation of the error. Defaults to a standard message about format mismatch.

    Raises:
        FormatMismatchError: An error occurred due to a mismatch in the expected output format.
    """

    def __init__(self, expression: Optional[str] = None, message: Optional[str] = None) -> None:
        self.expression = expression
        self.message = message or "An error occurred due to a mismatch in the expected format"
        error_message: str = f"{self.expression}: {self.message}" if expression else self.message
        super().__init__(error_message)

    def __str__(self) -> str:
        return self.message
