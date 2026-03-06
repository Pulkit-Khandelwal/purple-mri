working_dir=$1
str_split=$2
freesurfer_path=$3
num_threads=$4
external_atlases_path=$5
hemis=$6
for i in $str_split; do subjects+=($i) ; done

if [[ "$hemis" == "rh" ]]; then
    hemis_other="lh"
else
    hemis_other="rh"
fi

for subj in "${subjects[@]}"
do

echo ${subj}
start=$SECONDS
SUBJECTS_DIR=${working_dir}

mris_place_surface --adgws-in ${working_dir}/autodet.gw.stats.binary.dat  \
--wm ${SUBJECTS_DIR}/${subj}/mri/wm.mgz --threads ${num_threads} --invol ${SUBJECTS_DIR}/${subj}/mri/aseg.presurf_100.mgz --${hemis} \
--i ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig \
--o ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white.preaparc --white --nsmooth 5 --seg ${SUBJECTS_DIR}/${subj}/mri/aseg.presurf.mgz

mri_label2label --label-cortex ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white.preaparc ${SUBJECTS_DIR}/${subj}/mri/aseg.presurf.mgz 0 ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label

mris_smooth -n 7 -nw ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white.preaparc ${SUBJECTS_DIR}/${subj}/surf/${hemis}.smoothwm
mris_inflate -n 40 ${SUBJECTS_DIR}/${subj}/surf/${hemis}.smoothwm ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated

mris_curvature -w ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white.preaparc
mris_curvature -thresh .999 -n -a 5 -w -distances 10 10 ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated

mris_sphere ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated ${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere

# MCRIBS
mris_register -multi_level 2 -curv -threads ${num_threads} -inflated \
-init -reg ${SUBJECTS_DIR}/${subj}/mri/transforms/init_for_mris_register_mcribs.lta \
${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere \
${external_atlases_path}/mcribs/${hemis}.template2.tif \
${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere.reg

mrisp_paint -a 5 ${external_atlases_path}/mcribs/${hemis}.template2.tif \
${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere.reg ${SUBJECTS_DIR}/${subj}/surf/${hemis}.avg_curv

mris_ca_label -l ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label \
-aseg ${SUBJECTS_DIR}/${subj}/mri/aseg.presurf.mgz ${subj} ${hemis} ${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere.reg \
${external_atlases_path}/mcribs/${hemis}.aparc+DKTatlas.gcs \
${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.mcribs.annot


cd ${SUBJECTS_DIR}/${subj}/mri
mris_place_surface --adgws-in ${working_dir}/autodet.gw.stats.binary.dat \
--seg aseg.presurf.mgz --threads ${num_threads} --wm wm.mgz --invol aseg.presurf_100.mgz --${hemis} --i ../surf/${hemis}.white.preaparc --o ../surf/${hemis}.white --white --nsmooth 5 \
--rip-label ../label/${hemis}.cortex.label --rip-bg --rip-surf ../surf/${hemis}.white.preaparc --aparc ../label/${hemis}.aparc.mcribs.annot


#########################
###### native ######
#########################

cd ${SUBJECTS_DIR}/${subj}/mri
num_iters=20
input_surf="../surf/${hemis}.smoothwm"
for ((iter=1; iter<=num_iters; iter++)); do
  echo "iteration >>>>>>>" $iter
  output_surf="../surf/${hemis}.pial.T1.iter${iter}"

  # Use previous iteration's pial surface as repulse & white surf after first iteration
  if [[ $iter -gt 1 ]]; then
    input_surf="../surf/${hemis}.pial.T1.iter$((iter-1))"
  fi
  
  mris_place_surface \
    --adgws-in ${working_dir}/autodet.gw.stats.binary.dat \
    --seg aseg.presurf_100.mgz \
    --threads ${num_threads} \
    --nsmooth 1 \
    --wm wm.mgz \
    --invol aseg.presurf_100.mgz \
    --${hemis} \
    --i "${input_surf}" \
    --o "${output_surf}" \
    --pial \
    --repulse-surf "${input_surf}" \
    --white-surf "${input_surf}" \
    --no-intensity-proc \
    --max-cbv-dist 4.0 \
    --intensity 30.0 --curv 5.0

done

cd ${SUBJECTS_DIR}/${subj}/mri
cp ../surf/${hemis}.pial.T1.iter20 ../surf/${hemis}.pial.T1
cp ../surf/${hemis}.pial.T1.iter20 ../surf/${hemis}.pial
mris_smooth -n 3 -nw ../surf/${hemis}.pial ../surf/${hemis}.pial.smoothed


SUBJECTS_DIR=${working_dir}
######## dummy left hemis needed for stats computation
cp ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white ${SUBJECTS_DIR}/${subj}/surf/${hemis_other}.white
cp ${SUBJECTS_DIR}/${subj}/surf/${hemis}.pial ${SUBJECTS_DIR}/${subj}/surf/${hemis_other}.pial
cp ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.nofix ${SUBJECTS_DIR}/${subj}/surf/${hemis_other}.orig.nofix
cp ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label ${SUBJECTS_DIR}/${subj}/label/${hemis_other}.cortex.label
cp ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.mcribs.annot ${SUBJECTS_DIR}/${subj}/label/${hemis_other}.aparc.mcribs.annot


cd ${SUBJECTS_DIR}/${subj}/mri
mri_surf2volseg --o aparc.mcribs.mgz \
--label-cortex --i aseg.mgz --threads ${num_threads} \
--lh-annot ${SUBJECTS_DIR}/${subj}/label/lh.aparc.mcribs.annot 1000 \
--lh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/lh.cortex.label \
--lh-white ${SUBJECTS_DIR}/${subj}/surf/lh.white \
--lh-pial ${SUBJECTS_DIR}/${subj}/surf/lh.pial \
--rh-annot ${SUBJECTS_DIR}/${subj}/label/rh.aparc.mcribs.annot 2000 \
--rh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/rh.cortex.label \
--rh-white ${SUBJECTS_DIR}/${subj}/surf/rh.white \
--rh-pial ${SUBJECTS_DIR}/${subj}/surf/rh.pial

done
