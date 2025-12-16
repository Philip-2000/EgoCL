from collections import defaultdict

# class timeStamp:
#     def __init__(self, config, s_ANNO=None):
#         self.start_s = config.get("start_s", 0)
#         self.end_s = config.get("end_s", self.start_s)
#         self.start_f = config.get("start_f", 0)
#         self.end_f = config.get("end_f", self.start_f)
#         self.s_ANNO = s_ANNO

#     def __iadd__(self, offset_s: float):
#         self.start_s += offset_s
#         self.end_s += offset_s
#         return self

#     @property
#     def mid_s(self):
#         return (self.start_s + self.end_s) / 2.0

#     @property
#     def duration_s(self):
#         return self.end_s - self.start_s
    
#     @property
#     def duration_f(self):
#         return self.end_f - self.start_f
    
#     @property
#     def time_s(self):
#         return self.start_s

#     @property
#     def frame_f(self):
#         return self.start_f

#     def __repr__(self):
#         #return f'timeStamp(start_s={self.start_s} {"" if self.end_s==self.start_s else "(->"+self.end_s+")"}, start_f={self.start_f}  {"" if self.end_f==self.start_f else "(->"+self.end_f+")"})'
#         return "timeStamp(start_s=%.3f %s, start_f=%d  %s)" % ( self.start_s, "" if self.end_s==self.start_s else "(->%.3f)"%self.end_s, self.start_f, "" if self.end_f==self.start_f else "(->%d)"%self.end_f)
    
#     @property
#     def to_dict(self):
#         return {
#             "start_s": self.start_s,
#             "end_s": self.end_s,
#             "start_f": self.start_f,
#             "end_f": self.end_f
#         }

from .TimeStamp import TimeStamp, TimeSpan
class Anno:
    def __init__(self, config, s_ANNOS=None):
        self.category = config.get("category","None")
        self.TIMESPAN = TimeSpan.from_dict(config.get("TIMESPAN", {}), None, s_ANNOS.s_ACTIVITY if s_ANNOS is not None else None)
        self.information = config.get("information", {})
        self.s_ANNOS = s_ANNOS
    
    def offset_start(self, start_s: float, EXPERIENCE):
        self.TIMESPAN.offset_start(start_s, EXPERIENCE)
        self.s_ANNOS = s_ANNOS

    def __repr__(self):
        return f'Anno({self.category}\t timespan={self.TIMESPAN}, information={self.information})'
    
    def __lt__(self, other): 
        return self.TIMESPAN < other.TIMESPAN
    
    def __gt__(self, other): 
        return self.TIMESPAN > other.TIMESPAN

    @property
    def info(self):
        #the most important information of this annotation / self.information stores everything, but some key information is more important
        if self.category == 'narration':
            return self.information.get('text', '')
        elif self.category == 'summary':
            return self.information.get('text', '')
        elif self.category == 'action':
            return self.information.get('text', '')
        else:
            raise NotImplementedError(f"info property not implemented for category {self.category}, please set its most important information manually.")
    
    @property
    def to_dict(self):
        if not hasattr(self, '_cached_to_dict'):
            self._cached_to_dict = {
                "category": self.category,
                "TIMESPAN": self.TIMESPAN.to_dict,
                "information": self.information
            }
        return self._cached_to_dict

    def from_dict(self, data_dict, s_ANNOS=None):
        self.category = data_dict.get("category")
        self.TIMESPAN = TimeSpan.from_dict(data_dict.get("TIMESPAN", {}), None, s_ANNOS.s_ACTIVITY if s_ANNOS is not None else None)
        self.information = data_dict.get("information", {})
        self.s_ANNOS = s_ANNOS

    # @property
    # def start_s(self):
    #     return self.time.start_s  #FIXME

    # @property
    # def end_s(self):
    #     return self.time.end_s #FIXME
    
    # @property
    # def mid_s(self):
    #     return self.time.mid_s #FIXME

    # @property
    # def start_f(self):
    #     return self.time.start_f #FIXME

    # @property
    # def end_f(self):
    #     return self.time.end_f #FIXME

    # @property
    # def time_s(self):
    #     return self.time.time_s #FIXME

    # @property
    # def frame_f(self):
    #     return self.time.frame_f #FIXME

    # @property
    # def duration_s(self):
    #     return self.time.duration_s #FIXME

    # @property
    # def duration_f(self):
    #     return self.time.duration_f #FIXME



