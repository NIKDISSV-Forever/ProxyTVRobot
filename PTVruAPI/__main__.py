from __future__ import annotations

import argparse

from PTVruAPI import Srch, SearchEngine, Proxy


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', '--forever', action=argparse.BooleanOptionalAction)
    arg_parser.add_argument('-t', '--threading', action=argparse.BooleanOptionalAction, default=True)
    arg_parser.add_argument('-cd', '--cooldown', type=float, default=1., help='Cooldown in seconds. Default: 1')
    arg_parser.add_argument('-x', '--proxy', type=str, help='Proxy <protocol>://<ip>')
    args: argparse.Namespace = arg_parser.parse_args()
    if args.threading:
        from PTVruAPI import ProxyTVRobotThreading as Robot
    else:
        from PTVruAPI import ProxyTVRobot as Robot
    proxy = args.proxy
    Robot(args.forever, args.cooldown, Srch(Proxy(*proxy.split('://', 1)[::-1])) if proxy else SearchEngine)


if __name__ == '__main__':
    main()
