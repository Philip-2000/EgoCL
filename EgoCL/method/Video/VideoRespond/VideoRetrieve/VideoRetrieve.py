import re, json
from os.path import join as opj
from .....paths import MEMORY_DIR
from ....Base import Retrieve

class VideoRetrieve(Retrieve):
    def __init__(self, RESPOND, top_k=3, **kwargs):
        super().__init__()
        self.name = "VideoRetrieve"
        self.RESPOND = RESPOND

        from ... import VideoMemory
        self.MEMOR = VideoMemory(self.RESPOND.METHOD.MEMORIZER, **kwargs)
        self.top_k = top_k

        self.search_field={"transcript":kwargs.get("search_field", {}).get("transcript", True), "screenshot":kwargs.get("search_field", {}).get("screenshot", True), "summary":kwargs.get("search_field", {}).get("summary", True)} 

    @property
    def fsize_kB(self):
        return self.MEMORY.fsize_kB

    @property
    def EXPERIENCE(self):
        return self.RESPOND.EXPERIENCE

    @property
    def EXPERIMENT(self):
        return self.METHOD.EXPERIMENT
    
    @property
    def ENCODER(self):
        return self.METHOD.ENCODER

    def encode(self, s):
        return self.METHOD.encode(s)

    @property
    def METHOD(self):
        return self.RESPOND.METHOD

    @property
    def TIME(self):
        return self.MEMORY.TIME

    @property
    def ENCODINGS(self):
        return self.MEMORY.ENCODINGS

    # @property
    # def matrix(self):
    #     return self.MEMORY.matrix

    @property
    def MEMORY(self):
        return self.MEMOR

    def load(self, seconds_experience):
        self.MEMOR.load(seconds_experience)
        
        #self._texts = [atom.data for atom in self.MEMORY.iterate_everything()]
        # self._texts = [json.dumps({"meta":atom.meta, "summary":atom.data}, ensure_ascii=False) for atom in self.MEMORY.iterate_atoms()]
        # self.ENCODINGS.dump(len([_ for _ in self.MEMORY.iterate_atoms()]))
        #配置这一波的目的就是为了管理这个“待编码内容”、“显示内容”等等。
        #我觉得还是把它作为这个VideoMemory的原生属性来管理的话会比较正确一些；不然的话就很不对了。
        #那么这里需要管理数据结构的什么呢，需要管理（1）待编码内容，（2）显示内容
        
        #然后编码内容组织方式又是在哪里管理的呢？
        #是不是也是VideoMemory的属性？
        #还有一些就是编码结果？码值？存储了读取，还是重新编码？
        #这些都是VideoMemory类中管理的，

        #而这里VideoRetrieve的话，是不是直接从VideoMemory中读取待编码内容就可以了？
        #那编码过程其实也是在VideoMemory中进行的？它是读取还是重新编码，随它的，我这边VideoRetrieve只负责读取编码编好了东西就行了，在我这边都编码完成了，
        #甚至我觉得可以在那边设置成懒惰加载的方式，只有在需要编码的时候，如果发现没有，才进行编码，

        
        #对，即使是说上面这一部分，那也是通过顶层的配置文件，来调整VideoMemory中的StringEncodings的结构的，
        #相关的逻辑不体现在这里VideoRetrieve中，那我这边就是只调用它的（1）全部待检索内容的列表？idx怎么说？
        #因为它直接出的时候出的是一个idx，就是np.argsort出来的是整数，这个整数是下表，并不是一个可以被StringEncoding对象识别的index，也不是一个可以被它定义过的一个个性化的索引
        #所以是不是就需要StringEncodings对象来为这个索引建立一个反向映射关系？
        #不是反向映射，是正向映射，
        #

        #之后还有一些事情，比如说，这个编码如果存储的事情。存储的格式和我的要求不一致的时候，怎么处理的问题，
        #是不是说，需要去assert一下，读取的时候，读取到的编码格式和我当前的编码格式不一致的时候，报错？
        #但是不管怎么说，这一部分是靠后做的了，现在先做上面这部分的事情，就是每次都重新编码这个，
        
        # self.matrix = self.encode(self._texts) #self.model.encode(self._texts)

    @property
    def ENCODER(self):
        return self.METHOD.ENCODER

    @property
    def matrix(self):
        m, i = self.ENCODINGS.submatrix(self.search_field)
        return m

    def __call__(self, query: str, image=None):
        from . import YOG
        import numpy as np
        YOG.info(("Querying VectorRetrieve with query:", query))
        sims = self.ENCODER.sim(query, self.matrix)[0]
        
        r,i = self.ENCODINGS.results(sims, self.top_k) # [ self._texts[int(idx)] for idx in idxs]

        if image is not None:
            sims = self.ENCODER.sim(image, self.matrix)[0]
            r_image, i_image = self.ENCODINGS.results(sims, self.top_k)
            i = list(set(i) | set(i_image))
            r = [self.ENCODINGS.present(idx) for idx in i]
        
        return r