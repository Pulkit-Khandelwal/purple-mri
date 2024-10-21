# Setting-up the Box developer account to downlaod files and folders in Python
### Author: Pulkit Khandelwal


##### Locate the Box Developer console on the bottom left
<div align="center">
         <img src="https://github.com/Pulkit-Khandelwal/picsl-brain-ex-vivo/blob/main/files/box-dev-1.png" style="width:25%; height:10%">
      </a>
</div>

##### Click on create new app
<div align="center">
         <img src="https://github.com/Pulkit-Khandelwal/picsl-brain-ex-vivo/blob/main/files/box-dev-2-1.png" style="width:100%; height:100%">
      </a>
</div>

##### Enter a name for your app
<div align="center">
         <img src="https://github.com/Pulkit-Khandelwal/picsl-brain-ex-vivo/blob/main/files/box-dev-2.png" style="width:50%; height:40%">
      </a>
</div>


##### Have the following settings and then create the app
<div align="center">
         <img src="https://github.com/Pulkit-Khandelwal/picsl-brain-ex-vivo/blob/main/files/box-dev-3.png" style="width:50%; height:40%">
      </a>
</div>

##### Now, click on configuration and generate a developer token. You will need the Developer Token, Client ID and Client Secret later
<div align="center">
         <img src="https://github.com/Pulkit-Khandelwal/picsl-brain-ex-vivo/blob/main/files/box-dev-4.png" style="width:50%; height:40%">
      </a>
</div>


###### Let's write some simple Python code for locating and downloading your files and folders to a specific folder

You will need to download ```boxsdk``` library from [here](https://github.com/box/box-python-sdk) via ```pip3 install boxsdk```. You will need the ```Developer Token, Client ID and Client Secret``` from above. You might have to refresh the ```Get Developer Token``` again in future if it expires.


```
# Imports and authentication
import os
from boxsdk import OAuth2, Client
import pathlib

auth = OAuth2(
    client_id='GET_FROM_THE_DEV_ACCOUNT',
    client_secret='GET_FROM_THE_DEV_ACCOUNT',
    access_token='GET_FROM_THE_DEV_ACCOUNT',
)
client = Client(auth)

user = client.user().get()
print(f'The current user ID is {user.id}')
```

```
# Try to locate the files and folders in your box folder and get the corresponding file ID
# Folder 111442091060 is named "Hemisphere_segmentation" in Pulkit's box account (might be different for you)
# Folder 112217518064 is named "subjects" which I need in Pulkit's box account (might be different for you)

root_folder = client.root_folder().get()
items = root_folder.get_items()
for item in items:
    print('{0} {1} is named "{2}"'.format(item.type.capitalize(), item.id, item.name))
```

```
# The foler where I want to save the files from Box in my local directory
parent_dir = '/data/pulkit/exvivo_data_revised'

# Folder iD, as identified above, where my data lives
items = client.folder(folder_id='112217518064').get_items()

# Now, I write custom code to download files
# Here, for example. I want to loop through the INDD folders on Box and then download the files ending in _reslice.nii.gz or _cortexdots_final.nii.gz for each INDD subject

for item in items:
    print(f'{item.type.capitalize()} {item.id} is named "{item.name}"')
    current_subject_id = item.id
    current_subject_name = item.name
    path = os.path.join(parent_dir, current_subject_name)
    os.mkdir(path)

    items_in_subj_folder = client.folder(folder_id=current_subject_id).get_items()
    for itm_subj in items_in_subj_folder:
        print(f'{itm_subj.type.capitalize()} {itm_subj.id} is named "{itm_subj.name}"')

        if itm_subj.name.endswith('_ciss_reslice.nii.gz') or itm_subj.name.endswith('_reslice.nii.gz') or itm_subj.name.endswith('_cortexdots_final.nii.gz'):
            print("Downloading file...... ", itm_subj.name)
            with open(os.path.join(path, itm_subj.name), 'wb') as open_file:
                client.file(itm_subj.id).download_to(open_file)
                open_file.close()
```

##### What if I have a shared link to the data?
```
web_link_url = 'https://upenn.app.box.com/s/BLAH_BLAH_BLAH'

shared_folder = client.get_shared_item(web_link_url,'' )
print(f"Shared Folder: {shared_folder.id}: {shared_folder.name}")

items = shared_folder.get_items()
for item in items:
    print(f"{item.type}\t{item.id}\t{item.name}")
    
    with open(os.path.join(parent_dir, item.name), 'wb') as open_file:
        item.download_to(open_file)
        open_file.close()
```

##### How to uplaod files from a local folder to a specific folder on box?
```
root_folder = client.root_folder().get()
items = root_folder.get_items()
for item in items:
    print('{0} {1} is named "{2}"'.format(item.type.capitalize(), item.id, item.name))
    current_subject_id = item.id
    if current_subject_id == 'FOLDER_ID_YOU_WANT':
        items_in_subj_folder = client.folder(folder_id=current_subject_id).get_items()
        for item in items_in_subj_folder:
            print('{0} {1} is named "{2}"'.format(item.type.capitalize(), item.id, item.name))

# Once you have the ID of the folder you want to upload the files to, do this:
local_folder_path='/direectory/where/all/files/are/stored'
local_folder = pathlib.Path(local_folder_path)
for file_path in local_folder.iterdir():
    print(file_path)
    file_name = os.path.basename(file_path)
    client.folder(FOLDER_ID_YOU_WANT).upload(file_path, file_name)
```

### That's it! Let me know of any questions :)
