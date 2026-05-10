from ... import YOG
Comparer = None

class Question:
    def __init__(self, TIME=None, question: str = None, ref_time = None, answer: str = None, response: str = None, choices: list = None, QID : str = None, image = None):
        self.QUESTIONS = None
        self.TIME = TIME
        
        self.question = question
        self.ref_time = ref_time
        self.answer = answer
        self.response = response
        self.response_strong = None
        self.score = {}
        self.choices = choices
        self.QID = QID
        self.image = image
    
    @property
    def Image(self):
        if self.image is None:
            return None
        if self.image == "current":
            return self.EXPERIENCE.time_to_image(self.TIME.seconds_experience)
        import os
        if os.path.exists(self.image) and os.path.isfile(self.image) and self.image.lower().endswith(('.png', '.jpg', '.jpeg')):
            return self.image
        
    @property
    def query(self):
        return self.question + (" Options: " + " ".join([chr(65+i) + ". " + str(option) for i, option in enumerate(self.choices)]) if self.choices else "")

    @property
    def answer_string(self):
        if self.choices is None:
            return str(self.answer)
        else:
            return self.choices[ord(self.answer[0])-ord('A')]

    @property
    def OPTIONAL(self):
        return self.QUESTIONS.OPTIONAL
    
    @property
    def EXPERIMENT(self):
        return self.QUESTIONS.EXPERIMENT

    @property
    def METHOD(self):
        return self.QUESTIONS.METHOD
    
    # @property
    # def mode(self):
    #     return self.QUESTIONS.mode

    @property
    def option(self):
        return self.QUESTIONS.option
    
    @property
    def strong(self):
        return self.QUESTIONS.strong

    @property
    def EXECUTION(self):
        return self.QUESTIONS.EXECUTION

    @property
    def EXPERIENCE(self):
        return self.EXECUTION.EXPERIENCE
    
    @property
    def to_dict(self):
        return {
            'image': self.image,
            'uid': self.QID,
            'TIME': self.TIME.to_dict if self.TIME is not None else None,
            'question': self.question,
            'ref_time': self.ref_time.to_dict if self.ref_time is not None else None,
            'answer': self.answer,
            'response': str(self.response) if self.response is not None else None,
            'response_strong': str(self.response_strong) if getattr(self, 'response_strong', None) is not None else None,
            'score': self.score,
            'choices': self.choices,
            'open_ended': getattr(self, 'open_ended', None)
        }
    
    def res_dict(self, caching_video=True):
        return {
            'uid': self.QID,
            'TIME': self.TIME.to_dict if self.TIME is not None else None,
            'question': self.question,
            'ref_time': self.ref_time.to_dict if self.ref_time is not None else None,
            'ground_truth': self.ground_truth(caching_video=caching_video),
            'answer': self.answer,
            'choices': self.choices,
            'response': (self.response.res_dict if hasattr(self.response, "res_dict") else str(self.response)) if self.response is not None else None,
            'response_strong': (self.response_strong.res_dict if hasattr(self.response_strong, "res_dict") else str(self.response_strong)) if getattr(self, 'response_strong', None) is not None else None,
            'score': self.score,
            'open_ended': (self.open_ended.res_dict if hasattr(self.open_ended, "res_dict") else str(self.open_ended)) if getattr(self, 'open_ended', None) is not None else None,
            'image': self.image
        }
    
    # def save_res(self, dir, caching_video=True):
    #     YOG.info(f"Saving result for Question ID: {self.QID} at {dir}", tag="Question Save Result")
    #     import os, json
    #     os.makedirs(dir, exist_ok=True)
    #     cache_dir = os.path.join(dir, "..", "RefVideos")
    #     os.makedirs(cache_dir, exist_ok=True)
    #     file_path = os.path.join(dir, "results.json")
    #     if os.path.exists(file_path):
    #         json_data = json.load(open(file_path, 'r'))
    #         json_data = [q for q in json_data if q['uid'] != self.QID] + [self.res_dict(CACHE_DIR=cache_dir, caching_video=caching_video)]
    #         with open(file_path, 'w') as f:
    #             json.dump(json_data, f, indent=4, ensure_ascii=False)
    #     else:
    #         with open(file_path, 'w') as f:
    #             json.dump([self.res_dict(CACHE_DIR=cache_dir, caching_video=caching_video)], f, indent=4, ensure_ascii=False)
    

    def call(self, *args, **kwargs):
        return self.QUESTIONS.call(*args, **kwargs)

    def tall(self, *args, **kwargs):
        return self.QUESTIONS.tall(*args, **kwargs)

    def encode(self, s):
        return self.QUESTIONS.encode(s)
    
    @property
    def ENCODER(self):
        return self.QUESTIONS.ENCODER

    @property
    def I_Dont_Know(self):
        return self.QUESTIONS.I_Dont_Know if hasattr(self.QUESTIONS, "I_Dont_Know") else False

    @property
    def file_name(self):
        from EgoCL.paths import RESULTS_FILE
        return RESULTS_FILE(self)

    def save_res(self, caching_video=True):
        import os, json
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        with open(self.file_name, 'w') as f:
            json.dump(self.res_dict(caching_video=caching_video), f, indent=4, ensure_ascii=False)

    def from_dict(self, data_dict, load_style_respond="FORCE_LOAD"):
        from ...data.elements import TimeStamp, TimeSpan

        self.TIME = TimeStamp()
        self.TIME.from_dict(data_dict.get('TIME', {}),None,None)
        self.ref_time = TimeSpan(TimeStamp(),TimeStamp())
        self.ref_time.from_dict(data_dict.get('ref_time', {}),None,None)
        self.question = data_dict.get('question', None)
        self.answer = data_dict.get('answer', None)
        self.response = data_dict.get('response', None) if load_style_respond == "FORCE_LOAD" else None #For FORCE_CREATE, we do not load response, wishing the method to give new response later
        self.response_strong = data_dict.get('response_strong', None) if load_style_respond == "FORCE_LOAD" else None
        self.score = data_dict.get('score', {}) if load_style_respond == "FORCE_LOAD" else {}
        self.choices = data_dict.get('choices', None)
        self.QID = data_dict.get('uid', None)
        self.image = data_dict.get('image', None)

    def respond(self, response, response_strong=None):
        if self.option:
            self.response = response

        if self.strong:
            self.response_strong = response_strong

        self.evaluate()

        # return
        # if self.mode == "normal":
        #     self.response = response
        #     self.evaluate()
        # else:  #strong mode
        #     self.open_ended = response
        #     from .. import CHOOSER_PROMPT
        #     full_prompt = CHOOSER_PROMPT + f"\nQuestion: {self.question}\nOpen-ended Answer: {self.open_ended}\nChoices: " + " ".join([chr(65+i) + ". " + str(option) for i, option in enumerate(self.choices)]) + "\nYour Answer:"
        #     self.response = self.METHOD.VlmBase({"content":[{"text": full_prompt}]})
        #     self.evaluate()
    
    def __cache_video(self, clip, start_s, end_s, caching_video=True):
        import os
        # from ...paths import CACHE_DIR
        from EgoCL.paths import REFVIDEO_FILE
        # os.makedirs(CACHE_DIR, exist_ok=True)
        video_cache_path = REFVIDEO_FILE(self, start_s, end_s)
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

    def ground_truth(self, caching_video=True):

        video, transcript = self.EXPERIENCE.time_to_video(max(self.ref_time.STARTSTAMP.seconds_experience-5.0,0.0), min(self.ref_time.ENDSTAMP.seconds_experience+5.0, self.EXPERIENCE.duration_s))
        
        if caching_video:
            video_path = self.__cache_video(video, max(self.ref_time.STARTSTAMP.seconds_experience-5.0,0.0), min(self.ref_time.ENDSTAMP.seconds_experience+5.0, self.EXPERIENCE.duration_s), caching_video=caching_video)
        else:
            from EgoCL.paths import REFVIDEO_FILE
            video_path = REFVIDEO_FILE(self, max(self.ref_time.STARTSTAMP.seconds_experience-5.0,0.0), min(self.ref_time.ENDSTAMP.seconds_experience+5.0, self.EXPERIENCE.duration_s))

        return {'video_path': video_path, 'transcript': self.transform_transcripts(transcript)}

    def evaluate(self):
        if self.I_Dont_Know:
            self.score = {}
            return

        if self.option and self.response is not None:
            self.score["option"] = int(str(self.answer)[:1].lower() == str(self.response)[:1].lower())*1.0  #compare the first character only
        
        if self.strong and self.response_strong is not None:
            
            
            # answer_string_encode = self.encode([self.answer_string])
            # encodes = self.encode(self.choices)
            response_strong_raw = str(self.response_strong).strip()
            # response_strong_encode = self.encode([response_strong_raw])

            # simis = self.ENCODER.similarity(response_strong_encode, encodes)  #smaller is closer

            simis = self.ENCODER.sim(response_strong_raw, self.choices)  #larger is closer

            closest_idx = simis.flatten(start_dim=0).argmax().item()
            self.score["closest"] = int(closest_idx == (ord(self.answer[0])-ord('A')))*1.0
            # self.score["similarity"] = float(self.ENCODER.similarity(response_strong_encode, answer_string_encode))
            self.score["similarity"] = float(self.ENCODER.sim(response_strong_raw, self.answer_string))
            
            llm_choose_force = self.tall(
                {"content":[{"user":f"Question: {self.question}\nChoices: " + " ".join([chr(65+i) + ". " + str(option) for i, option in enumerate(self.choices)]) + f"\nYour Answer: {response_strong_raw}\nWhich option (A, B, C, ...) is the closest answer? Pick one even you think that none of them is appropriate."}]}
            ).strip()
            self.score["llm_choose_force"] = int(llm_choose_force[0].upper() == self.answer[0].upper())
            llm_choose = self.tall(
                {"content":[{"user":f"Question: {self.question}\nChoices: " + " ".join([chr(65+i) + ". " + str(option) for i, option in enumerate(self.choices)]) + f"\nYour Answer: {response_strong_raw}\nWhich option (A, B, C, ...) is the closest answer? If you think that none of them is appropriate, please say N."}]}
            ).strip()
            self.score["llm_choose"] = int(llm_choose[0].upper() == self.answer[0].upper())
            llm_judge = self.tall(
                {"content":[{"user":f"Question: {self.question}" + f"\nThe correct answer is {self.answer_string}. Is the answer '{response_strong_raw}' correct? Answer with Yes or No."}]}
            ).strip()
            self.score["llm_judge"] = int(llm_judge.strip().lower()[:3] == "yes")*1.0

        # return
        # if self.OPTIONAL:
        #     self.score = int(str(self.answer)[:1].lower() == str(self.response)[:1].lower())*1.0 #compare the first character only
        #     return
        # global Comparer
        # if Comparer is None:
        #     from sentence_transformers import SentenceTransformer
        #     Comparer = SentenceTransformer("/mnt/data/models/Qwen3-Embedding-0.6B")
        # self.score = float(Comparer.similarity(Comparer.encode([self.answer]), Comparer.encode([self.response]))[0][0])
        
