"""递归解析 compose（相对目录版）"""
from pathlib import Path
from omegaconf import DictConfig, OmegaConf

def resolve_compose(cfg: DictConfig, base_dir: Path) -> DictConfig:
    if "compose" not in cfg:
        return cfg
    for item in cfg.compose:
        for key, stem in item.items():
            sub_yaml = base_dir / key / f"{stem}.yaml"
            if not sub_yaml.exists():
                print(f"[debug] compose missing: {sub_yaml}")
                raise FileNotFoundError(sub_yaml)
            sub_cfg = OmegaConf.load(sub_yaml)
            sub_cfg = resolve_compose(sub_cfg, sub_yaml.parent)
            cfg[key] = sub_cfg
    del cfg["compose"]
    return cfg