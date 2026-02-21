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

class Loader:
    def __init__(self, config):
        self.config = config
        self.DATAS = Datas(config)
    
    @property
    def SOURCES(self):
        return self.DATAS.SOURCES
    
    @property
    def TRAILS(self):
        return self.DATAS.TRAILS

    @property
    def METRICS(self):
        return self.DATAS.METRICS

    def __call__(self):
        self.DATAS.SOURCES.load(self)