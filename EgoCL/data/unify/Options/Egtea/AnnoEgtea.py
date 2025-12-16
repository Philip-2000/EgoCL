import os, json

class AnnoEgtea:
    def __init__(self, json_base, anno_tags=["action"], *args, **kwds):
        pass

        #["action", "hand", "gaze"]
        self.anno_tags = anno_tags
        #load the annotation json files from os
        self.json_base = json_base
        self.configs = {}
        for anno_tag in self.anno_tags:
            getattr(self, f"_{self.__class__.__name__}__{anno_tag}_load")()
    
    def __call__(self, ACTIVITY):
        for anno_tag in self.anno_tags:
            getattr(self, f"_{self.__class__.__name__}__{anno_tag}")(ACTIVITY)
    

    def __action_load(self):
        import pandas as pd
        self.configs['action'] = pd.read_csv(
            os.path.join(self.json_base, 'action_annotation', 'raw_annotations', 'action_labels.csv'),
            sep=';',
            skipinitialspace=True,
            encoding='utf-8'
        )

        # if not os.path.exists(os.path.join(self.json_base, 'action_annotation', 'raw_annotations', 'action_labels_comma.csv')):
        #     txt = open(os.path.join(self.json_base, 'action_annotation', 'raw_annotations', 'action_labels.csv')).read()
        #     txt = txt.replace('; ', ',')
        #     with open(os.path.join(self.json_base, 'action_annotation', 'raw_annotations', 'action_labels_comma.csv'), 'w') as f:
        #         f.write(txt)
        # self.configs['action'] = pd.read_csv(os.path.join(self.json_base, 'action_annotation', 'raw_annotations', 'action_labels_comma.csv'))

    def __action(self, ACTIVITY):

        #configs['action'] example
        ## Clip ID (Unique, used only internally); Clip Prefix (Unique); Video Session; Starting Time (ms);  Ending Time (ms); Action Label; Verb Label; Noun Label(s)
        # 1; P05-R01-PastaSalad-583261-586055; P05-R01-PastaSalad; 583261; 586055; Cut tomato; Cut; tomato
        # 2; P07-R01-PastaSalad-91730-93630; P07-R01-PastaSalad; 91730; 93630; Take eating_utensil; Take; eating_utensil
        # 3; P03-R01-PastaSalad-1409619-1415214; P03-R01-PastaSalad; 1409619; 1415214; Transfer cucumber,cutting_board,bowl; Transfer; cucumber,cutting_board,bowl
        # 4; P11-R02-TurkeySandwich-523575-527805; P11-R02-TurkeySandwich; 523575; 527805; Squeeze condiment,sandwich; Squeeze; condiment,sandwich
        # 5; P06-R02-TurkeySandwich-443615-444488; P06-R02-TurkeySandwich; 443615; 444488; Squeeze washing_liquid,plate; Squeeze; washing_liquid,plate
        # 6; P17-R03-BaconAndEggs-1282100-1288200; P17-R03-BaconAndEggs; 1282100; 1288200; Wash cooking_utensil; Wash; cooking_utensil

        name = ACTIVITY.name #where name is like P05-R01-PastaSalad, so we need to match the prefix
        current_config = self.configs['action'][self.configs['action']['Video Session'] == name]
        for raw_config in current_config.to_dict('records'):
            anno_dict = {
                "category": "action",
                "time": {
                    "start_s": raw_config['Starting Time (ms)'] / 1000.0,
                    "end_s": raw_config['Ending Time (ms)'] / 1000.0
                },
                "information": {
                    "text": raw_config['Action Label'],
                    "verb label": raw_config['Verb Label'],
                    "noun label(s)": raw_config['Noun Label(s)'],
                }
            }
            ACTIVITY += anno_dict
        pass

    def __hand_load(self):
        self.configs['hand'] = os.listdir(os.path.join(self.json_base, 'hand14k', "Images"))

    def __hand(self, ACTIVITY):
        raise NotImplementedError("AnnoEgtea::__hand not implemented yet.")

    def __gaze_load(self):
        self.configs['gaze'] = os.listdir(os.path.join(self.json_base, 'gaze_data', "gaze_data"))

    def __gaze(self, ACTIVITY):
        raise NotImplementedError("AnnoEgtea::__gaze not implemented yet.")
    

