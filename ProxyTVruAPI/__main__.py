if __name__ == '__main__':
    from argparse import ArgumentParser, Namespace
    from . import Srch, SEARCH_ENGINE

    arg_parser = ArgumentParser()
    arg_parser.add_argument('--forever', action='store_true')
    arg_parser.add_argument('--threading', action='store_true')
    arg_parser.add_argument('--cooldown', type=float, default=1., help='Cooldown in seconds. Default: 1')
    arg_parser.add_argument('--proxy', type=str, help='Proxy <protocol>://<ip>')
    args: Namespace = arg_parser.parse_args()
    if args.threading:
        from . import ProxyTVRobotThreading as Robot
    else:
        from . import ProxyTVRobot as Robot
    proxy = args.proxy
    if proxy:
        SE = Srch(proxy.split('://', 1)[::-1])
    else:
        SE = SEARCH_ENGINE
    Robot(args.forever, args.cooldown, SE)
