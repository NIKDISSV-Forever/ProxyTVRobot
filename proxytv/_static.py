# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from http.client import HTTPResponse

__all__ = ('RegularExpressions', 'clear_html', 'resp_to_str')


class RegularExpressions:
    __slots__ = ()
    PROVIDER: re.Pattern = re.compile(r'робот "([^"]+)"')
    PLIST: re.Pattern = re.compile(r'плейлист "([^"]+)"')
    EXTINF_FAST: re.Pattern = re.compile(r'(#EXTINF:[^\n]+)\n(.+$)', re.M | re.I)
    EXTINF_DETAILS: re.Pattern = re.compile(r'#EXTINF:(-?\d+)\s*([^,]*)\s*,\s*([\S\s]+)\s*', re.I)
    EXTINF_ATTRS: re.Pattern = re.compile(r'\s*([^=]+)="([^"]+)"\s*')
    HTML_TEG: re.Pattern = re.compile(r'<[^>]+?>')
    HTML_BR: re.Pattern = re.compile(r'<br>', re.I)
    CH_NAME_WITH_TVCH_ID: re.Pattern = re.compile(r'([\s\S]+)-(\d+)$')
    HTML_ESCAPE: re.Pattern = re.compile(r'(&#(\d+);)')


def clear_html(text) -> str:
    clean_html = RegularExpressions.HTML_TEG.sub('',
                                                 RegularExpressions.HTML_BR.sub('\n', resp_to_str(text))).strip()
    for escape, ch in {*RegularExpressions.HTML_ESCAPE.findall(clean_html)}:
        clean_html = clean_html.replace(escape, chr(int(ch)))
    return clean_html


def resp_to_str(resp) -> str:
    if isinstance(resp, HTTPResponse):
        resp = resp.read()
    if not isinstance(resp, str):
        resp = resp.decode('UTF-8') if isinstance(resp, (bytes, bytearray)) else str(resp)
    return resp
