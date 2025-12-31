class Experiment:
    def __init__(self, exp_config):
        self.exp_config = exp_config
        self.name = exp_config.get("name", "default_experiment")
        self.EXPERIENCES = exp_config.get("EXPERIENCES", [])
        self.EXECUTIONS  = exp_config.get("EXECUTIONS", "testing")
        self.METHODS = exp_config.get("METHODS", "DumpMethod")
        self.LOAD_STYLES = exp_config.get("LOAD_STYLES", "FORCE_CREATE")
        self.LOAD_STYLE_QUESTIONS = exp_config.get("LOAD_STYLE_QUESTIONS", "FORCE_CREATE")
        self.EGO = exp_config.get("EGO", True)
        self.OPTIONAL = exp_config.get("OPTIONAL", False)

    def __call__(self):
        from .Elements import Execution
        from ..data import Experience

        for id, EXP in enumerate(self.EXPERIENCES):

            experience_name = EXP
            execution_name = self.EXECUTIONS if isinstance(self.EXECUTIONS, str) else self.EXECUTIONS[id] #these experiments usually shares the same execution name and settings, so we should allow setting the execution name and settings globally for all experiences in the experiment
            load_style = self.LOAD_STYLES if isinstance(self.LOAD_STYLES, str) else self.LOAD_STYLES[id]
            load_style_questions = self.LOAD_STYLE_QUESTIONS if isinstance(self.LOAD_STYLE_QUESTIONS, str) else self.LOAD_STYLE_QUESTIONS[id]
            method = self.METHODS if isinstance(self.METHODS, str) else self.METHODS[id]

            En = Execution(name=execution_name, load_style=load_style, load_style_questions=load_style_questions, **self.exp_config.get("EXECUTION_KWARGS", {}))
            Ee = Experience.load_from_name(experience_name=experience_name)
            Ee.EGO = self.EGO
            En.OPTIONAL = self.OPTIONAL
            En.EXPERIENCE = Ee
            En.load()

            M = getattr(__import__("EgoCL.method", fromlist=[method]), method)(Ee, EXECUTION=En, **self.exp_config.get("METHOD_KWARGS", {}))
            En(METHOD=M)
        