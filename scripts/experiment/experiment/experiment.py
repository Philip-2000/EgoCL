def parse():
    import argparse, os
    parser = argparse.ArgumentParser(description="Run an experiment based on a JSON configuration file.")
    parser.add_argument("-c","--config_path", type=str, default=None, help="Path to the experiment configuration JSON file.")
    parser.add_argument("-m","--method", type=str, default="Video", help="Method YAML name to use if config_path is not provided.")
    parser.add_argument("-e","--experience", type=str, default="EgoLifeQA_J", help="Experience YAML name to use if config_path is not provided.")
    return parser.parse_args()


if __name__ == "__main__":
    from EgoCL import Experiment
    args = parse()
    E = Experiment(config_path=args.config_path, method_yaml_name=args.method, experience_yaml_name=args.experience)
    E()