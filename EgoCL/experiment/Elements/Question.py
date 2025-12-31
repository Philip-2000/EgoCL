import clip, torch
Comparer = None #clip.load("ViT-B/32")

class Question:
    def __init__(self, TIME=None, question: str = None, ref_time = None, answer: str = None, response: str = None, choices: list = None, QID : str = None):
        self.QUESTIONS = None
        self.TIME = TIME
        
        self.question = question
        self.ref_time = ref_time
        self.answer = answer
        self.response = response
        self.score = None
        self.choices = choices
        self.QID = QID
    
    @property
    def query(self):
        return self.question + (" Options: " + " ".join([chr(65+i) + ". " + str(option) for i, option in enumerate(self.choices)]) if self.choices else "")

    @property
    def OPTIONAL(self):
        return self.QUESTIONS.OPTIONAL
        
    @property
    def EXECUTION(self):
        return self.QUESTIONS.EXECUTION

    @property
    def EXPERIENCE(self):
        return self.EXECUTION.EXPERIENCE
    
    @property
    def to_dict(self):
        return {
            'TIME': self.TIME.to_dict if self.TIME is not None else None,
            'question': self.question,
            'ref_time': self.ref_time.to_dict if self.ref_time is not None else None,
            'answer': self.answer,
            'response': self.response,
            'score': self.score,
            'choices': self.choices
        }

    def from_dict(self, data_dict, load_style_respond="FORCE_LOAD"):
        from ...data.elements import TimeStamp

        self.TIME = TimeStamp()
        self.TIME.from_dict(data_dict.get('TIME', {}),None,None)
        self.ref_time = TimeStamp()
        self.ref_time.from_dict(data_dict.get('ref_time', {}),None,None)
        self.question = data_dict.get('question', None)
        self.answer = data_dict.get('answer', None)
        self.response = data_dict.get('response', None) if load_style_respond == "FORCE_LOAD" else None #For FORCE_CREATE, we do not load response, wishing the method to give new response later
        self.score = data_dict.get('score', None) if load_style_respond == "FORCE_LOAD" else None
        self.choices = data_dict.get('choices', None)

    def respond(self, response: str):
        self.response = response
        self.evaluate()

    def evaluate(self):
        if self.OPTIONAL:
            self.score = int(self.answer[:1].lower() == self.response[:1].lower())*1.0 #compare the first character only
            return
        global Comparer
        if Comparer is None:
            Comparer, _ = clip.load("ViT-B/32")
            Comparer.eval()
        with torch.no_grad():
            a = str(self.answer)
            b = str(self.response)
            # tokenize and move to model device
            device = next(Comparer.parameters()).device
            tokens = clip.tokenize([a, b], truncate=True).to(device)
            embeds = Comparer.encode_text(tokens)  # (2, D)
            # normalize and compute cosine similarity
            embeds = embeds / embeds.norm(dim=-1, keepdim=True)
            self.score = float((embeds[0] * embeds[1]).sum().item())

class Questions:
    def __init__(self, load_style_question, load_style_respond):
        self.EXECUTION = None
        self.RESULTS = None
        self.QUESTIONS = []
        self.load_style_question = load_style_question
        self.load_style_respond = load_style_respond
    
    def __iadd__(self, question: Question):
        self.QUESTIONS.append(question)
        question.QUESTIONS = self
        return self

    @property
    def EXPERIENCE(self):
        return self.EXECUTION.EXPERIENCE

    @property
    def OPTIONAL(self):
        return self.EXECUTION.OPTIONAL

    def from_dict(self, data_list: list, load_style_respond="FORCE_LOAD"):
        from .Question import Question
        for q_data in data_list:
            Q = Question()
            Q.from_dict(q_data, load_style_respond=load_style_respond)
            self += Q

    @property
    def to_dict(self):
        return [q.to_dict for q in self.QUESTIONS]

    def evaluate_all(self):
        for q in self.QUESTIONS:
            q.evaluate()

    def short_report(self, TIME):
        scores = [q.score for q in self.QUESTIONS if abs(q.TIME.seconds_experience - TIME.seconds_experience)< self.EXECUTION.METHOD.atom_s * 1.1 and q.score is not None]
        return f"At TIME {TIME.seconds_experience}s, {len(scores)} questions evaluated, Average Score: {sum(scores)/len(scores) if len(scores)>0 else 'N/A'}"
    
    def __iter__(self):
        return iter(self.QUESTIONS)
    
    def __len__(self):
        return len(self.QUESTIONS)