from threading import Thread
from time import sleep

from .ExtinfParse import *
from .Search import *
from .Types import EXTINF_DATA
from .static import parse_extinf_format

__all__ = (
    'ProxyTVRobot', 'ProxyTVRobotThreading', 'Extinf', 'Srch', 'save_extinf', 'parse_extinf_format', 'SEARCH_ENGINE'
)

SEARCH_ENGINE = Srch()


class ProxyTVRobot:
    """A class describing a parser robot. Designed for inheritance."""

    __slots__ = 'end_extinf', 'plist', 'plist_len', 'search_engine'

    def __init__(self, forever: bool = True, cooldown: float = 0., search: Srch = SEARCH_ENGINE):
        """Runs the order of actions, if forever is true then it does it forever."""
        self.search_engine = search
        if forever:
            while True:
                try:
                    self._loop()
                    sleep(cooldown)
                except KeyboardInterrupt:
                    return
                except Exception as e:
                    print('Error:', e)
        else:
            try:
                self._loop()
            except KeyboardInterrupt:
                return

    def _loop(self):
        self.on_start()
        self.during()
        self.on_end()

    # noinspection PyAttributeOutsideInit
    def on_start(self):
        """Initial actions."""
        self.end_extinf = Extinf()
        self.plist = self.search_engine.plist()
        self.plist_len = len(self.plist)

    def during(self):
        """Actions in the middle of the process."""
        plist_len = self.plist_len
        for i, pl_name in enumerate(self.plist, 1):
            pl = self.search_engine.pl(pl_name)
            print(f'Pl: {pl_name} ({i}/{plist_len}) Channels: {len(pl)}')
            self.end_extinf += pl

    def on_end(self):
        """Completion Actions"""
        self.upload(save_extinf(self.end_extinf, 'all-channels.m3u8'))

    def upload(self, fn: str):
        """Used to upload files to a remote host, used in on_end."""
        pass

    def __del__(self):
        """When you exit the program."""
        pass


class ProxyTVRobotThreading(ProxyTVRobot):
    """An example of implementing your own robot, with multithreading"""
    __slots__ = 'end_extinf', 'pl_i'

    def search_pl(self, pl_name: str):
        """Method for adding a playlist to a shared Extinf object in multi-threaded mode"""
        pl = self.search_engine.pl(pl_name)
        self.end_extinf += pl
        print(f'Pl: {pl_name} ({self.pl_i}/{self.plist_len}) Channels: {len(pl)}')
        self.pl_i += 1

    def on_start(self):
        super().on_start()
        self.pl_i = 1

    def during(self):
        """Creates streams to search for each playlist."""
        threads = ()
        for pl_name in self.plist:
            threads += Thread(target=self.search_pl, args=(pl_name,)),
            threads[-1].start()
        for th in threads:
            th.join()

    @staticmethod
    def sort_key(extinf: EXTINF_DATA):
        return parse_extinf_format(extinf[0])[1].get('group-title', '')

    def on_end(self):
        """Sort by self.sort_key function and save."""
        self.end_extinf.data.sort(key=self.sort_key)
        super().on_end()
