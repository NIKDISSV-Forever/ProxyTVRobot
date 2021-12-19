import typing
from abc import abstractmethod
from http.client import HTTPResponse

__all__ = (
    'typing', 'HTTPResponse',
    'RESPONSE_OR_SUPPORT_STR', 'LIST_OF_STR', 'SupportsStr',
    'EXTINF_DATA',
    'IP', 'PROTOCOL', 'PROXY'
)


@typing.runtime_checkable
class SupportsStr(typing.Protocol):
    __slots__ = ()

    @abstractmethod
    def __str__(self) -> str:
        ...


RESPONSE_OR_SUPPORT_STR = typing.Union[HTTPResponse, typing.AnyStr, SupportsStr]
LIST_OF_STR = list[str]
EXTINF_DATA = typing.TypeVar('EXTINF_DATA', list[tuple[str, str]], str)

PROTOCOL = IP = typing.Type[str]
PROXY = typing.Union[tuple[IP, PROTOCOL], list[IP, PROTOCOL]]
