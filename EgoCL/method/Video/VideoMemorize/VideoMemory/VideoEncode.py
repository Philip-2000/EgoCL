import os, json, numpy as np


def _alias_numpy_core():
    return
    import sys
    import numpy.core
    if "numpy._core" not in sys.modules:
        sys.modules["numpy._core"] = numpy.core

class StringEncoding:
    def __init__(self, ENCODINGS, index, part=(0,0), force_encoding=False, screenshot_id=-1, screenshot_content="path"):
        self.ENCODINGS = ENCODINGS
        self.index = index
        self.part = part
        self._encode = None
        self.screenshot = {"id": screenshot_id, "valid": screenshot_id >= 0, "content": screenshot_content}
        if force_encoding: _ = self.encode #force encoding at initialization
        
    @property
    def field(self):
        return self.content.split("_")[0]
        
    @property
    def content(self):
        if self.screenshot["valid"]:
            return f"screenshot_{self.screenshot['id']}_path" if self.screenshot["content"] == "path" else f"screenshot_{self.screenshot['id']}_description"
        elif self.entire:
            return "entire"
        elif self.part == (-1, -1):
            return "summary"
        else:
            return f"transcript_{self.part[0]}_{self.part[1]}"

    @property
    def entire(self):
        return self.ENCODINGS.entire

    @property
    def encode(self):
        if self._encode is None: self._encode = self.ENCODINGS.encode([self.string])[0]
        return self._encode

    @property
    def MEMORY(self):
        return self.ENCODINGS.MEMORY

    @property
    def string(self):
        if self.screenshot["id"] == -1:
            atom = self.MEMORY.get(self.index)
            if self.entire:
                return json.dumps({"data": atom.data, "meta": {"start_natural": atom.meta["start_natural"], "transcripts":atom.meta["transcripts"]} if "transcripts" in atom.meta else {"start_natural": atom.meta["start_natural"]} })
            else:
                lst = [atom.data] + atom.meta.get("transcripts", [])
                return "\n".join(lst[self.part[0]+1:self.part[1]+2])
        else:
            atom = self.MEMORY.get(self.index)
            if "screenshots" in atom.meta and self.screenshot["id"] < len(atom.meta["screenshots"]):
                if self.screenshot["content"] == "path":
                    return atom.meta["screenshots"][self.screenshot["id"]]["path"]
                else:
                    return atom.meta["screenshots"][self.screenshot["id"]]["description"]
            else:
                raise ValueError(f"Invalid screenshot_id {self.screenshot['id']} for atom index {self.index}.")

    @property
    def present(self):
        atom = self.MEMORY.get(self.index)
        return json.dumps({"data": atom.data, "meta": atom.meta})

    @property
    def ENCODER(self):
        return self.ENCODINGS.ENCODER

    def to_dict(self):
        return {
            "index": self.index, "part": self.part,
            "encode": self._encode.tolist() if self._encode is not None else None,
        }
    
    def from_dict(self, data: dict):
        self.index = data.get("index", 0)
        self.part = data.get("part", (0,0))
        self._encode = np.array(data["encode"]) if data.get("encode", None) is not None else None

