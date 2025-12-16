def parse():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="EgoCL Experience Concatenator")
    parser.add_argument('--item_config', type=str, default='', help='Path to the item file.')
    parser.add_argument('--style', type=str, default='sequential', help='Concatenation style: sequential, random, clip.')
    parser.add_argument('--clip', type=int, default=-1, help='Number of clips to select if style is clip.')
    parser.add_argument('--name', type=str, default='concatenated_experience', help='Name of the output experience.')
    return parser.parse_args()


if __name__ == '__main__':
    args=parse()
    from EgoCL import Concatenator as C
    E = C(**vars(args))(args.item_config)
    E.name = args.name
    E.save()