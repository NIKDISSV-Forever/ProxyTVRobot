from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

from proxytv import Extinf, OneChannel, make_search


def _names_list(arg: str) -> set[str]:
    mb_file = Path(arg)
    return {*filter(str.strip, mb_file.read_text('UTF-8').splitlines() if mb_file.is_file() else arg.split(';'))}


def main():
    arg_parser = argparse.ArgumentParser('proxytv')
    arg_parser.add_argument('-f', '--forever', action='store_true', help='Run the script again every cooldown seconds.')
    arg_parser.add_argument('-t', '--threading', action='store_true',
                            help='Send and parse the request for each playlist in a separate thread. (Default: True)')
    arg_parser.add_argument('-q', '--query',
                            help='Send only one request with the specified text. For example: "ch: HD" or "pl: aist"')
    arg_parser.add_argument('-cd', '--cooldown', type=float, default=1., help='Cooldown in seconds. (Default: 1)')
    arg_parser.add_argument('-x', '--proxy', help='Proxy <protocol>://<ip>')
    arg_parser.add_argument('-chf', '--channel-filters', type=_names_list,
                            help='Filters for received channels')
    arg_parser.add_argument('-pl', nargs='*', help='Playlist name(s)')
    arg_parser.add_argument('-o', '--output', help='Output .m3u(8) file. (Default: <stdout>)')
    args: argparse.Namespace = arg_parser.parse_args()

    if args.threading:
        from proxytv import RobotThreading as Robot
    else:
        from proxytv import Robot
    channel_filters: Iterable[str] | None = args.channel_filters
    query: str = args.query
    pl = args.pl
    if query:
        class Robot(Robot):
            __slots__ = ()

            def on_start(self):
                self.end_extinf = Extinf()

            def during(self):
                self.end_extinf += self.search_engine(query).extinf()

    if channel_filters or pl:
        class Robot(Robot):
            __slots__ = ()

            if pl:
                def on_start(self):
                    super().on_start()
                    self.plist = pl
            if channel_filters:
                def on_end(self):
                    self.end_extinf = self.end_extinf[self._filter_extinf]
                    super().on_end()

                @staticmethod
                def _filter_extinf(one_channel: OneChannel) -> bool:
                    filters = ()
                    for filter_match in channel_filters:
                        filter_ip_address = filter_match.startswith(':')
                        if filter_ip_address:
                            filter_match = filter_match.removeprefix(':')
                        if filter_match.startswith('#'):
                            filter_match = f".*{re.escape(filter_match.removeprefix('#'))}.*"
                        filters += (re.compile(filter_match.removeprefix('\\'), re.I).match, filter_ip_address),
                    for filter_match, filter_ip_address in filters:
                        if filter_match(one_channel.address if filter_ip_address else one_channel.extinf_string):
                            return True
                    return False

    Robot(args.forever, args.cooldown, make_search(args.proxy), args.output)


if __name__ == '__main__':
    main()
