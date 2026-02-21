#(1) Experience Name
#(2) Method Kwargs
#(3) 我后来还在想，就是那个从Method参数，匹配到这个Experiment的name上
#可以搞一个矩阵，但是就需要一个模块来管理这个矩阵，
#这个模块应该在哪里呢？
#而且他和answering的关系是什么呢？
#现在answering模块默认从memory.json中加载记忆，但是招我们刚才想的东西，其实可以让他从一个指定的位置来读取对吧？
#因为我们已经要把memory.json这个文件的名字改成experiment的名字了对吧。
#所以可以从这里搞出来？

#我感觉要不然就放在experiment这个文件夹之下，形成一个叫Answerings的文件夹，然后来管理矩阵，需要能：（1）生成对应的yaml文件，（2）正确索引到对应的yaml文件，（3）利用yaml运行Answering程序之后，能够正确访问到结果的保存位置，（4）根据矩阵中的关系，把结果读取出来，形成一个可视化结果。
#先别做这个，先做那个Experience Name和Method Kwargs拼接起来的东西吧？
import os
configs_path = os.path.join( os.path.dirname( os.path.abspath(__file__) ), 'configs' )
def exp_config(config_path=None, method_yaml_name=None, experience_yaml_name=None, **kwargs):
    import yaml, os
    if config_path is not None:
        config = yaml.safe_load(open(config_path, 'r'))
        assert "EXPERIENCE" in config and "METHOD" in config, "Experiment config file must contain 'EXPERIENCE' and 'METHOD' fields."
        return config

    # assert method_yaml_name != "Test" or experience_yaml_name == "EgoLifeQA_J", "Test Method can only be used for test experience, i.e., 'EgoLifeQA_J'. Please do not use Test Method for other experiences to avoid unexpected issues."
    from os.path import join as opj, dirname as opd, abspath as opa
    method_yaml_name = method_yaml_name if method_yaml_name is not None else "Video"
    experience_yaml_name = experience_yaml_name if experience_yaml_name is not None else "EgoLifeQA_J"

    method_f = opj(configs_path, "methods", method_yaml_name+".yaml")
    experience_f = opj(opd(opa(__file__)), "configs", "experiences", experience_yaml_name+".yaml")
    return { **(yaml.safe_load(open(method_f, 'r'))), **(yaml.safe_load(open(experience_f, 'r'))) }




#你还要考虑怎么和auto配合的问题，
#就是你这一套东西重构完了之后，和那个auto的关系是什么呢？
#但是没关系，到时候只改auto的代码就行了