
def parse():
    import argparse
    parser = argparse.ArgumentParser(description="Execute an experiment's execution.")
    parser.add_argument('--experiment_name', type=str, default="bin_1", help="Name of the experiment.")
    parser.add_argument('--execution_name', type=str, default="testing", help="Name of the execution to run.")
    parser.add_argument('--method', type=str, default="DumpMethod", help="Name of the method to use for execution.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse()
    from EgoCL import Execution, Experience
    En = Execution(name=args.execution_name, load_style="FORCE_CREATE", load_style_questions="FORCE_CREATE")
    Ee = Experience.load_from_name(experience_name=args.experiment_name)
    En.EXPERIENCE = Ee
    En.load()

    En(METHOD=getattr(__import__("EgoCL.method", fromlist=[args.method]), args.method)())
