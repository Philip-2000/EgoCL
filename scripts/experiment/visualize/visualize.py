def parse():
    import argparse, os
    parser = argparse.ArgumentParser(description="Visualization Experiment Runner")
    parser.add_argument("-e", "--experience_name", type=str, default="EgoLifeQA_A1_J", help="Name of the experience to visualize.")
    parser.add_argument("-m", "--method", type=str, default="VideoMethod", help="Name of the method whose results to visualize.")
    return parser.parse_args()


if __name__ == "__main__":
    from EgoCL import Visualize
    args = parse()
    V = Visualize(Experience_name=args.experience_name, Method=args.method)
    V()