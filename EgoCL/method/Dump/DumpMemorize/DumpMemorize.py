from ...Base import Memorize

class DumpMemorize(Memorize):
    def __init__(self, METHOD):
        super().__init__()
        self.name = "DumpMemorize"
        self.METHOD = METHOD

        from . import DumpMemory
        self.MEMORY = DumpMemory(self)

    @property
    def EXPERIENCE(self):
        return self.METHOD.EXPERIENCE
    
    @property
    def TIME(self):
        return self.MEMORY.TIME

    def save(self):
        self.MEMORY.save()

    def __call__(self, anno):
        self.MEMORY(anno)
        