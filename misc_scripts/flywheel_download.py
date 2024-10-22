import flywheel
import pandas as pd

###### get your unqiue client ID from flywheel settings. Replace "PLACE_IT_HERE" in the next line:
fw = flywheel.Client('upenn.flywheel.io:PLACE_IT_HERE')
user = fw.get_current_user()

# csv file which has multiple acquisition IDs for each subject
filename = 'filename.csv'
acq_sheet = pd.read_csv(filename)

# we iterate over each row and download all the associated files
# see the code below and you can also donwload more files
# I've downloaded only the nifti files
# locally we will QC and select the files we like
for index, row in acq_sheet.iterrows():
    subject_id = row['INDDID']
    acquisition_id = row['FlywheelAcquisitionInternalID']
    session_date = row['FlywheelSessionDate']
    print(subject_id, acquisition_id)
    acquisition = fw.get(acquisition_id)
    for counter, f in enumerate(acquisition.files):
        if f.type == 'nifti':
            check_this = f.name
            session_date = str(session_date)
            session_date = session_date.replace('/', '--')            
            acquisition.download_file(check_this, '/path/to/download' +  'INDD_' + str(int(subject_id)) + '_count_' + str(counter) + '_acq_' + str(acquisition_id) + '_sess_dt_' + session_date + '_imageName_' + check_this)