class Annos:
    def __init__(self, annos_config={}, s_ACTIVITY=None):
        self.ANNOS = annos_config
        self.s_ACTIVITY = s_ACTIVITY
        #self.start_s = 0.0 #FIXME

    def offset_start(self, start_s: float, EXPERIENCE):
        for category in self.ANNOS:
            for anno in self.ANNOS[category]:
                anno.TIMESPAN.offset_start(start_s, EXPERIENCE)
                anno.s_ANNOS = self
        
    def __iadd__(self, anno_dict):
        # print("before", len(self.ANNOS.get(anno_dict.get("category"), [])))
        # print(self)
        anno = Anno(anno_dict, self)

        if anno.category not in self.ANNOS:
            self.ANNOS[anno.category] = [anno]
        else:
            self.ANNOS[anno.category].append(anno) #we use insertion sort to keep the list sorted, because the annotations are generally already added in order, so such insertion sort is efficient
            for i in range(len(self.ANNOS[anno.category])-1, 0, -1):
                if self.ANNOS[anno.category][i] < self.ANNOS[anno.category][i-1]: self.ANNOS[anno.category][i], self.ANNOS[anno.category][i-1] = self.ANNOS[anno.category][i-1], self.ANNOS[anno.category][i]
                else: break
                
        # print("after", len(self.ANNOS.get(anno_dict.get("category"), [])))
        # print(self.ANNOS)
        return self

    def __getitem__(self, name):
        if isinstance(name, str):
            return self.ANNOS.get(name, [])
        elif isinstance(name, tuple):
            category, idx = name
            if isinstance(idx, int):
                return self.ANNOS.get(category, [])[idx]
            elif isinstance(idx, slice):
                return self.ANNOS.get(category, [])[idx]
            elif isinstance(idx, float):
                #search by time
                for anno in self.ANNOS.get(category, []):
                    if anno.time.start_s <= idx < anno.time.end_s: #FIXME
                        return anno
            else:
                raise TypeError("Index must be int, slice, or float (for time search).")
        else:
            raise TypeError("Index must be str (category) or tuple (category, index).")
            
    def __repr__(self):
        return f'Annos(num_annotations={len(self.ANNOS)})'
    
    @property
    def to_dict(self):
        if not hasattr(self, '_cached_to_dict'):
            self._cached_to_dict = {}
            for category, anno_list in self.ANNOS.items():
                self._cached_to_dict[category] = [anno.to_dict for anno in anno_list]
        return self._cached_to_dict
    
    @property
    def duration_s(self):
        return max(anno.end_s for category in self.ANNOS for anno in self.ANNOS[category]) if self.ANNOS else 0.0

    def from_dict(self, data_dict):
        self.ANNOS = {}
        for category, anno_list in data_dict.items():
            self.ANNOS[category] = []
            for anno_dict in anno_list:
                anno = Anno(anno_dict, self)
                self.ANNOS[category].append(anno)
        
    def clip(self, start_s: float, end_s: float): #FIXME
        clipped_annos = Annos({}, self.s_ACTIVITY)
        print(f"[Annos.clip] entered: start_s={start_s}, end_s={end_s}, s_ACTIVITY={self.s_ACTIVITY}")
        total_annos = sum(len(v) for v in self.ANNOS.values()) if self.ANNOS else 0
        # print(f"[Annos.clip] original categories={list(self.ANNOS.keys()) if self.ANNOS else []}, total_annotations={total_annos}")
        # for cat, lst in (self.ANNOS.items() if self.ANNOS else []):
            # print(f"[Annos.clip] category='{cat}' count={len(lst)}")
        for category, anno_list in self.ANNOS.items():
            # print("start clipping category:", category, "with", len(anno_list), "annotations")
            for anno in anno_list:
                # print("  checking anno:", anno.category,"start_s:", anno.start_s, "end_s:", anno.end_s)
                if anno.end_s <= start_s:
                    # print("    skipping before start_s", start_s)
                    continue
                if anno.start_s >= end_s:
                    # print("    skipping after end_s", end_s)
                    continue
                #clip the annotation time
                new_start_s = max(anno.start_s, start_s)
                new_end_s = min(anno.end_s, end_s)
                new_start_f = anno.start_f + int((new_start_s - anno.start_s) * 30)  #assuming 30 fps
                new_end_f = anno.start_f + int((new_end_s - anno.start_s) * 30)
                # print("    clipping to new_start_s:", new_start_s, "new_end_s:", new_end_s)
                new_anno_dict = {
                    "category": anno.category,
                    "time": {
                        "start_s": new_start_s,
                        "end_s": new_end_s,
                        "start_f": new_start_f,
                        "end_f": new_end_f
                    },
                    "information": anno.information
                }
                clipped_annos += new_anno_dict
                # print("clipping result:")
                # print(clipped_annos)
        return clipped_annos