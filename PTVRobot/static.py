from __future__ import annotations

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
    CH_NAME_WITH_TVCH_ID: re.Pattern = re.compile(r'(.+)-(\d+)$')
    HTML_ESCAPE = re.compile(r'(&#(\d+);)')


def clear_html(text: typing.Any) -> str:
    clean_html = RegularExpressions.HTML_TEG_RE.sub('',
                                                    RegularExpressions.HTML_BR_RE.sub('\n', resp_to_str(text))).strip()
    for escape, ch in {*RegularExpressions.HTML_ESCAPE.findall(clean_html)}:
        clean_html = clean_html.replace(escape, chr(int(ch)))
    return clean_html


def resp_to_str(resp: ResponseOrSupportsStr) -> str:
    return (resp.read().decode('UTF-8') if isinstance(resp, HTTPResponse)
            else (resp if isinstance(resp, str)
                  else (resp.decode('UTF-8') if isinstance(resp, bytes)
                        else (str(resp)))))


def parse_extinf_format(extinf_line):
    if extinf_line.casefold().startswith('#extinf:'):
        extinf_line = extinf_line[8:]
    inf, name = extinf_line.split(',', 1)
    result = {}
    n, d = inf.split(' ', 1)
    result[0] = n
    d = [i for i in d.split('"') if i]
    for k, v in [d[i:i + 2] for i in range(0, len(d), 2)]:
        if v.isdigit():
            v = int(v)
        result[k.removesuffix('=').strip()] = v
    return name, result
