import os,json

class Loader:
    def __init__(self, path):
        self.path = path
    
    def load(self):
        pass

class Visualize:
    def __init__(self,config):
        from ...paths import MEMORY_ROOT
        self.path = os.path.join(MEMORY_ROOT, Experience_name, Method)
        self.LOADER = Loader(self.path)
        self.DATAS = self.LOADER.load()
        self.config = {}
    
    def __call__(self):
        return
        j = []
        for t in sorted([t for t in os.listdir(self.path) if str(t).isdigit()], key=lambda x: int(x)):
            filenames = [f for f in os.listdir( os.path.join(self.path, t) ) if f.endswith("result.json") and f.startswith("default")]
            for f in filenames:
                try:
                    data = json.load( open( os.path.join(self.path, t, f), 'r') )
                    # for d in [d for d in data if d['uid'] not in [item['uid'] for item in j]]: j.append(d)
                    if data['uid'] not in [item['uid'] for item in j]: j.append(data)
                except:
                    pass
        
        print(f"Average score: {round(sum([item['score'] for item in j])/len(j),4)}, {sum([item['score'] for item in j])} out of {len(j)} questions answered correctly.")


#啥意思，就是说这边需要
#（1）筹备数据
#   数据有哪些要素：（a）它是哪个方法的，一共A种方法；（b）它是哪条实验的，一共B条实验（c）它是哪个测试指标的，一共C个测试指标
#就这样形成了一个三维的矩阵，数据魔方
#（2）展示数据
#那么如何展示呢？（a）命令行打印的话，就A行，每一行是一个方法，一行中依次是各个实验的结果，每个结果用一个括号中的C个元素的元组表示不同的测试指标
#（b）图表展示的话，就更复杂一些了，可能需要用不同的图表类型来展示不同的维度

#如何展示三维矩阵呢？
#还是需要用C张图，每张图B组的柱状图，每组柱状图A根柱子，

