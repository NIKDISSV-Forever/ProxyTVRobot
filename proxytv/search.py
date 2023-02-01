from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from urllib.request import Request, urlopen

from proxytv.extinf import *
from proxytv.static import RegularExpressions, _clear_html, _resp_to_str
from proxytv.types import *

__all__ = ('Srch', 'Proxy', 'SearchEngine', 'make_search')


@dataclass
class Proxy:
    """It is not recommended to use proxies, the host isn't friendly with them."""
    host: str = None
    protocol: str = None

    def __bool__(self):
        return not not (self.host and self.protocol)


class Srch:
    """The main class for site search."""
    __slots__ = ('_proxy',)
    _mkq = '{0}: {1}'.format

    def __init__(self, proxy: Proxy = Proxy()):
        """Accepts and stores a name (any) for further retrieval."""
        self._proxy = Proxy()
        self.proxy = proxy

    def __call__(self, query) -> Parse:
        return Parse(self._srch(query))

    def help(self) -> str:
        return _clear_html(repr(self('?')))

    def providers(self) -> ListOfStr:
        return self('provider').providers()

    def plist(self) -> ListOfStr:
        return self('plist').plist()

    def ch(self, query: str) -> Extinf | OneChannel:
        query = str(query)
        tvch_id = RegularExpressions.CH_NAME_WITH_TVCH_ID.findall(query)
        if tvch_id:
            _query = query
            query, tvch_id = tvch_id[0]
        extinf = Parse(self._srch(self._mkq('ch', query))).extinf()
        # noinspection PyUnboundLocalVariable
        return extinf[_query] if tvch_id else extinf

    def pl(self, query: str) -> Extinf:
        return self(self._mkq('pl', query)).extinf()

    def gr(self, query: str) -> Extinf:
        return self(self._mkq('gr', query)).extinf()

    def collect_all(self, threads: int | bool | None = None) -> Extinf:
        """Get all available playlists (self.plist()) and collect all channels from the playlist into one Extinf"""
        if isinstance(threads, bool):
            threads = cpu_count() if threads else 1
        if threads is None or (threads := int(threads)) > 1:
            with ThreadPool(threads) as pool:
                result = pool.map(self.pl, self.plist())
            return sum(result, Extinf())

        container = Extinf()
        for name in self.plist():
            container += self.pl(name)
        return container

    def _srch(self, udpxyaddr) -> str:
        proxy = self.proxy
        protocol = proxy.protocol or 'https'
        __request = Request(
            f'{protocol}://proxytv.ru/iptv/php/srch.php',
            b'udpxyaddr=%b' % self._get_bytes(udpxyaddr),
            {'Referer': 'https://proxytv.ru/index.php'}, method='POST')
        if self.proxy:
            __request.set_proxy(proxy.host, protocol)
        with urlopen(__request) as resp:
            return _resp_to_str(resp.read())

    @property
    def proxy(self) -> Proxy:
        return self._proxy

    @proxy.setter
    def proxy(self, value: Proxy):
        if self._proxy != value:
            self._proxy = value

    @staticmethod
    def _get_bytes(obj) -> bytes:
        if isinstance(obj, (bytes, bytearray)):
            return obj
        if not isinstance(obj, str):
            obj = str(obj)
        return obj.encode('UTF-8')


def make_search(proxy: str = None) -> Srch:
    return Srch(Proxy(*proxy.split('://', 1)[::-1])) if proxy else SearchEngine


SearchEngine = Srch()
