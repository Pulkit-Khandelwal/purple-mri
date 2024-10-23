working_dir=$1
str_split=$2
freesurfer_path=$3
num_threads=$4
external_atlases_path=$5
autodet_stats_dat=$6
for i in $str_split; do subjects+=($i) ; done

hemis=rh
hemis_other=lh
for subj in "${subjects[@]}"
do
echo ${subj}
start=$SECONDS

SUBJECTS_DIR=${working_dir}

######### segm_parc file
mris_place_surface --adgws-in ${autodet_stats_dat} \
--wm ${SUBJECTS_DIR}/${subj}/mri/wm.mgz --threads ${num_threads} --invol ${SUBJECTS_DIR}/${subj}/mri/aseg.presurf_100.mgz --${hemis} \
--i ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig \
--o ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white.preaparc --white --seg ${SUBJECTS_DIR}/${subj}/mri/aseg.presurf.mgz

mri_label2label --label-cortex ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white.preaparc ${SUBJECTS_DIR}/${subj}/mri/aseg.presurf.mgz 0 ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label

mris_smooth -n 3 -nw ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white.preaparc ${SUBJECTS_DIR}/${subj}/surf/${hemis}.smoothwm
mris_inflate ${SUBJECTS_DIR}/${subj}/surf/${hemis}.smoothwm ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated

mris_curvature -w ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white.preaparc
mris_curvature -thresh .999 -n -a 5 -w -distances 10 10 ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated

