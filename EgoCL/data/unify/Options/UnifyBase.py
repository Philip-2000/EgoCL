
class UnifyBase:
    def __init__(self, cfg):
        self.cfg = cfg
        #这种基类能为子类提供什么便利呢
        #不知道啊，好像子类的东西全都不太一样啊
        #算了，谁知道呢，万一未来发现有一些功能是所有子类都需要的呢
        #到时候再把这些功能加到基类里吧

    def __repr__(self):
        return f'{self.__class__}(cfg={self.cfg})'
    
    def __call__(self, **kwargs):
        raise NotImplementedError("Virtual Function: Subclasses should implement this method.")

    def save(self):
        pass