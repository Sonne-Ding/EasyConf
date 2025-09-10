from src.easyconf import easyconf, instantiate
import torch
from omegaconf import OmegaConf
from torchvision.models import resnet18

@easyconf("config", "gwcnet_SceneFlowFull_pretrain", instantiate_cfg=False)
def my_app(cfg):
    print(OmegaConf.to_yaml(cfg))
    model = resnet18()
    optimizer = instantiate(cfg.trainer.optimizer, params=model.parameters())
    print(optimizer)
    print(type(optimizer))
    torch.optim.lr_scheduler.StepLR()

if __name__ == "__main__":
    my_app()
    