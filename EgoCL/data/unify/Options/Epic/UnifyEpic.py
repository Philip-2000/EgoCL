from ..UnifyBase import UnifyBase
class UnifyEpic(UnifyBase):
    def __init__(self, cfg):
        super().__init__(cfg)
        # Initialize Epic specific processing parameters here

    def __repr__(self):
        return f'{self.__class__}(cfg={self.cfg})'
    
    def __call__(self, item):
        # Implement the Epic specific processing logic here
        print(item)
        pass