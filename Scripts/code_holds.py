from My_Book import *
import pandas as pd

def code_holds(df_priority):

    df_priority = df_priority[~df_priority['IS SUCCESFUL'].isin(['R'])].reset_index(drop= True)
    df_priority['PO DATE'] = pd.to_datetime(df_priority['PO DATE'])

    groups = df_priority.sort_values(by='PO DATE', ascending=True).groupby(['PO'])

    df_priority = df_priority[0:0]

    for name,group in groups:

        array = []
        remove_list = ['HR','SR','ZD','DR','ZR']
        ignore_list = ['AC','SI','CD','PL','ST','CI','CT','NC','DP','CID']

        group.reset_index(drop = True, inplace=True)

        for i in range(0,len(group.index)):
        
            code_type = group['CHANGE TYPE CODE'][i]
            
            if i == 0 and code_type not in remove_list and code_type not in ignore_list:

                array.append(code_type)
            
            if i > 0 and (group['CHANGE TYPE CODE'][i] == group['CHANGE TYPE CODE'][i-1]) == False:

                if code_type not in array and code_type not in ignore_list:

                    if code_type in remove_list:

                        if code_type == 'HR':

                            if 'BH' in array:
                                array.remove('BH')

                        elif code_type == 'SR':

                            if 'SH' in array:
                                array.remove('SH')
                                
                        elif code_type == 'ZD':

                            if 'BB' in array:
                                array.remove('BB')

                        elif code_type == 'DR':

                            if 'BS' in array:
                                array.remove('BS')
                            
                        else:
                            code_type == 'ZR'

                            if 'RZ' in array:
                                array.remove('RZ')

                    else:

                        array.append(code_type)

        group = group.drop_duplicates(subset= 'PO').reset_index(drop= True)
        
        if not array:

            group['CHANGE TYPE CODE'] = 'HOLD NOT FOUND IN 860 PRIO CODES'
            
        else:

            order_list = ['BH','BB','SH','DI','CH','CA','SC']
            holds_array = []

            reorder = [ele for ele in order_list if ele in array]

            group['CHANGE TYPE CODE'] = str(reorder)

            for i in range(len(reorder)):
                if reorder[i] == 'BH':
                    reorder[i] = 'BUILD HOLD'
                    holds_array.append('BUILD HOLD')
                elif reorder[i] == 'BB':
                    reorder[i] = 'PRE BUILD'
                    holds_array.append('PRE BUILD')
                elif reorder[i] == 'SH':
                    reorder[i] = 'SHIP HOLD'
                    holds_array.append('SHIP HOLD')
                elif reorder[i] == 'DI':
                    reorder[i] = 'DELETE ITEM'
                elif reorder[i] == 'CH':
                    reorder[i] = 'CID'
                elif reorder[i] == 'CA':
                    reorder[i] = 'CARRIER CHANGE'
                elif reorder[i] == 'SC':
                    reorder[i] = 'SHIPPING CONDITION'

            group['HPE RESTRICTIONS'] = ' '.join([str(elem) for elem in holds_array])
            group['HPE RESTRICTIONS DETAILS'] = ' '.join([str(elem) for elem in reorder])

        df_priority = pd.concat([df_priority,group])

    df_priority.to_excel(share_path()+r'\Master_Analysis\860_Holds.xlsx', index= False)