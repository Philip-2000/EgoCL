
from .Source import Sources
def SourceFactory(name, *args, **kwargs):
    OpenSourceNames=["EgoR1", "EgoRAG", "M3Agent", "HippoMM", "MemVerse"]
    if name in OpenSourceNames:
        from .OpenSource import OpenSource
        return OpenSource(name, *args, **kwargs)
    elif name.startswith("MINE_"):
        from .Mine import Mine
        return Mine(name.replace("MINE_",""), *args, **kwargs)
    else:
        from .Statics import Statics
        return Statics(name, *args, **kwargs)

"""
/mnt/data/yl/C/MyLm/MyLm/LmEvaluate/res/

paths = [
        "/mnt/data/yl/W/EgoCL/Memory/EgoLifeQA_A1_JAKE_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A1_JAKE_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A2_ALICE_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A3_TASHA_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A4_LUCIA_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A5_KATRINA_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A6_SHURE_D1/VideoMethod",
    ]


"""
import os, json
from os.path import join as opj
MineBase=opj("/mnt","data","yl","W","EgoCL","Memory")
EgoR1Persons=["A1_JAKE","A2_ALICE","A3_TASHA","A4_LUCIA","A5_KATRINA","A6_SHURE"]
StaticsBase=opj("/mnt","data","yl","C","MyLm","MyLm","LmEvaluate","res")
# StaticsFiles=[


#     "20260131_175914.json",
#     "20260131_180136.json",
#     "20260131_182944.json",
#     "20260131_183044.json",
#     "20260131_195151.json",
#     "20260131_195256.json",

#     "20260201_060652.json",
#     "20260201_073840.json",
#     "20260201_090135.json",
#     "20260201_133951.json",
#     "20260201_140157.json",
#     "20260201_143043.json",
#     "20260201_152011.json",
#     "20260201_171711.json",
#     "20260201_211754.json",
#     "20260202_024511.json"
# ]

StaticsFiles=[
    #EgoSchema
    #Qwen3
    "20260214_122625_fix.json", #Qwen3 EgoSchema
    #Qwen2.5
    "20260214_141823_scored_fix.json", #Qwen2.5 EgoSchema
    #InternVL3.5
    # "20260214_130303_fix.json", #InternVL3.5 EgoSchema 8B???????????????????????????????????????
    "20260217_110547.json", #InternVL3.5 EgoSchema 38B
    #InternVideo2.5
    "20260214_181514_fix.json", #InternVideo2.5 EgoSchema
    #EgoGPT
    "20260214_165636_fix.json", #EgoGPT EgoSchema
    #LongVA
    "20260214_170259_fix.json", #LongVA EgoSchema
    #LLaVA_Video
    "20260215_003854_fix.json", #LLaVA_Video EgoSchema
    #llava_ov
    "20260215_071919_fix.json", #llava_ov EgoSchema

    #EgoLifeQA
    #Qwen3
    "20260207_083909_merged_fix.json", #Qwen3 EgoLifeQA
    #Qwen2.5
    "20260207_142148_merged_fix.json", #Qwen2.5 EgoLifeQA
    #InternVL3.5
    "20260217_074933_fix.json", #InternVL3.5 EgoLifeQA 38B
    #"20260207_160128_merged_fix.json", #InternVL3.5 EgoLifeQA 8B???????????????????????????????????????
    #InternVideo2.5
    "20260207_130053_merged_fix.json", #InternVideo2.5 EgoLifeQA
    #EgoGPT
    "20260207_125414_merged_fix.json", #EgoGPT EgoLifeQA
    #LongVA
    "20260207_134011_merged_fix.json", #LongVA EgoLifeQA
    #LLaVA_Video
    "20260208_155749_merged_fix.json", #LLaVA_Video EgoLifeQA
    #llava_ov
    "20260208_121000_merged_fix.json", #llava_ov EgoLifeQA

    #EgoR1Bench
    #Qwen3
    "20260207_060339_merged_fix.json", #Qwen3 EgoR1Bench
    #Qwen2.5
    "20260207_075507_merged_fix.json", #Qwen2.5 EgoR1Bench
    #InternVL3.5
    "20260216_214804_fix.json", #InternVL3.5 EgoR1Bench 38B
    # "20260207_093705_merged_fix.json", #InternVL3.5 EgoR1Bench 8B???????????????????????????????????????
    #InternVideo2.5
    "20260207_122304_merged_fix.json", #InternVideo2.5 EgoR1Bench
    #EgoGPT
    "20260207_123817_merged_fix.json", #EgoGPT EgoR1Bench
    #LongVA
    "20260207_131519_merged_fix.json", #LongVA EgoR1Bench
    #LLaVA_Video
    "20260208_114647_merged_fix.json", #llava_ov EgoR1Bench
    #llava_ov
    "20260208_135726_merged_fix.json", #LLaVA_Video EgoR1Bench
]