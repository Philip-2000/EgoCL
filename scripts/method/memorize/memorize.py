def parse():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="EgoCL Memorize")
    parser.add_argument('--file', type=bool, default=True, help='Construct Experience from file (True) or from concatenation (False).')
    #if file from file
    parser.add_argument('--experience_name', type=str, default='Unnamed_1117_11_38_12', help='Name of the experience file to load.')

    #else from concatenation
    parser.add_argument('--item_config', type=str, default='', help='Path to the item file.')
    parser.add_argument('--style', type=str, default='sequential', help='Concatenation style: sequential, random, clip.')
    parser.add_argument('--clip', type=int, default=-1, help='Number of clips to select if style is clip.')
    return parser.parse_args()


if __name__ == '__main__':
    args=parse()
    if args.file:
        from EgoCL import Experience as Eprc
        E = Eprc.load_from_name(args.experience_name)
    else:
        from EgoCL import Concatenator as C
        E = C(**vars(args))(args.item_config, durations=[520.0])
    
    from EgoCL import CheatMemorize as M
    m = M()(E) #saved in this __call__ function (with parameter "save" defaulted to True)
    print(m)
    