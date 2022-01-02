from __future__ import annotations

import typing
from abc import abstractmethod
from http.client import HTTPResponse

__all__ = (
    'typing', 'HTTPResponse',
    'ResponseOrSupportsStr', 'ListOfStr', 'SupportsStr',
    'UdpxyaddrQuery', 'ExtinfData',
    'ExtinfFormatInfDict', 'ExtinfFormat', 'OneChannel',
)


@typing.runtime_checkable
class SupportsStr(typing.Protocol):
    __slots__ = ()

    @abstractmethod
    def __str__(self) -> str:
        ...


UdpxyaddrQuery = typing.TypeVar('UdpxyaddrQuery', typing.Union[str, SupportsStr], typing.Union[bytes, bytearray])
ResponseOrSupportsStr = typing.Union[HTTPResponse, typing.AnyStr, SupportsStr]
ListOfStr = list[str]
ExtinfData = typing.TypeVar('ExtinfData', list[tuple[str, str]], str)

ExtinfFormatInfDict = dict[typing.Union[str, int], typing.Any]
ExtinfFormat = tuple[str, ExtinfFormatInfDict]
OneChannel = tuple[ExtinfFormat, str]
