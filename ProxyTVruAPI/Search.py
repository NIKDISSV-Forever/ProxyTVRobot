from urllib.request import urlopen, Request

from .ExtinfParse import *
from .Types import *

__all__ = 'Srch',


class Srch:
    """The main class for site search."""
    __slots__ = '__proxy',

    def __init__(self, proxy: PROXY = None):
        """Accepts and stores a name (any) for further retrieval."""
        self.proxy = proxy

    def __call__(self, query) -> Extinf:
        return Parse(self.__udpxyaddr(query)).extinf()

    def providers(self):
        return Parse(self.__udpxyaddr('provider')).providers()

    def plist(self):
        return Parse(self.__udpxyaddr('plist')).plist()

    def ch(self, query: SupportsStr):
        return Parse(self.__udpxyaddr(self.__mkq('ch', query))).extinf()

    def pl(self, query: SupportsStr):
        return Parse(self.__udpxyaddr(self.__mkq('pl', query))).extinf()

    def gr(self, query: SupportsStr):
        return Parse(self.__udpxyaddr(self.__mkq('gr', query))).extinf()

    @staticmethod
    def __mkq(wt: SupportsStr, query: SupportsStr) -> str:
        return f'{wt}: {query}'

    def __udpxyaddr(self, __srch: typing.Union[typing.AnyStr, SupportsStr]) -> HTTPResponse:
        _req = Request('https://proxytv.ru/iptv/php/srch.php', b'udpxyaddr='
                       + (__srch if isinstance(__srch, bytes)
                          else (__srch.encode('utf-8') if isinstance(__srch, str)
                                else str(__srch).encode('utf-8'))),
                       {'Referer': 'https://proxytv.ru/index.php'}, method='POST')
        proxy = self.proxy
        if proxy:
            _req.set_proxy(proxy[0], proxy[1])
        return urlopen(_req)

    @property
    def proxy(self) -> PROXY:
        return self.__proxy

    @proxy.setter
    def proxy(self, value: PROXY):
        if not hasattr(self, '__proxy') or self.__proxy != value:
            if value is not None and not isinstance(value, tuple):
                value = tuple(value)
            self.__proxy = value
