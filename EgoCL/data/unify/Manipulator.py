
class ManipulatorArgs:
    def __init__(self, **kwargs):
        #An intelligent argument parser for Manipulator class
        #Its highest priority use the kwargs information
        #then use the ConfigExample.yaml file to fill in missing arguments
        #then use the RAW_PATHS_GLOBAL and UNI_PATHS_GLOBAL to fill in missing paths

        #Finally, it will provide a complete set of arguments for Manipulator class to use

        #(1) so firstly, it should load the ConfigExample.yaml file
        # import yaml, os
        # f = open(kwargs["item_config"])#os.path.join(os.path.dirname(os.path.abspath(__file__)),'ConfigExample.yaml'), 'r')
        # config_data = yaml.safe_load(f)
        from .. import itemParse
        config_data = itemParse(kwargs["item_config"])
        #(1.1) however, in config_data, the "base" section has lower priority than the specific dataset sections; but when the specific dataset sections miss some parameters, they should be filled in from the "base" section
        base_config = config_data.get('base', {})
        for dataset_name, dataset_config in config_data["datasets"].items():
            for key, value in base_config.items():
                if  dataset_config and key not in dataset_config:
                    dataset_config[key] = value
        self.config_data = config_data
        #(1.2) so now, each dataset section has all the parameters from base section

        #(2) then, it should merge the GLOBAL paths, however, the in_path and out_path in ConfigExample.yaml has higher priority than GLOBAL paths
        from .. import RAW_PATHS_GLOBAL, UNI_PATHS_GLOBAL
        for dataset_name, dataset_config in self.config_data["datasets"].items():
            if dataset_config is None:
                self.config_data["datasets"][dataset_name] = {}
                dataset_config = {}
            if 'in_path' not in dataset_config or dataset_config['in_path'] is None:
                if dataset_name in RAW_PATHS_GLOBAL:
                    self.config_data["datasets"][dataset_name]['in_path'] = RAW_PATHS_GLOBAL[dataset_name]
            if 'out_path' not in dataset_config or dataset_config['out_path'] is None:
                if dataset_name in UNI_PATHS_GLOBAL:
                    self.config_data["datasets"][dataset_name]['out_path'] = UNI_PATHS_GLOBAL[dataset_name]

        #(3) then, it should merge the kwargs information, however, the kwargs has the highest priority
        # for key, value in kwargs.items():
        #     if isinstance(value, dict):
        #         if key in self.config_data:
        #             self.config_data[key].update(value)
        #     else:
        #         if key in self.config_data:
        #             self.config_data[key] = value
    
    


    def __getitem__(self, key):
        return self.config_data.get(key, None)

class Manipulator:
    def __init__(self, **kwargs):
        #考虑一下这个类的作用是什么
        #他主要负责了数据从原始数据文件夹到统一格式的转化过程，
        #他要负责什么呢，负责参数的整合与解析，
        #他要负责开启数据转换的过程，每一份过程一个对象吗？
        
        #也没必要，一般是用一个统一的对象，然后用他的__call__方法去依次处理各个数据条目
        #关键是不同的数据集或者格式，采用的是不同的派生类对象，虽然都是从处理者基类中继承下来的
        #但是还是会要求他们不是同一个类

        #到时候检测一下吧，检测出类别不一样再重新实例化一个对象，
        #因为这些数据集都是依次处理的，所以连续的数据条目基本上是同一个数据集的
        #这样检测加重置开销也不大，因为基本不会重置、

        pass
        #所以说这个类要做什么呢
        #基本就是两步（1）初始化参数（在__init__中），2）处理数据条目（在__call__中）
        self.UNIFIER_S = None  #具体的统一处理器对象
        self.ARGS = ManipulatorArgs(**kwargs)
        self.ACTIVITES=[]
        #self.sep=True #True for saving each activity individually (easy to check, see and debug), False for saving all activities together ( when large scale processing is needed, and generally, all the bugs are done_

    
    @property
    def DATASETS(self):
        return self.ARGS.config_data.get('datasets', {})

    def __call__(self, out_dir=None):
        
        for k, ds in self.DATASETS.items():
            self.UNIFIER_S = self.__unifier(k, ds)
            ACTIVITIES = self.UNIFIER_S(out_dir)
            self.ACTIVITES.extend(ACTIVITIES)
        
        # if not self.sep: self.save_parquet(out_path)

    def save_parquet(self, fname, data=None):
        import pyarrow
        pyarrow.parquet.write_table(pyarrow.Table.from_pylist([_.dicti for _ in (data if data else self.ACTIVITES)]), fname)

    def __unifier(self, NAME, dataset_cfg):
        import importlib
        if NAME not in self.DATASETS:
            raise ValueError(f'Unknown dataset name: {NAME}')
        name = f'Unify{NAME[:1].upper() + NAME[1:]}_S'
        opts = importlib.import_module('..Options', package=__name__)
        Unifier_s = getattr(opts, name)
        return Unifier_s(dataset_cfg)
        if NAME == 'ego4d':
            return importlib.import_module('.Options.UnifyEgo4d')(dataset_cfg)
        elif NAME == 'epic':
            return importlib.import_module('.Options.UnifyEpic')(dataset_cfg)
        elif NAME == 'egtea':
            return importlib.import_module('.Options.UnifyEgtea')(dataset_cfg)
        elif NAME == 'egolife':
            return importlib.import_module('.Options.UnifyEgolife')(dataset_cfg)
        else:
            raise ValueError(f'Unknown dataset name: {NAME}')