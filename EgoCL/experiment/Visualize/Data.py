class Data:
    def __init__(self, DATAS, i, v=None):
        self.DATAS = DATAS
        self.i = i
        self.v = v

    def source_name(self):
        return self.DATAS.SOURCES[i[0]].name

    def trail_name(self):
        return self.DATAS.TRAILS[i[1]].name

    def metric_name(self):
        return self.DATAS.METRICS[i[2]].name

class Datas():
    def __init__(self, config):
        if isinstance(config, dict):
            self.souce_load(config)
        if isinstance(config, str) and config.endswith('.tex'):
            self.tex_load(config)
    
    def tex_load(self, tex_path):
        import pylatex, os
        from pylatex import Tabular
        from pylatex.utils import NoEscape
        self.name = os.path.basename(tex_path).split('.')[0]
        
    def source_load(self, source_name):
        self.name = config['Name']
        config = config['Loader']
        from .Source import Sources
        from .Trail import Trails
        from .Metric import Metrics
        self.SOURCES = Sources(config["Sources"])
        self.TRAILS = Trails(config["Trails"])
        self.METRICS = Metrics(config["Metrics"])

        self.DATA = [[[Data(self,(i,j,k)) for k in range(len(self.METRICS))] for j in range(len(self.TRAILS))] for i in range(len(self.SOURCES))]

    def __getitem__(self,i):
        return self.DATA[self.SOURCES.idx(i[0])][self.TRAILS.idx(i[1])][self.METRICS.idx(i[2])]

    def __setitem__(self,i,v):
        self.DATA[self.SOURCES.idx(i[0])][self.TRAILS.idx(i[1])][self.METRICS.idx(i[2])].v = v

    @property
    def file_name(self):
        return "Datas.npz"

    @property
    def file_path(self):
        from EgoCL.paths import DATAS_ROOT
        from os.path import join as opj
        return opj(DATAS_ROOT, self.file_name)

    @property
    def exists(self):
        import os
        return os.path.exists(self.file_path)

    def to_dict(self):
        return {
            "name": self.name,
            "sources": [source.name for source in self.SOURCES],
            "trails": [trail.name for trail in self.TRAILS],
            "metrics": [metric.name for metric in self.METRICS],
            "data": [[[data.v for data in data_k] for data_k in data_j] for data_j in self.DATA]
        }

    def save(self):
        import numpy as np
        np.savez(self.file_path, **self.to_dict())

    def from_dict(self, data_dict):
        self.name = data_dict["name"]
        self.SOURCES = Sources(data_dict["sources"])
        self.TRAILS = Trails(data_dict["trails"])
        self.METRICS = Metrics(data_dict["metrics"])
        self.DATA = [[[Data(self,(i,j,k), data_dict["data"][i][j][k]) for k in range(len(self.METRICS))] for j in range(len(self.TRAILS))] for i in range(len(self.SOURCES))]

    def load(self):
        import numpy as np
        data_dict = np.load(self.file_path, allow_pickle=True)
        self.from_dict(data_dict)

class Loader:
    def __init__(self, config, raw=False):
        self.config = config
        self.DATAS = Datas(config)
        self.raw = raw
    
    @property
    def SOURCES(self):
        return self.DATAS.SOURCES
    
    @property
    def TRAILS(self):
        return self.DATAS.TRAILS

    @property
    def METRICS(self):
        return self.DATAS.METRICS
    
    def save(self):
        self.DATAS.save()

    def __call__(self):
        if self.raw or not self.DATAS.exists:
            self.DATAS.SOURCES.load(self)
            self.save()
        else:
            self.DATAS.load()