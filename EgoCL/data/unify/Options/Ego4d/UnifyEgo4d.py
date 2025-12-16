from ..UnifyBase import UnifyBase
from ....elements import Activity
from .AnnoEgo4d import AnnoEgo4d
import os

class UnifyEgo4d(UnifyBase):
    def __init__(self, cfg):
        super().__init__(cfg)
        # Initialize Ego4D specific processing parameters here
        self.cfg = cfg

        json_base = os.path.join(self.cfg['in_path'], 'annotations')
        self.ANNOEGO4D = AnnoEgo4d(json_base=json_base, anno_tags=cfg.get('anno_tags', ['summary']))#['narration', 'summary']))# 
        self.video_base = os.path.join(self.cfg['in_path'], 'full_scale')
  
    def __repr__(self):
        return f'{self.__class__}(cfg={self.cfg})'
    
    def __length(self, path):
        import subprocess
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ]
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
            return float(out)
        except Exception:
            return None

    def __call__(self, item, **kwargs):
        #print(item)
        #这里肯定是需要扩展的，看看咋扩展吧，就是到时候只搞一些片段这个样子
        ss,es = 0 if "start_s" not in kwargs else kwargs['start_s'], self.__length(f"{self.video_base}/{item}.mp4") if "end_s" not in kwargs else kwargs['end_s']
        activity_config = {
            'name': item,
            'source': 'Ego4D',
            'ANNOS': {},
            'VIDEO': {
                'video_path': f"{self.video_base}/{item}.mp4",
                'TIMESPAN': {
                    'STARTSTAMP': {
                        "seconds_activity_s": ss,
                        "seconds_video_s": ss
                        
                    },
                    'ENDSTAMP': {
                        "seconds_activity_s": es,
                        "seconds_video_s": es
                    }
                }
                #'start_s': 0 if "start_s" not in kwargs else kwargs['start_s'],
                #'end_s': self.__length(f"{self.video_base}/{item}.mp4") if "end_s" not in kwargs else kwargs['end_s']
            }
        }
        a = Activity(activity_config)
        self.ANNOEGO4D(a)
        return a


class UnifyEgo4d_S:
    def __init__(self, datset_cfg):
        self.list = []
        #self.kwargs = dict(kwargs).copy()
        kwargs = datset_cfg
        
        
        
        import os
        if 'items' in kwargs and len(kwargs['items']) > 0:
            self.list = kwargs['items'].copy()
        elif 'item_file' in kwargs and len(kwargs['item_file']) > 0  and os.path.exists(kwargs['item_file']):
            self.list = open(kwargs['item_file'], 'r').read().splitlines()
        else:
            self.list = os.listdir(kwargs['in_path'])


        if 'num' in kwargs and kwargs['num'] > 0:
            self.list = self.list[:kwargs['num']]

        # for dataset_name, dataset_config in self.config_data["datasets"].items():
        #     dataset_config['ITEMS'] = [] #final version of ITEMS list
        #     if 'items' in dataset_config and len(dataset_config['items']) > 0:
        #         self.config_data["datasets"][dataset_name]['ITEMS'] = dataset_config['items'].copy() #highest priority, directly set ITEMS
        #     elif 'item_file' in dataset_config and len(dataset_config['item_file']) > 0 and os.path.exists(dataset_config['item_file']):
        #         self.config_data["datasets"][dataset_name]['ITEMS'] = open(dataset_config['item_file'], 'r').read().splitlines()
        #     elif 'num' in dataset_config and dataset_config['num'] > 0:
        #         self.config_data["datasets"][dataset_name]['ITEMS'] = os.listdir(dataset_config['in_path'])[:dataset_config['num']]
        #     else:
        #         self.config_data["datasets"][dataset_name]['ITEMS'] = os.listdir(dataset_config['in_path'])
        self.UNIFIER = UnifyEgo4d(kwargs)
        self.ACTIVITIES = []

    def __call__(self, out_dir=None):
        from tqdm import tqdm

        with tqdm(self.list) as pbar:
            for item in pbar:
                pbar.set_description(f"Processing {item[:8]}...")
                try:
                    act = self.UNIFIER(item)
                    act.save(self.UNIFIER.cfg['out_path'] if out_dir is None else out_dir)
                    self.ACTIVITIES.append(act)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Error processing item {item}: {e}")
        return self.ACTIVITIES


            