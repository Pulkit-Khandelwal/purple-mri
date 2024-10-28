subjects=()
echo ${#subjects[@]}

SUBJECTS_DIR=
for subj in "${subjects[@]}"
do
echo ${subj}

ls ${SUBJECTS_DIR}/${subj}/surf

freeview -f ${SUBJECTS_DIR}/${subj}/surf/rh.pial:annot=${SUBJECTS_DIR}/${subj}/label/rh.aparc.DKTatlas.annot \
--viewport '3d' --viewsize 900 900 -cam zoom 1.0 -ss ${SUBJECTS_DIR}/screenshots/${subj}.png

done;

:<<'VIZ'
freeview -v mri/orig.mgz mri/aparc.DKTatlas+aseg.mgz:colormap=LUT \
-f surf/rh.pial:annot=label/rh.aparc.DKTatlas.annot:edgecolor=yellow surf/rh.inflated:annot=label/rh.aparc.DKTatlas.annot:edgecolor=yellow
VIZ
