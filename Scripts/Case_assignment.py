from My_Book import *
import pandas as pd
import numpy as np

def case_assignnment(df_master,prev_master):

    df_master['WORK ORDER'] = df_master['WORK ORDER'].astype(str).str.replace(r'\.0$', "",regex = True)
    df_master = df_master.merge(prev_master[['WORK ORDER','SCHEDULED DATE','STATUS']],on = 'WORK ORDER', how = 'left')
    df_master.fillna('NA',inplace = True)
    df_master = df_master[(df_master['ITEM'] != 'NA')].reset_index(drop = True)

    df_master['PRODUCTION BUCKET'] = np.where(df_master['PRODUCTION STATUS'] == 'PLANNED','KITTING',df_master['PRODUCTION BUCKET'])

    df_master['BUCKET'] = np.where((df_master['PRODUCTION BUCKET'].str.contains('ASSEMBLY|TESTING|QA') == True),'WIP',
                            (np.where((df_master['PRODUCTION BUCKET'].str.contains('PACKING|SHIPPING') == True),'PACKING',
                            (np.where((df_master['PRODUCTION BUCKET'].str.contains('KITTING') == True),'KITTING',
                            (np.where((df_master['PRODUCTION BUCKET'].str.contains('COMPLETE WITH CD FLAG') == True),'COMPLETE WITH CD FLAG',
                            (np.where(((df_master['PRODUCTION BUCKET'].str.contains('RELEASED') == True) & (df_master['STATUS'].str.contains('CTB') == True)) | 
                            (df_master['STATUS'].str.contains('CTB') == True),'CTB','NA')))))))))

    cd_flag_array = df_master['PO'][df_master['PRODUCTION BUCKET'].str.contains('CD FLAG') == True].to_numpy()
    df_master_header = df_master.loc[(df_master['PO'].isin(cd_flag_array)) & (df_master['BUCKET'].str.contains('COMPLETE') == True)].reset_index(drop = True)
    df_master_header['CASE'] = 'COMPLETE WITH CD FLAG'
    df_master_nested = df_master.loc[(df_master['PO'].isin(cd_flag_array)) & (df_master['BUCKET'].str.contains('COMPLETE') == False)].reset_index(drop = True)

    #-------------------------SHORT BUCKET-------------------------

    master_tbc = df_master_nested[df_master_nested['SCHEDULED DATE'].astype(str).str.contains('TBC') == True]
    master_tbc['BUCKET'] = np.where(master_tbc['STATUS'] == 'SHORT','SHORT TBC',master_tbc['BUCKET'])

    master_non_tbc = df_master_nested[df_master_nested['SCHEDULED DATE'].astype(str).str.contains('TBC') == False]
    master_non_tbc['SCHEDULED DATE'] = pd.to_datetime(master_non_tbc['SCHEDULED DATE'])

    df_schedule_dt_max = master_non_tbc.sort_values('SCHEDULED DATE', ascending = False).drop_duplicates(subset = 'PO',keep = 'first').reset_index(drop=True)
    master_non_tbc = upgrade_column(master_non_tbc,df_schedule_dt_max,'PO','SCHEDULED DATE',16)

    SOC_date,SAB_date = get_SOC_SAB()

    master_non_tbc['RECOVERY DAYS'] = (master_non_tbc['SCHEDULED DATE'] - current_date()).dt.days
    master_non_tbc = assing_buckets(master_non_tbc,'RECOVERY DAYS','RECOVERY DAYS')

    master_non_tbc['BUCKET'] = np.where((master_non_tbc['BUCKET'].str.contains('NA') == True),(np.where(master_non_tbc['SCHEDULED DATE'].dt.date <= SOC_date,'SHORT SOC',
                        (np.where((master_non_tbc['SCHEDULED DATE'].dt.date > SOC_date) & (master_non_tbc['SCHEDULED DATE'].dt.date <= SAB_date),
                        'SHORT SAB','SHORT ('+master_non_tbc['RECOVERY DAYS']+')')))),master_non_tbc['BUCKET'])
   
    df_master_nested = df_master_nested[0:0]
    df_master_nested = pd.concat([master_non_tbc,master_tbc]).reset_index(drop = True)

    #----------------------ASSIGN CASE-------------------------------------

    grouped = df_master_nested.groupby('PO')
    df_master_nested = df_master_nested[0:0]

    for name,group in grouped:

        group.reset_index(drop = True,inplace = True)

        possible_cases(group,'CTB')
        possible_cases(group,'PACKING')
        possible_cases(group,'WIP')
        possible_cases(group,'KITTING')
        possible_cases(group,'SHORT TBC')

        group['CASE'] = group['BUCKET'] +' - LINKED TO FGI'

        df_master_nested = pd.concat([df_master_nested,group])

    short_master = df_master_nested[['PO','BUCKET']][df_master_nested['BUCKET'].astype(str).str.contains('SHORT') == True].drop_duplicates()
    short_master.rename(columns = {'BUCKET':'SHORT'},inplace = True)
    df_master_nested = df_master_nested.merge(short_master,on='PO',how= 'left')
    df_master_nested.fillna('NA',inplace = True)

    df_master_nested['CASE'] = np.where(((df_master_nested['SHORT'].str.contains('NA') == False) & (df_master_nested['BUCKET'] != df_master_nested['SHORT'])),
                        (df_master_nested['BUCKET']+' - LINKED TO '+ df_master_nested['SHORT']),(df_master_nested['CASE']))

    df_master = pd.concat([df_master_header,df_master_nested]).reset_index(drop=True)
    df_master.drop(columns=['SHORT'],inplace = True)

    df_master = priority_bucket(df_master)
    df_master.to_excel(path()+r'\Files\\Cases_assignment.xlsx',index = False)

#df_master = pd.read_excel(path()+r'\Files\\RAWDATA.xlsx')
#case_assignnment(df_master)
