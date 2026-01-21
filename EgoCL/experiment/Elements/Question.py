from ... import YOG
Comparer = None

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
    def METHOD(self):
        return self.QUESTIONS.METHOD
    
    @property
    def mode(self):
        return self.QUESTIONS.mode

    @property
    def EXECUTION(self):
        return self.QUESTIONS.EXECUTION

    @property
    def EXPERIENCE(self):
        return self.EXECUTION.EXPERIENCE
    
    @property
    def to_dict(self):
        return {
            'uid': self.QID,
            'TIME': self.TIME.to_dict if self.TIME is not None else None,
            'question': self.question,
            'ref_time': self.ref_time.to_dict if self.ref_time is not None else None,
            'answer': self.answer,
            'response': str(self.response) if self.response is not None else None,
            'score': self.score,
            'choices': self.choices,
            'open_ended': getattr(self, 'open_ended', None)
        }
    
    def res_dict(self, CACHE_DIR):
        return {
            'uid': self.QID,
            'TIME': self.TIME.to_dict if self.TIME is not None else None,
            'question': self.question,
            'ref_time': self.ref_time.to_dict if self.ref_time is not None else None,
            'ground_truth': self.ground_truth(CACHE_DIR),
            'answer': self.answer,
            'choices': self.choices,
            'response': (self.response.res_dict if hasattr(self.response, "res_dict") else str(self.response)) if self.response is not None else None,
            'score': self.score,
            'open_ended': (self.open_ended.res_dict if hasattr(self.open_ended, "res_dict") else str(self.open_ended)) if getattr(self, 'open_ended', None) is not None else None,
        }

    def from_dict(self, data_dict, load_style_respond="FORCE_LOAD"):
        from ...data.elements import TimeStamp, TimeSpan

        self.TIME = TimeStamp()
        self.TIME.from_dict(data_dict.get('TIME', {}),None,None)
        self.ref_time = TimeSpan(TimeStamp(),TimeStamp())
        self.ref_time.from_dict(data_dict.get('ref_time', {}),None,None)
        self.question = data_dict.get('question', None)
        self.answer = data_dict.get('answer', None)
        self.response = data_dict.get('response', None) if load_style_respond == "FORCE_LOAD" else None #For FORCE_CREATE, we do not load response, wishing the method to give new response later
        self.score = data_dict.get('score', None) if load_style_respond == "FORCE_LOAD" else None
        self.choices = data_dict.get('choices', None)
        self.QID = data_dict.get('uid', None)

    def respond(self, response):
        if self.mode == "normal":
            self.response = response
            self.evaluate()
        else:  #strong mode
            self.open_ended = response
            from .. import CHOOSER_PROMPT
            full_prompt = CHOOSER_PROMPT + f"\nQuestion: {self.question}\nOpen-ended Answer: {self.open_ended}\nChoices: " + " ".join([chr(65+i) + ". " + str(option) for i, option in enumerate(self.choices)]) + "\nYour Answer:"
            self.response = self.METHOD.VlmBase({"content":[{"text": full_prompt}]})
            self.evaluate()
    
    def __cache_video(self, CACHE_DIR, clip, start_s, end_s):
        import os
        # from ...paths import CACHE_DIR
        os.makedirs(CACHE_DIR, exist_ok=True)
        video_cache_path = os.path.join(CACHE_DIR, f"{self.EXPERIENCE.name}_{self.QID}_{int(start_s)}_{int(end_s)}.mp4")
        if os.path.exists(video_cache_path):
            return video_cache_path
        
        #clip.write_videofile(video_cache_path, codec="libx264", audio_codec="aac", logger=None, fps=self.num_segments / self.atom_s)
        #change the following line to, get the frames at 0/self.num_segments, 1/self.num_segments, 2/self.num_segments...... (self.num_segments-1)/self.num_segments time position of "clip", whose length is self.atom_s, and concatenate them with a frame rate of 2, as a new clip, and then save that clip
        from moviepy import concatenate_videoclips, ImageClip
        frame_clips = []
        self.num_segments = 20
        self.FPS = 2
        self.width = 540
        for i in range(self.num_segments):
            t = (i / self.num_segments) * (end_s - start_s)
            frame = clip.get_frame(t)
            ratio = frame.shape[1] / frame.shape[0]
            img_clip = ImageClip(frame).with_duration(1/self.FPS)
            img_clip = img_clip.resized((self.width, int(self.width * ratio)))
            frame_clips.append(img_clip)
        sampled_clip = concatenate_videoclips(frame_clips, method="compose")
        sampled_clip.write_videofile(video_cache_path, codec="libx264", audio_codec="aac", logger=None, fps=self.FPS)
                
        YOG.debug(f"Video cached at {video_cache_path}", tag="Video Caching")
        return video_cache_path


    def transform_transcripts(self, transcripts):
        # transcripts is a list of pysrts.Subtitle, please convert it to time + text
        # convert to text
        text_list = []
        for subtitle in transcripts:
            start_time = subtitle.start.to_time()
            end_time = subtitle.end.to_time()
            #the start_time and end_time are datetime.time object, convert them to string
            start_time = f"{start_time.minute:01d}min{start_time.second:02d}s"
            end_time = f"{end_time.minute:01d}min{end_time.second:02d}s"
            text = subtitle.text.replace("\n", " ")
            text_list.append(f"[{start_time}-{end_time}] {text}")
        return text_list

    def ground_truth(self, CACHE_DIR):
        video, transcript = self.EXPERIENCE.time_to_video(max(self.ref_time.STARTSTAMP.seconds_experience-5.0,0.0), min(self.ref_time.ENDSTAMP.seconds_experience+5.0, self.EXPERIENCE.duration_s))
        
        video_path = self.__cache_video(CACHE_DIR,video, max(self.ref_time.STARTSTAMP.seconds_experience-5.0,0.0), min(self.ref_time.ENDSTAMP.seconds_experience+5.0, self.EXPERIENCE.duration_s))
        
        return {'video_path': video_path, 'transcript': self.transform_transcripts(transcript)}

    def evaluate(self):
        if self.OPTIONAL:
            self.score = int(str(self.answer)[:1].lower() == str(self.response)[:1].lower())*1.0 #compare the first character only
            return
        global Comparer
        if Comparer is None:
            from sentence_transformers import SentenceTransformer
            Comparer = SentenceTransformer("/mnt/data/models/Qwen3-Embedding-0.6B")
        self.score = float(Comparer.similarity(Comparer.encode([self.answer]), Comparer.encode([self.response]))[0][0])
        
