def parse():
    from argparse import ArgumentParser
    import os
    parser = ArgumentParser(description="EgoCL Loading Process")
    parser.add_argument('--num', type=int, default=-1, help='Number of items to process. 0 means all items.')
    parser.add_argument('--item_config', type=str, default=os.path.join(os.path.dirname(__file__),'item.yaml'), help='Path to the item config YAML file, default to the item.yaml file beside this script.')
    return parser.parse_args()

if __name__ == '__main__':
    args=parse()
    from EgoCL import loader, APP
    app = APP(loader(args))()