from __future__ import annotations

from http.client import HTTPResponse
from typing import Any, AnyStr, TypeVar

__all__ = (
    'HTTPResponse',
    'ResponseOrSupportsStr', 'ListOfStr', 'ExtinfData',
    'ExtinfFormatInfDict',
)

ResponseOrSupportsStr = HTTPResponse | AnyStr
ListOfStr = list[str]
ExtinfData = TypeVar('ExtinfData', list[(str, str)], str)
ExtinfFormatInfDict = dict[str | int, Any]
