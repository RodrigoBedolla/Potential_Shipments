from My_Book import *
import pandas as pd
import numpy as np
from Hold_tool_report import hold_tool
from Email import send_email
import shutil
import time
from potential_shipments import *


def case_assignnment(df_master,prev_master):

    df_master['WORK ORDER'] = df_master['WORK ORDER'].astype(str).str.replace("\.0$", "",regex = True)
    df_master = df_master.merge(prev_master[['WORK ORDER','SCHEDULED DATE','STATUS']],on = 'WORK ORDER', how = 'left')
    df_master.fillna('NA',inplace = True)
    df_master = df_master[(df_master['ITEM'] != 'NA') & (df_master['SCHEDULED DATE'] != 'NA')].reset_index(drop = True)

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
    master_non_tbc.to_csv(path()+'\Files\\master_non_tbc.csv',index = False)
    master_non_tbc['SCHEDULED DATE'] = pd.to_datetime(master_non_tbc['SCHEDULED DATE'],errors='coerce')

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
    df_master['CD_FLAG_BUCKET'] = np.where(df_master['FINAL STATUS'].str.contains('SHORT'),'SHORT',df_master['FINAL STATUS'])
    df_master['NET VALUE'] = 0    
    df_master.rename(columns={'CASE':'DETAIL'},inplace=True)

    return df_master

def ship_partial_validation(df):

    df_partial = df[(df['SHIP TYPE'] == 'SP')].reset_index(drop = True)

    grouped_SP = df_partial.groupby('PO + ITEM')
    array_sp = []

    for name,group in grouped_SP:

        subgroup = group['PO'][group['SHIPPABLE'].str.contains('READY')]

        if len(subgroup) != len(group):
            array_sp = array_sp + [name]

    df['SHIPPABLE'] = np.where((df['SHIPPABLE'] == 'READY TO SHIP') & (df['PO + ITEM'].isin(array_sp) & (df['SHIP TYPE'] == 'SP')),'NA',df['SHIPPABLE'])

    return df

def standalone(df):

    df['WORK ORDER'] = df['WORK ORDER'].astype('int64')

    master_base = pd.read_excel(share_path()+'\Master Template\master_base.xlsx')
    df = df.merge(master_base[['WORK ORDER','STANDALONE']],on='WORK ORDER',how='left').drop_duplicates().reset_index(drop=True)

    try:
        signal_855 = pd.read_excel(share_path()+'\OM_RPAs_Files\Backup\\Open\\Open '+format_date(3)+'.xlsx')
    except:
        signal_855 = pd.read_excel(share_path()+'\OM_RPAs_Files\Backup\\Open\\Open '+previous_labor_day().strftime('%m%d%Y')+'.xlsx')
        
    df = df.merge(signal_855[['WORK ORDER','F ACK D']],on='WORK ORDER',how='left').fillna(datetime.datetime.today().date()).drop_duplicates().reset_index(drop=True)

    fmx_holidays=np.array([datetime.datetime.strptime(x,'%m/%d/%Y') for x in txt_array('holidays.txt')], dtype='datetime64[D]')
    df['STFA DELTA'] = np.busday_count(df['F ACK D'].values.astype('datetime64[D]'),np.datetime64(datetime.date.today(), 'D'), weekmask=[1,1,1,1,1,0,0], holidays=fmx_holidays)
    df['STANDALONE'] = np.where((df['COMPLEXITY CATEGORY'].astype(str).str.contains('PPS|BTO')) & ((df['STFA DELTA'] == -4) | (df['STFA DELTA'] == -5)) & (df['STANDALONE'] == 'Y'),'Y','N')

    STFA_restricted = df[df['STANDALONE'] == 'Y'].reset_index(drop=True)
    STFA_restricted['ESD'] = np.where(STFA_restricted['STFA DELTA'] == -4,get_next_business_day(1),get_next_business_day(2))
    STFA_restricted['F ACK D'] = pd.to_datetime(STFA_restricted['F ACK D'])

    df = df[df['STANDALONE'] == 'N'].reset_index(drop=True)
    df.drop(columns={'F ACK D','STFA DELTA','STANDALONE'},inplace=True)

    return df,STFA_restricted

