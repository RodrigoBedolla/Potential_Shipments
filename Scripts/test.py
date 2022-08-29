from My_Book import *

def order_assign(df):

    data = [['SHORT TBC',1],['SHORT',2],['SHORT BEFORE SOC',3],['SHORT BEDORE SAB',4],['CTB',5],['KITTING',6],['WIP',7],['PACKING',8]]
    order_bucket = pd.DataFrame(data, columns=['BUCKET', 'PRIORITY'])

    df['BUCKET'] = np.where(df['BUCKET'].str.contains('SHORT'),np.where(df['BUCKET'].str.contains('SOC'),'SHORT BEFORE SOC',
                                np.where(df['BUCKET'].str.contains('SAB'),'SHORT BEFORE SAB',
                                np.where(df['BUCKET'].str.contains('TBC'),'SHORT TBC','SHORT'))),df['BUCKET'])

    case_assignment_temp = df.merge(order_bucket,on = 'BUCKET', how = 'left')
    case_assignment_temp = case_assignment_temp[['PO','BUCKET','PRIORITY']].sort_values(by='PRIORITY').drop_duplicates(subset='PO',keep='first').reset_index(drop = True)
    case_assignment_temp.rename(columns={'BUCKET':'GENERAL'},inplace = True)\

    case_assignment = case_assignment.merge(case_assignment_temp[['PO','GENERAL']],on = 'PO',how = 'left')
    
    return case_assignment