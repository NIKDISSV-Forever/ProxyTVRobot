from threading import Thread
from time import sleep

from .ExtinfParse import *
from .Search import *
from .Types import ExtinfData
from .static import parse_extinf_format

__all__ = (
    'ProxyTVRobot', 'ProxyTVRobotThreading',
    'Extinf', 'Srch', 'SearchEngine',
    'save_extinf', 'parse_extinf_format',
    'Proxy'
)

SearchEngine = Srch()


class ProxyTVRobot:
    """A class describing a parser robot. Designed for inheritance."""

    __slots__ = 'end_extinf', 'plist', 'PLIST_LEN', 'search_engine'

    def __init__(self, forever: bool = True, cooldown: float = 0., search: Srch = None):
        """Runs the order of actions, if forever is true then it does it forever."""
        self.search_engine = search if search else SearchEngine
        self.__post_init__()
        if forever:
            while True:
                try:
                    self.loop()
                    sleep(cooldown)
                except KeyboardInterrupt:
                    return
                except Exception as e:
                    print('Error:', e)
        else:
            try:
                self.loop()
            except KeyboardInterrupt:
                return

    def __post_init__(self):
        """Execute after initialization."""
        pass

    def loop(self):
        self.on_start()
        self.during()
        self.on_end()

    # noinspection PyAttributeOutsideInit
    def on_start(self):
        """Initial actions."""
        self.end_extinf = Extinf()
        self.plist = self.search_engine.plist()
        self.PLIST_LEN = len(self.plist)

    def during(self):
        """Actions in the middle of the process."""
        plist_len = self.PLIST_LEN
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
        print(f'Pl: {pl_name} ({self.pl_i}/{self.PLIST_LEN}) Channels: {len(pl)}')
        self.pl_i += 1

    def on_start(self):
        super().on_start()
        # noinspection PyAttributeOutsideInit
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
    def sort_key(extinf: ExtinfData):
        return parse_extinf_format(extinf[0])[1].get('group-title', '')

    def on_end(self):
        """Sort by self.sort_key function and save."""
        self.end_extinf.data.sort(key=self.sort_key)
        super().on_end()
