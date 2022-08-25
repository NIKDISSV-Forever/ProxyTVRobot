from __future__ import annotations

import argparse
from pathlib import Path

from PTVRobot import Proxy, SearchEngine, Srch


def _names_list(arg: str):
    if_file = Path(arg)
    if if_file.is_file():
        lines = if_file.read_text('UTF-8').splitlines()
    else:
        lines = arg.split(';')
    return {i.strip().casefold() for i in lines if i.strip()}


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', '--forever', action='store_true')
    arg_parser.add_argument('-t', '--threading', action='store_true', default=True)
    arg_parser.add_argument('-cd', '--cooldown', type=float, default=1., help='Cooldown in seconds. Default: 1')
    arg_parser.add_argument('-x', '--proxy', type=str, help='Proxy <protocol>://<ip>')
    arg_parser.add_argument('-chn', '--channel-names', type=_names_list,
                            help='Name of the file with filters for channels.')
    arg_parser.add_argument('-pl', type=str, nargs='*', help='Playlist name(s)')
    arg_parser.add_argument('-o', '--output', type=str)
    args: argparse.Namespace = arg_parser.parse_args()
    if args.threading:
        from PTVRobot import ProxyTVRobotThreading as Robot
    else:
        from PTVRobot import ProxyTVRobot as Robot
    channel_names = args.channel_names
    pl = args.pl
    if channel_names or pl:
        class Robot(Robot):
            if pl:
                def on_start(self):
                    super().on_start()
                    self.plist = pl
            if channel_names:
                def on_end(self):
                    def _filter(one_channel):
                        ch_name = one_channel.name.strip().casefold()
                        for name in channel_names:
                            if name in ch_name:
                                return True
                        return False

                    self.end_extinf = self.end_extinf[_filter]
                    super().on_end()

    proxy = args.proxy
    out = args.output
    Robot(args.forever, args.cooldown, Srch(Proxy(*proxy.split('://', 1)[::-1])) if proxy else SearchEngine, out)


if __name__ == '__main__':
    main()
