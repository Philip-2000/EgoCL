# def parse():
#     import argparse, os
#     parser = argparse.ArgumentParser(description="Answering Experiment Runner")
#     parser.add_argument("-c","--config_path", type=str, default=os.path.join(os.path.dirname(__file__),"experiment.yaml"), help="Path to the experiment configuration JSON file.")
#     parser.add_argument("-q","--q_list", type=str, default="all", help="Comma-separated list of question IDs to answer, or 'all' for all questions.")
#     return parser.parse_args()

# if __name__ == "__main__":
#     from EgoCL import Answering, Experience
#     args = parse()
#     import yaml
#     exp_config = yaml.safe_load(open(args.config_path))
    
#     E = Experience.load_from_name(experience_name=exp_config["EXPERIENCES"][0])
#     E.EGO = exp_config.get("EGO", True)
#     A = Answering(name=exp_config["EXECUTIONS"], EXPERIENCE=E, q_list=args.q_list.split(",") if args.q_list != "all" else "all", load_style=exp_config.get("LOAD_STYLES", "FORCE_LOAD"), load_style_questions=exp_config.get("LOAD_STYLE_QUESTIONS", "FORCE_LOAD"), load_style_respond=exp_config.get("load_style_respond", "FORCE_CREATE"), **exp_config.get("EXECUTION_KWARGS", {}))
#     A.OPTIONAL = exp_config.get("OPTIONAL", True)
            
#     A.METHOD = getattr(__import__("EgoCL.method", fromlist=[exp_config["METHODS"]]), exp_config["METHODS"])(E, EXECUTION=A, **exp_config.get("METHOD_KWARGS", {}))
#     A()

def parse():
    import argparse, os
    parser = argparse.ArgumentParser(description="Answering Experiment Runner")
    parser.add_argument("-c","--config_path", type=str, default=None, help="Path to the experiment configuration JSON file.")
    parser.add_argument("-e","--experience", type=str, default="EgoLifeQA_J", help="Name of the experience to load.")
    parser.add_argument("-m","--method", type=str, default="Video", help="Name of the method to use.")
    parser.add_argument("-q","--q_list", type=str, default="all", help="Comma-separated list of question IDs to answer, or 'all' for all questions.")
    parser.add_argument("-o","--encode_only", action="store_true", help="If set, only encode the questions without responding.")
    return parser.parse_args()

if __name__ == "__main__":
    from EgoCL import AnswerExperiment
    args = parse()
    E = AnswerExperiment(config_path=args.config_path, method_yaml_name=args.method, experience_yaml_name=args.experience, q_list=args.q_list.split(",") if args.q_list != "all" else "all", encode_only=args.encode_only)
    E()