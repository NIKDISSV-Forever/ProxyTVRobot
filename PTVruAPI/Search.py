from dataclasses import dataclass
from urllib.request import urlopen, Request

from PTVruAPI.ExtinfParse import *
from PTVruAPI.Types import *

__all__ = 'Srch', 'Proxy'

from .static import RegularExpressions


@dataclass
class Proxy:
    """It is not recommended to use proxies, the host isn't friendly with them."""
    host: str = None
    protocol: str = None

    def __bool__(self) -> bool:
        return bool(self.host and self.protocol)


class Srch:
    """The main class for site search."""
    __slots__ = '__proxy',

    def __init__(self, proxy: Proxy = Proxy()):
        """Accepts and stores a name (any) for further retrieval."""
        self.proxy = proxy

    def __call__(self, query: UdpxyaddrQuery) -> Parse:
        return Parse(self.__udpxyaddr(query))

    def help(self) -> str:
        return clear_html(repr(self('?')))

    def providers(self) -> ListOfStr:
        return Parse(self.__udpxyaddr('provider')).providers()

    def plist(self) -> ListOfStr:
        return Parse(self.__udpxyaddr('plist')).plist()

    def ch(self, query: SupportsStr) -> typing.Union[Extinf, OneChannel]:
        query = str(query)
        tvch_id = RegularExpressions.CH_NAME_WITH_TVCH_ID.findall(query)
        if tvch_id:
            _query = query
            query, tvch_id = tvch_id[0]
        extinf = Parse(self.__udpxyaddr(self.__mkq('ch', query))).extinf()
        # noinspection PyUnboundLocalVariable
        return Extinf(extinf[_query]) if tvch_id else extinf

    def pl(self, query: SupportsStr) -> Extinf:
        return Parse(self.__udpxyaddr(self.__mkq('pl', query))).extinf()

    def gr(self, query: SupportsStr) -> Extinf:
        return Parse(self.__udpxyaddr(self.__mkq('gr', query))).extinf()

    @staticmethod
    def __mkq(wt: SupportsStr, query: SupportsStr) -> str:
        return f'{wt}: {query}'

    def __udpxyaddr(self,
                    __srch: UdpxyaddrQuery) -> HTTPResponse:
        proxy = self.proxy
        protocol = proxy.protocol or 'https'
        __request = Request(
            f'{protocol}://proxytv.ru/iptv/php/srch.php',
            b'udpxyaddr=' + (__srch if isinstance(__srch, (bytes, bytearray)) else (
                __srch.encode('utf-8') if isinstance(__srch, str) else str(__srch).encode('utf-8'))),
            {'Referer': 'https://proxytv.ru/index.php'}, method='POST')
        if proxy:
            __request.set_proxy(proxy.host, protocol)
        return urlopen(__request)

    @property
    def proxy(self) -> Proxy:
        return self.__proxy

    @proxy.setter
    def proxy(self, value: Proxy):
        if not hasattr(self, '__proxy') or self.__proxy != value:
            self.__proxy = value
