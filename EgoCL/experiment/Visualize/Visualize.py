import os,json,yaml
from os.path import dirname as opd, abspath as opa, join as opj


class Visualizer:
    def __init__(self, config_path):
        if not config_path.endswith('.yaml'):
            config_path = opj(opd(opa(__file__)), 'configs', f'{config_path}.yaml')
            assert os.path.exists(config_path), f"Config file {config_path} does not exist."
        config = yaml.load( open(config_path, 'r'), Loader=yaml.FullLoader )

        from ...paths import MEMORY_ROOT
        from .Data import Loader
        self.LOADER = Loader(config)
        self.config = config['Visualizer']
        self.LOADER()
    
    @property
    def name(self):
        return self.DATAS.name
    
    @property
    def DATAS(self):
        return self.LOADER.DATAS
    
    def __call__(self):
        if self.config['Print']:
            # for TRAIL in self.DATAS.TRAILS:
            #     print(f"  Trail: {TRAIL.name}")
            #     # Print header
            #     header = ["Source/Trail"] + [f"{metric.name:<10}" for metric in self.DATAS.METRICS]
            #     print('\t'.join(header))
            #     for SOURCE in self.DATAS.SOURCES:
            #         row = [f"{SOURCE.name[:15]}"]
            #         for METRIC in self.DATAS.METRICS:
            #             data = self.DATAS[(SOURCE.name, TRAIL.name, METRIC.name)].v
            #             assert data is not None, f"Data for Source: {SOURCE.name}, Trail: {TRAIL.name}, Metric: {METRIC.name} is None."
            #             row.append(f"{data:.3g}" if not (METRIC.name.endswith("Delay_Rate")) else f"{data:.3e}" )
            #         print('\t'.join(row))
            
            header = ["Source/Trail"] + [f"{metric.name:<10}" for TRAIL in self.DATAS.TRAILS for metric in self.DATAS.METRICS]
            print('\n', '\t& '.join(header))
            for SOURCE in self.DATAS.SOURCES:
                row = [f"{SOURCE.name[:15]}"]
                for TRAIL in self.DATAS.TRAILS:
                    for METRIC in self.DATAS.METRICS:
                        data = self.DATAS[(SOURCE.name, TRAIL.name, METRIC.name)].v
                        # assert data is not None, f"Data for Source: {SOURCE.name}, Trail: {TRAIL.name}, Metric: {METRIC.name} is None."
                        if METRIC.name == "Similarity":
                            data_str = (f"{data:.3g}")[1:] if data is not None else "--"
                        elif METRIC.name.endswith("Delay_Rate"):
                            shift = 10.0 if TRAIL.name == "EgoSchema" else (10000.0)
                            data_str = f"{data*shift:.3g}" if data is not None else "--"
                            data_str = data_str[1:] if data_str.startswith("0") else data_str
                        elif METRIC.name.endswith("Delay"):
                            data_str = f"{data:.3g}" if data is not None else "--"
                        else:
                            data_str = f"{data*100:.3g}\%" if data is not None else "--"
                        row.append(data_str)
                print('\t& '.join(row), "\\\\")

        if self.config['Plot']:
            import matplotlib.pyplot as plt
            colors = ['b', '#4B8BBE', '#306998', '#6A5ACD', '#483D8B', '#8A2BE2', '#7B68EE', '#5F9EA0', '#20B2AA']
            for metric in self.DATAS.METRICS:
                plt.figure(figsize=(10,6))
                plt.title(f'Metric: {metric.name}')
                
                W = 1.0 / (len(self.DATAS.SOURCES) + 1)
                for i, SOURCE in enumerate(self.DATAS.SOURCES):
                    values = []
                    labels = []
                    for TRIAL in self.DATAS.TRAILS:
                        data = self.DATAS[(SOURCE.name, TRIAL.name, metric.name)].v
                        assert data is not None, f"Data for Source: {SOURCE.name}, Trail: {TRIAL.name}, Metric: {metric.name} is None."
                        values.append( data )
                        labels.append( TRIAL.name )
                    x = [j + i*W for j in range(len(values))]
                    plt.bar(x, values, width=W, label=SOURCE.name, color=colors[i % len(colors)])
                
                plt.xticks( [j + W*(len(self.DATAS.SOURCES)-1)/2 for j in range(len(self.DATAS.TRAILS))], labels)
                plt.ylabel(metric.name)
                plt.legend(loc='upper left')
                plt.grid(axis='y')
                plt.tight_layout()
                plt.savefig( f'{metric.name}.png' )
                plt.close()
        
        if self.config['Latex']:
            from pylatex import Document, Tabular, NoEscape

            doc = Document()
            num_cols = len(self.DATAS.TRAILS) + 1
            table = Tabular('l' + 'c' * (num_cols - 1))
            header = ['Method \\ Benchmark'] + [trail.name for trail in self.DATAS.TRAILS]
            table.add_row(header)
            table.add_hline()
            for SOURCE in self.DATAS.SOURCES:
                row = [SOURCE.name]
                for TRAIL in self.DATAS.TRAILS:
                    data = self.DATAS[(SOURCE.name, TRAIL.name, self.DATAS.METRICS[0].name)].v
                    assert data is not None, f"Data for Source: {SOURCE.name}, Trail: {TRAIL.name}, Metric: {self.DATAS.METRICS[0].name} is None."
                    row.append(f'{data*100:.2f}\\%')
                table.add_row(row)
            doc.append(table)
            with open('results_table.tex', 'w') as f:
                f.write(doc.dumps())

        
#啥意思，就是说这边需要
#（1）筹备数据
#   数据有哪些要素：（a）它是哪个方法的，一共A种方法；（b）它是哪条实验的，一共B条实验（c）它是哪个测试指标的，一共C个测试指标
#就这样形成了一个三维的矩阵，数据魔方
#（2）展示数据
#那么如何展示呢？（a）命令行打印的话，就A行，每一行是一个方法，一行中依次是各个实验的结果，每个结果用一个括号中的C个元素的元组表示不同的测试指标
#（b）图表展示的话，就更复杂一些了，可能需要用不同的图表类型来展示不同的维度

#如何展示三维矩阵呢？
#还是需要用C张图，每张图B组的柱状图，每组柱状图A根柱子，

