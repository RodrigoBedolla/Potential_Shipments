from My_Book import *
import pandas as pd
import numpy as np
from Hold_tool_report import hold_tool
from Email import send_email

def case_assignnment(df_master,prev_master):

    df_master['WORK ORDER'] = df_master['WORK ORDER'].astype(str).str.replace("\.0$", "",regex = True)
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

    return df_master

def Shippeable():

    file = path()+'\Files\\Shippeable_'+format_date(3)+'(CA).xlsx'

    previous_master_share()
    prev_master = pd.read_excel(path()+'\Files\\Previous_Master.xlsx')
    prev_master['WORK ORDER'] = prev_master['WORK ORDER'].astype(str).str.replace("\.0$", "",regex = True)
    prev_master.fillna('NA',inplace = True)

    hold_tool()

    master_summary = pd.read_excel(share_path()+'\Master Template\\master_base.xlsx')
    master_summary = complexities(master_summary)
    master_summary = primary_key_by_so(master_summary)
    master_summary = dailys(master_summary)
    master_summary = master_summary[txt_array_local('Master_columns.txt')]
    master_summary['WORK ORDER'] = master_summary['WORK ORDER'].astype(str).str.replace("\.0$", "",regex=True)
    master_summary = primary_key(master_summary)
    master_summary['ITEM RDD'] = pd.to_datetime(master_summary['ITEM RDD'])
    master_summary.drop(columns=['ITEM'],inplace = True)

    #HPE RESTRICTIONS and HOLD TOOL(INTERNAL HOLDS) from fill_holds function
    master_summary = fill_holds(master_summary)

    #from SHIPSTATUS get SHIP TYPE,SHIP STATUS,GENERAL STATUS,PRD STATUS,PRD BUCKET
    ship_status = pd.read_excel(share_path()+'\OM_RPAs_Files\Backup\SHIP_STATUS\\SHIP_STATUS.xlsx',sheet_name = 'SHIP STATUS',usecols = txt_array_local('Ship_columns.txt'))

    master_summary = master_summary.merge(ship_status, on = 'PRIMARY KEY', how = 'left').drop_duplicates().reset_index(drop = True)
    master_summary.fillna('NA',inplace=True)
    master_summary['ITEM'] = master_summary['ITEM'].astype(str).str.replace("\.0$", "",regex=True)
    master_summary['PO + ITEM'] = master_summary['PO'].astype(str) + master_summary['ITEM']
    master_summary = master_summary[txt_array_local('Summary_columns.txt')]

    master_summary = rdd_validation(master_summary)
    master_summary.fillna('NA',inplace=True)

    master_summary['SHIPPEABLE'] = np.where((master_summary['GENERAL STATUS'] == 'READY TO SHIP') & (master_summary['COMPLEXITY CATEGORY'] != 'BTS REMAN') & (master_summary['ITEM RDD'].dt.strftime('%Y-%m-%d') <= current_date().strftime('%Y-%m-%d')),
                        (np.where(master_summary['HPE RESTRICTIONS'] != 'NA','FG - HPE RESTRICTED',(np.where((master_summary['INTERNAL HOLDS'] == 'NA') | ((master_summary['INTERNAL HOLDS'].str.contains('GLOBAL TRADE')) 
                        & (master_summary['INTERNAL HOLDS'].apply(len)<170)),'READY TO SHIP',(np.where(master_summary['INTERNAL HOLDS'].str.contains('WORKORDER'),'FG - HOLD BY WO',
                        (np.where(master_summary['INTERNAL HOLDS'].str.contains('HOLD_SKU'),'FG - HOLD BY SKU',(np.where(master_summary['INTERNAL HOLDS'].str.contains('HOLD_SSN'),'FG - HOLD BY SSN',
                        (np.where(master_summary['INTERNAL HOLDS'].str.contains('HOLD_PARTNO'),'FG - HOLD BY PARTNO','NA')))))))))))),
                        (np.where(master_summary['GENERAL STATUS'].str.contains('SHIPPED '+str(format_date(4))),'SHIPPED '+str(format_date(4)),'NA')))

    #--------------UPDATE DN QTY WITH SHIP STATUS PARTIAL SHIPMENTS---------------
    
    df_partial_ship = pd.read_excel(share_path()+'\OM_RPAs_Files\\Backup\\SHIP_STATUS\\SHIP_STATUS.xlsx',sheet_name='SHIP STATUS')
    df_partial_ship.fillna('NA',inplace = True)
    df_partial_ship['PGI DATE'] = df_partial_ship['PGI DATE'].astype(str)
    df_partial_ship = df_partial_ship[['WORK ORDER','DN QTY']][(df_partial_ship['PARTIAL SHIPMENTS'].str.contains('X') == True) & (df_partial_ship['PGI DATE'].str.contains(str(current_date())))].reset_index(drop = True)
    
    summary_pivot = pd.pivot_table(df_partial_ship,index = ['WORK ORDER'],values=['DN QTY'],aggfunc='sum',margins_name = 'DN QTY')
    summary_pivot = pd.DataFrame(summary_pivot.to_records()).reset_index(drop = True)
    summary_pivot['WORK ORDER'] = summary_pivot['WORK ORDER'].astype(str).str.replace("\.0$", "",regex=True)
    
    if summary_pivot.empty == False:

        master_summary = master_summary.merge(summary_pivot,on='WORK ORDER',how ='left')
        master_summary.fillna('NA',inplace = True)
        master_summary['DN QTY'] = np.where((master_summary['DN QTY'] != 'NA') & (master_summary['GENERAL STATUS'] =='READY TO SHIP'),master_summary['OPEN QTY'],master_summary['DN QTY'])
        master_summary['SHIPPEABLE'] = np.where((master_summary['SHIPPEABLE'] != 'READY TO SHIP') & (master_summary['DN QTY'] != 'NA'),'READY TO SHIP',master_summary['SHIPPEABLE'])
        master_summary['SHIPPEABLE'] = np.where(((master_summary['DN QTY'] != 'NA') & (master_summary['GENERAL STATUS'] != 'READY TO SHIP') & (master_summary['GENERAL STATUS'] != 'SHIPPED '+format_date(4))),'PARTIAL SHIPMENT',master_summary['SHIPPEABLE'])

        master_summary['DN QTY'] = np.where((master_summary['DN QTY'] == 'NA'),master_summary['OPEN QTY'],master_summary['DN QTY'])
        master_summary.drop(columns=['OPEN QTY'],inplace = True)
        master_summary.rename(columns = {'DN QTY':'OPEN QTY'},inplace = True)

    po_holds = master_summary['PO + ITEM'][master_summary['SHIPPEABLE'].str.contains('HOLD')].to_numpy()
    grouped = master_summary.groupby('PO')
    master_summary_sc = pd.DataFrame()

    for name,group in grouped:
        
        subgroup = group[group['SHIPPEABLE'].str.contains('READY') & (group['SHIP TYPE'] == 'SC')]

        if len(subgroup) == len(group):
            master_summary_sc = pd.concat([master_summary_sc,subgroup]).reset_index(drop = True)
        
    master_shippped = master_summary[master_summary['SHIPPEABLE'].str.contains('SHIPPED|PARTIAL') | 
                (master_summary['SHIPPEABLE'].str.contains('READY') & (master_summary['SHIP TYPE'] == 'SP'))]
    master_summary_sc = pd.concat([master_summary_sc,master_shippped]).reset_index(drop = True)
  
    master_summary_sc = master_summary_sc.loc[~master_summary_sc['PO + ITEM'].isin(po_holds)]
    
    ship_pivot = pd.pivot_table(master_summary_sc,index = ['COMPLEXITY CATEGORY'],values = ['OPEN QTY'],aggfunc = 'sum',margins_name = 'SHIPPEABLE')
    ship_pivot = pd.DataFrame(ship_pivot.to_records())
    ship_pivot['OPEN QTY'] = ship_pivot['OPEN QTY'].astype(str).str.replace("\.0$", "",regex = True)
    ship_pivot.rename(columns = {'COMPLEXITY CATEGORY': 'COMPLEXITY','OPEN QTY':'QTY'}, inplace = True)

    mail_format = master_summary_sc[['PO','SO','OPEN QTY','WORK ORDER','SHIPPEABLE','COMPLEXITY','COMPLEXITY CATEGORY']]
    df_case_assign = case_assignnment(master_summary,prev_master)
                    
    writer = pd.ExcelWriter(file)
    mail_format.to_excel(writer,'SHIPPEABLE', index = False)
    ship_pivot.to_excel(writer,'SUMMARY', index = False)
    master_summary.to_excel(writer,'RAWDATA',index = False)
    df_case_assign.to_excel(writer,'CASE ASSIGNMENT',index = False)
    writer.save()

    delete_local_files()

Shippeable()