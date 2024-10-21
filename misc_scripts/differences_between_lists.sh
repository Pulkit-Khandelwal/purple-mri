list1=()
list2=()
list3=()


diff_list=()
common_list=()
#loop through the first list comparing an item from list1 with every item in list2
for i in "${!list1[@]}"; do
#begin looping through list2
    for x in "${!list2[@]}"; do
#compare the two items
        if test "${list1[i]}"  == "${list2[x]}"; then
#add item to the common_list, then remove it from list1 and list2 so that we can 
#later use those to generate the diff_list            
            common_list+=("${list2[x]}")
            unset 'list1[i]'
            unset 'list2[x]'
        fi
    done
done

#add unique items from list1 to diff_list
for i in "${!list1[@]}"; do
    diff_list+=("${list1[i]}")
done
#add unique items from list2 to diff_list
for i in "${!list2[@]}"; do
    diff_list+=("${list2[i]}")
done

#print out the results
echo "Here are the common items between list1 & list2:"
printf '%s\n' "${common_list[@]}"

echo "Here are the unique items between list1 & list2:"
printf '%s\n' "${diff_list[@]}"
