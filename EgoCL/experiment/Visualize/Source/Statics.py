from .Source import Source
class Statics(Source):
    FULL_DATA = []
    def __init__(self, name):
        self.name = name
        if len(Statics.FULL_DATA): return
        from . import StaticsBase, StaticsFiles
        import os, json
        from os.path import join as opj
        Statics.FULL_DATA = [json.load( open( opj(StaticsBase, f), 'r') )[0] for f in StaticsFiles]

    def load(self, LOADER):
        # raise NotImplementedError("Not Implemented")
        from . import StaticsBase, EgoR1Persons
        for TRAIL in LOADER.TRAILS:
            if TRAIL.name == "EgoSchema":
                USED_DATA = [d for d in Statics.FULL_DATA if d['benchmark'] == TRAIL.name and d['method'] == self.name]
                for METRIC in LOADER.METRICS:
                    dct = self.metric(USED_DATA, METRIC)
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)] = dct["avg"]
            elif TRAIL.name == "EgoLifeQA":
                USED_DATA = [d for d in Statics.FULL_DATA if d['benchmark'] == TRAIL.name and d['method'] == self.name]
                for METRIC in LOADER.METRICS:
                    dct = self.metric(USED_DATA, METRIC)
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)] = dct["avg"]
            elif TRAIL.name == "EgoR1Bench":
                USED_DATA = [d for d in Statics.FULL_DATA if d['benchmark'] == TRAIL.name and d['method'] == self.name]
                for METRIC in LOADER.METRICS:
                    dct = self.metric(USED_DATA, METRIC)
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)] = dct["avg"]
            elif TRAIL.name in EgoR1Persons:
                USED_DATA = [d for d in Statics.FULL_DATA if d['benchmark'] == "EgoR1Bench" and d['method'] == self.name]
                for ud in USED_DATA: ud["records"] = {k:v for k,v in ud["records"].items() if k.startswith(TRAIL.name)}
                for METRIC in LOADER.METRICS:
                    dct = self.metric(USED_DATA, METRIC)
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)] = dct["avg"]
            elif TRAIL.name == "XLeBench":
                raise NotImplementedError("Statics.load for XLeBench not implemented yet.")
                USED_DATA = [d for d in Statics.FULL_DATA if d['benchmark'] == TRAIL.name and d['method'] == self.name]
                for METRIC in LOADER.METRICS:
                    dct = self.metric(USED_DATA, METRIC)
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)] = dct["avg"]
            else:
                raise AssertionError(f"Statics.load unrecognized TRAIL.name {TRAIL.name}")
        return

    def process(self, lst):
        L = len(lst)
        avg = sum(lst) / L if L > 0 else 0.0
        dev = (sum([(x - avg) ** 2 for x in lst]) / L) ** 0.5 if L > 0 else 0.0
        ratio_to_avg = [item / avg for item in lst] if avg != 0 else [0.0 for item in lst]
        dev_ratio_to_avg = (sum([(r - 1) ** 2 for r in ratio_to_avg]) / L) ** 0.5 if L > 0 else 0.0
        return {"avg": avg, "dev": dev, "dev_ratio_to_avg": dev_ratio_to_avg}
    
    def metric(self, USED_DATA, METRIC):
        if METRIC.name == "Accuracy":
            return self.process([int(record['score']['correct'] if 'correct' in record['score'] else record['score']['option']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "Closest":
            return self.process([int(record['score']['closest']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "Similarity":
            return self.process([float(record['score']['similarity']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "LLMChoose":
            return self.process([int(record['score']['llm_choose_force']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "LLMChoose_Abstent":
            return self.process([int(record['score']['llm_choose']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "LLMJudge":
            return self.process([int(record['score']['llm_judge']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "MCDelay":
            return self.process([float(record['delay_s']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "OEDelay":
            return self.process([float(record['delay_strong_s']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "MCDelay_Rate":
            return self.process([float(record['delay_rate']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "OEDelay_Rate":
            return self.process([float(record['delay_strong_rate']) for data in USED_DATA for record in data['records'].values()])
        elif METRIC.name == "Memorize_Rate":
            return {"avg": None, "dev": None, "dev_ratio_to_avg": None}
        elif METRIC.name == "Space_Rate":
            return {"avg": None, "dev": None, "dev_ratio_to_avg": None}
        else:
            raise AssertionError(f"Statics.metric unrecognized METRIC.name {METRIC.name}")

        return {"avg": None, "dev": None, "dev_ratio_to_avg": None}
        
        if METRIC.name == "Accuracy":
            correct_s = [int(record['correct']) for data in USED_DATA for record in data['records'].values()]
            avg_correct = sum(correct_s) / len(correct_s) if len(correct_s) > 0 else 0.0
            dev_correct = (sum([(c - avg_correct) ** 2 for c in correct_s]) / len(correct_s)) ** 0.5 if len(correct_s) > 0 else 0.0
            return avg_correct, dev_correct
            
        elif METRIC.name == "TimeCost":
            delay_s_s = [record['delay_s'] for data in USED_DATA for record in data['records'].values()]
            avg_delay_s = sum(delay_s_s) / len(delay_s_s) if len(delay_s_s) > 0 else 0.0

            ratio_to_avg_delay_s = [item / avg_delay_s for item in delay_s_s]
            dev_ratio_to_avg_delay_s = (sum([(r - 1) ** 2 for r in ratio_to_avg_delay_s]) / len(ratio_to_avg_delay_s)) ** 0.5 if len(ratio_to_avg_delay_s) > 0 else 0.0
            return avg_delay_s, dev_ratio_to_avg_delay_s
            
        elif METRIC.name == "TimeRate":
            delay_rate_s = [record['delay_rate'] for data in USED_DATA for record in data['records'].values()]
            avg_delay_rate = sum(delay_rate_s) / len(delay_rate_s) if len(delay_rate_s) > 0 else 0.0
            ratio_to_avg_delay_s = [item / avg_delay_rate for item in delay_rate_s]
            dev_ratio_to_avg_delay_s = (sum([(r - 1) ** 2 for r in ratio_to_avg_delay_s]) / len(ratio_to_avg_delay_s)) ** 0.5 if len(ratio_to_avg_delay_s) > 0 else 0.0
            return avg_delay_rate, dev_ratio_to_avg_delay_s
        elif METRIC.name == "SpaceCost":
            return None, None
        elif METRIC.name == "SpaceRate":
            return None, None
        else:
            raise AssertionError(f"Statics.metric unrecognized METRIC.name {METRIC.name}")