mris_sphere ${SUBJECTS_DIR}/${subj}/surf/${hemis}.inflated ${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere

mris_register -curv -threads ${num_threads} -inflated -init \
-reg ${SUBJECTS_DIR}/${subj}/mri/transforms/init_for_mris_register.lta \
${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere ${freesurfer_path}/average/${hemis}.folding.atlas.acfb40.noaparc.i12.2016-08-02.tif ${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere.reg

ln -sf ${hemis}.sphere.reg ${hemis}.fsaverage.sphere.reg

mris_jacobian ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white.preaparc ${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere.reg ${SUBJECTS_DIR}/${subj}/surf/${hemis}.jacobian_white
mrisp_paint -a 5 ${freesurfer_path}/average/${hemis}.folding.atlas.acfb40.noaparc.i12.2016-08-02.tif#6 ${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere.reg ${SUBJECTS_DIR}/${subj}/surf/${hemis}.avg_curv 

mris_ca_label -l ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label -aseg ${SUBJECTS_DIR}/${subj}/mri/aseg.presurf.mgz ${subj} ${hemis} ${SUBJECTS_DIR}/${subj}/surf/${hemis}.sphere.reg ${freesurfer_path}/average/${hemis}.DKaparc.atlas.acfb40.noaparc.i12.2016-08-02.gcs ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.annot 

SUBJECTS_DIR=${working_dir}

cd ${SUBJECTS_DIR}/${subj}/mri
mris_place_surface --adgws-in ${autodet_stats_dat} \
--seg aseg.presurf.mgz --threads ${num_threads} --wm wm.mgz --invol aseg.presurf_100.mgz --${hemis} --i ../surf/${hemis}.white.preaparc --o ../surf/${hemis}.white --white --nsmooth 0 \
--rip-label ../label/${hemis}.cortex.label --rip-bg --rip-surf ../surf/${hemis}.white.preaparc --aparc ../label/${hemis}.aparc.annot

cd ${SUBJECTS_DIR}/${subj}/mri
mris_place_surface --adgws-in ${autodet_stats_dat} \
--seg aseg.presurf.mgz --threads ${num_threads} --wm wm.mgz \
--invol aseg.presurf_100.mgz --${hemis} --i ../surf/${hemis}.white --o ../surf/${hemis}.pial.T1 --pial --nsmooth 0 \
--pin-medial-wall ../label/${hemis}.cortex.label --aparc ../label/${hemis}.aparc.annot \
--repulse-surf ../surf/${hemis}.white --white-surf ../surf/${hemis}.white \
--no-rip --intensity 10.00 --curv 10.00

cp ${SUBJECTS_DIR}/${subj}/surf/${hemis}.pial.T1 ${SUBJECTS_DIR}/${subj}/surf/${hemis}.pial

######## white curv
cd ${SUBJECTS_DIR}/${subj}/mri
mris_place_surface --curv-map ../surf/${hemis}.white 2 10 ../surf/${hemis}.curv

######## white area
cd ${SUBJECTS_DIR}/${subj}/mri
mris_place_surface --area-map ../surf/${hemis}.white ../surf/${hemis}.area

######## pial curv
cd ${SUBJECTS_DIR}/${subj}/mri
mris_place_surface --curv-map ../surf/${hemis}.pial 2 10 ../surf/${hemis}.curv.pial

######## pial area
cd ${SUBJECTS_DIR}/${subj}/mri
mris_place_surface --area-map ../surf/${hemis}.pial ../surf/${hemis}.area.pial

######## thickness
cd ${SUBJECTS_DIR}/${subj}/mri
mris_place_surface --thickness ../surf/${hemis}.white ../surf/${hemis}.pial 20 5 ../surf/${hemis}.thickness

######## area and vertex vol
cd ${SUBJECTS_DIR}/${subj}/mri
mris_place_surface --thickness ../surf/${hemis}.white ../surf/${hemis}.pial 20 5 ../surf/${hemis}.thickness

mris_curvature_stats -m --writeCurvatureFiles -G -o ${SUBJECTS_DIR}/${subj}/stats/${hemis}.curv.stats -F smoothwm ${subj} ${hemis} curv sulc

######## Cortical Parc 2
cd ${SUBJECTS_DIR}/${subj}/mri
mris_ca_label -l ../label/${hemis}.cortex.label -aseg ../mri/aseg.presurf.mgz ${subj} ${hemis} ../surf/${hemis}.sphere.reg ${freesurfer_path}/average/${hemis}.CDaparc.atlas.acfb40.noaparc.i12.2016-08-02.gcs ../label/${hemis}.aparc.a2009s.annot 

######## Cortical Parc 3
cd ${SUBJECTS_DIR}/${subj}/mri
mris_ca_label -l ../label/${hemis}.cortex.label -aseg ../mri/aseg.presurf.mgz ${subj} ${hemis} ../surf/${hemis}.sphere.reg ${freesurfer_path}/average/${hemis}.DKTaparc.atlas.acfb40.noaparc.i12.2016-08-02.gcs ../label/${hemis}.aparc.DKTatlas.annot 

ln -sf ${hemis}.sphere.reg ${hemis}.fsaverage.sphere.reg 

SUBJECTS_DIR=${working_dir}

##### Cortical Parc Schaefer atlas: 7 and 17 networks
cd ${SUBJECTS_DIR}/${subj}/mri
mri_surf2surf --hemi ${hemis} \
  --srcsubject fsaverage \
  --trgsubject ${subj} \
  --sval-annot ${external_atlases_path}/schaefer/${hemis}.Schaefer2018_400Parcels_17Networks_order.annot \
  --tval ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.Schaefer2018_400Parcels_17Networks.annot

##### Economo-Koskinos atlas
cd ${SUBJECTS_DIR}/${subj}/mri
mris_ca_label -t ${external_atlases_path}/economo/${hemis}.colortable.txt ${subj} ${hemis} ../surf/${hemis}.sphere.reg ${external_atlases_path}/economo/${hemis}.economo.gcs \
${SUBJECTS_DIR}/${subj}/label/${hemis}.economo.annot

##### Glasser atlas
cd ${SUBJECTS_DIR}/${subj}/mri
mri_surf2surf --hemi ${hemis} \
  --srcsubject fsaverage \
  --trgsubject ${subj} \
  --sval-annot ${external_atlases_path}/glasser/${hemis}.HCP-MMP1.annot \
  --tval ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.HCP-MMP1.glasser.annot

SUBJECTS_DIR=${working_dir}

######## dummy left hemis needed for stats computation
cp ${SUBJECTS_DIR}/${subj}/surf/${hemis}.white ${SUBJECTS_DIR}/${subj}/surf/${hemis_other}.white
cp ${SUBJECTS_DIR}/${subj}/surf/${hemis}.pial ${SUBJECTS_DIR}/${subj}/surf/${hemis_other}.pial
cp ${SUBJECTS_DIR}/${subj}/surf/${hemis}.orig.nofix ${SUBJECTS_DIR}/${subj}/surf/${hemis_other}.orig.nofix
cp ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label ${SUBJECTS_DIR}/${subj}/label/${hemis_other}.cortex.label
cp ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.annot ${SUBJECTS_DIR}/${subj}/label/${hemis_other}.aparc.annot 
cp ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.DKTatlas.annot ${SUBJECTS_DIR}/${subj}/label/${hemis_other}.aparc.DKTatlas.annot
cp ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.a2009s.annot ${SUBJECTS_DIR}/${subj}/label/${hemis_other}.aparc.a2009s.annot

pctsurfcon --s ${subj} --${hemis}-only

mri_brainvol_stats --subject ${subj}

######## AParc-to-ASeg aparc
cd ${SUBJECTS_DIR}/${subj}/mri
mri_surf2volseg --o aparc+aseg.mgz --label-cortex --i aseg.mgz --threads ${num_threads} \
--lh-annot ${SUBJECTS_DIR}/${subj}/label/lh.aparc.annot 1000 \
--lh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/lh.cortex.label \
--lh-white ${SUBJECTS_DIR}/${subj}/surf/lh.white \
--lh-pial ${SUBJECTS_DIR}/${subj}/surf/lh.pial \
--rh-annot ${SUBJECTS_DIR}/${subj}/label/rh.aparc.annot 2000 \
--rh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/rh.cortex.label \
--rh-white ${SUBJECTS_DIR}/${subj}/surf/rh.white \
--rh-pial ${SUBJECTS_DIR}/${subj}/surf/rh.pial

######## AParc-to-ASeg aparc.a2009s
cd ${SUBJECTS_DIR}/${subj}/mri
mri_surf2volseg --o aparc.a2009s+aseg.mgz \
--label-cortex --i aseg.mgz --threads ${num_threads} \
--lh-annot ${SUBJECTS_DIR}/${subj}/label/lh.aparc.a2009s.annot 11100 \
--lh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/lh.cortex.label \
--lh-white ${SUBJECTS_DIR}/${subj}/surf/lh.white \
--lh-pial ${SUBJECTS_DIR}/${subj}/surf/lh.pial \
--rh-annot ${SUBJECTS_DIR}/${subj}/label/rh.aparc.a2009s.annot 12100 \
--rh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/rh.cortex.label \
--rh-white ${SUBJECTS_DIR}/${subj}/surf/rh.white \
--rh-pial ${SUBJECTS_DIR}/${subj}/surf/rh.pial

######## AParc-to-ASeg aparc.DKTatlas
cd ${SUBJECTS_DIR}/${subj}/mri
mri_surf2volseg --o aparc.DKTatlas+aseg.mgz \
--label-cortex --i aseg.mgz --threads ${num_threads} \
--lh-annot ${SUBJECTS_DIR}/${subj}/label/lh.aparc.DKTatlas.annot 1000 \
--lh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/lh.cortex.label \
--lh-white ${SUBJECTS_DIR}/${subj}/surf/lh.white \
--lh-pial ${SUBJECTS_DIR}/${subj}/surf/lh.pial \
--rh-annot ${SUBJECTS_DIR}/${subj}/label/rh.aparc.DKTatlas.annot 2000 \
--rh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/rh.cortex.label \
--rh-white ${SUBJECTS_DIR}/${subj}/surf/rh.white \
--rh-pial ${SUBJECTS_DIR}/${subj}/surf/rh.pial

######## WMParc
cd ${SUBJECTS_DIR}/${subj}/mri
mri_surf2volseg --o wmparc.mgz \
--label-wm --i aparc+aseg.mgz --threads ${num_threads} \
--lh-annot ${SUBJECTS_DIR}/${subj}/label/lh.aparc.annot 3000 \
--lh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/lh.cortex.label \
--lh-white ${SUBJECTS_DIR}/${subj}/surf/lh.white \
--lh-pial ${SUBJECTS_DIR}/${subj}/surf/lh.pial \
--rh-annot ${SUBJECTS_DIR}/${subj}/label/rh.aparc.annot 4000 \
--rh-cortex-mask ${SUBJECTS_DIR}/${subj}/label/rh.cortex.label \
--rh-white ${SUBJECTS_DIR}/${subj}/surf/rh.white \
--rh-pial ${SUBJECTS_DIR}/${subj}/surf/rh.pial

cd ${SUBJECTS_DIR}/${subj}
mri_segstats --seg mri/wmparc.mgz \
--sum stats/wmparc.stats --pv mri/norm.mgz \
--excludeid 0 --brainmask mri/brainmask.mgz --in mri/norm.mgz \
--in-intensity-name norm --in-intensity-units MR \
--subject ${subj} \
--surf-wm-vol --ctab ${freesurfer_path}/WMParcStatsLUT.txt --etiv

######## Parcellation Stats
mris_anatomical_stats -th3 -mgz \
-cortex ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label \
-f ${SUBJECTS_DIR}/${subj}/stats/${hemis}.aparc.stats \
-b -a ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.annot \
-c ${SUBJECTS_DIR}/${subj}/label/aparc.annot.ctab ${subj} ${hemis} white

mri_brainvol_stats --subject ${subj}

mris_anatomical_stats -th3 -mgz \
-cortex ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label \
-f ${SUBJECTS_DIR}/${subj}/stats/${hemis}.aparc.pial.stats \
-b -a ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.annot \
-c ${SUBJECTS_DIR}/${subj}/label/aparc.annot.ctab ${subj} ${hemis} pial

######## Parcellation Stats 2
mris_anatomical_stats -th3 -mgz \
-cortex ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label \
-f ${SUBJECTS_DIR}/${subj}/stats/${hemis}.aparc.a2009s.stats \
-b -a ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.a2009s.annot \
-c ${SUBJECTS_DIR}/${subj}/label/aparc.annot.a2009s.ctab ${subj} ${hemis} white

######## Parcellation Stats 3
mris_anatomical_stats -th3 -mgz \
-cortex ${SUBJECTS_DIR}/${subj}/label/${hemis}.cortex.label \
-f ${SUBJECTS_DIR}/${subj}/stats/${hemis}.aparc.DKTatlas.stats \
-b -a ${SUBJECTS_DIR}/${subj}/label/${hemis}.aparc.DKTatlas.annot \
-c ${SUBJECTS_DIR}/${subj}/label/aparc.annot.DKTatlas.ctab ${subj} ${hemis} white

######## ASeg Stats
mri_segstats --seg ${SUBJECTS_DIR}/${subj}/mri/aseg.mgz \
--sum ${SUBJECTS_DIR}/${subj}/stats/aseg.stats --pv ${SUBJECTS_DIR}/${subj}/mri/norm.mgz \
--empty --brainmask ${SUBJECTS_DIR}/${subj}/mri/brainmask.mgz --brain-vol-from-seg \
--excludeid 0 --excl-ctxgmwm --supratent --subcortgray \
--in ${SUBJECTS_DIR}/${subj}/mri/norm.mgz --in-intensity-name norm --in-intensity-units MR \
--etiv --surf-wm-vol --surf-ctx-vol --totalgray --euler \
--ctab ${freesurfer_path}/ASegStatsLUT.txt \
--subject ${subj}

duration=$(( SECONDS - start ))
echo "total time for this subject:" $duration
done