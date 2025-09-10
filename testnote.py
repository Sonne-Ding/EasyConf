from omegaconf import OmegaConf


cfg = OmegaConf.create({"model": {"lr": 1e-3}, "debug": False})
cli = OmegaConf.from_cli()      # 捕获命令行
final = OmegaConf.merge(cfg, cli)
print(OmegaConf.to_yaml(final))