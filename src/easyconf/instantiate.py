import importlib
from functools import partial
from typing import Any

from omegaconf import DictConfig, ListConfig, OmegaConf

def _locate(target: str) -> Any:
    module, name = target.rsplit(".", 1)
    return getattr(importlib.import_module(module), name)

def instantiate(cfg: Any, **kwargs) -> Any:
    """仅接受 DictConfig/ListConfig，递归实例化含 _target_ 的子树"""
    if isinstance(cfg, ListConfig):
        return [instantiate(x, **kwargs) for x in cfg]
    if isinstance(cfg, DictConfig) and "_target_" in cfg:
        # 当前层转容器，方便 pop / 调用
        cfg = OmegaConf.to_container(cfg, resolve=True)
        target = _locate(cfg.pop("_target_"))
        args   = cfg.pop("_args_", ())
        partial_flag = cfg.pop("_partial_", False)
        # 关键字参数再递归
        cfg = {k: instantiate(v) for k, v in cfg.items()}
        return (partial(target, *args, **cfg, **kwargs) if partial_flag
                else target(*args, **cfg, **kwargs))
    # 无 _target_ 的 DictConfig → 继续递归子树
    if isinstance(cfg, DictConfig):
        return {k: instantiate(v) for k, v in cfg.items()}
    # 标量
    return cfg