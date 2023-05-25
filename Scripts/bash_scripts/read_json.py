import pandas as pd
import json
from pathlib import Path

def path(): #Current project path delimited by '\'
    path = str(Path(__file__).parent.parent)
    return path

#next steps....
column_list = ['JDOName','token','client','windowsAuthToken','CyGtkn','photoRef']
with open(path()+'\\bash_scripts\\auth_result.json', 'r') as f:  
    data = json.load(f)

#JDOName=HPE&token=40e1ffaa-2f81-4f4a-981d-f86d0fc41969&client=HPE&windowsAuthToken=
login_json = pd.DataFrame(data={'JDOName':['HPE'],'client':['HPE'],'windowsAuthToken':['']})

data = pd.json_normalize(data)

login_json = pd.concat([login_json,data], axis=1)
login_json = login_json[column_list].reset_index(drop=True)

data_raw = ''

for i in column_list:
    
    if i == 'photoRef':
        data_raw = data_raw + i + '=' + login_json[i][0].replace('=','%3D').replace('/',f'%2F').replace('+',f'%2B')
    else:
        data_raw = data_raw + i + '=' + login_json[i][0] + '&'

file = open("data_raw.txt", "w")
a = file.write(data_raw)
file.close()