class Questions:
    def __init__(self, load_style_question, load_style_respond):
        self.EXECUTION = None
        self.RESULTS = None
        self.QUESTIONS = []
        self.load_style_question = load_style_question
        self.load_style_respond = load_style_respond
    
    def get_question_by_QID(self, QID):
        for q in self.QUESTIONS:
            if q.QID == QID: return q
        return None
    
    def sort_by_time(self):
        self.QUESTIONS = sorted(self.QUESTIONS, key=lambda x: x.TIME.seconds_experience)

    def __iadd__(self, question: Question):
        self.QUESTIONS.append(question)
        question.QUESTIONS = self
        return self

    @property
    def I_Dont_Know(self):
        return self.EXECUTION.I_Dont_Know if hasattr(self.EXECUTION, "I_Dont_Know") else False

    def call(self, *args, **kwargs):
        return self.EXECUTION.call(*args, **kwargs)

    def tall(self, *args, **kwargs):
        return self.EXECUTION.tall(*args, **kwargs)
    
    def encode(self, s):
        return self.EXECUTION.encode(s)
    
    @property
    def ENCODER(self):
        return self.EXECUTION.ENCODER

    @property
    def option(self):
        return self.EXECUTION.option

    @property
    def strong(self):
        return self.EXECUTION.strong

    @property
    def EXPERIENCE(self):
        return self.EXECUTION.EXPERIENCE
    
    @property
    def EXPERIMENT(self):
        return self.EXECUTION.EXPERIMENT

    # @property
    # def OPTIONAL(self):
    #     return self.EXECUTION.OPTIONAL
    
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

    # def save_res(self, dir, caching_video=True):
    #     raise AssertionError("Saving all question results in one file is deprecated. Please use each Question's save_res method instead.")
    #     import os, json
    #     os.makedirs(dir, exist_ok=True)
    #     cache_dir = os.path.join(dir, "..", "RefVideos")
    #     os.makedirs(cache_dir, exist_ok=True)
    #     file_path = os.path.join(dir, "results.json")
    #     with open(file_path, 'w') as f:
    #         json.dump([q.res_dict(CACHE_DIR=cache_dir, caching_video=caching_video) for q in self.QUESTIONS if q.response is not None], f, indent=4, ensure_ascii=False)
    
    # def load_res(self, dir):
    #     import os, json
    #     file_path = os.path.join(dir, "results.json")
    #     if not os.path.exists(file_path):
    #         return
    #     with open(file_path, 'r') as f:
    #         res_list = json.load(f)
    #     res_dict = {res['uid']: res for res in res_list}
    #     for q in self.QUESTIONS:
    #         if q.QID in res_dict:
    #             q.response = res_dict[q.QID]['response']
    #             q.score = res_dict[q.QID]['score']

    def evaluate_all(self):
        for q in self.QUESTIONS:
            q.evaluate()

    def short_report(self, TIME):
        scores = [q.score for q in self.QUESTIONS if abs(q.TIME.seconds_experience - TIME.seconds_experience)< self.EXECUTION.METHOD.atom_s * 1.1 and q.score is not None]
        return f"At TIME {TIME.seconds_experience}s, {len(scores)} questions evaluated, Average Score: {sum([s['option'] for s in scores])/len(scores) if len(scores)>0 and 'option' in scores[0] else 'N/A'}"
    
    def __iter__(self):
        return iter(self.QUESTIONS)
    
    def __len__(self):
        return len(self.QUESTIONS)