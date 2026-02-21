class Source:
    def __init__(self, name):
        self.name = name

        #感觉这个Source类是需要对Metrics类和Trails类有所感知的，
        #它才能知道“这个方法，它跑这这这次实验的时候，他的这个指标，存在了哪里”
        #这些代码是不是不能独立地存在在那个Trail和Metric类里面？

        #他们其实都是构建Datas对象，或者说填充Datas对象，往里面填充Data对象，
        #所以构建过程其实是需要Source类中的代码来完成的
        #那么

    def load(self, LOADER):
        raise NotImplementedError("Virtual Function")
    
    def __eq__(self,o):
        if isinstance(o, str): return o == self.name
        else: return o == self
    
    

class Sources(list):
    def __init__(self, config):
        for n in config:
            from . import SourceFactory
            self.append( SourceFactory(n) )
            
    def idx(self, i):
        if isinstance(i, int): return i
        elif isinstance(i, str): return self.index(i)
        else:
            raise AssertionError
    
    def load(self, LOADER):
        for SOURCE in self: SOURCE.load(LOADER)
