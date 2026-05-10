txts = open("../schemas.txt").readlines()
vs = ["Base","Len8","Len12","NoCon","PlainEncode"]
ids = ["a","b","c","d"]
for v in vs:
    for i, id in enumerate(ids):
        print(f"EgoSchema_{id}_{v}")
        with open("./schemas/EgoSchema_"+id+"_"+v+".bash", "w") as f:
            for txt in txts[125*i:125*(i+1)]:
                f.write("python encode.py -c /mnt/data/yl/C/EgoCL/scripts/experiment/auto/res/configs/schemas/EgoSchema_"+txt.strip()+"_"+v+".yaml\n")
