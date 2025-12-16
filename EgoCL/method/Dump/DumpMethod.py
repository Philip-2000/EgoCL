from ..Base import Method

class DumpMethod(Method):
    def __init__(self, EXPERIENCE):
        super().__init__()
        self.name = "DumpMethod"
        self.EXPERIENCE = EXPERIENCE
        from . import DumpMemorize, DumpRespond
        self.MEMORIZER = DumpMemorize(self)
        self.RESPOND = DumpRespond(self)
    
    @property
    def TIME(self):
        return self.MEMORIZER.TIME
    
    @property
    def MEMORY(self):
        return self.MEMORIZER.MEMORY

    def progress(self, start_s, end_s):
        for anno in self.EXPERIENCE.iterate_annos(start_s, end_s):
            self.MEMORIZER(anno)
    
    def query(self, question):
        #first check the self.RESPOND.TIME and self.TIME
        if self.RESPOND.TIME.seconds_experience < self.TIME.seconds_experience:
            self.MEMORIZER.save()
            self.RESPOND.load(self.TIME.seconds_experience)

        return self.RESPOND(question)