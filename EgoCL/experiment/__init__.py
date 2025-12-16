from .AnnoExperiment import AnnoExperiment
from .Experiment import Experiment
from .Elements import Execution, Questions
from ..paths import EXPERIMENT_ROOT

QUESTION_GENERATOR_PROMPT="You are a question generator which generate a question based on the provided experience annotations.\
    You will be provided with experience annotations, and please ask a detailed question about the experience based on the annotations and generate the answer.\
    Seperate the question and the answer with <|answer_separator|>\
    The question should be specific and related to the details mentioned in the annotations.\
    For example, if the annotations mention an object or an action, you can ask about its characteristics, purpose, or context.\
    For an annotation like 'Person A is holding a red ball', you might give 'What is the color of the ball that Person A is holding? <|answer_separator|> The ball is red."
