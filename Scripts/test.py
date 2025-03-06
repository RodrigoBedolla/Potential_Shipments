from My_Book import *

df_master = pd.read_excel(share_path()+'\Master Template\\master_base.xlsx')

#-----NonCTR added 01/15/2025--------- 
df_non_ctr = non_ctr(df_master)
df_non_ctr['HOLD LEVEL'] = 'PO'
df_non_ctr['HOLD TYPE'] = 'Type: HOLD_PO | Hold Date: '+current_date().strftime('%m/%d/%Y')+' | Hold Description: '+df_non_ctr['DESCRIPTION']+' | Part No: '+df_non_ctr['PART NO']+' | Hold Reason: NON CTR'
df_non_ctr = df_non_ctr[['PO','HOLD TYPE']]
df_non_ctr.rename(columns={'PO':'ID'},inplace=True)
df_non_ctr = df_non_ctr.groupby('ID')['HOLD TYPE'].apply(lambda x: '\n'.join(x)).reset_index()
