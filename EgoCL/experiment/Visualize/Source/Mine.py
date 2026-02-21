from .Source import Source
class Mine(Source):
    def __init__(self, name):
        self.name = name
    

    # @property
    # def path(self):
    #     import os
    #     from . import MineBase
    # 

    def load(self, LOADER):
        # raise NotImplementedError("Not Implemented")
        from . import MineBase, EgoR1Persons
        import os
        from os.path import join as opj
        for TRAIL in LOADER.TRAILS:
            if TRAIL.name == "EgoSchema":
                raise NotImplementedError("Mine.load for EgoSchema not implemented yet.")
                DIR_LIST = []
                for METRIC in LOADER.METRICS:
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)], _ = self.metric(DIR_LIST, METRIC)
            elif TRAIL.name == "EgoLifeQA":
                DIR_LIST = sorted([opj(MineBase, "EgoLifeQA_A1_JAKE_D1", "VideoMethod", t) for t in os.listdir( opj(MineBase, "EgoLifeQA_A1_JAKE_D1", "VideoMethod") ) if str(t).isdigit()], key=lambda x: int(os.path.basename(x)) )
                #"/mnt/data/yl/W/EgoCL/Memory/EgoLifeQA_A1_JAKE_D1/VideoMethod",
                for METRIC in LOADER.METRICS:
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)], _ = self.metric(DIR_LIST, METRIC)
            elif TRAIL.name == "EgoR1Bench":
                DIR_LIST = []
                for Person in EgoR1Persons: DIR_LIST += sorted([opj(MineBase, f"EgoR1Bench_{Person}_D1", "VideoMethod", t) for t in os.listdir( opj(MineBase, f"EgoR1Bench_{Person}_D1", "VideoMethod") ) if str(t).isdigit()], key=lambda x: int(os.path.basename(x)) )
                for METRIC in LOADER.METRICS:
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)], _ = self.metric(DIR_LIST, METRIC)
            elif TRAIL.name in EgoR1Persons:
                DIR_LIST = sorted([opj(MineBase, f"EgoR1Bench_{TRAIL.name}_D1", "VideoMethod", t) for t in os.listdir( opj(MineBase, "EgoR1Bench_A1_JAKE_D1", "VideoMethod") ) if str(t).isdigit()], key=lambda x: int(os.path.basename(x)) )
                for METRIC in LOADER.METRICS:
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)], _ = self.metric(DIR_LIST, METRIC)
            elif TRAIL.name == "XLeBench":
                raise NotImplementedError("Mine.load for XLeBench not implemented yet.")
                DIR_LIST = []
                for METRIC in LOADER.METRICS:
                    LOADER.DATAS[(self.name, TRAIL.name, METRIC.name)], _ = self.metric(DIR_LIST, METRIC)
            else:
                raise AssertionError(f"Mine.load unrecognized TRAIL.name {TRAIL.name}")
        return
        j = []
        for t in sorted([t for t in os.listdir(self.path) if str(t).isdigit()], key=lambda x: int(x)):
            filenames = [f for f in os.listdir( os.path.join(self.path, t) ) if f.endswith("result.json") and f.startswith("default")]
            for f in filenames:
                try:
                    data = json.load( open( os.path.join(self.path, t, f), 'r') )
                    # for d in [d for d in data if d['uid'] not in [item['uid'] for item in j]]: j.append(d)
                    if data['uid'] not in [item['uid'] for item in j]: j.append(data)
                except:
                    pass
        
        # print(f"Average score: {round(sum([item['score'] for item in j])/len(j),4)}, {sum([item['score'] for item in j])} out of {len(j)} questions answered correctly.")

    def metric(self, DIR_LIST, METRIC):
        import os, json
        USED_DATA = []
        for di in DIR_LIST:
            filenames = [f for f in os.listdir( di ) if f.endswith("result.json") and f.startswith(self.name)]
            for f in filenames:
                try:
                    data = json.load( open( os.path.join(di, f), 'r') )
                    if data['uid'] not in [item['uid'] for item in USED_DATA]: USED_DATA.append( data )
                except:
                    pass
        if len(USED_DATA) == 0:  return None, None
        if METRIC.name == "Accuracy":
            correct_s = [item['score'] for item in USED_DATA]
            avg_correct = sum(correct_s) / len(correct_s) if len(correct_s) > 0 else 0.0
            dev_correct = (sum([(c - avg_correct) ** 2 for c in correct_s]) / len(correct_s)) ** 0.5 if len(correct_s) > 0 else 0.0
            return avg_correct, dev_correct
            
        elif METRIC.name == "TimeCost":
            delay_s_s = [item['response']['delay_s'] for item in USED_DATA]
            avg_delay_s = sum(delay_s_s) / len(delay_s_s) if len(delay_s_s) > 0 else 0.0

            ratio_to_avg_delay_s = [item / avg_delay_s for item in delay_s_s]
            dev_ratio_to_avg_delay_s = (sum([(r - 1) ** 2 for r in ratio_to_avg_delay_s]) / len(ratio_to_avg_delay_s)) ** 0.5 if len(ratio_to_avg_delay_s) > 0 else 0.0
            return avg_delay_s, dev_ratio_to_avg_delay_s
            
        elif METRIC.name == "TimeRate":
            delay_rate_s = [item['response']['delay_rate'] for item in USED_DATA]
            avg_delay_rate = sum(delay_rate_s) / len(delay_rate_s) if len(delay_rate_s) > 0 else 0.0
            ratio_to_avg_delay_s = [item / avg_delay_rate for item in delay_rate_s]
            dev_ratio_to_avg_delay_s = (sum([(r - 1) ** 2 for r in ratio_to_avg_delay_s]) / len(ratio_to_avg_delay_s)) ** 0.5 if len(ratio_to_avg_delay_s) > 0 else 0.0
            return avg_delay_rate, dev_ratio_to_avg_delay_s
        elif METRIC.name == "SpaceCost":
            fsize_kB_s = [item['response']['fsize_kB'] for item in USED_DATA]
            avg_fsize_kB = sum(fsize_kB_s) / len(fsize_kB_s) if len(fsize_kB_s) > 0 else 0.0
            ratio_to_avg_fsize_kB = [item / avg_fsize_kB for item in fsize_kB_s]
            dev_ratio_to_avg_fsize_kB = (sum([(r - 1) ** 2 for r in ratio_to_avg_fsize_kB]) / len(ratio_to_avg_fsize_kB)) ** 0.5 if len(ratio_to_avg_fsize_kB) > 0 else 0.0
            return avg_fsize_kB, dev_ratio_to_avg_fsize_kB
        elif METRIC.name == "SpaceRate":
            fsize_rate_s = [item['response']['fsize_rate'] if item['response']['fsize_rate'] is not None else item['response']['fsize_kB']/item['TIME']['seconds_experience_s'] for item in USED_DATA]
            avg_fsize_rate = sum(fsize_rate_s) / len(fsize_rate_s) if len(fsize_rate_s) > 0 else 0.0
            ratio_to_avg_fsize_rate = [item / avg_fsize_rate for item in fsize_rate_s]
            dev_ratio_to_avg_fsize_rate = (sum([(r - 1) ** 2 for r in ratio_to_avg_fsize_rate]) / len(ratio_to_avg_fsize_rate)) ** 0.5 if len(ratio_to_avg_fsize_rate) > 0 else 0.0
            return avg_fsize_rate, dev_ratio_to_avg_fsize_rate
        else:
            raise AssertionError(f"Mine.metric unrecognized METRIC.name {METRIC.name}")