def Shippable_complete():
    
    delete_local_files()    
    shutil.copy(share_path()+'\Master_History\\\Master '+previous_labor_day().strftime('%m%d%Y')+'.xlsx',path()+'\Files\Previous_Master.xlsx')
    
    prev_master = pd.read_excel(path()+'\Files\\Previous_Master.xlsx')
    prev_master['WORK ORDER'] = prev_master['WORK ORDER'].astype(str).str.replace("\.0$", "",regex = True)
    prev_master.fillna('NA',inplace = True)

    try:
        cookie_cygnus()
        hold_tool()
        cyg_logout()
    except:
        pass

    master_summary = pd.read_excel(share_path()+'\Master Template\\master_base.xlsx')
    master_summary = master_summary[master_summary['WO TYPE'] != 'ZJMW'].reset_index(drop=True) #Changed done on 05092024 by shipping; Sebastian Campos

    df_country = master_summary[['WORK ORDER','COUNTRY']]

    rdd_list = master_summary['PO'][master_summary['ITEM RDD'] == '00/00/0000'].drop_duplicates().to_numpy()
    rdd_date = master_summary[['PO','ITEM RDD']][(master_summary['PO'].isin(rdd_list)) & (master_summary['ITEM RDD'] != '00/00/0000')].drop_duplicates().reset_index(drop=True)

    if rdd_date.empty:
    # Filter rdd_list to get 'SO DATE'
        rdd_date = master_summary[['PO', 'SO DATE']][master_summary['PO'].isin(rdd_list)].drop_duplicates().reset_index(drop=True)
        rdd_date.rename(columns={'SO DATE':'ITEM RDD'},inplace=True)

    for i in range(len(rdd_date.index)):
        master_summary['ITEM RDD'] = np.where((master_summary['PO'] == rdd_date['PO'][i]) & (master_summary['ITEM RDD'] == '00/00/0000'),rdd_date['ITEM RDD'][i],master_summary['ITEM RDD'])
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
    
    ship_status['PRIMARY KEY'] = ship_status['PRIMARY KEY'].astype(str).str.replace("\.0$", "",regex=True)
    master_summary = master_summary.merge(ship_status, on = 'PRIMARY KEY', how = 'left').drop_duplicates().reset_index(drop = True)
    master_summary.fillna('NA',inplace=True)
    master_summary['ITEM'] = master_summary['ITEM'].astype(str).str.replace("\.0$", "",regex=True)
    master_summary['PO + ITEM'] = master_summary['PO'].astype(str) + master_summary['ITEM']
    master_summary = master_summary[txt_array_local('Summary_columns.txt')]

    master_summary = rdd_validation(master_summary)
    master_summary.fillna('NA',inplace=True)

    master_summary['SHIPPABLE'] = np.where((master_summary['GENERAL STATUS'] == 'READY TO SHIP') & (master_summary['COMPLEXITY CATEGORY'] != 'BTS REMAN') & (master_summary['ITEM RDD'].dt.strftime('%Y-%m-%d') <= current_date().strftime('%Y-%m-%d')),
                        (np.where(master_summary['HPE RESTRICTIONS'] != 'NA','FG - HPE RESTRICTED',(np.where((master_summary['INTERNAL HOLDS'] == 'NA') | ((master_summary['INTERNAL HOLDS'].str.contains('GLOBAL TRADE')) 
                        & (master_summary['INTERNAL HOLDS'].apply(len)<170)),'READY TO SHIP',(np.where(master_summary['INTERNAL HOLDS'].str.contains('WORKORDER'),'FG - HOLD BY WO',
                        (np.where(master_summary['INTERNAL HOLDS'].str.contains('HOLD_SKU'),'FG - HOLD BY SKU',(np.where(master_summary['INTERNAL HOLDS'].str.contains('HOLD_SSN'),'FG - HOLD BY SSN',
                        (np.where(master_summary['INTERNAL HOLDS'].str.contains('HOLD_PARTNO'),'FG - HOLD BY PARTNO','NA')))))))))))),
                        (np.where(master_summary['GENERAL STATUS'].str.contains('SHIPPED '+str(format_date(4))),'SHIPPED '+str(format_date(4)),'NA')))

    master_summary = ship_partial_validation(master_summary)

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
        master_summary['SHIPPABLE'] = np.where((master_summary['SHIPPABLE'] != 'READY TO SHIP') & (master_summary['DN QTY'] != 'NA'),'READY TO SHIP',master_summary['SHIPPABLE'])
        master_summary['SHIPPABLE'] = np.where(((master_summary['DN QTY'] != 'NA') & (master_summary['GENERAL STATUS'] != 'READY TO SHIP') & (master_summary['GENERAL STATUS'] != 'SHIPPED '+format_date(4))),'PARTIAL SHIPMENT',master_summary['SHIPPABLE'])

        master_summary['DN QTY'] = np.where((master_summary['DN QTY'] == 'NA'),master_summary['OPEN QTY'],master_summary['DN QTY'])
        master_summary.drop(columns=['OPEN QTY'],inplace = True)
        master_summary.rename(columns = {'DN QTY':'OPEN QTY'},inplace = True) 

    po_holds = master_summary['PO + ITEM'][master_summary['SHIPPABLE'].str.contains('HOLD')].to_numpy()
    grouped = master_summary.groupby('PO')
    master_summary_sc = pd.DataFrame()

    for name,group in grouped:
        
        subgroup = group[group['SHIPPABLE'].str.contains('READY') & (group['SHIP TYPE'] == 'SC')]

        if len(subgroup) == len(group):
            master_summary_sc = pd.concat([master_summary_sc,subgroup]).reset_index(drop = True)
        
    master_shippped = master_summary[master_summary['SHIPPABLE'].str.contains('SHIPPED|PARTIAL') | 
                (master_summary['SHIPPABLE'].str.contains('READY') & (master_summary['SHIP TYPE'] == 'SP'))]

    master_summary_sc = pd.concat([master_summary_sc,master_shippped]).reset_index(drop = True)
  
    master_summary_sc = master_summary_sc.loc[~master_summary_sc['PO + ITEM'].isin(po_holds)]

    master_summary_sc['PGI'] = np.where((master_summary_sc['SHIPPABLE'] != 'READY TO SHIP'), ('SHIPPED (PGI)'),('PENDING PGI'))

    #----------CLOSED DATE VALIDATION---------------
    #Add analysis level column
    master_summary_sc = analysis_level_column_id(master_summary_sc)
    df_closed_date = prd_order_list(master_summary_sc)

    master_summary_sc.rename(columns={'WO':'WORK ORDER'},inplace=True)
    master_summary_sc['WORK ORDER'] = master_summary_sc['WORK ORDER'].astype(np.int64)
    master_summary_sc = master_summary_sc.merge(df_closed_date[['WORK ORDER','CLOSED DATE']],on='WORK ORDER',how='left').drop_duplicates().reset_index(drop=True)
    master_summary_sc = cd_flag_dates_aligment(master_summary_sc,'CLOSED DATE')
    master_summary_sc['AGING'] = datetime.datetime.now() - master_summary_sc['CLOSED DATE']
    master_summary_sc['AGING'] = master_summary_sc['AGING'].apply(format_timedelta)

    #error price
    error_price_list = master_summary_sc['ANALYSIS_LEVEL'][master_summary_sc['WORK ORDER'].isin(wo_error_price())].drop_duplicates().to_list()
    master_summary_sc['ERROR PRICE'] = np.where(master_summary_sc['ANALYSIS_LEVEL'].isin(error_price_list),'X','-')

    #Get CATEGORY and SEQUENCE from previous backlog sequence
    backlog_sequence = pd.read_excel(share_path()+'\\Backlog_Sequence\\Backlog_Sequence_'+previous_labor_day().strftime('%m%d%Y')+'.xlsx',usecols=['WORK ORDER','CATEGORY','CATEGORY VALUE'])
    master_summary_sc = master_summary_sc.merge(backlog_sequence,on='WORK ORDER',how='left').drop_duplicates().reset_index(drop=True)
    master_summary_sc['CATEGORY VALUE'] = np.where(master_summary_sc['CATEGORY'].str.contains('HPE AGED LIST'),0,master_summary_sc['CATEGORY VALUE'])
    master_summary_sc.sort_values(by=['CATEGORY VALUE','CLOSED DATE'],ascending=[True, True],inplace=True)
    master_summary_sc.reset_index(drop=True, inplace=True)
    master_summary_sc['PRIORITY'] = master_summary_sc.index + 1
    master_summary_sc.to_excel(path()+'\Files\\master_summary_sc.xlsx',index=False)

    ship_pivot = pd.pivot_table(master_summary_sc,index = ['COMPLEXITY CATEGORY'],columns={'PGI'},values = ['OPEN QTY'],aggfunc = 'sum',margins=True,margins_name = 'TOTAL',fill_value=0)
    ship_pivot = pd.DataFrame(ship_pivot.to_records())

    ship_pivot.rename(columns = {'COMPLEXITY CATEGORY': 'COMPLEXITY',"('OPEN QTY', 'PENDING PGI')":'PENDING PGI',"('OPEN QTY', 'SHIPPED (PGI)')":'SHIPPED (PGI)',"('OPEN QTY', 'TOTAL')":'TOTAL'}, inplace = True)
    ship_pivot['TOTAL'] = ship_pivot['TOTAL'].astype(str).str.replace("\.0$", "",regex = True)

    mail_format = master_summary_sc[['PO','SO','OPEN QTY','WORK ORDER','SHIPPABLE','COMPLEXITY','COMPLEXITY CATEGORY','CLOSED DATE','AGING','CATEGORY','PRIORITY','ERROR PRICE']]
    mail_format = mail_format.merge(df_country,on='WORK ORDER',how='left').reset_index(drop = True)    

    with pd.ExcelWriter(path()+'\Files\\Shippable_'+format_date(3)+'.xlsx') as writer:
        mail_format.to_excel(writer,'SHIPPABLE', index = False)
        ship_pivot.to_excel(writer,'SUMMARY', index = False)
        master_summary.to_excel(writer,'RAWDATA',index = False)

    send_email('ecmms.OM@FII-NA.com ; ecmms.shipping@fii-na.com','valeria.pereyra@fii-na.com ; Bryan.Rodriguez@FII-NA.com ; alejandro.prado@fii-na.com','Shippable '+format_date(4),ship_pivot)
    #send_email('rodrigo.bedolla@FII-NA.com','Bryan.Rodriguez@FII-NA.com','Shippable '+format_date(4),ship_pivot)

    df_case_assign = case_assignnment(master_summary,prev_master)

    with pd.ExcelWriter(path()+'\Files\\Shippable_'+format_date(3)+'(CA).xlsx') as writer_complete:
        df_case_assign.to_excel(writer_complete,'CASE ASSIGNMENT',index = False)

    try:
        potential_shipments()
    except Exception as e:
        print('New Shipments Overview Error: '+str(e))

Shippable_complete()