import re

from .Types import *

__all__ = 'RegularExpressions', 'clear_html', 'resp_to_str', 'parse_extinf_format'


class RegularExpressions:
    __slots__ = ()
    PROVIDER_RE: re.Pattern = re.compile(r'робот "(.+)"')
    PLIST_RE: re.Pattern = re.compile(r'плейлист "(.+)"')
    EXTINF_RE: re.Pattern = re.compile(r'(#EXTINF:.+)\n(.+$)', re.M)
    HTML_TEG_RE: re.Pattern = re.compile(r'<.+?>')
    HTML_BR_RE: re.Pattern = re.compile(r'<br>', re.I)


def clear_html(text: typing.Any) -> str:
    return RegularExpressions.HTML_TEG_RE.sub('', RegularExpressions.HTML_BR_RE.sub('\n', resp_to_str(text)))


def resp_to_str(resp: RESPONSE_OR_SUPPORT_STR) -> str:
    return (resp.read().decode('UTF-8') if isinstance(resp, HTTPResponse)
            else (resp if isinstance(resp, str)
                  else (resp.decode('UTF-8') if isinstance(resp, bytes)
                        else (str(resp)))))


def parse_extinf_format(extinf_line: str) -> ExtinfFormat:
    if extinf_line[:8].upper() == '#EXTINF:':
        extinf_line = extinf_line[8:]
    inf, name = extinf_line.split(',', 1)
    result = {}
    counter = 0
    for v in inf.split(' '):
        if '=' in v:
            i, v = v.split('=', 1)
        else:
            i = counter
            counter += 1
        try:
            v = eval(v)
        except Exception:
            pass
        result[i] = v
    return name, result
