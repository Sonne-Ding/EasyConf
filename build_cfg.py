from pathlib import Path
from omegaconf import OmegaConf, DictConfig

def _resolve_compose(cfg: DictConfig, base_dir: Path) -> DictConfig:
    """base_dir：当前 yaml 所在文件夹"""
    if "compose" not in cfg:
        return cfg

    for item in cfg.compose:          # List[Dict[str,str]]
        for sub_key, stem in item.items():
            # 1. 子配置必须放在 base_dir / sub_key / <stem>.yaml
            sub_yaml = base_dir / sub_key / f"{stem}.yaml"
            if not sub_yaml.exists():
                raise FileNotFoundError(sub_yaml)

            # 2. 读 + 递归（以子文件夹为新基准）
            sub_cfg = OmegaConf.load(sub_yaml)
            sub_cfg = _resolve_compose(sub_cfg, sub_yaml.parent)

            # 3. 挂到当前 cfg.sub_key 下
            cfg[sub_key] = sub_cfg

    del cfg["compose"]
    return cfg

def load_config(entry_yaml: Path) -> DictConfig:
    return _resolve_compose(OmegaConf.load(entry_yaml), entry_yaml.parent)

# ---------------- 入口 ----------------
if __name__ == "__main__":
    final = load_config(Path("config/base1.yaml"))
    print(OmegaConf.to_yaml(final))
