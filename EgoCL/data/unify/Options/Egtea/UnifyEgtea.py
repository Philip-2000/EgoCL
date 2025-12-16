from ..UnifyBase import UnifyBase
from ....elements import Activity
from .AnnoEgtea import AnnoEgtea
import os

class UnifyEgtea(UnifyBase):
    def __init__(self, cfg):
        super().__init__(cfg)
        # Initialize Egtea specific processing parameters here
        self.cfg = cfg

        json_base = os.path.join(self.cfg['in_path'])
        self.ANNOEGTEA = AnnoEgtea(json_base=json_base, anno_tags=cfg.get('anno_tags', ['action']))
        self.video_base = os.path.join(self.cfg['in_path'], 'screened_videos')
        

    def annotation(self):
        #现在有个问题就是他妈的egtea的数据集的标注文件格式太太太太复杂了
        #各种各样的标注文件夹和标注文件，都是纵向的，同一个视频的各种不同类型的标注散落在各自类别的标注之中
        #而不是横向的，所有对于该视频的所有标注都在一个文件中
        #想整合总结起来呢也很困难
        #想总结成字典，也会出现很多长度不相同的列表，于是就没法彻底对齐
        #所以非常的复杂，不想弄了
        #咱们必须重新思考这个问题，那就是对于下游任务，咱们到底需要哪个角度的标注，优先处理这个角度的标注文件
        #将他们对齐
        #另外什么呢，另外就是这个数据结构可能只能以JSON的形式保存了，没法设成Parquet了，因为长度不对齐
        
        pass
        #还有一个事情就是在整个过程中，越想这个持续学习的技术路线，越觉得这个技术路线不靠谱
        #毕竟持续学习的技术路线，核心就是在于模型能够不断的吸收新的知识，而不会遗忘旧的知识
        #但是对于“记忆”型的任务，比如说智能眼镜助手，持续学习的技术路线就显得不太合适
        #因为智能眼镜助手，更多的是需要对用户的长期习惯和偏好进行记忆和适应，而不是不断地学习新的知识
        #所以说，在这个过程中，咱们可能需要重新评估一下持续学习的技术路线是否适合于智能眼镜助手这个应用场景
        #也许咱们需要考虑其他的技术路线，比如说强化学习，或者说基于规则的系统
        #总之，咱们需要深入思考一下这个问题，找到最适合智能眼镜助手的技术路线

        #但是在此之前，至少写代码的时候，可以暂时先放下这些思考，专注于代码的实现
        #就记一下每一个视频各个段落分别发生了什么，然后就是，每一个都是，我觉得关键还是一些容易忘记可能需要记下来的“细节信息”吧，
        
        #还有一个很有意思的值得一做的点就是，关键问题的采样提取，关键问题提取，
        #这种提取的自动的、透明的，非交互式触发的，所以需要一个自动化的关键问题触发模块？
        #一边经历、一边判断当前的经历是否比较关键，然后来决定是否存储（或按照原来的想法，是否交付微调训练）

        #挺有意思的，包括用户在用这些记忆的时候，是会怎么用的呢？应该也不是很直截了当地问当时发生了什么吧，
        #而是会有一些模糊的、间接的、关联性的提问，
        #这种模糊到清晰的过程，肯定还是调用语言模型来帮忙理解处理，
        #

        #看这个文献说是什么，记忆化系统已经有了，甚至有开源平台了；啥业务逻辑？
        #好像是自动从过往对话中提取信息构成知识库，


        #做什么呢，论文现在读了一半了，还读还总结吗？
        #我觉得现在的核心矛盾在于，应该是要做RAG了，但是RAG来RAG去的，那些方法之间真的有什么区别吗？
        #如果没有区别的话，那就没必要搞那么多不同的方法了，直接选一个简单好用的就行了

        #当然，在RAG的同时，CL不能彻底放弃，因为这是导师点名要做的东西
        #我只是说想向他证明CL这条路走不通
        #但是即使是做CL，我也有点不知道CL该怎么做了，
        #因为一个核心矛盾，那就是他的原始数据内容是“记忆”，交付训练的内容可能是“未来对记忆的提问”或者“未来可能的对这个记忆的提问”，这种提问很多很多，随时可能提问，所以感觉就是很难预知训练数据长什么样子的
        #那怎么说嘛

        #那我有两个想法（1）上那些parametric long-term memory的工作中去看一看，看看他们怎么训的，训得数据是怎样的
        #            看完了，结论是他们巨傻逼！或者说首先北大那个不是我们要找的；然后AI原生那个还挺有意思的，感觉总的来说是我们想的那个意思，但是论文写的太冲了，然后实验可能不成熟；，Echo那个也挺有意思，是我们想象的意思，但是实验太简陋了；
        #（2）还有一个注意事项吧，算不上是想法，那就是需要到之前的那些memory工作中看一看他是采的哪些信息，它有没有“挑选信息”来处理；如果没有的话，那就说明可能文本式记忆工作中，信息挑选并不是必要的
        #但是其实眼镜助手的记忆和文本式记忆还是不太一样的，眼镜助手的记忆更多的是多模态的，视频、音频、传感器数据都有
        #它如果不挑选信息的话，那就说明可能需要把所有的信息都存下来，非常庞大
        #那这种挑选其实可以作为一种贡献点写进论文里（即使他们有，那也要根据眼镜的情景进行改进，然后写进论文里）

        #那现在就干三件事？一个是（1），二个是（2）这个也太多了咋看呀，三个是继续写代码实现；


    #还有一个问题就是说，那个Egtea的视频长度太长了，到时候做实验或者做训练的时候真的不一定全都交付进去，
    #我觉得肯定还是有必要引入这个“片段”这个处理的，或者在后期处理的时候，再认为各个片段是独立的视频
    #但是问题在于，“片段”是Egtea数据中的一种抽象，不是一种真实存在的python对象，在对象层面，是不存在这种“片段”对象的，顶多就是在“视频”或者“活动”中设置少量的标记声明它是一个“片段”

    def __repr__(self):
        return f'{self.__class__}(cfg={self.cfg})'
    
    def __length(self, path):
        import subprocess
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ]
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
            return float(out)
        except Exception:
            return None

    def __call__(self, item, **kwargs):
        #print(item)
        #这里肯定是需要扩展的，看看咋扩展吧，就是到时候只搞一些片段这个样子
        activity_config = {
            'name': item,
            'source': 'Egtea',
            'ANNOS': {},
            'VIDEO': {
                'video_path': f"{self.video_base}/{item}.mp4",
                'start_s': 0 if "start_s" not in kwargs else kwargs['start_s'],
                'end_s': self.__length(f"{self.video_base}/{item}.mp4") if "end_s" not in kwargs else kwargs['end_s']
            }
        }
        a = Activity(activity_config)
        self.ANNOEGTEA(a)
        return a


