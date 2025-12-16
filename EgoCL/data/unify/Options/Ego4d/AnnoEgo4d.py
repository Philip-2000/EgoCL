import os, json

class AnnoEgo4d:
    def __init__(self, json_base, anno_tags=["narration", "summary"], *args, **kwds):
        
        #activate annotation set
        #["narration", "fho", "nlq", "vq", "moments"，"av", "goalstep"]  # list of available annotation types
        self.anno_tags = anno_tags
        #load the annotation json files from os
        self.json_base = json_base
        self.configs = {}
        for anno_tag in self.anno_tags:
            getattr(self, f"_{self.__class__.__name__}__{anno_tag}_load")()

    def __call__(self, ACTIVITY):
        for anno_tag in self.anno_tags:
            getattr(self, f"_{self.__class__.__name__}__{anno_tag}")(ACTIVITY)

    def __summary_load(self):
        if self.configs.get('narration', None) is None: self.__narration_load()

    def __summary(self, ACTIVITY):
        name = ACTIVITY.name
        current_config = self.configs['narration'].get(name, None)
        for raw_config in current_config['narration_pass_1']["summaries"]:
            anno_dict = {
                "category": "summary",
                "TIMESPAN": {
                    "STARTSTAMP":{
                        "seconds_activity_s": raw_config['start_sec'],
                        "seconds_video_s": raw_config['start_sec']
                    },
                    "ENDSTAMP":{
                        "seconds_activity_s": raw_config['end_sec'],
                        "seconds_video_s": raw_config['end_sec']
                    }
                },
                "information": {
                    "text": raw_config['summary_text'],
                    "annotation_uid": raw_config.get('annotation_uid', None),
                    "pass": "summary_pass_1"
                }
            }
            #print("summary_pass_1 start_s:", anno_dict["time"]["start_s"], "end_s:", anno_dict["time"]["end_s"], "text:", anno_dict["information"]["text"][:30]+"....")
            ACTIVITY += anno_dict
        for raw_config in current_config['narration_pass_2']["summaries"]:
            anno_dict = {
                "category": "summary",
                "TIMESPAN": {
                    "STARTSTAMP":{
                        "seconds_activity_s": raw_config['start_sec'],
                        "seconds_video_s": raw_config['start_sec']
                    },
                    "ENDSTAMP":{
                        "seconds_activity_s": raw_config['end_sec'],
                        "seconds_video_s": raw_config['end_sec']
                    }
                },
                "information": {
                    "text": raw_config['summary_text'],
                    "annotation_uid": raw_config.get('annotation_uid', None),
                    "pass": "summary_pass_2"
                }
            }
            #print("summary_pass_2 start_s:", anno_dict["time"]["start_s"], "end_s:", anno_dict["time"]["end_s"], "text:", anno_dict["information"]["text"][:30]+"....")
            ACTIVITY += anno_dict

    def __narration_load(self): #use narrationn.json but not narration.json for debug because narration.json is too large
        self.configs['narration'] = json.load(open(os.path.join(self.json_base, 'narration.json'), 'r')) #'narrationn.json'), 'r')) #

    def __narration(self, ACTIVITY):
        name = ACTIVITY.name
        current_config = self.configs['narration'].get(name, None)
        for raw_config in current_config['narration_pass_1']["narrations"]:
            anno_dict = {
                "category": "narration",
                "time": {
                    "start_s": raw_config['timestamp_sec'],
                    "start_f": raw_config['timestamp_frame'],
                },
                "information": {
                    "text": raw_config['narration_text'],
                    "annotation_uid": raw_config.get('annotation_uid', None),
                    "pass": "narration_pass_1"
                }
            }
            #print("narration_pass_1 start_s:", anno_dict["time"]["start_s"], "start_f:", anno_dict["time"]["start_f"], "text:", anno_dict["information"]["text"][:30]+"....")
            ACTIVITY += anno_dict
        for raw_config in current_config['narration_pass_2']["narrations"]:
            anno_dict = {
                "category": "narration",
                "time": {
                    "start_s": raw_config['timestamp_sec'],
                    "start_f": raw_config['timestamp_frame'],
                },
                "information": {
                    "text": raw_config['narration_text'],
                    "annotation_uid": raw_config.get('annotation_uid', None),
                    "pass": "narration_pass_2"
                }
            }
            #print("narration_pass_2 start_s:", anno_dict["time"]["start_s"], "start_f:", anno_dict["time"]["start_f"], "text:", anno_dict["information"]["text"][:30]+"....")
            ACTIVITY += anno_dict

    def __fho_load(self):
        self.configs['fho'] = {}
        raise NotImplementedError("FHO annotations are not yet implemented.")

    def __fho(self, ACTIVITY):
        raise NotImplementedError("FHO annotations are not yet implemented.")

    def __nlq_load(self):
        self.configs['nlq'] = json.load(open(os.path.join(self.json_base, 'nlq_train.json'), 'r'))
        n = json.load(open(os.path.join(self.json_base, 'nlq_test.json'), 'r'))
        self.configs['nlq']["videos"] += n["videos"]

    def __nlq(self, ACTIVITY):
        raise NotImplementedError("NLQ annotations are not yet implemented.")

    def __vq_load(self):
        self.configs['vq'] = json.load(open(os.path.join(self.json_base, 'vq_train.json'), 'r'))
        n = json.load(open(os.path.join(self.json_base, 'vq_test.json'), 'r'))
        self.configs['vq']["videos"] += n["videos"]

    def __vq(self, ACTIVITY):
        raise NotImplementedError("VQ annotations are not yet implemented.")
    
    def __moments_load(self):
        self.configs['moments'] = json.load(open(os.path.join(self.json_base, 'moments_train.json'), 'r'))
        n = json.load(open(os.path.join(self.json_base, 'moments_test.json'), 'r'))
        self.configs['moments']["videos"] += n["videos"]

    def __moments(self, ACTIVITY):
        raise NotImplementedError("Moment annotations are not yet implemented.")
    
    def __av_load(self):
        self.configs['av'] = json.load(open(os.path.join(self.json_base, 'av_train.json'), 'r'))
        n = json.load(open(os.path.join(self.json_base, 'av_test.json'), 'r'))
        self.configs['av']["videos"] += n["videos"]

    def __av(self, ACTIVITY):
        raise NotImplementedError("AV annotations are not yet implemented.")
    
    def __goalstep_load(self):
        self.configs['goalstep'] = json.load(open(os.path.join(self.json_base, 'goalstep_train.json'), 'r'))
        n = json.load(open(os.path.join(self.json_base, 'goalstep_test.json'), 'r'))
        self.configs['goalstep']["videos"] += n["videos"]
    
    def __goalstep(self, ACTIVITY):
        raise NotImplementedError("Goalstep annotations are not yet implemented.")