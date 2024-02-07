from My_Book import *
import shutil

def potential_shipments():

    mail_format = pd.read_excel(path()+'\Files\Shippable_'+str(format_date(3))+'.xlsx', sheet_name='SHIPPABLE')
    master_summary = pd.read_excel(path()+'\Files\Shippable_'+str(format_date(3))+'.xlsx', sheet_name='RAWDATA')
    master_base = pd.read_excel(share_path()+'\Master Template\master_base.xlsx', usecols=['WORK ORDER','STANDALONE']).drop_duplicates(subset='WORK ORDER')
    previous_master = pd.read_excel(path()+'\Files\Previous_Master.xlsx', usecols=['WORK ORDER','STATUS']).drop_duplicates(subset='WORK ORDER')
    df5 = pd.read_excel(path()+'\Files\Shippable_'+str(format_date(3))+'(CA).xlsx')
    ship_status = pd.read_excel(share_path()+'\OM_RPAs_Files\Backup\SHIP_STATUS\\SHIP_STATUS.xlsx',sheet_name = 'SHIP STATUS',usecols=['WORK ORDER','OPEN FAILURE','HARDWARE FAILURES'])

    shippable_list = mail_format['WORK ORDER'].drop_duplicates().to_list()
    master_summary['SHIPPABLE'] = np.where(master_summary['WORK ORDER'].isin(shippable_list),'Y','N')
    master_summary = master_summary.merge(master_base, on='WORK ORDER', how='left')
    master_summary = master_summary.merge(previous_master, on='WORK ORDER', how='left')

    master_summary = master_summary[(master_summary['STANDALONE']=='Y') | (master_summary['SHIPPABLE']=='Y')].reset_index(drop=True)

    master_summary['CD_FLAG_BUCKET'] = np.where(master_summary['SHIPPABLE']=='Y',np.where(master_summary['PRODUCTION BUCKET'].str.contains('SHIPPED'),'SHIPPED','COMPLETED'),
                            np.where(master_summary['PRODUCTION BUCKET'].str.contains('ASSEMBLY|TESTING|QA|AIC'),'WIP',
                            (np.where(master_summary['PRODUCTION BUCKET'].str.contains('PACKING|SHIPPING'),'PACKING',
                            (np.where(master_summary['PRODUCTION BUCKET'].str.contains('KITTING'),'KITTING',
                            (np.where(master_summary['PRODUCTION BUCKET'].str.contains('COMPLETE WITH CD FLAG'),'COMPLETE WITH CD FLAG',
                            (np.where(((master_summary['PRODUCTION BUCKET'].str.contains('RELEASED')) & (master_summary['STATUS'].str.contains('CTB'))) | (master_summary['STATUS'].str.contains('CTB')),'CTB',
                            (np.where(master_summary['PRODUCTION BUCKET'].str.contains('CREATED|RELEASED|COMPLETED'),master_summary['PRODUCTION BUCKET'],'-'))))))))))))

    df5['CD FLAG'] = 'Y'

    master_summary.fillna('-', inplace=True)
    master_summary['INTERNAL_HOLDS_FLAG'] = np.where(((master_summary['INTERNAL HOLDS'].str.contains('GLOBAL TRADE')) & (master_summary['INTERNAL HOLDS'].apply(len)<170)) | 
                                          ((master_summary['INTERNAL HOLDS'].str.contains('GLOBAL TRADE')) & (master_summary['INTERNAL HOLDS'].apply(len)<210) & (master_summary['INTERNAL HOLDS'].str.contains('JOSE LUIS LARIS|JORGE ADRIAN RODRIGUEZ'))) | 
                                          (master_summary['INTERNAL HOLDS']=='-'),'N','Y')

    master_summary = pd.concat([df5,master_summary]).reset_index(drop=True)
    master_summary['CD FLAG'] = master_summary['CD FLAG'].fillna('N')
    master_summary['CD_FLAG_BUCKET'] = np.where(master_summary['PRODUCTION BUCKET']=='CANCELLED','CANCELLED',master_summary['CD_FLAG_BUCKET'])
    master_summary = master_summary.merge(ship_status.drop_duplicates(subset=['WORK ORDER']),on='WORK ORDER', how='left').reset_index(drop=True)
    master_summary.fillna('-', inplace=True)
    master_summary.to_excel(path()+'\Files\Qlik_Shippable_'+str(format_date(3))+'.xlsx', index=False)

    shutil.copy(path()+'\Files\Qlik_Shippable_'+str(format_date(3))+'.xlsx',share_path()+'\Qlik_Files')

    shutil.copy(path()+'\Files\Qlik_Shippable_'+str(format_date(3))+'.xlsx','\\\\10.19.16.56\Order Management\OM Projects\Qlik_Files')
#potential_shipments()