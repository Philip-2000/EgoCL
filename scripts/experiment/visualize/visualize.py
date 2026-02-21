def parse():
    import argparse, os
    parser = argparse.ArgumentParser(description="Visualization Experiment Runner")
    parser.add_argument("-c", "--config", type=str, default="default", help="Name of the configuration to use for visualization.")

    args = parser.parse_args()
    from os.path import dirname as opd
    from os.path import abspath as opa
    from os.path import join    as opj
    path = opj( os.path.dirname( opa(__file__) ), f'{args.config}.yaml' )
    return path if os.path.exists( path ) else args.config


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

"""
/mnt/data/yl/C/MyLm/MyLm/LmEvaluate/res/

20260131_204118.json #这个不太对

20260131_175914.json
20260131_180136.json
20260131_182944.json
20260131_183044.json
20260131_195151.json
20260131_195256.json

20260201_060652.json
20260201_073840.json
20260201_090135.json
20260201_133951.json
20260201_140157.json
20260201_143043.json
20260201_152011.json
20260201_171711.json
20260201_211754.json
#这里还欠一个




"""

if __name__ != "__main__":
    paths = [
        "/mnt/data/yl/W/EgoCL/Memory/EgoLifeQA_A1_JAKE_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A1_JAKE_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A2_ALICE_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A3_TASHA_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A4_LUCIA_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A5_KATRINA_D1/VideoMethod",
        "/mnt/data/yl/W/EgoCL/Memory/EgoR1Bench_A6_SHURE_D1/VideoMethod",
    ]
    import os, json
    J = []
    for path in paths:
        j = []
        for t in sorted([t for t in os.listdir(path) if str(t).isdigit()], key=lambda x: int(x)):
            filenames = [f for f in os.listdir( os.path.join(path, t) ) if f.endswith("result.json") and f.startswith("default")]
            for f in filenames:
                try:
                    data = json.load( open( os.path.join(path, t, f), 'r') )
                    # for d in [d for d in data if d['uid'] not in [item['uid'] for item in j]]: j.append(d)
                    if data['uid'] not in [item['uid'] for item in j]: j.append(data)
                except:
                    pass
        # print(j[0].keys())
        
        delay_s_s = [item['response']['delay_s'] for item in j]
        avg_delay_s = sum(delay_s_s) / len(delay_s_s)
        ratio_to_avg_delay_s = [item / avg_delay_s for item in delay_s_s]
        avg_ratio_to_avg_delay_s = sum(ratio_to_avg_delay_s) / len(ratio_to_avg_delay_s)
        dev_delay_s = ( sum( [(item - avg_delay_s)**2 for item in delay_s_s] ) / len(delay_s_s) ) ** 0.5
        dev_ratio_to_avg_delay_s = ( sum( [(item - avg_ratio_to_avg_delay_s)**2 for item in ratio_to_avg_delay_s] ) / len(ratio_to_avg_delay_s) ) ** 0.5

        # print(delay_s_s)
        delay_rate_s = [item['response']['delay_rate'] for item in j]
        avg_delay_rate_s = sum(delay_rate_s) / len(delay_rate_s)
        ratio_to_avg_delay_rate_s = [item / avg_delay_rate_s for item in delay_rate_s]
        avg_ratio_to_avg_delay_rate_s = sum(ratio_to_avg_delay_rate_s) / len(ratio_to_avg_delay_rate_s)
        dev_delay_rate_s = ( sum( [(item - avg_delay_rate_s)**2 for item in delay_rate_s] ) / len(delay_rate_s) ) ** 0.5
        dev_ratio_to_avg_delay_rate_s = ( sum( [(item - avg_ratio_to_avg_delay_rate_s)**2 for item in ratio_to_avg_delay_rate_s] ) / len(ratio_to_avg_delay_rate_s) ) ** 0.5

        # print(delay_rate_s)
        print(f"Average score: {round(sum([item['score'] for item in j])/len(j),4)}, {sum([item['score'] for item in j])} out of {len(j)} questions answered correctly")

        print(f"Average delay_s: {round(avg_delay_s,4)}s ± {round(dev_delay_s,4)}s, Average ratio to avg delay_s: {round(avg_ratio_to_avg_delay_s,4)} ± {round(dev_ratio_to_avg_delay_s,4)}")
        print(f"Average delay_rate: {round(avg_delay_rate_s,4)}% ± {round(dev_delay_rate_s,4)}%, Average ratio to avg delay_rate: {round(avg_ratio_to_avg_delay_rate_s,4)}% ± {round(dev_ratio_to_avg_delay_rate_s,4)}%")           
        
        fsize_kB_s = [item['response']['fsize_kB'] for item in j]
        avg_fsize_kB = sum(fsize_kB_s) / len(fsize_kB_s)
        ratio_to_avg_fsize_kB = [item / avg_fsize_kB for item in fsize_kB_s]
        avg_ratio_to_avg_fsize_kB = sum(ratio_to_avg_fsize_kB) / len(ratio_to_avg_fsize_kB)
        dev_fsize_kB = ( sum( [(item - avg_fsize_kB)**2 for item in fsize_kB_s] ) / len(fsize_kB_s) ) ** 0.5
        dev_ratio_to_avg_fsize_kB = ( sum( [(item - avg_ratio_to_avg_fsize_kB)**2 for item in ratio_to_avg_fsize_kB] ) / len(ratio_to_avg_fsize_kB) ) ** 0.5
        print(f"Average fsize_kB: {round(avg_fsize_kB,4)}kB ± {round(dev_fsize_kB,4)}kB, Average ratio to avg fsize_kB: {round(avg_ratio_to_avg_fsize_kB,4)} ± {round(dev_ratio_to_avg_fsize_kB,4)}")

        fsize_rate_s = [item['response']['fsize_rate'] if item['response']['fsize_rate'] is not None else item['response']['fsize_kB']/item['TIME']['seconds_experience_s'] for item in j]
        avg_fsize_rate_s = sum(fsize_rate_s) / len(fsize_rate_s)
        ratio_to_avg_fsize_rate_s = [item / avg_fsize_rate_s for item in fsize_rate_s]
        avg_ratio_to_avg_fsize_rate_s = sum(ratio_to_avg_fsize_rate_s) / len(ratio_to_avg_fsize_rate_s)
        dev_fsize_rate_s = ( sum( [(item - avg_fsize_rate_s)**2 for item in fsize_rate_s] ) / len(fsize_rate_s) ) ** 0.5
        dev_ratio_to_avg_fsize_rate_s = ( sum( [(item - avg_ratio_to_avg_fsize_rate_s)**2 for item in ratio_to_avg_fsize_rate_s] ) / len(ratio_to_avg_fsize_rate_s) ) ** 0.5
        print(f"Average fsize_rate: {round(avg_fsize_rate_s,4)}kB/s ± {round(dev_fsize_rate_s,4)}kB/s, Average ratio to avg fsize_rate: {round(avg_ratio_to_avg_fsize_rate_s,4)} ± {round(dev_ratio_to_avg_fsize_rate_s,4)}")
        
        J += j
    

    delay_s_s = [item['response']['delay_s'] for item in J]
    avg_delay_s = sum(delay_s_s) / len(delay_s_s)
    ratio_to_avg_delay_s = [item / avg_delay_s for item in delay_s_s]
    avg_ratio_to_avg_delay_s = sum(ratio_to_avg_delay_s) / len(ratio_to_avg_delay_s)
    dev_delay_s = ( sum( [(item - avg_delay_s)**2 for item in delay_s_s] ) / len(delay_s_s) ) ** 0.5
    dev_ratio_to_avg_delay_s = ( sum( [(item - avg_ratio_to_avg_delay_s)**2 for item in ratio_to_avg_delay_s] ) / len(ratio_to_avg_delay_s) ) ** 0.5
    delay_rate_s = [item['response']['delay_rate'] for item in J]
    avg_delay_rate_s = sum(delay_rate_s) / len(delay_rate_s)
    ratio_to_avg_delay_rate_s = [item / avg_delay_rate_s for item in delay_rate_s]
    avg_ratio_to_avg_delay_rate_s = sum(ratio_to_avg_delay_rate_s) / len(ratio_to_avg_delay_rate_s)
    dev_delay_rate_s = ( sum( [(item - avg_delay_rate_s)**2 for item in delay_rate_s] ) / len(delay_rate_s) ) ** 0.5
    dev_ratio_to_avg_delay_rate_s = ( sum( [(item - avg_ratio_to_avg_delay_rate_s)**2 for item in ratio_to_avg_delay_rate_s] ) / len(ratio_to_avg_delay_rate_s) ) ** 0.5

    print(f"Overall Average score: {round(sum([item['score'] for item in J])/len(J),4)}, {sum([item['score'] for item in J])} out of {len(J)} questions answered correctly")
    print(f"Overall Average delay_s: {round(avg_delay_s,4)}s ± {round(dev_delay_s,4)}s, Overall Average ratio to avg delay_s: {round(avg_ratio_to_avg_delay_s,4)} ± {round(dev_ratio_to_avg_delay_s,4)}")
    print(f"Overall Average delay_rate: {round(avg_delay_rate_s,4)}% ± {round(dev_delay_rate_s,4)}%, Overall Average ratio to avg delay_rate: {round(avg_ratio_to_avg_delay_rate_s,4)}% ± {round(dev_ratio_to_avg_delay_rate_s,4)}%")

    fsize_kB_s = [item['response']['fsize_kB'] for item in J]
    avg_fsize_kB = sum(fsize_kB_s) / len(fsize_kB_s)
    ratio_to_avg_fsize_kB = [item / avg_fsize_kB for item in fsize_kB_s]
    avg_ratio_to_avg_fsize_kB = sum(ratio_to_avg_fsize_kB) / len(ratio_to_avg_fsize_kB)
    dev_fsize_kB = ( sum( [(item - avg_fsize_kB)**2 for item in fsize_kB_s] ) / len(fsize_kB_s) ) ** 0.5
    dev_ratio_to_avg_fsize_kB = ( sum( [(item - avg_ratio_to_avg_fsize_kB)**2 for item in ratio_to_avg_fsize_kB] ) / len(ratio_to_avg_fsize_kB) ) ** 0.5
    print(f"Overall Average fsize_kB: {round(avg_fsize_kB,4)}kB ± {round(dev_fsize_kB,4)}kB, Overall Average ratio to avg fsize_kB: {round(avg_ratio_to_avg_fsize_kB,4)} ± {round(dev_ratio_to_avg_fsize_kB,4)}")

    fsize_rate_s = [item['response']['fsize_rate'] if item['response']['fsize_rate'] is not None else item['response']['fsize_kB']/item['TIME']['seconds_experience_s'] for item in J]
    avg_fsize_rate_s = sum(fsize_rate_s) / len(fsize_rate_s)
    ratio_to_avg_fsize_rate_s = [item / avg_fsize_rate_s for item in fsize_rate_s]
    avg_ratio_to_avg_fsize_rate_s = sum(ratio_to_avg_fsize_rate_s) / len(ratio_to_avg_fsize_rate_s)
    dev_fsize_rate_s = ( sum( [(item - avg_fsize_rate_s)**2 for item in fsize_rate_s] ) / len(fsize_rate_s) ) ** 0.5
    dev_ratio_to_avg_fsize_rate_s = ( sum( [(item - avg_ratio_to_avg_fsize_rate_s)**2 for item in ratio_to_avg_fsize_rate_s] ) / len(ratio_to_avg_fsize_rate_s) ) ** 0.5
    print(f"Overall Average fsize_rate: {round(avg_fsize_rate_s,4)}kB/s ± {round(dev_fsize_rate_s,4)}kB/s, Overall Average ratio to avg fsize_rate: {round(avg_ratio_to_avg_fsize_rate_s,4)} ± {round(dev_ratio_to_avg_fsize_rate_s,4)}")

else:
    from EgoCL import Visualizer
    args = parse()
    V = Visualizer(args)
    V()