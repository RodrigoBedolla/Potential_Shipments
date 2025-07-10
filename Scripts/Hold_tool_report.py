import subprocess
import pandas as pd
import json as json
from My_Book import *
from io import StringIO
from datetime import date 
from dateutil.relativedelta import relativedelta
from code_holds import code_holds
from Hold_tool import po_validation,Hold_type_column
from SAP import saplogin

def hold_by_pn(df):

    df = df[['ID','Type']][df['Type'].str.contains('PARTNO')==True].drop_duplicates(subset='ID').reset_index(drop=True)
    sap_input(df,'ID')
    if not df.empty:
        saplogin(4)

    df = zpp9_format()
    df = df.rename(columns={'Material':'ID'})

    return df

def hold_tool():
  
    initial_date = (date.today() + relativedelta(months=-6)).strftime("%Y-%m-%d")
    final_date = (date.today()).strftime("%Y-%m-%d")
    subprocess.call('sh bash_scripts/request.sh ' + initial_date + ' ' + final_date + ' HOLD_TOOL')  
    df_1 = hold_tool_rpt()

    initial_date = (date.today() + relativedelta(months=-12)).strftime("%Y-%m-%d")
    final_date = (date.today() + relativedelta(months=-6)).strftime("%Y-%m-%d")
    subprocess.call('sh bash_scripts/request.sh ' + initial_date + ' ' + final_date + ' HOLD_TOOL')  
    df_2 = hold_tool_rpt()
   
    df = pd.concat([df_1,df_2]).drop_duplicates().reset_index(drop=True)
    try:
        zpp9 = hold_by_pn(df)
        df = df.merge(zpp9[['ID','Order']],on='ID',how='left')
    except:
        df['Order'] = 0
    df.fillna(0,inplace=True)

    df['Type'] = np.where(df['Type'].str.contains('PARTNO'),df['Type'].astype(str) + ': ' + df['ID'].astype(str),df['Type'])
    df['ID'] = np.where(df['Order']==0,df['ID'],df['Order'].astype(np.int64))

    #-------------------------------------------------------------------------------
   
    df_master = pd.read_excel(share_path()+r'\Master Template\\master_base.xlsx')

    #-----NonCTR added 01/15/2025--------- 
    df_non_ctr = non_ctr(df_master)
    df_non_ctr['HOLD TYPE'] = 'Type: HOLD_PO | Hold Date: '+current_date().strftime('%m/%d/%Y')+' | Hold Description: '+df_non_ctr['DESCRIPTION']+' | Part No: '+df_non_ctr['PART NO']+' | Hold Reason: NON CTR'
    df_non_ctr = df_non_ctr[['PO','HOLD TYPE']]
    df_non_ctr.rename(columns={'PO':'ID'},inplace=True)
    df_non_ctr = df_non_ctr.groupby('ID')['HOLD TYPE'].apply(lambda x: '\n'.join(x)).reset_index()

    for i in range(0,len(df.index)):

        id = df['ID'][i]
        type_c = df['Type'][i]

        if '52C' in str(id):

            df.loc[i,'HOLD LEVEL'] = 'PO'

        elif type(id) == int and (len(str(id)) == 8 or len(str(id)) == 9):

            df.loc[i,'HOLD LEVEL'] = 'WO'

        elif ('SKU' in type_c) or ('PARTNO' in type_c):

            df.loc[i,'HOLD LEVEL'] = 'BASE SKU'

        else:

            df.loc[i,'HOLD LEVEL'] = 'OTHERS / HOLD_SSN'

    df = Hold_type_column(df)
    df_po = df[df['HOLD LEVEL'].str.contains('PO') == True].reset_index(drop= True)
    df_po = df_po.rename(columns = {'ID':'PO'})
    df_po['PO'] = df_po['PO'].astype(str).str.replace(r'\.0$', "",regex=True)
    df_po = pd.merge(df_po,df_master['PO'].astype(str).str.replace(r'\.0$', "",regex=True), on= ['PO'], how= 'inner').drop_duplicates().reset_index(drop=True)
    df_po = df_po.rename(columns = {'PO':'ID'})

    df_wo = df[df['HOLD LEVEL'].str.contains('WO') == True].reset_index(drop= True)
    df_wo = df_wo.rename(columns = {'ID':'WORK ORDER'})
    df_wo = pd.merge(df_wo,df_master['WORK ORDER'], on= ['WORK ORDER'], how= 'inner').drop_duplicates().reset_index(drop=True)
    df_wo = df_wo.rename(columns = {'WORK ORDER':'ID'})

    df_sku = df[df['HOLD LEVEL'].str.contains('BASE SKU') == True].reset_index(drop= True)
    df_sku = df_sku.rename(columns = {'ID':'BASE SKU'})
    df_sku = pd.merge(df_sku,df_master['BASE SKU'], on= ['BASE SKU'], how= 'inner').drop_duplicates().reset_index(drop=True)
    df_sku = pd.merge(df_sku, df_master[['BASE SKU','WORK ORDER']], on = 'BASE SKU', how = "left").drop_duplicates().reset_index(drop=True)
    #df_sku['WORK ORDER'] = df_sku['WORK ORDER'].astype(int)
    df_sku.pop('BASE SKU')
    df_sku.insert(0, 'WORK ORDER', (df_sku.pop('WORK ORDER')))
    df_sku = df_sku.rename(columns = {'WORK ORDER':'ID'})

    df_final = pd.concat([df_po,df_wo,df_sku,df_non_ctr])
    df_final.to_excel(share_path()+r'\Master_Analysis\hold_tool_report.xlsx',index= False)
    
    print(df_po)
    po_priority_code = po_validation(df_po)
    code_holds(po_priority_code)


#hold_tool()