from easyconf import easyconf, instantiate

@easyconf("conf", "train", instantiate_cfg=True)
def main(cfg):
    model = cfg.model          # 已实例化
    print(model)

if __name__ == "__main__":
    main()