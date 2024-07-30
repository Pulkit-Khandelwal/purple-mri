import os
from os.path import join as pjoin
from surfer import Brain

subjects = []

for subject_id in subjects:
    print(subject_id)
    hemi = 'rh'
    surf = 'pial'
    subjects_dir = ''

    brain = Brain(subject_id, hemi, surf, views=['med'],
                cortex="bone", background="ivory", subjects_dir=subjects_dir)

    annot_path = pjoin(subjects_dir, subject_id, "label", "rh.aparc.annot")
    brain.add_annotation(annot_path, hemi='rh', borders=False, alpha=.75)
    brain.save_image("%s.png" % subject_id)