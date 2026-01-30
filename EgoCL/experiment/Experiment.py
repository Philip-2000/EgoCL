class Experiment:
    def __init__(self, **kwargs):
        from .Config import exp_config
        self.exp_config = exp_config(**kwargs) 
        self.name = self.exp_config.get("name", "experiment")
        self.EXPERIENCE = self.exp_config["EXPERIENCE"]
        self.EXECUTION  = self.exp_config["EXECUTION"]
        self.METHOD = self.exp_config["METHOD"]
        
    def __call__(self):
        from .Elements import Execution
        from ..data import Experience

        En = Execution(name=self.EXECUTION, EXPERIMENT=self, **self.exp_config.get("EXECUTION_KWARGS", {}))
        En.EXPERIENCE = Experience.load_from_name(experience_name=self.EXPERIENCE)
        En.METHOD = getattr(__import__("EgoCL.method", fromlist=[self.METHOD]), self.METHOD)(En.EXPERIENCE, EXECUTION=En, EXPERIMENT=self, **self.exp_config.get("METHOD_KWARGS", {}))
        En.load()
        En()