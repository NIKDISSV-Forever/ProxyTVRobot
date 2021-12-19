#### Documentation in Russian

**ProxyTVruAPI** - это API для сайта https://proxytv.ru/

А именно для поиска IPTV каналов.

## CLI

> python -m ProxyTVruAPI -h

## Python

```python
from ProxyTVruAPI import ProxyTVRobot

ProxyTVRobot(forever=True)
```

Или для многопоточного исполнения

```python
from ProxyTVruAPI import ProxyTVRobotThreading

ProxyTVRobotThreading(forever=True)
```

```python
def __init__(self,
             forever: bool = True,
             cooldown: float = 0.,
             search: Srch = SEARCH_ENGINE):
    ...
```

От обоих этих классов можно наследоваться и доработать функционал.

По умолчанию он будет пробигаться по всем плейлистам

И записывать в файл **'all-channels.m3u8'**.

Если forever указан _True_ то будет делать это по кругу

С задержков в _cooldown_ секунд.

### Srch

```python
class Srch:

    def __init__(self, proxy: Sequence[IP, PROTOCOL] = None):
        ...
```

Для **детальной** документациии всех функций и методов, воспользуйтесь *pydoc*
> python -m pydoc -w ProxyTVruAPI
