from __future__ import annotations

import sys
from multiprocessing.pool import ThreadPool
from time import sleep

from PTVRobot.ExtinfParse import *
from PTVRobot.Search import *
from PTVRobot.Types import *
from PTVRobot.static import parse_extinf_format

__all__ = (
    'ProxyTVRobot', 'ProxyTVRobotThreading',
    'Extinf', 'Srch', 'SearchEngine',
    'save_extinf', 'parse_extinf_format',
    'Proxy'
)

SearchEngine = Srch()


class ProxyTVRobot:
    """A class describing a parser robot. Designed for inheritance."""

    __slots__ = ('end_extinf', 'plist', 'PLIST_LEN', 'search_engine', 'pl_number', 'output')

    def __init__(self, forever: bool = True, cooldown: typing.SupportsFloat = 0.,
                 search: Srch = None, output=None, except_types=(Exception,)):
        """Runs the order of actions, if forever is true then it does it forever."""
        self.output = output or sys.stdout
        if not isinstance(cooldown, float):
            cooldown = float(cooldown)
        self.search_engine = search if search else SearchEngine
        self.post_init()
        if isinstance(except_types, typing.Iterable):
            if not isinstance(except_types, tuple):
                except_types = (*except_types,)
        elif issubclass(except_types, BaseException):
            except_types = except_types,
        no_keyboard_interrupt_except = KeyboardInterrupt not in except_types
        if no_keyboard_interrupt_except:
            except_types += KeyboardInterrupt,
        if forever:
            while True:
                try:
                    self.loop()
                    sleep(cooldown)
                except except_types as e:
                    if no_keyboard_interrupt_except and isinstance(e, KeyboardInterrupt):
                        return
                    print(f'Error: {e}')
        else:
            try:
                self.loop()
            except KeyboardInterrupt:
                return

    def post_init(self):
        """Execute after initialization."""
        pass

    def loop(self):
        self.on_start()
        self.during()
        self.on_end()

    # noinspection PyAttributeOutsideInit
    def on_start(self):
        """Initial actions."""
        self.plist = self.search_engine.plist()
        self.PLIST_LEN = len(self.plist)
        self.end_extinf = Extinf()
        self.pl_number = 1

    def search_pl(self, pl_name: str):
        pl = self.search_engine.pl(pl_name)
        print(f'Pl: {pl_name} ({self.pl_number}/{self.PLIST_LEN}) Channels: {len(pl)}')
        self.end_extinf += pl
        self.pl_number += 1

    def during(self):
        """Actions in the middle of the process."""
        for pl_name in self.plist:
            self.search_pl(pl_name)

    def on_end(self):
        """Completion Actions"""
        self.end_extinf.data = sorted(self.end_extinf.data)
        self.upload(save_extinf(self.end_extinf, self.output))

    def upload(self, fn: str):
        """Used to upload files to a remote host, used in on_end."""
        pass

    def __del__(self):
        """When you exit the program."""
        pass


class ProxyTVRobotThreading(ProxyTVRobot):
    """An example of implementing your own robot, with multithreading"""
    __slots__ = ('end_extinf', 'pl_number')

    def during(self):
        """Creates threads to search for each playlist."""
        with ThreadPool() as pool:
            pool.map(self.search_pl, self.plist)

    @staticmethod
    def sort_key(extinf: OneChannel):
        return extinf.info.get('group-title', '')

    def on_end(self):
        """Sort by self.sort_key function and save."""
        self.end_extinf.data.sort(key=self.sort_key)
        super().on_end()