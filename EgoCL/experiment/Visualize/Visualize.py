import os,json
class Visualize:
    def __init__(self,Experience_name, Method):
        from ...paths import MEMORY_ROOT
        self.path = os.path.join(MEMORY_ROOT, Experience_name, Method)
    
    def __call__(self):
        j = []
        for t in sorted([t for t in os.listdir(self.path) if str(t).isdigit()], key=lambda x: int(x)):
            data = json.load( open( os.path.join(self.path, t, "results.json"), 'r') )
            for d in [d for d in data if d['uid'] not in [item['uid'] for item in j]]: j.append(d)
        
        print(f"Average score: {sum([item['score'] for item in j])/len(j)}, {sum([item['score'] for item in j])} out of {len(j)} questions answered correctly.")
        

