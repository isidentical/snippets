# Not Ready
from abc import ABC, abstractmethod
from enum import Enum

class Backend(ABC):
    @abstractmethod
    def get(self, key):
        pass

class Environment(Backend):
    import os
    
    get = os.environ.get

def __getattr__(config: str):
    import __main__
    settings = __main__.settings
    
    if config.startswith("__") and config.endswith("__"):
        return getattr(__main__, config, None)
    
    if hasattr(settings.Config, config):
        return getattr(settings.Config, config).value
    
    for backend in Backend.__subclasses__():
        if (value := backend.get(config)):
            return value
    else:
        raise LookupError(config)
        
def initalize():
    import __main__
    settings = __main__.settings

    if hasattr(settings, "Config"):
        items = {k: v for k, v in vars(settings.Config).items() if not (k.startswith("__") or k.endswith("__"))}
    else:
        items = {}
    
    __main__.settings.Config = Enum("Config", items)
