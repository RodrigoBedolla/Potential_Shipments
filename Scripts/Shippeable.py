from My_Book import *
import pandas as pd
import numpy as np
from Hold_tool_report import hold_tool
from Email import send_email
from Case_assignment import case_assignnment

def Shippeable():

    file = path()+'\Files\\Shippeable_'+format_date(3)+'.xlsx'

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
                    
    writer = pd.ExcelWriter(file)
    mail_format.to_excel(writer,'SHIPPEABLE', index = False)
    ship_pivot.to_excel(writer,'SUMMARY', index = False)
    master_summary.to_excel(writer,'RAWDATA',index = False)
    writer.save()

    master_summary.to_excel(path()+'\Files\\RAWDATA.xlsx',  index = False)

    send_email('ecmms.OM@FII-NA.com','','Shippeable '+format_date(4),ship_pivot)
    delete_local_files()
    case_assignnment(master_summary,prev_master)
    

#Shippeable()