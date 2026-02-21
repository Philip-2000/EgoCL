class Metric:
    def __init__(self, name):
        self.name = name

    def __eq__(self,o):
        if isinstance(o, str): return o == self.name
        else: return o == self

class Metrics(list):
    def __init__(self, config):
        for n in config:  self.append(Metric(n))
    
    def idx(self, i):
        if isinstance(i, int): return i
        elif isinstance(i, str): return self.index(i)
        else:
            raise AssertionError
