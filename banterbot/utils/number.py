import math
from typing import Union

from typing_extensions import Self


class Number:
    """
    An object that contains an integer, float, or complex value. This class is meant to be used as a wrapper around a
    number, allowing it to be passed by reference instead of by value.
    """

    def __init__(self, value: int):
        """
        Initializes the current instance with a value.
        """
        self.set(value=value)

    def is_null(self) -> None:
        """
        Returns whether or not the current instance is null.
        """
        return self.value is None

    def set(self, value) -> None:
        """
        Sets the value of the current instance.
        """
        if isinstance(value, (int, float, complex)) or value is None:
            self.value = value
        else:
            raise TypeError(f"Unsupported type for class `{self.__class__.__name__}`: '{type(value).__name__}'")

    def __call__(self) -> int:
        """
        Returns the value of the current instance.

        Returns:
            int: The value of the current instance.
        """
        return self.value

    def __str__(self) -> str:
        """
        Returns the string representation of the current instance.

        Returns:
            str: The string representation of the current instance.
        """
        return str(self.value)

    def __repr__(self) -> str:
        """
        Returns the string representation of the current instance.

        Returns:
            str: The string representation of the current instance.
        """
        return str(self.value)

    def __bool__(self) -> bool:
        """
        Returns the truthiness of the current instance.

        Returns:
            bool: The truthiness of the current instance.
        """
        return bool(self.value)

    def __int__(self) -> int:
        """
        Returns the value of the current instance as an int.

        Returns:
            int: The value of the current instance.
        """
        return int(self.value)

    def __float__(self) -> float:
        """
        Returns the value of the current instance as a float.

        Returns:
            float: The value of the current instance.
        """
        return float(self.value)

    def __complex__(self) -> complex:
        """
        Returns the value of the current instance as a complex number.

        Returns:
            complex: The value of the current instance.
        """
        return complex(self.value)

    def __add__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Adds the value of the current instance to another value.

        Args:
            value (Union[int, float, complex, Self]): The value to add to the current instance.

        Returns:
            Union[float, Self]: The result of adding the value to the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for +: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.__class__(self.value + value.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(self.value + value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for +: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __radd__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Adds the value of the current instance to another value.

        Args:
            value (Union[int, float, complex, Self]): The value to add to the current instance.

        Returns:
            Self: The result of adding the value to the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for +: '{type(value).__name__}' and `Nonetype`")
        elif isinstance(value, self.__class__):
            return self.__class__(value.value + self.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(value + self.value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for +: '{type(value).__name__}' and '{self.__class__.__name__}'"
            )

    def __iadd__(self, value: Union[int, float, complex, Self]) -> None:
        """
        Adds a value to the current instance.

        Args:
            value (Union[int, float, complex, Self]): The value to add to the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for +=: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            self.value += value.value
        elif isinstance(value, (int, float, complex)):
            self.value += value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for +=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __sub__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Subtracts a value from the current instance.

        Args:
            value (Union[int, float, complex, Self]): The value to subtract from the current instance.

        Returns:
            Union[float, Self]: The result of subtracting the value from the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for -: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.__class__(self.value - value.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(self.value - value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for -: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __rsub__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Subtracts the value of the current instance from another value.

        Args:
            value (Union[int, float, complex, Self]): The value the current instance will be subtracted from.

        Returns:
            Self: The result of subing the value to the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for -: '{type(value).__name__}' and `Nonetype`")
        elif isinstance(value, self.__class__):
            return self.__class__(value.value - self.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(value - self.value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for -: '{type(value).__name__}' and '{self.__class__.__name__}'"
            )

    def __isub__(self, value: Union[int, float, complex, Self]) -> None:
        """
        Subtracts a value from the current instance.

        Args:
            value (Union[int, float, complex, Self]): The value to sub to the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for -: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            self.value -= value.value
        elif isinstance(value, (int, float, complex)):
            self.value -= value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for -=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __mul__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Multiplies the value of the current instance by another value.

        Args:
            value (Union[int, float, complex, Self]): The value to multiply the current instance by.

        Returns:
            Self: The result of multiplying the input value by the current instance's value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for *: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.__class__(self.value * value.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(self.value * value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for *: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __rmul__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Multiplies another value by the value of the current instance.

        Args:
            value (Union[int, float, complex, Self]): The value that will be multiplied the current instance.

        Returns:
            Self: The result of multiplying the input value by the current instance's value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for *: '{type(value).__name__}' and `Nonetype`")
        elif isinstance(value, self.__class__):
            return self.__class__(value * self.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(value * self.value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for *: '{type(value).__name__}' and '{self.__class__.__name__}'"
            )

    def __imul__(self, value: Union[int, float, complex, Self]) -> None:
        """
        Multiplies the value of the current instance by another value.

        Args:
            value (Union[int, float, complex, Self]): The value to multiply the current instance by.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for *: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            self.value *= value.value
        elif isinstance(value, (int, float, complex)):
            self.value *= value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for *=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __truediv__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Divides the value of the current instance by another value.

        Args:
            value (Union[int, float, complex, Self]): The value to divide the current instance by.

        Returns:
            Self: The result of dividing the input value by the current instance's value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for /: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.__class__(self.value / value.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(self.value / value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for /: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __rtruediv__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Divides another value by the value of the current instance.

        Args:
            value (Union[int, float, complex, Self]): The value that will be divided by the current instance's value.

        Returns:
            Self: The result of dividing the input value by the current instance's value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for /: '{type(value).__name__}' and `Nonetype`")
        elif isinstance(value, self.__class__):
            return self.__class__(value.value / self.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(value / self.value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for /: '{type(value).__name__}' and '{self.__class__.__name__}'"
            )

    def __itruediv__(self, value: Union[int, float, complex, Self]) -> None:
        """
        Divides the value of the current instance by another value.

        Args:
            value (Union[int, float, complex, Self]): The value to divide the current instance by.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for /: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            self.value /= value.value
        elif isinstance(value, (int, float, complex)):
            self.value /= value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for /=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __floordiv__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Floors the value of the current instance by another value.

        Args:
            value (Union[int, float, complex, Self]): The value to floor the current instance by.

        Returns:
            Self: The result of flooring the input value by the current instance's value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for //: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.__class__(self.value // value.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(self.value // value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for //: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __rfloordiv__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Floors another value by the value of the current instance.

        Args:
            value (Union[int, float, complex, Self]): The value that will be floored by the current instance's value.

        Returns:
            Self: The result of flooring the input value by the current instance's value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for //: '{type(value).__name__}' and `Nonetype`")
        elif isinstance(value, self.__class__):
            return self.__class__(value.value // self.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(value // self.value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for //: '{type(value).__name__}' and '{self.__class__.__name__}'"
            )

    def __ifloordiv__(self, value: Union[int, float, complex, Self]) -> None:
        """
        Floors the value of the current instance by another value.

        Args:
            value (Union[int, float, complex, Self]): The value to floor the current instance by.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for //: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            self.value //= value.value
        elif isinstance(value, (int, float, complex)):
            self.value //= value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for //=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __mod__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Modulos the value of the current instance by another value.

        Args:
            value (Union[int, float, complex, Self]): The value to modulo the current instance by.

        Returns:
            Self: The result of moduloing the current instance's value by the input value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for %: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.__class__(self.value % value.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(self.value % value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for %: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __rmod__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Modulos another value by the value of the current instance.

        Args:
            value (Union[int, float, complex, Self]): The value that will be moduloed by the current instance's value.

        Returns:
            Self: The result of moduloing the input value by the current instance's value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for %: '{type(value).__name__}' and `Nonetype`")
        elif isinstance(value, self.__class__):
            return self.__class__(value.value % self.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(value % self.value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for %: '{type(value).__name__}' and '{self.__class__.__name__}'"
            )

    def __imod__(self, value: Union[int, float, complex, Self]) -> None:
        """
        Modulos the value of the current instance by another value.

        Args:
            value (Union[int, float, complex, Self]): The value to modulo the current instance by.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for %: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            self.value %= value.value
        elif isinstance(value, (int, float, complex)):
            self.value %= value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for %=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __pow__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Raises the value of the current instance to the power of another value.

        Args:
            value (Union[int, float, complex, Self]): The value to raise the current instance to the power of.

        Returns:
            Self: The result of raising the value to the power of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for **: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.__class__(self.value**value.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(self.value**value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for **: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __rpow__(self, value: Union[int, float, complex, Self]) -> Self:
        """
        Raises another value to the power of the value of the current instance.

        Args:
            value (Union[int, float, complex, Self]): The value that will be raised to the power of the current instance.

        Returns:
            Self: The result of raising the value to the power of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for **: '{type(value).__name__}' and `Nonetype`")
        elif isinstance(value, self.__class__):
            return self.__class__(value.value**self.value)
        elif isinstance(value, (int, float, complex)):
            return self.__class__(value**self.value)
        else:
            raise TypeError(
                f"Unsupported operand type(s) for **: '{type(value).__name__}' and '{self.__class__.__name__}'"
            )

    def __ipow__(self, value: Union[int, float, complex, Self]) -> None:
        """
        Raises the value of the current instance to the power of another value.

        Args:
            value (Union[int, float, complex, Self]): The value to raise the current instance to the power of.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for **: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            self.value **= value.value
        elif isinstance(value, (int, float, complex)):
            self.value **= value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for **=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __abs__(self) -> Self:
        """
        Returns the absolute value of the current instance.

        Returns:
            Self: The absolute value of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for abs(): 'Nonetype'")
        return self.__class__(abs(self.value))

    def __neg__(self) -> Self:
        """
        Returns the negative value of the current instance.

        Returns:
            Self: The negative value of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for __neg__(): 'Nonetype'")
        return self.__class__(-self.value)

    def __pos__(self) -> Self:
        """
        Returns the positive value of the current instance.

        Returns:
            Self: The positive value of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for __pos__(): 'Nonetype'")
        return self.__class__(+self.value)

    def __invert__(self) -> Self:
        """
        Returns the inverted value of the current instance.

        Returns:
            Self: The inverted value of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for ~: 'Nonetype'")
        return self.__class__(~self.value)

    def __round__(self, n: int = 0) -> Self:
        """
        Rounds the value of the current instance.

        Args:
            n (int): The number of decimal places to round to.

        Returns:
            Self: The rounded value of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for round(): 'Nonetype'")
        return self.__class__(round(self.value, n))

    def __floor__(self) -> Self:
        """
        Floors the value of the current instance.

        Returns:
            Self: The floored value of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for __floor__(): 'Nonetype'")
        return self.__class__(math.floor(self.value))

    def __ceil__(self) -> Self:
        """
        Ceils the value of the current instance.

        Returns:
            Self: The ceiled value of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for __ceil__(): 'Nonetype'")
        return self.__class__(math.ceil(self.value))

    def __trunc__(self) -> Self:
        """
        Truncs the value of the current instance.

        Returns:
            Self: The truncted value of the current instance.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for __trunc__(): 'Nonetype'")
        return self.__class__(math.trunc(self.value))

    def __lt__(self, value: Union[int, float, complex, Self]) -> bool:
        """
        Checks if the value of the current instance is less than another value.

        Args:
            value (Union[int, float, complex, Self]): The value to compare the current instance to.

        Returns:
            bool: Whether or not the value of the current instance is less than the other value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for <: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.value < value.value
        elif isinstance(value, (int, float, complex)):
            return self.value < value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for <: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __le__(self, value: Union[int, float, complex, Self]) -> bool:
        """
        Checks if the value of the current instance is less than or equal to another value.

        Args:
            value (Union[int, float, complex, Self]): The value to compare the current instance to.

        Returns:
            bool: Whether or not the value of the current instance is less than or equal to the other value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for <=: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.value <= value.value
        elif isinstance(value, (int, float, complex)):
            return self.value <= value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for <=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __eq__(self, value: Union[int, float, complex, Self]) -> bool:
        """
        Checks if the value of the current instance is equal to another value.

        Args:
            value (Union[int, float, complex, Self]): The value to compare the current instance to.

        Returns:
            bool: Whether or not the value of the current instance is equal to the other value.
        """
        if isinstance(value, self.__class__):
            return self.value == value.value
        elif isinstance(value, (int, float, complex)):
            return self.value == value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for ==: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __ne__(self, value: Union[int, float, complex, Self]) -> bool:
        """
        Checks if the value of the current instance is not equal to another value.

        Args:
            value (Union[int, float, complex, Self]): The value to compare the current instance to.

        Returns:
            bool: Whether or not the value of the current instance is not equal to the other value.
        """
        if isinstance(value, self.__class__):
            return self.value != value.value
        elif isinstance(value, (int, float, complex)):
            return self.value != value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for !=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __gt__(self, value: Union[int, float, complex, Self]) -> bool:
        """
        Checks if the value of the current instance is greater than another value.

        Args:
            value (Union[int, float, complex, Self]): The value to compare the current instance to.

        Returns:
            bool: Whether or not the value of the current instance is greater than the other value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for >: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.value > value.value
        elif isinstance(value, (int, float, complex)):
            return self.value > value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for >: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __ge__(self, value: Union[int, float, complex, Self]) -> bool:
        """
        Checks if the value of the current instance is greater than or equal to another value.

        Args:
            value (Union[int, float, complex, Self]): The value to compare the current instance to.

        Returns:
            bool: Whether or not the value of the current instance is greater than or equal to the other value.
        """
        if self.value is None:
            raise TypeError(f"Unsupported operand type(s) for >=: 'Nonetype' and '{type(value).__name__}'")
        elif isinstance(value, self.__class__):
            return self.value >= value.value
        elif isinstance(value, (int, float, complex)):
            return self.value >= value
        else:
            raise TypeError(
                f"Unsupported operand type(s) for >=: '{self.__class__.__name__}' and '{type(value).__name__}'"
            )

    def __hash__(self) -> int:
        """
        Returns the hash of the current instance.

        Returns:
            int: The hash of the current instance.
        """
        return hash(self.value)

    def __index__(self) -> int:
        """
        Returns the current instance for indexing.

        Returns:
            int: The value of the current instance.
        """
        return self.value
