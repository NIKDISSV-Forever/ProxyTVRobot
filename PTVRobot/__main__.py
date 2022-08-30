from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

from PTVRobot import *


def _names_list(arg: str):
    if_file = Path(arg)
    if if_file.is_file():
        lines = if_file.read_text('UTF-8').splitlines()
    else:
        lines = arg.split(';')
    return {i for i in lines if i.strip()}


def main():
    arg_parser = argparse.ArgumentParser('PTVRobot')
    arg_parser.add_argument('-f', '--forever', action='store_true', help='Run the script again every cooldown seconds.')
    arg_parser.add_argument('-t', '--threading', action='store_true', default=True,
                            help='Send and parse the request for each playlist in a separate thread. (Default: True)')
    arg_parser.add_argument('-q', '--query', type=str,
                            help='Send only one request with the specified text. For example: "ch: HD" or "pl: aist"')
    arg_parser.add_argument('-cd', '--cooldown', type=float, default=1., help='Cooldown in seconds. (Default: 1)')
    arg_parser.add_argument('-x', '--proxy', type=str, help='Proxy <protocol>://<ip>')
    arg_parser.add_argument('-chf', '--channel-filters', type=_names_list,
                            help='Filters for received channels')
    arg_parser.add_argument('-pl', type=str, nargs='*', help='Playlist name(s)')
    arg_parser.add_argument('-o', '--output', type=str, help='Output .m3u(8) file. (Default: <stdout>)')
    args: argparse.Namespace = arg_parser.parse_args()
    if args.threading:
        from PTVRobot import ProxyTVRobotThreading as Robot
    else:
        from PTVRobot import ProxyTVRobot as Robot
    channel_filters: Iterable[str] | None = args.channel_filters
    query: str = args.query
    pl = args.pl
    if query:
        class Robot(Robot):
            __slots__ = ('end_extinf',)

            def on_start(self):
                self.end_extinf = Extinf()

            def during(self):
                self.end_extinf += self.search_engine(query).extinf()

    if channel_filters or pl:
        class Robot(Robot):
            __slots__ = ('plist', 'end_extinf')
            if pl:
                def on_start(self):
                    super().on_start()
                    self.plist = pl
            if channel_filters:
                def on_end(self):
                    def _filter(one_channel: OneChannel):
                        filters = ()
                        for filter_ in channel_filters:
                            line = filter_.startswith(':')
                            if line:
                                filter_ = filter_.removeprefix(':')
                            if filter_.startswith('#'):
                                filter_ = f".*{re.escape(filter_.removeprefix('#'))}.*"
                            filters += (re.compile(filter_.removeprefix('\\'), re.I), line),
                        for filter_, line in filters:
                            if filter_.match(f'{one_channel!s}\n\n'.splitlines()[line]):
                                return True
                        return False

                    self.end_extinf = self.end_extinf[_filter]
                    super().on_end()

    proxy = args.proxy
    out = args.output
    Robot(args.forever, args.cooldown, Srch(Proxy(*proxy.split('://', 1)[::-1])) if proxy else SearchEngine, out)


if __name__ == '__main__':
    main()
