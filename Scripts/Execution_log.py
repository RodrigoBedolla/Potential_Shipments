# Author: Rodrigo Bedolla Fuerte
# Department: Order management
# Bedolla Fuerte, R. (Dec 15, 2021). Execution_Log (version No 2.0 | last update(May, 2025)). Cd. Juarez: Foxconn eCMMS S.A. DE C.V. V2.0
 
from My_Book import txt_array_2d, sql_parameters,format_date
from datetime import datetime
import pyodbc
import pandas as pd
 
def get_time():
 
    time_stamp = datetime.now()
 
    return time_stamp
 
def rpa_information(start, flag, error,manual_ex):
 
    # Get release info only once
    release_info = txt_array_2d('RPAs_releases.txt')[6]
 
    rpa_execution_data = {
        'rpa_id': release_info[0],
        'script_name': release_info[1],
        'release_date': release_info[2],
        'start_date': start,
        'finish_date': datetime.now(),
        'execution_status': flag,
        'failure_description': '' if flag == 'SUCCESS' else str(error),
        'execution_type': 'X' if manual_ex.upper() == 'X' else '-'
    }
    
    return rpa_execution_data
 
def Execution_log(start, flag, error,manual_ex):

    current_time = datetime.strptime(format_date(1),'%m-%d-%Y %H:%M:%S')
    elapsed_time = current_time - start
 
    conn = pyodbc.connect(sql_parameters())
    cursor = conn.cursor()
 
    insert_query = """
        INSERT INTO FMX_OM_RPA_execution_log 
        (rpa_id, script_name, release_date, start_date, finish_date, execution_status, failure_description,execution_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    rpa_execution_data = rpa_information(start, flag, error,manual_ex)
    
    df_log = pd.DataFrame([rpa_execution_data])
    df_log = df_log.drop(columns={'rpa_id','release_date','execution_type'})
    df_log = df_log.rename(columns={'script_name':'SCRIPT NAME','start_date':'START','finish_date':'FINISH','execution_status':'PASS/FAIL','failure_description':'FAILURE DESCRIPTION'})
    df_log['EXECUTION TIME'] =  elapsed_time
    
    cursor.execute(
        insert_query,
        rpa_execution_data['rpa_id'],
        rpa_execution_data['script_name'],
        rpa_execution_data['release_date'],
        rpa_execution_data['start_date'],
        rpa_execution_data['finish_date'],
        rpa_execution_data['execution_status'],
        rpa_execution_data['failure_description'],
        rpa_execution_data['execution_type']
    )
   
    conn.commit()
    cursor.close()
    conn.close()  

    return df_log
 
#Execution_log(get_time(), 'SUCCSESS', '')