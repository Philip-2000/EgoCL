
#Data:

from os.path import join as opj

RAW_ROOT = opj("/mnt", "data", "raw_data")
RAW_PATHS_GLOBAL = { #key name are all lowercase
    "epic": opj("/home", "yl", "EPIC-KITCHENS"), #temporarily only support for yl on -p 1022
    "ego4d": opj(RAW_ROOT, "Ego4d", "v2"),
    "egtea": opj("/home", "yl", "EGTEA"),
    "egolife": opj(RAW_ROOT, "EgoLife"), #these datasets are welcomed to be places side by side under DATA_ROOT, so u only need to change DATA_ROOT if necessary
}

UNI_ROOT = opj("/mnt", "data", "yl", "D", "EgoCL") #opj("/home", "yl", "D") #
UNI_PATHS_GLOBAL = { #key name are all lowercase
    "epic": opj(UNI_ROOT, "EPIC-KITCHENS"),
    "ego4d": opj(UNI_ROOT, "Ego4d"),
    "egtea": opj(UNI_ROOT, "EGTEA"),
    "egolife": opj(UNI_ROOT, "EgoLife"),
}

W_ROOT = opj("/mnt", "data", "yl", "W")
EgoCL_ROOT = opj(W_ROOT, "EgoCL")

EPRC_ROOT = opj(EgoCL_ROOT, "Experience")


#Method:


CACHE_DIR = opj(EgoCL_ROOT, "Cache")  # The cache directory for EgoCL
MEMORY_ROOT = opj(EgoCL_ROOT, "Memory")
MEMORY_PATHS_GLOBAL = { #key name are all lowercase
    
}

def MEMORY_DIR(E, M): # the final memory path is set as: MEMORY_ROOT / experience_id / method_name / memory_files
    return opj(MEMORY_ROOT, E if isinstance(E, str) else E.name, M if isinstance(M, str) else M.__class__.__name__)


#Experiment:
EXPERIMENT_ROOT = opj(EgoCL_ROOT, "Experiment")
#Experiment Images
EXPERIMENT_IMAGES_ROOT = opj(EXPERIMENT_ROOT, "images")

#Visualize:
VIS_ROOT = opj(EgoCL_ROOT, "Visualize")

#Model
# MODEL = "InternVideo2.5-Chat-8B"
# MODEL = "InternVL3_5-8B"
MODEL = "Qwen3-VL-8B-Instruct"
# MODEL = "Qwen2.5-VL-7B-Instruct"
# MODEL = "LLaVA-NeXT-Video-7B-hf"
# MODEL = "LLaVA-Video-7B-Qwen2"
# MODEL = "llava-onevision-qwen2-7b-ov"



def EXPERIENCE_FILE(experience_name):
    return opj(EPRC_ROOT, f"{experience_name}.json")

def EXECUTION_FILE(execution_object):
    return opj(EXPERIMENT_ROOT, execution_object.name, execution_object.EXPERIENCE.name, "execution.json")

def MEMORY_FILE(memory_object):
    #path = opj(MEMORY_ROOT, self.EXPERIENCE.name, self.METHOD.name, f"{int(self.TIME.seconds_experience):06d}", f"{self.EXPERIMENT.name}_memory.json")
    return opj(MEMORY_DIR(memory_object.EXPERIENCE, memory_object.METHOD), f"{int(memory_object.TIME.seconds_experience):06d}", f"{memory_object.EXPERIMENT.name}_memory.json")

def ENCODINGS_FILE(encodings_object):
    #file_path = opj(MEMORY_ROOT, self.EXPERIENCE.name, self.METHOD.name, f"{int(self.TIME.seconds_experience):06d}", f"{self.EXPERIMENT.name}_encodes.npz")
    name = encodings_object.EXPERIMENT.output_name if hasattr(encodings_object.EXPERIMENT, 'output_name') else encodings_object.METHOD.EXPERIMENT.name
    return opj(MEMORY_DIR(encodings_object.EXPERIENCE, encodings_object.METHOD), f"{int(encodings_object.TIME.seconds_experience):06d}", f"{name}_encodes.npz")

def SCREENSHOT_DIR(memory_object):
    #opj(MEMORY_ROOT, self.EXPERIENCE.name, self.METHOD.name, f"ScreenShots", f"{self.EXPERIMENT.name}")
    return opj(MEMORY_DIR(memory_object.EXPERIENCE, memory_object.METHOD), f"ScreenShots", f"{memory_object.EXPERIMENT.name}")

def RESULTS_FILE(question_object):
    #opj(MEMORY_DIR(self.EXPERIENCE, self.METHOD), "%06d" % int(self.METHOD.TIME.seconds_experience), f"{self.EXPERIMENT.name}_{self.QID}_result.json")
    return opj(MEMORY_DIR(question_object.EXPERIENCE, question_object.METHOD), "%06d" % int(question_object.METHOD.TIME.seconds_experience), f"{question_object.EXPERIMENT.name}_{question_object.QID}_result.json")

def REFVIDEO_FILE(question_object, start_s, end_s):
    #opj(MEMORY_DIR(self.EXPERIENCE, self.METHOD), "%06d" % int(self.METHOD.TIME.seconds_experience), f"{self.EXPERIMENT.name}_{self.QID}_result.json")
    return opj(MEMORY_DIR(question_object.EXPERIENCE, question_object.METHOD), "%06d" % int(question_object.METHOD.TIME.seconds_experience), f"{question_object.EXPERIENCE.name}_{question_object.QID}_{int(start_s)}_{int(end_s)}.mp4")

