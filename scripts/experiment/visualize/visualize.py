def parse():
    import argparse, os
    parser = argparse.ArgumentParser(description="Visualization Experiment Runner")
    parser.add_argument("-e", "--experience_name", type=str, default="EgoLifeQA_A1_J", help="Name of the experience to visualize.")
    parser.add_argument("-m", "--method", type=str, default="VideoMethod", help="Name of the method whose results to visualize.")
    

    #我：考虑一下这波实验结果可视化的代码怎么来构建，有哪些元素呢？COPILOT你和我一起想
    #COPILOT：嗯，我们需要考虑以下几个元素：
    #1. 实验数据列表，比如说这个EgoLifeQA_A1_JAKE, EgoR1Bench_A1_JAKE, EgoR1Bench_A2_ALICE, EgoR1Bench_A3_TASHA, EgoR1Bench_A4_LUCIA, EgoR1Bench_A5_KATRINA, EgoR1Bench_A6_SHURE这样
    #2. 方法名称列表，比如说VideoMethod, 主要是基线方法什么的，它的整合方式还是不在这边，而是在外面
    #现在考虑的一个解决方案，就是还是把那些跑完然后数据准备好，然后我这边直接读取就完事了
    #这个还需要和hrw沟通呢，
    #我觉得那些单次大模型调用的东西，其实已经有了实验结果了对吧，其实就可以以那些的格式为例子，要求hrw把结果存储好，然后我这边就方便读取了
    #

    #缺数字的是不是还要编数字呀？别，就用‘xx.xx%’这样的字符串来占位置就行

    #3. 结果存储路径，但我觉得这个不重要。可以把接口暴露出来，只是暂时输入的路径是固定的简单的就放在代码旁边就行
    
    #4. 展示方式，比如命令行打印，图表展示等，
    
    return parser.parse_args()


if __name__ == "__main__":
    from EgoCL import Visualize
    args = parse()
    V = Visualize(Experience_name=args.experience_name, Method=args.method)
    V()