from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from os.path import abspath
from typing import Callable, Iterable, Iterator, Mapping, SupportsInt, TextIO, TypeVar

from .static import *
from .static import _clear_html
from .types import *

__all__ = ('OneChannel', 'Extinf', 'save_extinf', 'Parse')

T1 = TypeVar('T1')
T2 = TypeVar('T2')


def _repl_double_quotes(v) -> str:
    _repr = repr(v)
    r0 = _repr[0]
    if r0 == _repr[-1]:
        if r0 == '"':
            return _repr
        elif r0 == "'":
            return f'"{_repr[1:-1]}"'
    return f'"{_repr}"'


@dataclass
class OneChannel:
    address: str
    name: str = ''
    info: dict = None

    def __lt__(self, other):
        tvch_id = self.info.get('tvch-id', '')
        other_tvch_id = other.info.get('tvch-id', '')
        if tvch_id and other_tvch_id:
            return tvch_id < other_tvch_id
        return self.name < other.name

    @property
    def extinf_string(self) -> str:
        """return #EXTINF:... string"""
        return f"""#EXTINF:{' '.join(f"{(f'{i}={_repl_double_quotes(v)}' if isinstance(i, str) else v)}"
                                     for i, v in self.info.items())},{self.name}"""

    def __str__(self):
        return f'{self.extinf_string}\n{self.address}'


class Extinf:
    """The class represents information from the m3u8 format."""

    __slots__ = ('data', '_author')

    def __init__(self, data: ExtinfData | list[OneChannel] = None, author: str = 'NIKDISSV') -> None:
        """Takes a list of sources and author. Stores them in an instance of the class."""
        if isinstance(data, (tuple, set)):
            data = [*data]
        if not isinstance(data, list):
            data = RegularExpressions.EXTINF_RE.findall(_clear_html(data))
        self.data: list[OneChannel] = [(one_channel
                                        if isinstance(one_channel, OneChannel)
                                        else OneChannel(one_channel[1], *parse_extinf_format(one_channel[0])))
                                       for one_channel in data]
        self.author = author

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, value):
        self._author = f'#EXTM3U list-autor="{value}"\n' if value else ''

    @staticmethod
    def cmp_ch_info(ch_info: Mapping, need_info: Mapping) -> bool:
        for k, v in need_info.items():
            if k not in ch_info or ch_info[k] != v:
                return False
        return True

    def __getitem__(self,
                    find: str | OneChannel | SupportsInt | ExtinfFormatInfDict | Callable[[OneChannel], bool]
                    ) -> Extinf | OneChannel:
        """
        For example:
        self = Srch().ch('VIASAT HISTORY HD')
        | With a suitable name (For example self['VIASAT HISTORY HD-7171'])
            | self[lambda inf: inf.name.casefold() == 'viasat history hd-7171']
        | With matching information (For example self[{'tvch-id': '7171'}])
            | self[lambda inf: inf[0][1]['tvch-id'] == '7171']
        """
        if isinstance(find, Mapping):
            result = Extinf()
            for one_channel in self:
                if self.cmp_ch_info(one_channel.info, find):
                    result.data.append(one_channel)
            return result
        elif callable(find):
            filter_function = find
        elif isinstance(find, int):
            return self.data[find]
        elif isinstance(find, str):
            find = find.strip().casefold()

            def filter_function(info: OneChannel) -> bool:
                return info.name.strip().casefold() == find
        elif isinstance(find, Iterable):
            answer = copy(self)
            for f in find:
                answer = answer[f]
            return answer
        else:
            def filter_function(info: OneChannel):
                return info == find
        return Extinf([inf for inf in self.data if filter_function(inf)])

    def __iter__(self) -> Iterator[OneChannel]:
        return iter(self.data)

    def __copy__(self):
        return self.__class__(self.data.copy())

    def __str__(self) -> str:
        """Converts the transmitted data to m3u8 format, add the author if any."""
        return '{0}{1}'.format(self.author, '\n'.join(map(str, self.data)))

    def __repr__(self) -> str:
        """Will return all the service information passed in str format."""
        return f'<{self.__class__.__name__}(len={len(self)}; author={self.author!r})>'

    def __len__(self) -> int:
        """Will return the number of sources."""
        return len(self.data)

    def __iadd__(self, other):
        """Will append data from another instance to this one. (+=)"""
        self.data += other.data if hasattr(other, 'data') else other
        return self

    def __add__(self, other):
        """Will return a new instance with the combined data from both. (+)"""
        return Extinf(self.data + (other.data if hasattr(other, 'data') else other))

    def __bool__(self):
        """True if there is at least one source."""
        return not not self.data


class Parse:
    __slots__ = ('__resp_str',)

    def __init__(self, resp: str):
        self.__resp_str = resp

    def __repr__(self) -> str:
        return self.__resp_str

    def extinf(self) -> Extinf:
        return Extinf(self.__resp_str)

    def plist(self) -> ListOfStr:
        return RegularExpressions.PLIST_RE.findall(self.__resp_str)

    def providers(self) -> ListOfStr:
        return RegularExpressions.PROVIDER_RE.findall(self.__resp_str)


def save_extinf(extinf: Extinf = Extinf(), file: TextIO | str = None, only_ip: bool = False) -> str:
    """Save m3u8 to the specified file from the class. (The file will be closed after work)"""
    if not file:
        file = open(f'{extinf.author}.m3u8', 'w', encoding='utf-8')
    elif isinstance(file, str):
        file = open(file, 'w', encoding='utf-8')
    if only_ip:
        file.writelines((one_channel.address for one_channel in extinf.data))
    else:
        file.write(str(extinf))
    return abspath(file.name)


def parse_extinf_format(extinf_line: str):
    if extinf_line.casefold().startswith('#extinf:'):
        extinf_line = extinf_line[8:]
    inf, name = extinf_line.split(',', 1)
    result = {}
    n, d = inf.split(' ', 1)
    result[0] = n
    d = [i for i in d.split('"') if i]
    for i in range(0, len(d), 2):
        k = d[i]
        v = d[i + 1]
        if v.isdigit():
            v = int(v)
        result[k.removesuffix('=').strip()] = v
    return name, result
