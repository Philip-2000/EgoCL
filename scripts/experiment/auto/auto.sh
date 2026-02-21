#!/bin/bash

method="Video"
model="Qwen2.5-VL-7B-Instruct"
d="1"

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
        --model)
            model="${2:-$model}"
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

#result_dir is the absolute path of the folder of this "auto.sh" file
result_dir=$(dirname "$(readlink -f "$0")")/configs/


if [[ "${SERVER_NAME: -1}" == "a" ]]; then
    if [ $d == "1" ]; then
        files=( "A1_JAKE_D1" "A2_ALICE_D1" "A3_TASHA_D1" "A4_LUCIA_D1" )
    else
        files=( "A1_JAKE" "A2_ALICE" "A3_TASHA" "A4_LUCIA" )
    fi
else
    if [ $d == "1" ]; then
        files=( "A5_KATRINA_D1" "A6_SHURE_D1" "EgoLifeQA_D1" )
    else
        files=( "A5_KATRINA" "A6_SHURE" "EgoLifeQA" )
    fi
fi

echo "method=$method"
echo "model=$model"
echo "result_dir=$result_dir"
echo "files=${files[*]}"




replicas=(
    "a"
    "b"
    "c"
    "d"
    "e"
)
server_replicas=(
    "sa"
    "sb"
    "sc"
    "sd"
    "se"
)
runner_replicas=(
    "ra"
    "rb"
    "rc"
    "rd"
    "re"
)



#(1) Step Two: Start tmux sessions for server
for i in "${!files[@]}"; do
    file="${files[$i]}"
    echo "Starting server tmux session: ${server_replicas[$i]} for file: $file, at model replica: ${replicas[$i]}, CUDA_VISIBLE_DEVICES=$i"
    tmux kill-session -t "${server_replicas[$i]}" 2>/dev/null
    tmux new-session -d -s "${server_replicas[$i]}"
    tmux send-keys -t "${server_replicas[$i]}" 'fserv' C-m
    tmux send-keys -t "${server_replicas[$i]}" "CUDA_VISIBLE_DEVICES=$i  python LmServe.py ${model}:${replicas[$i]}" C-m
done

#(2) Step One: Create Yaml from Yaml base
for i in "${!files[@]}"; do
    file="${files[$i]}"
    
    echo "Creating configuration for file: $file with model replica: ${replicas[$i]}"
    python create.py --METHOD "$method" --MODEL "$model:${replicas[$i]}" --EXPERIENCE "${file}" --RESULT_FILE "${result_dir}${file}.yaml"
done


#(3) Step 2.9: Wait a bit for servers to start
echo "Waiting 60 seconds for servers to start..."
sleep 60

#(4) Step Three: Start tmux sessions for runner
for i in "${!files[@]}"; do
    file="${files[$i]}"
    echo "Starting runner tmux session: ${runner_replicas[$i]} for file: $file"
    tmux kill-session -t "${runner_replicas[$i]}" 2>/dev/null
    tmux new-session -d -s "${runner_replicas[$i]}"
    tmux send-keys -t "${runner_replicas[$i]}" 'fmemo' C-m
    tmux send-keys -t "${runner_replicas[$i]}" "python experiment.py -c ${result_dir}${file}.yaml" C-m
done

