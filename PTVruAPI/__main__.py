if __name__ == '__main__':
    from argparse import ArgumentParser, Namespace
    from . import Srch, SearchEngine, Proxy

    arg_parser = ArgumentParser()
    arg_parser.add_argument('-f', '--forever', action='store_true')
    arg_parser.add_argument('-t', '--threading', action='store_true')
    arg_parser.add_argument('-cd', '--cooldown', type=float, default=1., help='Cooldown in seconds. Default: 1')
    arg_parser.add_argument('-x', '--proxy', type=str, help='Proxy <protocol>://<ip>')
    args: Namespace = arg_parser.parse_args()
    if args.threading:
        from . import ProxyTVRobotThreading as Robot
    else:
        from . import ProxyTVRobot as Robot
    proxy = args.proxy
    Robot(args.forever, args.cooldown, Srch(Proxy(*proxy.split('://', 1)[::-1])) if proxy else SearchEngine)
