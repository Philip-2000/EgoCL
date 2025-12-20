from .Annotation import Annos
from .Video import Videos
import os, json

from .TimeStamp import TimeStamp, TimeSpan

class Activity:
    def __init__(self, activity_config={}):
        self.name = activity_config.get('name', 'Unknown Activity')
        self.source = activity_config.get('source', 'Unknown Source')
        self.ANNOS = Annos(activity_config.get('ANNOS', {}), self)
        self.VIDEOS= Videos(activity_config.get('VIDEOS', []), self)
        #self.start_s = 0.0 #FIXME
        self.s_EXPERIENCE = None
        self.TIMESPAN = TimeSpan.from_dict(activity_config.get('TIMESPAN', {}), None, self, self.s_EXPERIENCE)
        self.update_timespan()

    def offset_start(self, start_experience_s: float, EXPERIENCE): #print(f"Activity.offset_start, start_experience_s={start_experience_s}, EXPERIENCE.name={EXPERIENCE.name}")
        self.TIMESPAN.offset_start(start_experience_s, EXPERIENCE)
        self.VIDEOS.offset_start(start_experience_s, EXPERIENCE)
        self.ANNOS.offset_start(start_experience_s, EXPERIENCE)

    def __iadd__(self, anno_dict):
        self.ANNOS += anno_dict
        return self
    
    def update_timespan(self):

        p = min(self.VIDEOS.TIMESPAN.STARTSTAMP,  min([ANNO.TIMESPAN.STARTSTAMP for cat in self.ANNOS.ANNOS for ANNO in self.ANNOS.ANNOS[cat]]) if len(self.ANNOS.ANNOS) > 0 else self.VIDEOS.TIMESPAN.STARTSTAMP)
        
        self.TIMESPAN.STARTSTAMP.seconds_experience = p.seconds_experience
        self.TIMESPAN.STARTSTAMP.seconds_activity = p.seconds_activity
        self.TIMESPAN.STARTSTAMP.seconds_video = p.seconds_video
        
        p = max(self.VIDEOS.TIMESPAN.ENDSTAMP, max([ANNO.TIMESPAN.ENDSTAMP for cat in self.ANNOS.ANNOS for ANNO in self.ANNOS.ANNOS[cat]]) if len(self.ANNOS.ANNOS) > 0 else self.VIDEOS.TIMESPAN.ENDSTAMP)

        self.TIMESPAN.ENDSTAMP.seconds_experience = p.seconds_experience
        self.TIMESPAN.ENDSTAMP.seconds_activity = p.seconds_activity
        self.TIMESPAN.ENDSTAMP.seconds_video = p.seconds_video

    @property
    def to_dict(self):
        if not hasattr(self, '_cached_to_dict'):
            self._cached_to_dict = {
                'name': self.name,
                'source': self.source, #dataset name
                'VIDEOS': self.VIDEOS.to_dict,
                'ANNOS': self.ANNOS.to_dict,
                'TIMESPAN': self.TIMESPAN.to_dict,
            }
        return self._cached_to_dict

    def save(self, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, f"{self.name}_activity.json"), 'w') as f:
            json.dump(self.to_dict, f, indent=4)
    
    def from_dict(self, data_dict):
        self.name = data_dict.get('name', 'Unknown Activity')
        self.source = data_dict.get('source', 'Unknown Source')
        self.VIDEOS.from_dict(data_dict.get('VIDEOS', []))
        self.ANNOS.from_dict(data_dict.get('ANNOS', {}))
        self.TIMESPAN = TimeSpan.from_dict(data_dict.get('TIMESPAN', {}), None, self, self.s_EXPERIENCE)

    def load(self, in_dir):
        in_path = in_dir if os.path.isfile(in_dir) and in_dir.endswith('.json') else os.path.join(in_dir, f"{self.name}_activity.json")
        with open(in_path, 'r') as f:
            data_dict = json.load(f)
        self.from_dict(data_dict)
    
    # @property
    # def duration_s(self):
    #     return max(self.VIDEO.duration_s, self.ANNOS.duration_s) #FIXME
    
    # @property
    # def end_s(self):
    #     return self.TIMESPAN.end_s

    def clip(self, end_s: float, start_s: float = 0.0):
        raise NotImplementedError
        A = Activity({"name": f"{self.name}_s{int(start_s)}_e{int(end_s)}", "source": self.source})
        A.ANNOS = self.ANNOS.clip(start_s, end_s) #FIXME
        A.VIDEOS= self.VIDEOS.clip(start_s, end_s) #FIXME
        return A




class Activities:
    def __init__(self, activities_list=[]):
        self.activities = activities_list.copy()
    
    def __iadd__(self, activity):
        self.activities.append(activity)
        return self
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return Activities(self.activities[index])
        elif isinstance(index, int):
            return self.activities[index]
        elif isinstance(index, str):
            for activity in self.activities:
                if activity.name == index:
                    return activity
            return None
        
    def __iter__(self):
        return iter(self.activities)
    
    def __len__(self):
        return len(self.activities)
    

