class Concatenator:
    def __init__(self, **kwargs):
        self.style=kwargs.get('style','sequential') #'random', 'clip'
        self.clip=kwargs.get('clip',-1)

    def __call__(self, config, **kwargs):
        from .. import loader
        from ..elements.Experience import Experience
        import random
        activities = loader(type('', (), {'item_config': config})()).activities
        if self.style=='random': random.shuffle(activities)
        if self.style=='clip': activities = activities[:self.clip]            
        return Experience(activities, **kwargs)
        
        