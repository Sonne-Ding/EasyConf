"""EasyConf: mini-Hydra made simple."""
from .api import easyconf
from .instantiate import instantiate

__all__ = ["easyconf", "instantiate"]
__version__ = "0.1.0"