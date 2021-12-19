#### Documentation in Russian

> pip install [ProxyTVruAPI](https://pypi.org/project/ProxyTVruAPI/)

**ProxyTVruAPI** - это API для сайта https://proxytv.ru/

А именно для поиска IPTV каналов.

## В терминале

> python -m ProxyTVruAPI -h

## В коде

```python
from ProxyTVruAPI import ProxyTVRobot

ProxyTVRobot(forever=True)
```

Или для многопоточного исполнения

```python
from ProxyTVruAPI import ProxyTVRobotThreading

ProxyTVRobotThreading(forever=True)
```

От обоих этих классов можно наследоваться и доработать функционал.

По умолчанию он будет пробигаться по всем плейлистам

И записывать в файл **'all-channels.m3u8'**.

Если forever указан _True_ то будет делать это по кругу

С задержков в _cooldown_ секунд.

### Сигнатуры:

```python
class ProxyTVRobot:
    def __init__(self,
                 forever: bool = True,
                 cooldown: float = 0.,
                 search: Srch = SEARCH_ENGINE):
        ...
```

### Srch

```python
class Srch:

    def __init__(self, proxy: Sequence[IP, PROTOCOL] = None):
        ...
```

Для **детальной** документациии всех функций и методов, воспользуйтесь *pydoc*
> python -m pydoc -w ProxyTVruAPI
