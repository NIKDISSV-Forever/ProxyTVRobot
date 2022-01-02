from PTVruAPI.Types import *
from PTVruAPI.static import *

__all__ = 'Extinf', 'save_extinf', 'Parse', 'clear_html'

_DQ = '"'
_SQ = "'"


class Extinf:
    """The class represents information from the m3u8 format."""

    __slots__ = 'data', 'author'

    def __init__(self, data: typing.Union[ExtinfData, list[OneChannel]] = None, author: str = 'NIKDISSV') -> None:
        """Takes a list of sources and author. Stores them in an instance of the class."""
        if isinstance(data, (tuple, set)):
            data = list(data)
        if not isinstance(data, list):
            data = RegularExpressions.EXTINF_RE.findall(clear_html(data))
        self.data: list[OneChannel] = [(parse_extinf_format(inf), url) for inf, url in data] or []
        self.author = author

    def __getitem__(self, find: typing.Union[
        SupportsStr, ExtinfFormatInfDict, typing.Callable[[OneChannel], SupportsBool], OneChannel]
                    ) -> typing.Union[list[OneChannel]]:
        """
        For example:
        self = Srch().ch('VIASAT HISTORY HD')
        | With a suitable name (For example self['VIASAT HISTORY HD-7171'])
            | self[lambda inf: inf[0][0].lower() == 'VIASAT HISTORY HD-7171']
        | With matching information (For example self[{'tvch-id': '7171'}])
            | self[lambda inf: inf[0][1]['tvch-id'] == '7171']
        """
        if isinstance(find, dict):
            result = []
            for inf in self:
                inf_dict = inf[0][1]
                add = False
                for k, v in find.items():
                    if k in inf_dict:
                        add = inf_dict[k] == v
                if add:
                    result.append(inf)
            return result
        elif isinstance(find, str):
            find = find.lower()
            filter_function = lambda inf: inf[0][0].lower() == find
        elif callable(find):
            filter_function = find
        else:
            filter_function = lambda inf: inf == find
        return [inf for inf in self if filter_function(inf)]

    def __iter__(self) -> typing.Iterator[OneChannel]:
        return iter(self.data)

    def __str__(self) -> str:
        """Converts the transmitted data to m3u8 format, add the author if any."""
        return '{0}{1}'.format((f'#EXTM3U list-autor="{self.author}"\n' if self.author else ''
                                ), '\n'.join(
            f"""#EXTINF:{' '.join(f'{(f"{i}=" if isinstance(i, str) else "")}{repr(v).replace(_SQ, _DQ)}' for i, v in inf.items())},{name}\n{url}"""
            for (name, inf), url in self.data))

    def __repr__(self) -> str:
        """Will return all the service information passed in str format."""
        return f'<{self.__class__.__name__}(Len={len(self)}; Author={repr(self.author)})>'

    def __len__(self) -> int:
        """Will return the number of sources."""
        return len(self.data)

    def __iadd__(self, other):
        """Will append data from another instance to this one. (+=)"""
        self.data += other.data
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
