#!/bin/bash



#
#我先估算一下实验的时间吧，
#算上消融实验，一共有11种问答版本需要跑，其中有
#Base，Len8，Len12，NoCon，PlainEncode，PreEncode，NoSS, NoSum，NoTrans，Top2，Top4
#其中前5种需要现场编码，后6种不需要现场编码而是读取前面的编码
#前5种单个QA的时间大概是40秒，后6种单个QA的时间大概记作30秒，
#然后每一个EgoR1Bench的每个人的问题有50个问题，EgoLifeQA有500个问题，然后EgoSchema一共有500个问题
#
#那先考虑EgoSchema吧，我感觉还是需要拆成四份的，每一份125个问题
#那么跑完前5个就需要40*125*5=25000秒，大概7小时，跑完后6个就需要30*125*6=22500秒，大概6.25小时
#所以EgoSchema大概需要13个半小时的时间

#再说EgoR1Bench，每个人50个问题，前5个版本需要40*50*5=10000秒，大概2.8小时，后6个版本需要30*50*6=9000秒，大概2.5小时

#最可怕的是EgoLifeQA，500个问题，前5个版本需要40*500*5=100000秒，大概28小时，后6个版本需要30*500*6=90000秒，大概25小时
#跑完需要一天的时间
#
#     4Pa          2Pa         4Pb            1Pb        1Pa
#   A1_JAKE    A5_KATRINA   EgoSchema_A   EgoLifeQA   (for testing)
#   A2_ALICE    A6_SHURE    EgoSchema_B 
#   A3_TASHA                EgoSchema_C
#   A4_LUCIA                EgoSchema_D
#

#做几件事，（1）启动若干个"Qwen3-Embed-0.6B"模型（2）启动若干个"Qwen3-VL-Embedding-2B"模型 (3)依次启动各个版本的python answering.py -e blablabla -m version

#确认一下强制编码过程；确认一下answering拆分过程。命令是什么，是python answering.py -e E -m v -q 后面接着一个txt文件，要在命令行里把txt文件内容导入到-q的后面
#txt比如说是/mnt/data/yl/C/EgoCL/scripts/experiment/auto/EgoLifeQA_IDS/a.txt
#写法是 python answering.py -e E -m v -q "$(cat /mnt/data/yl/C/EgoCL/scripts/experiment/auto/EgoLifeQA_IDS/a.txt)"
#-e和-m也不对，也应该是拼出那个-c然后接着用-c来指定yaml文件，yaml文件里会指定-e和-m

#然后所有这些python answering.py程序，e相同但m不同的，都不能依次send送入，而是应该拼成一个bash文件，然后一次性send送入该bash文件，这样就能保证它们是连续执行的，不会在一个版本还没跑完的时候就开始跑下一个版本了


modele="Qwen3-Embed-0.6B"
modelm="Qwen3-VL-Embedding-2B"
d="7"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --method)
            method="${2:-$method}"
            shift 2
            ;;
        --d)
            d="${2:-$d}"
            shift 2
            ;;
        --modele)
            modele="${2:-$modele}"
            shift 2
            ;;
        --modelm)
            modelm="${2:-$modelm}"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# if [ $d == "1" ]; then
#     base_dir="/mnt/data/yl/C/EgoCL/scripts/experiment/experiment/D1_base/"
# else
#     base_dir="/mnt/data/yl/C/EgoCL/scripts/experiment/experiment/yaml_base/"
# fi

#result_dir is the absolute path of the folder of this "serve.sh" file
result_dir=$(dirname "$(readlink -f "$0")")/configs/





if [[ "${SERVER_NAME: -3}" == "4Pa" ]]; then
    if [ $d == "1" ]; then
        files=( "A1_JAKE_D1" "A2_ALICE_D1" "A3_TASHA_D1" "A4_LUCIA_D1" )
    else
        files=( "A1_JAKE" "A2_ALICE" "A3_TASHA" "A4_LUCIA" )
    fi
elif [[ "${SERVER_NAME: -3}" == "2Pa" ]]; then
    if [ $d == "1" ]; then
        files=( "A5_KATRINA_D1" "A6_SHURE_D1")
    else
        files=( "A5_KATRINA" "A6_SHURE")
    fi
elif [[ "${SERVER_NAME: -3}" == "4Pb" ]]; then
    files=( "EgoSchema_a" "EgoSchema_b" "EgoSchema_c" "EgoSchema_d")
elif [[ "${SERVER_NAME: -3}" == "4Pc" ]]; then
    if [ $d == "1" ]; then
        files=( "EgoLifeQA_D1_a" "EgoLifeQA_D1_b" "EgoLifeQA_D1_c" "EgoLifeQA_D1_d")
    else
        files=( "EgoLifeQA_a" "EgoLifeQA_b" "EgoLifeQA_c" "EgoLifeQA_d")
    fi
fi

echo "method=$method"
echo "modelm=$modelm"
echo "modele=$modele"
echo "result_dir=$result_dir"
echo "files=${files[*]}"
echo "SERVER_NAME=$SERVER_NAME"




replicas=(
    "a"
    "b"
    "c"
    "d"
    "e"
)
modelm_replicas=(
    "ta"
    "tb"
    "tc"
    "td"
    "te"
)
modele_replicas=(
    "ua"
    "ub"
    "uc"
    "ud"
    "ue"
)
runner_replicas=(
    "ra"
    "rb"
    "rc"
    "rd"
    "re"
)



for i in "${!files[@]}"; do
    file="${files[$i]}"
    echo "Starting server tmux session: ${modele_replicas[$i]} for file: $file, at modele replica: ${replicas[$i]}, CUDA_VISIBLE_DEVICES=$i"
    
    tmux kill-session -t "${modele_replicas[$i]}" 2>/dev/null
    tmux new-session -d -s "${modele_replicas[$i]}"
    tmux send-keys -t "${modele_replicas[$i]}" 'fserv' C-m
    tmux send-keys -t "${modele_replicas[$i]}" "CUDA_VISIBLE_DEVICES=$i  python LmServe.py ${modele}:${replicas[$i]}" C-m

    tmux kill-session -t "${modelm_replicas[$i]}" 2>/dev/null
    tmux new-session -d -s "${modelm_replicas[$i]}"
    tmux send-keys -t "${modelm_replicas[$i]}" 'fserv' C-m
    tmux send-keys -t "${modelm_replicas[$i]}" "CUDA_VISIBLE_DEVICES=$i  python LmServe.py ${modelm}:${replicas[$i]}" C-m
done
