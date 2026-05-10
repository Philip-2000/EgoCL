def single(e,m="VideoMethod"):
    MD = f"/mnt/data/yl/W/EgoCL/Memory/{e}/{m}/"
    print(f"Updating encodes in {MD} for {e}...")
    import os, tqdm, numpy as np, json
    
    digits = sorted([f for f in os.listdir(MD) if f.isdigit()], key=lambda x:-int(x))
    digits = digits[1:]
    for d in tqdm.tqdm(digits, desc="Updating encodes"):
        for f in os.listdir(os.path.join(MD, d)):
            if not f.endswith("_result.json"): continue
            json_path = os.path.join(MD, d, f)
            try:
                with open(json_path, 'r') as jf:
                    data = json.load(jf)
                if len(data["score"]) == 0:
                    os.remove(json_path)
                    print(f"Removed empty results file: {json_path}")
            except Exception as ex:
                os.remove(json_path)
                print(f"Removed invalid results file: {json_path} due to error: {ex}")

def main():
    Es = ['EgoR1Bench_A1_JAKE', 'EgoR1Bench_A2_ALICE', 'EgoR1Bench_A3_TASHA', 'EgoR1Bench_A4_LUCIA', 'EgoR1Bench_A5_KATRINA', 'EgoR1Bench_A6_SHURE', 'EgoLifeQA_A1_JAKE']
    from tqdm import tqdm
    for e in tqdm(Es, desc="Experiences"):
        single(e)

if __name__ == "__main__":
    main()