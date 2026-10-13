"""Pure conversion core: units, factors, parsing, validation, rounding, formatting."""
import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, localcontext

UNITS: tuple[str, ...] = ("millimeters", "centimeters", "meters", "kilometers",
                          "inches", "feet", "yards", "miles")

METERS_PER_UNIT: dict[str, Decimal] = {
    "millimeters": Decimal("0.001"),
    "centimeters": Decimal("0.01"),
    "meters":      Decimal("1"),
    "kilometers":  Decimal("1000"),
    "inches":      Decimal("0.0254"),
    "feet":        Decimal("0.3048"),
    "yards":       Decimal("0.9144"),
    "miles":       Decimal("1609.344"),
}

MSG_NOT_POSITIVE = "Please enter a number greater than zero."
MSG_INVALID = "Please enter a valid number."

_NUMBER_RE = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", re.ASCII)
_CENTS = Decimal("0.01")


class ConversionError(ValueError):
    """Base error; ``message`` holds the text to display."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidNumberError(ConversionError):
    def __init__(self) -> None:
        super().__init__(MSG_INVALID)


class NonPositiveValueError(ConversionError):
    def __init__(self) -> None:
        super().__init__(MSG_NOT_POSITIVE)


class UnknownUnitError(ConversionError):
    def __init__(self, unit: object) -> None:
        super().__init__(f"Unknown unit: {unit!r}")


def parse_amount(text: str) -> Decimal:
    s = text.strip()
    if not s or _NUMBER_RE.fullmatch(s) is None:
        raise InvalidNumberError()
    return Decimal(s)


def convert(value: Decimal | int | float | str, from_unit: str, to_unit: str) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise InvalidNumberError() from None
    if not amount.is_finite():
        raise InvalidNumberError()
    if amount <= 0:
        raise NonPositiveValueError()
    for unit in (from_unit, to_unit):
        if unit not in METERS_PER_UNIT:
            raise UnknownUnitError(unit)
    with localcontext() as ctx:
        ctx.prec = max(amount.adjusted(), 0) + 40
        result = amount * METERS_PER_UNIT[from_unit] / METERS_PER_UNIT[to_unit]
        return result.quantize(_CENTS, rounding=ROUND_HALF_UP)


def format_result(value: Decimal) -> str:
    return format(value, "f")


def convert_text(text: str, from_unit: str, to_unit: str) -> str:
    try:
        return format_result(convert(parse_amount(text), from_unit, to_unit))
    except ConversionError as err:
        return err.message
