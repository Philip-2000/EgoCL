

# import yaml, argparse, os
# def parse_args():
#     parser = argparse.ArgumentParser(description="Create a new configuration file based on the provided model name and its replicas.")
#     parser.add_argument("--METHODS", type=str, help="The output YAML file to write the configuration to.")
#     parser.add_argument("--MODEL", type=str, help="The name of the model for which to create the configuration.")
#     parser.add_argument("--BASE_FILE", type=str, help="The name of the model for which to create the configuration.")
#     parser.add_argument("--RESULT_FILE", type=str, help="The name of the model for which to create the configuration.")
#     return parser.parse_args()

# args = parse_args()
# with open(args.BASE_FILE, "r") as f:
#     base_config = yaml.safe_load(f)

# base_config["METHODS"] = args.METHODS
# base_config["EXECUTION_KWARGS"]["MODEL"] = args.MODEL
# base_config["METHOD_KWARGS"]["MODEL"] = args.MODEL

# os.makedirs(os.path.dirname(args.RESULT_FILE), exist_ok=True)
# with open(args.RESULT_FILE, "w") as f:
#     yaml.safe_dump(base_config, f)


from EgoCL.experiment import configs_path
import yaml, argparse, os
from os.path import join as opj, dirname as opd, abspath as opa
def parse_args():
    parser = argparse.ArgumentParser(description="Create a new configuration file based on the provided model name and its replicas.")
    parser.add_argument("--METHOD", type=str, help="The output YAML file to write the configuration to.")
    parser.add_argument("--MODEL", type=str, help="The name of the model for which to create the configuration.")
    parser.add_argument("--EXPERIENCE", type=str, help="The name of the model for which to create the configuration.")
    parser.add_argument("--RESULT_FILE", type=str, help="The name of the model for which to create the configuration.")
    return parser.parse_args()

args = parse_args()
base_config = {}

if args.EXPERIENCE.startswith("EgoSchema"):
    
    
    with open(opj(configs_path, "methods", args.METHOD+".yaml"), "r") as f:
        base_config.update(yaml.safe_load(f))

    base_config["EXECUTION_KWARGS"]["MODEL"] = args.MODEL
    base_config["METHOD_KWARGS"]["MODEL"] = args.MODEL
    base_config["EXECUTION"] = "benches"

    name_list = open(os.path.join(opd(opa(__file__)), "schemas", args.EXPERIENCE.split("_")[1].lower()+".txt")).read().strip().split("\n")
    result_dir = os.path.join(opd(opa(__file__)), "configs", "schemas")
    for name in name_list:
        this_config = base_config.copy()
        this_config["EXPERIENCE"] = f"EgoSchema_{name}"

    
        with open(os.path.join(result_dir, f"EgoSchema_{name}.yaml"), "w") as f:
            yaml.safe_dump(this_config, f)
        
    bash_file = os.path.join(opd(opa(__file__)), "configs", f"{args.EXPERIENCE}.bash")
    with open(bash_file, "w") as f:
        for name in name_list:
            f.write(f"python experiment.py -c {os.path.join(result_dir, f'EgoSchema_{name}.yaml')}\n")



else:
    with open(opj(configs_path, "experiences", args.EXPERIENCE+".yaml"), "r") as f:
        base_config.update(yaml.safe_load(f))
    with open(opj(configs_path, "methods", args.METHOD+".yaml"), "r") as f:
        base_config.update(yaml.safe_load(f))

    base_config["EXECUTION_KWARGS"]["MODEL"] = args.MODEL
    base_config["METHOD_KWARGS"]["MODEL"] = args.MODEL
    # base_config["EXECUTION_KWARGS"]["ckpt"] = "new"

    os.makedirs(os.path.dirname(args.RESULT_FILE), exist_ok=True)
    with open(args.RESULT_FILE, "w") as f:
        yaml.safe_dump(base_config, f)