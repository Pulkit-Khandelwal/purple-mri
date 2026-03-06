
freesurfer_path=$1
working_dir=$2
str_split=$3
for i in $str_split; do subjects+=($i) ; done

for subj in "${subjects[@]}"
do

  echo ${subj}
  SUBJECTS_DIR=${working_dir}/${subj}
  
  tkregister2 --mov ${SUBJECTS_DIR}/mri/rawavg.mgz --targ ${external_atlases_path}/mcribs/template-40_brain.mgz \
  --reg ${SUBJECTS_DIR}/mri/transforms/register.native.dat --regheader-center \
  --noedit --ltaout ${SUBJECTS_DIR}/mri/transforms/init_for_mris_register_mcribs.lta
  
  mri_add_xform_to_header -c ${SUBJECTS_DIR}/mri/transforms/talairach.xfm ${external_atlases_path}/mcribs/template-40_brain.mgz ${external_atlases_path}/mcribs/template-40_brain.mgz

  mri_info ${external_atlases_path}/mcribs/template-40_brain.mgz
  
  ${freesurfer_path}/bin/talairach_avi --i ${external_atlases_path}/mcribs/template-40_brain.mgz --xfm ${SUBJECTS_DIR}/mri/transforms/talairach.auto.xfm
  
  cp ${SUBJECTS_DIR}/mri/transforms/talairach.auto.xfm ${SUBJECTS_DIR}/mri/transforms/talairach.xfm
  
  lta_convert --src ${external_atlases_path}/mcribs/template-40_brain.mgz --trg ${freesurfer_path}/freesurfer/average/mni305.cor.mgz \
  --inxfm ${SUBJECTS_DIR}/mri/transforms/talairach.xfm --outlta ${SUBJECTS_DIR}/mri/transforms/talairach.xfm.lta --subject fsaverage --ltavox2vox
  
  mri_add_xform_to_header -c ${SUBJECTS_DIR}/mri/transforms/talairach.xfm ${external_atlases_path}/mcribs/template-40_brain.mgz ${external_atlases_path}/mcribs/template-40_brain.mgz

done;

