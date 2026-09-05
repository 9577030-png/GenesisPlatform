from __future__ import annotations

import re
from typing import List

from ..domain.entities.parameter import Parameter
from ..domain.exceptions import InvalidParameterError, ParsingError
from .parameter_normalizer import ParameterNormalizer


class RegexParser:
    """Parse laboratory-like text into normalized medical Parameters."""

    def __init__(self) -> None:
        self.normalizer = ParameterNormalizer()
        self.pattern_with_digits = re.compile(
            r"(?P<name>[A-Za-zА-Яа-я_]+[0-9]+)\s*(?P<value>-?[\d.]+)\s*(?P<unit>[A-Za-z/%]+)?"
        )
        self.pattern_with_spaces = re.compile(
            r"(?P<name>[A-Za-zА-Яа-я_ ]+)\s*(?P<value>-?[\d.]+)\s*(?P<unit>[A-Za-z/%]+)?"
        )

    def parse(self, raw_text: str) -> List[Parameter]:
        if not raw_text or not raw_text.strip():
            raise ParsingError("Input text is empty")

        parameters: List[Parameter] = []
        for line in (part.strip() for part in raw_text.strip().splitlines() if part.strip()):
            match = self.pattern_with_digits.search(line) or self.pattern_with_spaces.search(line)
            if not match:
                continue

            name = match.group("name").strip()
            value = float(match.group("value"))
            unit_str = match.group("unit") or ""
            try:
                canonical_name, normalized_value, unit_obj = self.normalizer.normalize(
                    name, value, unit_str
                )
            except InvalidParameterError:
                continue

            parameters.append(
                Parameter(
                    name=canonical_name,
                    value=normalized_value,
                    unit=unit_obj,
                )
            )

        if not parameters:
            raise ParsingError("No valid parameters could be extracted from input")
        return parameters
