import json, os
J = json.load(open("/mnt/data/raw_data/egoschema/merged.json"))
N = 4
for i in range(N):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{chr(ord('a') + i)}.txt"), 'w') as f:
        f.write("\n".join([j["q_uid"] for j in J[len(J)*i//N:len(J)*(i+1)//N]]))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"alpha.txt"), 'w') as f:
    f.write("\n".join([j["q_uid"] for j in J[:250]]))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"beta.txt"), 'w') as f:
    f.write("\n".join([j["q_uid"] for j in J[250:]]))
