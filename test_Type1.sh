shortest_arr=(0 0 0)
leastcap_arr=(0 0 0)
min_max__arr=(0 0 0)
conflict_arr=(0 0 0)

file_name=input/5-3.in

for i in {1..200}
do
    if [ $(($i%10)) = 0 ]
    then
        echo "iter = $i"
    fi

    python3 generate_test_case.py $file_name

    python3 main.py $file_name shortest_path >> exp_record
    ((shortest_arr[$?]+=1))

    python3 main.py $file_name least_used_capacity_percentage >> exp_record
    ((leastcap_arr[$?]+=1))

    python3 main.py $file_name min_max_percentage >> exp_record
    ((min_max__arr[$?]+=1))

    python3 main.py $file_name least_conflict_value >> exp_record
    ((conflict_arr[$?]+=1))
done

echo ${shortest_arr[@]}
echo ${leastcap_arr[@]}
echo ${min_max__arr[@]}
echo ${conflict_arr[@]}