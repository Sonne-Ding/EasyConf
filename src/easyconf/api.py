"""装饰器 + CLI 入口"""
import sys
from pathlib import Path
from functools import wraps
from typing import Any, Callable

from omegaconf import OmegaConf, DictConfig, ListConfig

from .compose import resolve_compose
from .instantiate import instantiate

def easyconf(
    config_path: str,
    config_name: str,
    *,
    resolve: bool = True,
    instantiate_cfg: bool = False,
) -> Callable[..., Any]:
    """
    用法：
        @easyconf("conf", "train")
        def main(cfg: DictConfig) -> None:
            ...
    命令行：
        python main.py lr=0.02 model.name=vit
    额外开关：
        instantiate_cfg=True  自动递归实例化含 __target__ 的子树
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # # 1. 加载主配置
            # yaml_file = Path(config_path) / f"{config_name}.yaml"
            # if not yaml_file.exists():
            #     raise FileNotFoundError(yaml_file)
            # cfg = OmegaConf.load(yaml_file)

            # # 2. 处理 compose
            # cfg = resolve_compose(cfg, yaml_file.parent)

            # # 3. 命令行覆盖（支持 -h / --help）
            # cli_args = sys.argv[1:]
            # if {"-h", "--help"} & set(cli_args):
            #     print("== Configuration Template ==")
            #     print(OmegaConf.to_yaml(cfg))
            #     sys.exit(0)
            # cli_cfg = OmegaConf.from_cli(cli_args)
            # cfg = OmegaConf.merge(cfg, cli_cfg)
            # 0. 加载主配置
            yaml_file = Path(config_path) / f"{config_name}.yaml"
            cfg = OmegaConf.load(yaml_file)
            cfg = resolve_compose(cfg, yaml_file.parent)      # 先走默认 compose
            # 1. 提取显式 compose.* 参数
            base_dir = yaml_file.parent
            cli_raw  = sys.argv[1:]
            compose_cli = {}
            normal_cli  = []
            for arg in cli_raw:
                if arg.startswith("compose."):
                    # compose.data.imgReader=D1reader  →  data.imgReader=D1reader
                    path_val = arg[8:]                      # 去掉 compose.
                    path, val = path_val.split("=", 1)
                    compose_cli[path] = val
                else:
                    normal_cli.append(arg)
            # 2. 正常 key=value 合并
            if normal_cli:
                cfg = OmegaConf.merge(cfg, OmegaConf.from_cli(normal_cli))
            # 3. 处理显式 compose 参数
            for mount_path, stem in compose_cli.items():
                # 分解挂载路径  data.imgReader  →  ["data", "imgReader"]
                folder_parts = mount_path.split(".")          # ← 新增
                sub_dir  = base_dir.joinpath(*folder_parts)   # ← 修正
                yaml_p  = sub_dir / f"{stem}.yaml"
                if not yaml_p.exists():
                    raise FileNotFoundError(yaml_p)
                # 加载 → 递归 compose → 挂载到指定节点
                sub_cfg = OmegaConf.load(yaml_p)
                sub_cfg = resolve_compose(sub_cfg, yaml_p.parent)
                OmegaConf.set_struct(cfg, False)          # 允许写入
                # OmegaConf.update(cfg, mount_path, sub_cfg)  # 整枝覆盖
                # update
                parent = OmegaConf.select(cfg, ".".join(folder_parts[:-1]))
                key = folder_parts[-1]
                parent.pop(key, None)          # 彻底删除旧枝
                parent[key] = sub_cfg          # 插上全新枝
            # 4. 可选：全局实例化
            if instantiate_cfg:
                cfg = instantiate(cfg)  # type: ignore
            # 5. 注入函数
            return func(cfg, *args, **kwargs)

        return wrapper

    return decorator