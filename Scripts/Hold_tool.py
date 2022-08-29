import subprocess
import json

from numpy import int64
from My_Book import upgrade_column, api_request, path, datetime_convertion
from datetime import datetime
import pandas as pd

today = datetime.now().strftime('%Y-%m-%d')

def po_validation(df):

    po_list = df['ID'].drop_duplicates()

    iteration = 1

    for i in po_list:

        final_df = api_request('PO',i,'860Codes','SHORT','')

        if iteration == 1:

            priority_codes = final_df

        else:
            
            frames = [priority_codes,final_df]
            priority_codes = pd.concat(frames)

        iteration += 1
    
    priority_codes['PO DATE'] = datetime_convertion(priority_codes,'PO DATE')
    priority_codes['CONTROL NO']  = priority_codes['CONTROL NO'].astype(int64)
    
    return priority_codes
    

def Hold_type_column(df_hold):

    df_hold['Hold DateTime'] = pd.to_datetime(df_hold['Hold DateTime'])

    for i in range(0,len(df_hold.index)):

        type_col = df_hold['Type'][i]
        hold_date = df_hold['Hold DateTime'][i]
        hold_des = df_hold['Hold Description'][i] 
        hold_reason = df_hold['Hold Reason'][i]
        station = df_hold['Station'][i]
        req_name = df_hold['Request Name'][i]
        depto = df_hold['Request Depto'][i]
        original_id = df_hold['ORIGINAL ID'][i]

        if 'EDI860_BB' in type_col:

            df_hold.loc[i,'HOLD TYPE'] = 'PREBUILD'

        elif 'EDI860_DI' in type_col:

            df_hold.loc[i,'HOLD TYPE'] = 'DELETE ITEM'

        elif 'SSN' in type_col:

            if len(hold_des) == 0 and len(hold_reason) == 0:
                
                df_hold.loc[i,'HOLD TYPE'] = 'Type: '+type_col+'| Hold Date: '+hold_date.strftime('%m/%d/%Y %H:%M:%S')+' | NO COMMENTS | Station: '+str(station)+' | Request Name: '+str(req_name)+' | Department: '+str(depto)+' | Original ID: '+str(original_id)
            
            else:

                df_hold.loc[i,'HOLD TYPE'] = 'Type: '+type_col+' | Hold Date: '+hold_date.strftime('%m/%d/%Y %H:%M:%S')+' | Hold Description: '+str(hold_des)+' | Hold Reason: '+str(hold_reason)+' | Station: '+str(station)+' | Request Name: '+str(req_name)+' | Department: '+str(depto)+' | Original ID: '+str(original_id)
        else:

            df_hold.loc[i,'HOLD TYPE'] = 'Type: '+type_col+' | Hold Date: '+hold_date.strftime('%m/%d/%Y %H:%M:%S')+' | Hold Description: '+str(hold_des)+' | Hold Reason: '+str(hold_reason)+' | Station: '+str(station)+' | Request Name: '+str(req_name)+' | Department: '+str(depto)


    df_hold_consol = df_hold.sort_values(by=['ID','Hold DateTime'], ascending=False).reset_index(drop=True)
    df_hold_consol = df_hold_consol[['ID','HOLD TYPE']].groupby('ID')['HOLD TYPE'].apply('\n\n'.join).reset_index()

    df_hold = upgrade_column(df_hold,df_hold_consol,'ID','HOLD TYPE',19)
    
    return df_hold