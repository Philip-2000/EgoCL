def single(e,m="VideoMethod"):
    MD = f"/mnt/data/yl/W/EgoCL/Memory/{e}/{m}/"
    print(f"Updating encodes in {MD} for {e}...")
    import os, tqdm, numpy as np, json
    
    digits = sorted([f for f in os.listdir(MD) if f.isdigit()], key=lambda x:-int(x))
    digits = digits[1:]
    for d in tqdm.tqdm(digits, desc="Updating encodes"):
        for f in os.listdir(os.path.join(MD, d)):
            if not f.endswith("_encodes.npz"): continue
            npz = np.load(os.path.join(MD, d, f), allow_pickle=True)
            if not "arr_0" in npz: continue
            full_path = os.path.join(MD, d, f)
            print(f"Updating encodes at {full_path}...")
            np.savez_compressed(full_path,  **(npz["arr_0"].item()), tqdm_desc="Updating encodes")
            print(f"Updated encodes at {full_path}.")

def main():
    Es = ['EgoR1Bench_A1_JAKE', 'EgoR1Bench_A2_ALICE', 'EgoR1Bench_A3_TASHA', 'EgoR1Bench_A4_LUCIA', 'EgoR1Bench_A5_KATRINA', 'EgoR1Bench_A6_SHURE', 'EgoLifeQA_A1_JAKE']
    from tqdm import tqdm
    for e in tqdm(Es, desc="Experiences"):
        single(e)

if __name__ == "__main__":
    main()