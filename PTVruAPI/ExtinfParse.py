from .Types import *
from .static import *

__all__ = 'Extinf', 'save_extinf', 'Parse', 'clear_html'


class Extinf:
    """The class represents information from the m3u8 format."""

    __slots__ = '__data', 'author'

    @property
    def data(self) -> ExtinfData:
        """Stores extinf data and source in raw form."""
        return self.__data

    def __init__(self, data: ExtinfData = None, author: str = 'NIKDISSV') -> None:
        """Takes a list of sources and author. Stores them in an instance of the class."""
        if isinstance(data, (tuple, set)):
            data = list(data)
        if not isinstance(data, list):
            data = RegularExpressions.EXTINF_RE.findall(clear_html(data))
        self.__data = data or []
        self.author = author

    def __getitem__(self, find: typing.Union[str, ExtinfFormatInfDict]) -> typing.Union[list[OneChannel], list]:
        """
        Will find an item with a suitable name (For example self['VIASAT HISTORY HD-7171'])
        Or with matching information (For example self[{'tech-id': '7171'}])
        """
        result = []
        if isinstance(find, dict):
            for inf in self:
                inf_dict = inf[0][1]
                for k, v in find.items():
                    if k in inf_dict and inf_dict[k] == v:
                        result.append(inf)
        elif isinstance(find, str):
            find = find.lower()
            result = [inf for inf in self if inf[0][0].lower() == find]
        else:
            result = [inf for inf in self if inf == find]
        return result

    def __iter__(self) -> typing.Iterator[OneChannel]:
        return ((parse_extinf_format(inf), url) for inf, url in self.data)

    def __str__(self) -> str:
        """Converts the transmitted data to m3u8 format, add the author if any."""
        result = '\n'.join('\n'.join(i) for i in sorted(set(self.data)))
        if self.author:
            result = f'#EXTM3U list-autor="{self.author}"\n{result}'
        return result

    def __repr__(self) -> str:
        """Will return all the service information passed in str format."""
        return f'<{self.__class__.__name__}(Len={len(self)}; Author={repr(self.author)})>'

    def __len__(self) -> int:
        """Will return the number of sources."""
        return len(self.data)

    def __iadd__(self, other):
        """Will append data from another instance to this one. (+=)"""
        self.__data += other.data
        return self

    def __add__(self, other):
        """Will return a new instance with the combined data from both. (+)"""
        return Extinf(self.data + other.data)

    def __bool__(self) -> bool:
        """True if there is at least one source."""
        return bool(self.data)


def save_extinf(extinf: Extinf = Extinf(), file: typing.Union[typing.TextIO, str] = None, only_ip: bool = False) -> str:
    """Save m3u8 to the specified file from the class."""
    data_m3u8 = '\n'.join(ip[1] for ip in extinf.data) if only_ip else str(extinf)
    if not file:
        file = open(f'{extinf.author}.m3u8', 'w', encoding='utf-8')
    elif isinstance(file, str):
        file = open(file, 'w', encoding='utf-8')
    with file:
        file.write(data_m3u8)
    return file.name


class Parse:
    __slots__ = '__resp_str',

    def __init__(self, resp: HTTPResponse) -> typing.NoReturn:
        self.__resp_str = resp_to_str(resp)

    def __repr__(self) -> str:
        return self.__resp_str

    def extinf(self) -> Extinf:
        return Extinf(self.__resp_str)

    def plist(self) -> ListOfStr:
        return RegularExpressions.PLIST_RE.findall(self.__resp_str)

    def providers(self) -> ListOfStr:
        return RegularExpressions.PROVIDER_RE.findall(self.__resp_str)
