def single(e,m="VideoMethod"):
    MD = f"/mnt/data/yl/W/EgoCL/Memory/{e}/{m}/"
    # print(f"Updating encodes in {MD} for {e}...")
    import os, tqdm, numpy as np, json
    
    d = '000180'
    if not os.path.exists(os.path.join(MD, d)):
        print(f"Directory {os.path.join(MD, d)} does not exist. Skipping.")
        return
    for f in os.listdir(os.path.join(MD, d)):
        if not f.endswith("_result.json"): continue
        json_path = os.path.join(MD, d, f)
        os.remove(json_path)
        # print(f"Removed results file: {json_path}")
        # try:
        #     with open(json_path, 'r') as jf:
        #         data = json.load(jf)
        #     if len(data["score"]) == 0:
        #         os.remove(json_path)
        #         print(f"Removed empty results file: {json_path}")
        # except Exception as ex:
        #     os.remove(json_path)
        #     print(f"Removed invalid results file: {json_path} due to error: {ex}")

def main():
    import os
    Es = [f for f in os.listdir("/mnt/data/yl/W/EgoCL/Memory/") if f.startswith("EgoSchema")]
    from tqdm import tqdm
    for e in tqdm(Es, desc="Experiences"):
        single(e)

if __name__ == "__main__":
    main()