import os
from ..UnifyBase import UnifyBase
from ...elements.Activity import Activity
from .AnnoEgolife import AnnoEgolife

class UnifyEgolife(UnifyBase):
    def __init__(self, cfg):
        super().__init__(cfg)
        # Initialize Egtea specific processing parameters here
        self.cfg = cfg

        json_base = os.path.join(self.cfg['in_path'])
        self.ANNOEGOLIFE = AnnoEgolife(json_base=json_base, anno_tags=cfg.get('anno_tags', ['action']))
        self.video_base = os.path.join(self.cfg['in_path'], 'screened_videos')
        

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
        activity_config = {
            'name': item,
            'source': 'Egolife',
            'ANNOS': {},
            'VIDEO': {
                'video_path': f"{self.video_base}/{item}.mp4",
                'start_s': 0 if "start_s" not in kwargs else kwargs['start_s'],
                'end_s': self.__length(f"{self.video_base}/{item}.mp4") if "end_s" not in kwargs else kwargs['end_s']
            }
        }
        a = Activity(activity_config)
        self.ANNOEGTEA(a)
        return a

class UnifyEgolife_S:
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
        self.UNIFIER = UnifyEgolife(kwargs)
        self.ACTIVITIES = []

    def __call__(self, out_dir=None):
        from tqdm import tqdm

        for item in tqdm(self.list):
            act = self.UNIFIER(item)
            act.save(self.UNIFIER.cfg['out_path'] if out_dir is None else out_dir)
            self.ACTIVITIES.append(act)
        return self.ACTIVITIES