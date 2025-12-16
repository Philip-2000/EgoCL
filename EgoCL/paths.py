
#Data:

from os.path import join as opj

RAW_ROOT = opj("/mnt", "data", "raw_data")
RAW_PATHS_GLOBAL = { #key name are all lowercase
    "epic": opj("/home", "yl", "EPIC-KITCHENS"), #temporarily only support for yl on -p 1022
    "ego4d": opj("/mnt", "data", "yl", "D", "Ego4D", "v2"),
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


CACHE_DIR = opj("/root", ".cache", "EgoCL")  # The cache directory for EgoCL

MEMORY_ROOT = opj(EgoCL_ROOT, "Memory")
MEMORY_PATHS_GLOBAL = { #key name are all lowercase
    
}

def MEMORY_DIR(E, M): # the final memory path is set as: MEMORY_ROOT / experience_id / method_name / memory_files
    return opj(MEMORY_ROOT, E if isinstance(E, str) else E.name, M if isinstance(M, str) else M.__class__.__name__)

#Experiment:
EXPERIMENT_ROOT = opj(EgoCL_ROOT, "Experiment")

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