class Questions:
    def __init__(self, load_style_question, load_style_respond):
        self.EXECUTION = None
        self.RESULTS = None
        self.QUESTIONS = []
        self.load_style_question = load_style_question
        self.load_style_respond = load_style_respond
    
    def get_question_by_QID(self, QID):
        for q in self.QUESTIONS:
            if q.QID == QID:
                return q
        return None
    
    def sort_by_time(self):
        self.QUESTIONS = sorted(self.QUESTIONS, key=lambda x: x.TIME.seconds_experience)

    def __iadd__(self, question: Question):
        self.QUESTIONS.append(question)
        question.QUESTIONS = self
        return self

    @property
    def mode(self):
        return self.EXECUTION.mode

    @property
    def EXPERIENCE(self):
        return self.EXECUTION.EXPERIENCE

    @property
    def OPTIONAL(self):
        return self.EXECUTION.OPTIONAL
    
    @property
    def METHOD(self):
        return self.EXECUTION.METHOD

    def from_dict(self, data_list: list, load_style_respond="FORCE_LOAD"):
        from .Question import Question
        for q_data in data_list:
            Q = Question()
            Q.from_dict(q_data, load_style_respond=load_style_respond)
            self += Q

    @property
    def to_dict(self):
        return [q.to_dict for q in self.QUESTIONS]

    def save_res(self, dir):
        import os, json
        os.makedirs(dir, exist_ok=True)
        cache_dir = os.path.join(dir, "..", "RefVideos")
        os.makedirs(cache_dir, exist_ok=True)
        file_path = os.path.join(dir, "results.json")
        with open(file_path, 'w') as f:
            json.dump([q.res_dict(CACHE_DIR=cache_dir) for q in self.QUESTIONS if q.response is not None], f, indent=4, ensure_ascii=False)
    
    def load_res(self, dir):
        import os, json
        file_path = os.path.join(dir, "results.json")
        if not os.path.exists(file_path):
            return
        with open(file_path, 'r') as f:
            res_list = json.load(f)
        res_dict = {res['uid']: res for res in res_list}
        for q in self.QUESTIONS:
            if q.QID in res_dict:
                q.response = res_dict[q.QID]['response']
                q.score = res_dict[q.QID]['score']

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