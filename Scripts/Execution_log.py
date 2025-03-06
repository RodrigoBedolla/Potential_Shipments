# Author: Rodrigo Bedolla Fuerte
# Department: Order management
# Bedolla Fuerte, R. (Dec 15, 2021). Execution_Log (version No 1.1 | last update(Dec 15, 2021)). Cd. Juarez: Foxconn eCMMS S.A. DE C.V. V1.1

from My_Book import txt_array_2d, format_date, share_path
import pandas as pd
from datetime import datetime
import time

def get_time():

    time_stamp = datetime.strptime(format_date(1),'%m-%d-%Y %H:%M:%S')

    return time_stamp

def Execution_log(start, flag, error):


    current_time = datetime.strptime(format_date(1),'%m-%d-%Y %H:%M:%S')
    elapsed_time = current_time - start
    td_mins = round(elapsed_time.total_seconds() / 60,3)

    execution_log = pd.read_excel(share_path()+'\Execution_log\Execution_log.xlsx')

    if flag == 'SUCCSESS':

        #execution_log = execution_log.append({'ID' : txt_array_2d('Description_of _RPAs_releases.txt')[6][0], 'SCRIPT NAME' : txt_array_2d('Description_of _RPAs_releases.txt')[6][1],
        #                                    'RELEASE DATE' : txt_array_2d('Description_of _RPAs_releases.txt')[6][2], 'START' : start,'FINISH' : current_time,
        #                                    'EXECUTION TIME' : td_mins,'PASS/FAIL' : flag,'FAILURE DESCRIPTION' : ''}, ignore_index=True)

        execution_log = pd.concat([execution_log, pd.DataFrame.from_records([{'ID' : txt_array_2d('Description_of _RPAs_releases.txt')[6][0], 'SCRIPT NAME' : txt_array_2d('Description_of _RPAs_releases.txt')[6][1],
                                            'RELEASE DATE' : txt_array_2d('Description_of _RPAs_releases.txt')[6][2], 'START' : start,'FINISH' : current_time,
                                            'EXECUTION TIME' : td_mins,'PASS/FAIL' : flag,'FAILURE DESCRIPTION' : ''}])], ignore_index=True)

    else:

        #execution_log = execution_log.append({'ID' : txt_array_2d('Description_of _RPAs_releases.txt')[6][0], 'SCRIPT NAME' : txt_array_2d('Description_of _RPAs_releases.txt')[6][1],
        #                                    'RELEASE DATE' : txt_array_2d('Description_of _RPAs_releases.txt')[6][2], 'START' : start, 'FINISH' : current_time,
        #                                    'EXECUTION TIME' : td_mins,'PASS/FAIL' : flag,'FAILURE DESCRIPTION' : error}, ignore_index=True)

        execution_log = pd.concat([execution_log, pd.DataFrame.from_records([{'ID' : txt_array_2d('Description_of _RPAs_releases.txt')[6][0], 'SCRIPT NAME' : txt_array_2d('Description_of _RPAs_releases.txt')[6][1],
                                            'RELEASE DATE' : txt_array_2d('Description_of _RPAs_releases.txt')[6][2], 'START' : start, 'FINISH' : current_time,
                                            'EXECUTION TIME' : td_mins,'PASS/FAIL' : flag,'FAILURE DESCRIPTION' : error}])], ignore_index=True)

    # Number of retries and delay in seconds
    retries = 5
    delay = 10

    for i in range(retries):
        try:
            execution_log.to_excel(share_path()+'\Execution_log\Execution_log.xlsx', index=False)
            break  # Exit loop if successful
        except PermissionError:
            print(f"Retrying in {delay} seconds...[{i + 1} of {retries}]")
            time.sleep(delay)  # Wait before retrying


    return_df = execution_log.iloc[-1:]

    return return_df