class UnifyEgtea_S:
    def __init__(self, datset_cfg):
        self.list = []
        #self.kwargs = dict(kwargs).copy()
        kwargs = datset_cfg
        
        import os
        if 'items' in kwargs and len(kwargs['items']) > 0:
            self.list = kwargs['items'].copy()
        elif 'item_file' in kwargs and len(kwargs['item_file']) > 0  and os.path.exists(kwargs['item_file']):
            self.list = open(kwargs['item_file'], 'r').read().splitlines()
        else:
            self.list = os.listdir(kwargs['in_path'])


        if 'num' in kwargs and kwargs['num'] > 0:
            self.list = self.list[:kwargs['num']]

        # for dataset_name, dataset_config in self.config_data["datasets"].items():
        #     dataset_config['ITEMS'] = [] #final version of ITEMS list
        #     if 'items' in dataset_config and len(dataset_config['items']) > 0:
        #         self.config_data["datasets"][dataset_name]['ITEMS'] = dataset_config['items'].copy() #highest priority, directly set ITEMS
        #     elif 'item_file' in dataset_config and len(dataset_config['item_file']) > 0 and os.path.exists(dataset_config['item_file']):
        #         self.config_data["datasets"][dataset_name]['ITEMS'] = open(dataset_config['item_file'], 'r').read().splitlines()
        #     elif 'num' in dataset_config and dataset_config['num'] > 0:
        #         self.config_data["datasets"][dataset_name]['ITEMS'] = os.listdir(dataset_config['in_path'])[:dataset_config['num']]
        #     else:
        #         self.config_data["datasets"][dataset_name]['ITEMS'] = os.listdir(dataset_config['in_path'])
        self.UNIFIER = UnifyEgtea(kwargs)
        self.ACTIVITIES = []

    def __call__(self, out_dir=None):
        from tqdm import tqdm

        for item in tqdm(self.list):
            act = self.UNIFIER(item)
            act.save(self.UNIFIER.cfg['out_path'] if out_dir is None else out_dir)
            self.ACTIVITIES.append(act)
        return self.ACTIVITIES


            