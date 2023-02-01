# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from http.client import HTTPResponse


class RegularExpressions:
    __slots__ = ()
    PROVIDER_RE: re.Pattern = re.compile(r'робот "(.+)"')
    PLIST_RE: re.Pattern = re.compile(r'плейлист "(.+)"')
    EXTINF_RE: re.Pattern = re.compile(r'(#EXTINF:.+)\n(.+$)', re.M)
    HTML_TEG_RE: re.Pattern = re.compile(r'<.+?>')
    HTML_BR_RE: re.Pattern = re.compile(r'<br>', re.I)
    CH_NAME_WITH_TVCH_ID: re.Pattern = re.compile(r'(.+)-(\d+)$')
    HTML_ESCAPE = re.compile(r'(&#(\d+);)')


def _clear_html(text) -> str:
    clean_html = RegularExpressions.HTML_TEG_RE.sub('',
                                                    RegularExpressions.HTML_BR_RE.sub('\n', _resp_to_str(text))).strip()
    for escape, ch in {*RegularExpressions.HTML_ESCAPE.findall(clean_html)}:
        clean_html = clean_html.replace(escape, chr(int(ch)))
    return clean_html


def _resp_to_str(resp) -> str:
    if isinstance(resp, HTTPResponse):
        resp = resp.read()
    if not isinstance(resp, str):
        resp = resp.decode('UTF-8') if isinstance(resp, (bytes, bytearray)) else str(resp)
    return resp
