from __future__ import annotations

import typing
from abc import abstractmethod
from http.client import HTTPResponse

__all__ = (
    'typing', 'HTTPResponse',
    'ResponseOrSupportsStr', 'ListOfStr',
    'SupportsStr', 'SupportsBool',
    'UdpxyaddrQuery', 'ExtinfData',
    'ExtinfFormatInfDict',
)


@typing.runtime_checkable
class SupportsStr(typing.Protocol):
    __slots__ = ()

    @abstractmethod
    def __str__(self) -> str:
        ...


@typing.runtime_checkable
class SupportsBool(typing.Protocol):
    __slots__ = ()

    @abstractmethod
    def __bool__(self) -> bool:
        ...


UdpxyaddrQuery = typing.TypeVar('UdpxyaddrQuery', str | SupportsStr, bytes | bytearray)
ResponseOrSupportsStr = HTTPResponse | typing.AnyStr | SupportsStr
ListOfStr = list[str]
ExtinfData = typing.TypeVar('ExtinfData', list[(str, str)], str)

ExtinfFormatInfDict = dict[str | int, typing.Any]

BaseExceptionType = type(BaseException)
