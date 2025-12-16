def parse():
    import argparse, os
    parser = argparse.ArgumentParser(description="Run an experiment based on a JSON configuration file.")
    parser.add_argument("-c","--config_path", type=str, default=os.path.join(os.path.dirname(__file__),"experiment.yaml"), help="Path to the experiment configuration JSON file.")
    return parser.parse_args()


if __name__ == "__main__":
    import yaml
    from EgoCL.experiment import Experiment
    args = parse()
    E = Experiment(yaml.safe_load(open(args.config_path)))
    E()