# PTVRobot

Robot for https://proxytv.ru/ (ProxyBot)

> pip install [PTVRobot](https://pypi.org/project/PTVRobot)

> python -m PTVRobot --help

```
usage: PTVRobot [-h] [-f] [-t] [-q QUERY] [-cd COOLDOWN] [-x PROXY] [-chf CHANNEL_FILTERS] [-pl [PL ...]] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  -f, --forever         Run the script again every cooldown seconds.
  -t, --threading       Send and parse the request for each playlist in a separate thread. (Default: True)
  -q QUERY, --query QUERY
                        Send only one request with the specified text. For example: "ch: HD" or "pl: aist"
  -cd COOLDOWN, --cooldown COOLDOWN
                        Cooldown in seconds. (Default: 1)
  -x PROXY, --proxy PROXY
                        Proxy <protocol>://<ip>
  -chf CHANNEL_FILTERS, --channel-filters CHANNEL_FILTERS
                        Filters for received channels
  -pl [PL ...]          Playlist name(s)
  -o OUTPUT, --output OUTPUT
                        Output .m3u(8) file. (Default: <stdout>)
```

---

Если запустить без доп. аргументов, будут получены все каналы, всех плейлистов (plist)
И записаны в файл output, по умолчание выведет результат в формате m3u в консоль.

Аругмент -pl: список плейлистов по которым будет происходить поиск, по умолчанию все доступные.

# Код

```python
from __future__ import annotations

import sys
import time
from multiprocessing.pool import ThreadPool
from typing import Iterable, SupportsFloat

from .extinf import *
from .search import *
from .static import *


class Robot:
    """A class describing a parser robot. Designed for inheritance."""

    __slots__ = ('end_extinf', 'plist', 'PLIST_LEN', 'search_engine', 'pl_number', 'output')
    sort_key = None  # sort channels

    def __init__(self, forever: bool = True, cooldown: SupportsFloat = 0.,
                 search: Srch = None, output=None, except_types=(Exception,)):
        """Runs the order of actions, if forever is true then it does it forever."""
        self.output = output or sys.stdout
        if not isinstance(cooldown, float):
            cooldown = float(cooldown)
        self.search_engine = search if search else SearchEngine
        self.post_init()
        if isinstance(except_types, Iterable):
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
                    time.sleep(cooldown)
                except except_types as e:
                    if no_keyboard_interrupt_except and isinstance(e, KeyboardInterrupt):
                        return
                    print(f'Error: {e}')
        try:
            self.loop()
        except except_types as e:
            if no_keyboard_interrupt_except and isinstance(e, KeyboardInterrupt):
                return
            print(f'Error: {e}')

    def post_init(self):
        """Execute after initialization."""
        pass

    def loop(self):
        self.on_start()
        self.during()
        self.on_end()

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
        """Sort by self.sort_key function and save"""
        self.end_extinf.data.sort(key=self.sort_key)
        ch_count = len(self.end_extinf)
        print(f"Saving {ch_count} channel{'' if ch_count == 1 else 's'}")
        self.upload(save_extinf(self.end_extinf, self.output))

    def upload(self, fn: str):
        """Used to upload files to a remote host, used in on_end."""
        pass


class RobotThreading(Robot):
    """An example of implementing your own robot, with multithreading"""
    __slots__ = ('end_extinf', 'pl_number')

    def during(self):
        """Creates threads to search for each playlist."""
        with ThreadPool() as pool:
            pool.map(self.search_pl, self.plist)
```

Классы для наследования, при написании более сложных роботов.

# Фильтры

Аргумент --channel-filters принимает файл с фильтрами в формате регулярного выражения,
применяемого к выходному m3u формату

Существуют некоторое упрощения для более быстрого составления файла фильтров.
Напомню, выходной m3u формат выглядит примерно так:

```m3u8
#EXTINF:-1 tvch-id="40025" group-title="ДЕТСКИЕ",DISNEY CHANNEL-40025
http://93.158.224.2:4022/udp/239.3.100.85:4321
```

Каждая строка в файле фильтров представляет собой фильтр в особом формате.

Чтобы канал прошёл фильтрацию, необходимо чтобы как минимум один фильтр к нему подошёл.

1. <kbd>\\</kbd> в начале строки всегда обрезается

2. Чтобы фильтровать IP адреса (вторую строку), фильтр должен начинаться со знака <kbd>:</kbd>

3. Чтобы проверить на присутствие подстроки в строке, фильтр должен начинаться с <kbd>#</kbd>

4. Или любое регулярное выражение (при использовании <kbd>#</kbd> регулярное выражение не применяется, строка
   экранируется), если строка начинается с <kbd>:</kbd>, регулярное выражение по-прежнему проверяется, но уже на IP
5. Все филтры не чувствительны к регистру (``re.IGNORECASE``)

---

Было:

```regexp
\:-1
```

Стало:

```regexp
:-1
```

---

```regexp
:.+:4022.+
```

Найти все IP с портом 1234

[http://93.158.224.2:<kbd>4022</kbd>/udp/239.3.100.85:4321](http://93.158.224.2:4022/udp/239.3.100.85:4321)

---

```regexp
:#:4321
```

```regexp
:.*:4321.*
```

[http://93.158.224.2:4022/udp/239.3.100.85<kbd>:4321</kbd>](http://93.158.224.2:4022/udp/239.3.100.85:4321)

---

```regexp
#group-title="ДЕТСКИЕ"
```

```regexp
.*group-title="ДЕТСКИЕ".*
```

Найти все каналы в группе детских

#EXTINF:-1 tvch-id="40025" <kbd>group-title="ДЕТСКИЕ"</kbd>,DISNEY CHANNEL-40025

---

```regexp
#HD
```

```regexp
.*HD.*
```

``Тоже что и -q "ch:HD" аргумет``

#EXTINF:-1 tvch-id="46046" group-title="ИНФ/РАЗВЛЕКАТЕЛЬНЫЕ",РОССИЯ 1 <kbd>HD</kbd>-46046

---
**Пример составления нужного плейлиста:**

filters.txt

```regexp
#NICKELODEON HD
#CARTOON NETWORK
#Рен ТВ
#ТНТ HD
#Пятница
#Россия 24
```

> python -m PTVRobot -chf filters.txt -f -cd 120 -o tv.m3u8

Каждые 2 минуты будет обновляться файл tv.m3u8 с перечисленными выше каналами.

---

_Вопросы задавайте на GitHub, на почту или загляните в исходный код, там всё прозрачно._