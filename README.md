#### Documentation in Russian

> pip install [ProxyTVruAPI](https://pypi.org/project/ProxyTVruAPI/)

**ProxyTVruAPI** - это API для сайта https://proxytv.ru/

А именно для поиска IPTV каналов.

# CLI

> python -m ProxyTVruAPI -h

# Базовое использование:

```python
from ProxyTVruAPI import *

USE_THREADS = True
FOREVER = True
COOLDOWN = 60.  # Минута.
PROXY = Proxy(host='199.19.225.54:3128', protocol='https')  # Не обязательно

if __name__ == '__main__':
    Robot = ProxyTVRobotThreading if USE_THREADS else ProxyTVRobot
    Robot(FOREVER, COOLDOWN,
          Srch(PROXY)
          )
```

# Простой поиск канала

```python
from ProxyTVruAPI import SearchEngine

print(SearchEngine.ch('VIASAT HISTORY HD'
                      )[{'tvch-id': '7171'}])
# Тоже что и
print(SearchEngine.ch('VIASAT HISTORY HD'
                      )['VIASAT HISTORY HD-7171'])
```

### Вывод:

```python
# Тип:
list[tuple[tuple[str, dict[str | int, Any]], str]]

[(
    ('VIASAT HISTORY HD-7171',
     {0: -1, 'tvch-id': '7171', 'group-title': 'ПОЗНАВАТЕЛЬНЫЕ'}),
    'http://...:.../udp/...:...'
)]
```

## Определить своего бота парсера.

```python
"""
Предположим,
Вам захотелось переспотреть все детские и развлекательные каналы на свете.
И вы хотите робота, который вам их соберёт.
Наследуемся от ProxyTVRobot и творим!
"""
from ProxyTVruAPI import *


class MyProxyTVRobot(ProxyTVRobot):
    __slots__ = 'extinf', 'GROUPS'

    def __post_init__(self):
        """
        Здесь определяют константы
        Или выполняют то, что нужно выполнить только в начале
        """
        # Константа с группами... (Для удобного расширения)
        self.GROUPS = 'Детские', 'Развлекательные'

    def on_start(self):
        """Всяческие подготовки, объявления переменных и т.п"""
        self.extinf = Extinf()
        # В self.extinf добавим все каналы из группы.

    def during(self):
        """
        Самая важная часть. Обращение к поисковику.
        Который любезно придоставит нам все UDP в группе 
        'Детские' и 'Развлекательные'
        """
        for group in self.GROUPS:
            # Воспользуемся self.search_engine созданом при инициализации.
            found = self.search_engine.gr(group)
            self.extinf += found  # Добавим его ко всем.
            print(f'Gr: {group.upper()} | Channels: {len(found)}')

    def on_end(self):
        """Функция on_end от родителя сохраняла бы всё в 'all-channels.m3u8'
        И пыталась бы загрузить это куда-то, используя метод self.upload()"""
        save_extinf(self.extinf, 'look-at-leisure.m3u8')


if __name__ == '__main__':
    MyProxyTVRobot(cooldown=120.)  # Каждые две минуты обновлять плейлист.

# Ещё одним примером кастомного робота является ProxyTVRobotThreading.
# Если этого примера не хватило, взгляните на исходный код __init__.py
```

### ```class ProxyTVRobot и ProxyTVRobotThreading```

```python
SearchEngine = Srch()


class ProxyTVRobot:
    """A class describing a parser robot. Designed for inheritance."""

    __slots__ = 'end_extinf', 'plist', 'plist_len', 'search_engine'

    def __init__(self,
                 forever: bool = True,
                 cooldown: float = 0.,
                 search: Srch = None):
        """Runs the order of actions, if forever is true then it does it forever."""
        ...

    def loop(self):
        self.on_start()
        self.during()
        self.on_end()

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


class ProxyTVRobotThreading(ProxyTVRobot): ...
```

### ```class Srch и Proxy```

```python
@dataclass
class Proxy:
    host: str = None
    protocol: str = None

    def __bool__(self) -> bool: ...


class Srch:
    proxy = property(...)

    def __init__(self, proxy: Proxy = Proxy()) -> None: ...

    def __call__(self, query) -> Extinf: ...

    def help(self) -> str: ...

    def providers(self) -> LIST_OF_STR: ...

    def plist(self) -> LIST_OF_STR: ...

    def ch(self, query: SupportsStr) -> Extinf: ...

    def pl(self, query: SupportsStr) -> Extinf: ...

    def gr(self, query: SupportsStr) -> Extinf: ...
```

### ```class Extinf и def save_extinf```

```python
class Extinf:
    """The class represents information from the m3u8 format."""

    def __init__(self,
                 data: EXTINF_DATA = None,
                 author: str = 'NIKDISSV') -> None:
        ...

    def __getitem__(self, find: typing.Union[str, ExtinfFormatInfDict]) -> Optional[list[OneChannel]]:
        """
        Will find an item with a suitable name (For example self['VIASAT HISTORY HD-7171'])
        Or with matching information (For example self[{'tech-id': '7171'}])
        """
        ...

    def __iter__(self) -> Iterator[OneChannel]: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __len__(self) -> int: ...  # Количество источников.

    def __iadd__(self, other): ...  # +=

    def __add__(self, other): ...  # +

    def __bool__(self) -> bool: ...


def save_extinf(extinf: Extinf = Extinf(),
                file: Union[TextIO, str] = None,
                only_ip: bool = False) -> str:
    """Save m3u8 to the specified file from the class."""
    ...
```
