working_dir=$1
str_split=$2
for i in $str_split; do subjects+=($i) ; done

hemis=rh
for subj in "${subjects[@]}"
do
echo ${subj}
start=$SECONDS

SUBJECTS_DIR=${working_dir}/${subj}
mris_extract_main_component ${SUBJECTS_DIR}/surf/${hemis}.orig.nofix ${SUBJECTS_DIR}/surf/${hemis}.orig.nofix

mris_smooth -nw ${SUBJECTS_DIR}/surf/${hemis}.orig.nofix ${SUBJECTS_DIR}/surf/${hemis}.smoothwm.nofix
mris_euler_number ${SUBJECTS_DIR}/surf/${hemis}.smoothwm.nofix

mris_inflate -no-save-sulc ${SUBJECTS_DIR}/surf/${hemis}.smoothwm.nofix ${SUBJECTS_DIR}/surf/${hemis}.inflated.nofix
mris_euler_number ${SUBJECTS_DIR}/surf/${hemis}.inflated.nofix

mris_sphere -q -p 6 -a 128 ${SUBJECTS_DIR}/surf/${hemis}.inflated.nofix ${SUBJECTS_DIR}/surf/${hemis}.qsphere.nofix

SUBJECTS_DIR=${working_dir}
mris_fix_topology -mgz -sphere qsphere.nofix -inflated inflated.nofix -orig orig.nofix -out orig.premesh -defect defect -ga ${subj} ${hemis} -threads 64 -verbose -errors -warnings
mris_euler_number ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.premesh

mris_inflate ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.premesh ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated.fixed
mris_euler_number ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated.fixed

mris_remove_intersection ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.premesh ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.premesh
mris_extract_main_component ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.premesh ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.premesh
mris_euler_number ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.premesh

cp ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.premesh ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig
cp ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated.fixed ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated
mris_euler_number ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig

duration=$(( SECONDS - start ))
echo "total time for this subject:" $duration
done