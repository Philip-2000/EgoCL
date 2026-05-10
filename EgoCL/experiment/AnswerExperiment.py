
class AnswerExperiment:
    def __init__(self, **kwargs):
        from .Config import exp_config
        self.answer_config = exp_config(**kwargs)
        self.q_list = kwargs.get("q_list", "all")
        self.encode_only = kwargs.get("encode_only", False)
        self.name = self.answer_config.get("name", "answer_experiment")

        self.input_name = self.answer_config.get("input_name", self.name)
        self.output_name = self.answer_config.get("output_name", self.name)

        self.EXPERIENCE = self.answer_config["EXPERIENCE"]
        self.ANSWERING  = self.answer_config["EXECUTION"]
        self.METHOD = self.answer_config["METHOD"]

    def __call__(self):
        from .Elements import Answering
        from ..data import Experience
        E = Experience.load_from_name(experience_name=self.EXPERIENCE)
        A = Answering(name=self.ANSWERING, EXPERIENCE=E, q_list=self.q_list, encode_only=self.encode_only, EXPERIMENT=self, **self.answer_config.get("EXECUTION_KWARGS", {}))
        
        A.METHOD = getattr(__import__("EgoCL.method", fromlist=[self.METHOD]), self.METHOD)(E, EXECUTION=A, EXPERIMENT=self, **self.answer_config.get("METHOD_KWARGS", {}))
        self.ANSWERING = A
        self.METHOD = A.METHOD
        self.EXPERIENCE = E
        A()
    
    @property
    def MEMORY(self):
        return self.METHOD.MEMORY
