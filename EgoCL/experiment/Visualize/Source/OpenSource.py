from .Source import Source
class OpenSource(Source):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #For HRW, please refer to other files besides this OpenSource.py
        #to connect the experimental results with the Visualizer framework
        
        #you are supposed to connect the experimental results of EgoR1, EgoRAG, M3Agent, HippoMM and MemVerse
        #it's strongly recommended to formulate their results in a unified format,
        #so you only need to write code once, in class OpenSource,
        #rather than writing code for each of these five experiments separately with the following subclasses.
        
        #however, please design such formats carefully, because once you design a format,
        #all these five experiments need to follow this format strictly.
        #So such format should be general enough to cover all these five experiments,
        #and should be specific enough to avoid ambiguity.

        #Good luck and have fun!

        #Don't forget to store the paths in __init__.py, and load from there.

# class EgoR1(OpenSource):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         #doing nothing, just for structure completeness
#         #in case of future extensions

# class EgoRAG(OpenSource):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         #doing nothing, just for structure completeness
#         #in case of future extensions

# class M3Agent(OpenSource):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         #doing nothing, just for structure completeness
#         #in case of future extensions

# class HippoMM(OpenSource):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         #doing nothing, just for structure completeness
#         #in case of future extensions
    
# class MemVerse(OpenSource):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         #doing nothing, just for structure completeness
#         #in case of future extensions