def parse():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="EgoCL Respond")
    parser.add_argument('--experience_name', type=str, default='default', help='Name of the experience.')
    parser.add_argument('--method_name', type=str, default='CheatMemorize', help='Name of the memory method.')
    parser.add_argument('--query', type=str, default="What is in the hands of C when he interacted with cats", help='Query string for retrieval.')
    return parser.parse_args()


if __name__ == '__main__':
    args=parse()
    from EgoCL import DumpRespond as R #R for Respond, and Re for Retrieve, because Respond is more frequently used than Retrieve
    r = R(experience_name=args.experience_name, method_name=args.method_name)(args.query)
    print(r)