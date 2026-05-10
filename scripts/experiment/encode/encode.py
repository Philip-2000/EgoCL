


def singleEncode(v, e):
    #(1) 新建一个answering过程，去
    pass

def versionEncode(v):
    from os.path import join as opj, dirname as opd, abspath as opa
    schemas = open(opj(opd(opa(__file__)), "schemas.txt")).readlines()
    schemas = ["EgoSchema_"+s.strip() for s in schemas]
    schemas += ["A1_JAKE", "A2_ALICE", "A3_TASHA", "A4_LUCIA", "A5_KATRINA", "A6_SHURE", "EgoLifeQA"]


    pass

def parse():
    import argparse, os
    parser = argparse.ArgumentParser(description="Answering Experiment Runner")
    parser.add_argument("-c","--config_path", type=str, default=None, help="Path to the experiment configuration JSON file.")
    parser.add_argument("-e","--experience", type=str, default="EgoLifeQA_J", help="Name of the experience to load.")
    parser.add_argument("-m","--method", type=str, default="Video", help="Name of the method to use.")
    # parser.add_argument("-q","--q_list", type=str, default="all", help="Comma-separated list of question IDs to answer, or 'all' for all questions.")
    # parser.add_argument("-o","--encode_only", action="store_true", help="If set, only encode the questions without responding.")
    parser.add_argument("-i", "--index", type=int, default=0)
    parser.add_argument("-k", "--kk", type=int)
    return parser.parse_args()

def last_q(e):
    if e.startswith("EgoLifeQA"):
        return "500"
    if e.startswith("EgoSchema"):
        return None
    r ={
        "EgoR1Bench_A1_JAKE":"A1_JAKE_293",
        "EgoR1Bench_A2_ALICE":"A2_ALICE_1326",
        "EgoR1Bench_A3_TASHA":"A3_TASHA_46",
        "EgoR1Bench_A4_LUCIA":"A4_LUCIA_1095",
        "EgoR1Bench_A5_KATRINA":"A5_KATRINA_1075",
        "EgoR1Bench_A6_SHURE":"A6_SHURE_868"}
    return r[e]

if __name__ == "__main__":
    from EgoCL import AnswerExperiment
    args = parse()
    import yaml, json
    conf = yaml.safe_load(open(args.config_path))
    EXPERIENCE = conf["EXPERIENCE"]
    METHOD = conf["METHOD"]
    name = conf["name"]
    input_name=conf.get("input_name", name)
    E = AnswerExperiment(config_path=args.config_path, method_yaml_name=args.method, experience_yaml_name=args.experience, q_list=[last_q(EXPERIENCE)], encode_only=True)
    # from EgoCL.experiment.Elements import Answering
    # from EgoCL.data import Experience
    # Ee = Experience.load_from_name(experience_name=E.EXPERIENCE)
    # A = Answering(name=E.ANSWERING, EXPERIENCE=Ee, q_list=E.q_list, encode_only=E.encode_only, EXPERIMENT=E, **E.answer_config.get("EXECUTION_KWARGS", {}))
        
    # A.METHOD = getattr(__import__("EgoCL.method", fromlist=[E.METHOD]), E.METHOD)(Ee, EXECUTION=A, EXPERIMENT=E, **E.answer_config.get("METHOD_KWARGS", {}))
        
    
    # A.METHOD.MEMORY.ENCODINGS.encode_all()
    E()
    


    e = E.ANSWERING.ENCODINGS
    
    from EgoCL.paths import MEMORY_DIR
    MD = MEMORY_DIR(E.METHOD.EXPERIENCE, E.METHOD)
    print(f"Updating encodes in {MD} for {name}...")
    import os, tqdm, numpy as np, json
    npz_path = e.file_name
    npz = np.load(npz_path, allow_pickle=True)
    
    digits = sorted([f for f in os.listdir(MD) if f.isdigit()], key=lambda x:-int(x))
    digits = digits[1:]
    digits = digits[53*args.index+args.kk:53*(args.index+1)]
    for d in tqdm.tqdm(digits, desc="Updating encodes"):
        path = os.path.join(MD, d, f"{name}_encodes.npz")
        memory_json = os.path.join(MD, d, f"{input_name}_memory.json")
        L = len(json.load(open(memory_json))["VIDEO_MEM_SEGMENTS"][0]["VIDEO_MEM_CLIPS"])
        print(L)
        print(e.ENCODINGS[0].index, e.ENCODINGS[-1].index, "before filtering")
        e.ENCODINGS = [encode for encode in e.ENCODINGS if encode.index < L]
        print(len(e.ENCODINGS), "encodes after filtering, L=", L, )
        
        np.savez_compressed(path, **{
                'ENCODER_PATH': npz['ENCODER_PATH'],
                'entire': npz['entire'],
                'length': npz['length'],
                'cover': npz['cover'],
                'indexs': npz['indexs'][:len(e.ENCODINGS)],
                'parts': npz['parts'][:len(e.ENCODINGS)],
                'encodes': npz['encodes'][:len(e.ENCODINGS)]
            }
        )
        