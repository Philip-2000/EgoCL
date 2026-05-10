versions=(
    "Base"
    "NoCon"
    "Len8"
    "Len12"
    "PlainEncode"
    "PreEncode"
    "NoSS"
    "NoSum"
    "NoTrans"
    "Top2"
    "Top4"
)

method="BaseMem"
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

#result_dir is the absolute path of the folder of this "auto.sh" file
result_dir=$(dirname "$(readlink -f "$0")")/configs/
bashs_dir=$(dirname "$(readlink -f "$0")")/bashs/
ids_dir=$(dirname "$(readlink -f "$0")")/EgoLifeQA_IDS/




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


for v in "${versions[@]}"; do
    
    for i in "${!files[@]}"; do
        file="${files[$i]}"
        
        echo "Creating configuration for file: $file with model replica: ${replicas[$i]}"
        if [[ "${v}" == "PlainEncode" ]]; then
            python create.py --METHOD "$v" --ENCODERE "$modele:${replicas[$i]}" --ENCODERM "$modele:${replicas[$i]}" --EXPERIENCE "${file}" --RESULT_FILE "${result_dir}${file}_${v}.yaml"
        else
            python create.py --METHOD "$v" --ENCODERE "$modele:${replicas[$i]}" --ENCODERM "$modelm:${replicas[$i]}" --EXPERIENCE "${file}" --RESULT_FILE "${result_dir}${file}_${v}.yaml"
        fi
    done
done

for i in "${!files[@]}"; do
    file="${files[$i]}"
    bash_file="${bashs_dir}${file}.sh"
    status_file="${bashs_dir}${file}.txt"
    echo "Creating bash file: $bash_file for file: $file"
    touch "$bash_file"
    #clear the content of bash_file and status_file
    > "$bash_file"
    touch "$status_file"
    > "$status_file"
    for v in "${versions[@]}"; do
        if [[ "${SERVER_NAME: -3}" == "4Pb" ]]; then
            echo "${result_dir}${file}_${v}.bash" >> "$bash_file"
        elif [[ "${SERVER_NAME: -3}" == "4Pc" ]]; then
            echo "python answering.py -c ${result_dir}${file}_${v}.yaml -q '$(cat ${ids_dir}${replicas[$i]}.txt)' " >> "$bash_file"    
        else
            echo "python answering.py -c ${result_dir}${file}_${v}.yaml" >> "$bash_file"
        fi
        echo "echo 'Finished ${v}' >> ${status_file}" >> "$bash_file"
    done
done

#对于EgoSchema：最小粒度的是yaml，其次是bash，最后是bashes。bash整合了一系列yaml，这些yaml的实验对象不同，但是消融版本相同；bashes整合了一系列bash，这些bash的消融版本不同。
#yaml都需要生成；bash需要生成，bashes也需要生成

#yaml最可怕的就是他需要把modelm和modele的版本都写进去，这个不能错。

#有几张卡就出几个bashes

#对于EgoLifeQA：最小粒度的是yaml，其次是bashes。我需要生成yaml，生成bashes

#有几张卡就出几个bashes

#对于EgoR1Bench：最小粒度是yaml，其次就是bashes了，