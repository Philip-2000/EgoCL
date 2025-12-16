def parse():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="EgoCL Unifying Manipulator")
    parser.add_argument('--item_config', type=str, default='', help='Path to the item config file.')
    return parser.parse_args()


if __name__ == '__main__':
    args=parse()
    from EgoCL import Manipulator
    Manipulator(**vars(args))()