class StringEncodings:
    def __init__(self, MEMORY, **kwargs):
        self.MEMORY = MEMORY
        self.entire = kwargs.get("entire", True)
        self.length = kwargs.get("length", 5)
        self.cover = kwargs.get("cover", False)

        self.encodes_config = kwargs.get("encodes", {"pre":False, "save":True, "load_force":False, "load_not":False})

        # self.load_encodes = kwargs.get("load_encodes", True)
        self.ENCODINGS=[]

        #下一步需要考虑的问题就是，将顶层YAML文件中的配置，和这个类的配置进行连接，
        #然后还有就是看视频的过程中，同时并行的编码的过程，
        #还有存储的过程，存储格式的问题，他是跟着load过程出来的吗？

        #哦对还有文件系统，文件命名等问题，
    def encode_all(self):
        from tqdm import tqdm
        batch_size = 32
        for i in tqdm(range(0, len(self.ENCODINGS), batch_size), desc="Encoding StringEncodings"):
            batch = self.ENCODINGS[i:i+batch_size]
            strings = [e.string for e in batch]
            encodes = self.ENCODER(strings)
            for j,e in enumerate(batch):
                e._encode = encodes[j]

    
    def to_npz(self):
        # ENCODINGS = [e.to_dict() for e in self.ENCODINGS]
        dict_data = {
            "ENCODER_PATH": self.METHOD.ENCODER_PATH,
            "entire": self.entire,
            "length": self.length,
            "cover": self.cover,
            "indexs": [e.index for e in self.ENCODINGS],
            "parts": [e.part for e in self.ENCODINGS],
            "encodes": [e._encode.tolist() if e._encode is not None else None for e in self.ENCODINGS], #for deeper storage efficiency, we can store encodes as a 2D numpy array
        }

        len_e=-1
        for e in [_ for _ in dict_data["encodes"] if _ is not None]:
            if len_e == -1: len_e = len(e)
            else: assert len_e == len(e), f"Encode length mismatch in StringEncodings. Expected {len_e}, got {len(e)}."
        len_e = max(len_e, 0)
        for i,e in enumerate(dict_data["encodes"]): dict_data["encodes"][i] = [0.0] * len_e if e is None else e
        
        # print(f"StringEncodings to_npz data size: indexs {len(dict_data['indexs'])}, parts {len(dict_data['parts'])}, encodes {len(dict_data['encodes'])}")
        return dict_data

    def from_npz(self, data):
        if "arr_0" in data: data = data["arr_0"].item()
        assert str(self.METHOD.ENCODER_PATH).split(":")[0] == str(data["ENCODER_PATH"]).split(":")[0], f"ENCODER_PATH mismatch when loading StringEncodings. self.METHOD.ENCODER_PATH: {self.METHOD.ENCODER_PATH}, data['ENCODER_PATH']: {data['ENCODER_PATH']}."
        #ignore the part after ":" which is only a version for GPU id
        self.entire = data["entire"]
        self.length = data["length"]
        self.cover = data["cover"]
        indexs = data["indexs"]
        parts = data["parts"]
        encodes = data["encodes"]
        assert len(indexs) == len(parts) == len(encodes) == len(self), f"Length mismatch when loading StringEncodings. Expected {len(self)}, got {len(indexs)}, {len(parts)}, {len(encodes)}."
        for i in range(len(self)):
            e = self.ENCODINGS[i]
            assert e.index == indexs[i] and e.part[0] == parts[i][0] and e.part[1] == parts[i][1], f"Index or part mismatch when loading StringEncodings. Expected index {e.index} and part {e.part}, got index {indexs[i]} and part {parts[i]}."
            e._encode = np.array(encodes[i], dtype=np.float32) if encodes[i] is not None else None
    
    @property
    def file_name(self):
        from EgoCL.paths import ENCODINGS_FILE
        return ENCODINGS_FILE(self)

    @property
    def fsize_bytes(self):
        import os
        return os.path.getsize(self.file_name) if os.path.exists(self.file_name) else 0

    def save(self):
        # from .... import MEMORY_ROOT
        # from os.path import join as opj
        # file_path = opj(MEMORY_ROOT, self.EXPERIENCE.name, self.METHOD.name, f"{int(self.TIME.seconds_experience):06d}", f"{self.EXPERIMENT.name}_encodes.npz")
        np.savez_compressed(self.file_name, **(self.to_npz()))
    
    def load(self, ts6d):
        if self.encodes_config['load_not']: return
        if self.encodes_config['load_force']:
            # print(self.encodes_config['load_force'], self.file_name, os.path.exists(self.file_name))
            self_name = self.EXPERIMENT.output_name if hasattr(self.EXPERIMENT, 'output_name') else self.METHOD.EXPERIMENT.name
            load_name = self.encodes_config['load_ver'] if 'load_ver' in self.encodes_config and isinstance(self.encodes_config['load_ver'], str) else self_name
            file_name = self.file_name.replace(self_name, load_name)
            assert os.path.exists(file_name), f"StringEncodings file not found: {file_name} while load_force is set."
            print(f"Loading StringEncodings from file: {file_name}")
            _alias_numpy_core()  # align pickle module path for older numpy saves
            self.from_npz(np.load(file_name, allow_pickle=True))
            return
        if os.path.exists(self.file_name):
            _alias_numpy_core()  # align pickle module path for older numpy saves
            self.from_npz(np.load(self.file_name, allow_pickle=True))

    def present(self, i):
        atom = self.MEMORY.get(i)
        return json.dumps({"data": atom.data, "meta": atom.meta})

    def build(self):
        self.ENCODINGS = []
        for i, atom in enumerate(self.MEMORY.iterate_atoms()):
            if self.entire:
                self.ENCODINGS.append(StringEncoding(self, i))
            else:
                # print(f"Building StringEncodings for atom {i} with {len(atom.meta.get('transcripts', []))} transcripts.")
                self.ENCODINGS.append(StringEncoding(self, i, part=(-1, -1)))
                L,start = len(atom.meta.get("transcripts", [])),0
                while start < L:
                    self.ENCODINGS.append(StringEncoding(self, i, part=(start, min(start + self.length - 1, L - 1))))
                    start += 1 if self.cover else self.length
                    # print(len(self.ENCODINGS))
        # print(f"Built {len(self.ENCODINGS)} StringEncodings for VideoMemory at time {self.TIME.seconds_experience} seconds.")
    
    def append_atom(self, atom, atom_id, force_encoding=False):
        if self.entire:
            self.ENCODINGS.append(StringEncoding(self, atom_id, force_encoding=force_encoding))
            # _ = self.ENCODINGS[-1].encode
        else:
            self.ENCODINGS.append(StringEncoding(self, atom_id, part=(-1, -1), force_encoding=force_encoding))
            # _ = self.ENCODINGS[-1].encode
            L,start = len(atom.meta.get("transcripts", [])),0
            while start < L:
                self.ENCODINGS.append(StringEncoding(self, atom_id, part=(start, min(start + self.length - 1, L - 1)), force_encoding=force_encoding))
                # _ = self.ENCODINGS[-1].encode
                start += 1 if self.cover else self.length
        for i,ss in enumerate(atom.meta.get("screenshots", [])):
            self.ENCODINGS.append(StringEncoding(self, atom_id, part=(-1, -1), screenshot_id=i, force_encoding=force_encoding, screenshot_content="path"))
            # _ = self.ENCODINGS[-1].encode
            self.ENCODINGS.append(StringEncoding(self, atom_id, part=(-1, -1), screenshot_id=i, force_encoding=force_encoding, screenshot_content="description"))
            # _ = self.ENCODINGS[-1].encode
        
    @property
    def METHOD(self):
        return self.MEMORY.METHOD

    @property
    def EXPERIENCE(self):
        return self.METHOD.EXPERIENCE
    
    @property
    def TIME(self):
        return self.MEMORY.TIME

    @property
    def EXPERIMENT(self):
        return self.MEMORY.EXPERIMENT

    @property
    def ENCODER(self):
        return self.MEMORY.ENCODER
    
    def encode(self, s):
        return self.ENCODER(s)

    def __getitem__(self, t):
        return self.ENCODINGS[t]
    
    def __len__(self):
        return len(self.ENCODINGS)
    
    def results(self, sims, top_k):
        ts = np.argsort(-sims)
        indexs = []
        while len(indexs) < top_k and len(ts) > 0:
            t,ts = ts[0], ts[1:]
            if self.ENCODINGS[t].index not in indexs: indexs.append(self.ENCODINGS[t].index)
        return [self.present(i) for i in indexs], indexs
    
    @property
    def matrix(self):
        import numpy as np
        return np.vstack([e.encode for e in self.ENCODINGS])

    def submatrix(self, search_field):
        import numpy as np
        indices = [i for i,e in enumerate(self.ENCODINGS) if search_field[e.field]]
        return np.vstack([self.ENCODINGS[i].encode for i in indices]), indices