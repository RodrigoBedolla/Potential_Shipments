
import win32com.client as win32
import pandas as pd
import os
import datetime
import calendar
from pathlib import Path
import subprocess
import json
from difflib import SequenceMatcher as SM
import sharepy
import numpy as np

#Shared Folder path
def share_path():

    #def_path = '\\\\10.19.16.56\Order Management\OM Projects'
    def_path = '\\\\10.19.17.32\\CygnusFiles\\OM_RPA\\OM Projects'
    
    #local test:

    #def_path = path()
    
    return def_path

#Convert xls file to xlsx file
def convert_xlsx(file):
    fname = path()+'\Files\\'+file
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    wb = excel.Workbooks.Open(fname)

    excel.DisplayAlerts = False

    wb.SaveAs(fname+"x", FileFormat = 51)    #FileFormat = 51 is for .xlsx extension
    wb.Close()                               #FileFormat = 56 is for .xls extension
    #excel.Application.Quit()

#Convert txt File 1 dimention to a array list
def txt_array(z_file):
    
    with open(share_path()+'\Files_Format\\'+z_file) as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content

#Convert txt File 1 dimention to a array list
def txt_array_local(z_file):
    
    with open(path()+'\Files\\'+z_file) as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content

#Create new txt File or append data to existing file
def create_txt(value,file_name,write_tipe):

    if write_tipe == 'append':

        with open(share_path()+'\Files_Format\\'+file_name, 'a') as f:
            f.write('\n'+value)
    
    else:

        with open(share_path()+'\Files_Format\\'+file_name, 'w') as f:
            f.write(value)

#ZSD5 Format
def zsd5_format(file_route):

    df_zsd5 = pd.read_excel(file_route)
    df_zsd5.rename(columns={"WO": "WORK ORDER"}, inplace=True)

    #identify Job finished! and drop empty rows
    value = df_zsd5["TYPE"].iloc[len(df_zsd5.index)-1]
    if value == 'Job finished!':
        df_zsd5=df_zsd5.drop(df_zsd5.index[len(df_zsd5.index)-2:len(df_zsd5.index)])

    return df_zsd5

#ZSD6 Format
def zsd6_format(file_route):

    zsd6_columns = txt_array('zsd6_columns.txt')
    df1 = pd.read_excel(file_route)

    df1=df1.drop(df1.index[[0]])
    df1.columns = df1.iloc[0]
    df1 = df1.drop(df1.index[[0]])
    df1 = df1.loc[:, df1.columns.notnull()]
    df1.columns = df1.columns[:0].tolist() + zsd6_columns

    #identify Job finished! and drop empty rows
    value = df1["TYPE"].iloc[len(df1.index)-1]
    if value == 'Job finished!':
        df1=df1.drop(df1.index[len(df1.index)-2:len(df1.index)])

    return df1

#ZSD6a Format
def zsd6a_format(file_route):

    zsd6a_columns = txt_array('zsd6a_columns.txt')

    df2 = pd.read_excel(file_route)

    df2=df2.drop(df2.index[[0]])
    df2.columns = df2.iloc[0]
    df2=df2.drop(df2.index[[0]])
    df2 = df2.loc[:, df2.columns.notnull()]
    df2.columns = df2.columns[:0].tolist() + zsd6a_columns

    value = df2["SO DATE"].iloc[len(df2.index)-1]

    if value == 'Job finished!':
        df2=df2.drop(df2.index[len(df2.index)-2:len(df2.index)])

    return df2

#Remove multiple column list from specific Dataframe
def drop_list_of_columns(column_list,df):

    for col in column_list: 
        for indice in df.columns:
            if col in indice and (len(col)==len(indice)):   
                del df[indice]
    return(df)
    
    #try this
    #return dataset.drop(cols, axis=1)

#Get specific column removing duplicates and export to txt file (sap input)
def sap_input(df,column):

    column_names = [column]
    df_sales_orders = pd.DataFrame(columns = column_names)

    if column == 'SO':
        df_sales_orders = df[column].drop_duplicates().astype(int)
    else:
        df_sales_orders = df[column].drop_duplicates().astype(str)

    df_sales_orders.to_csv(path()+'\Files\\' + str(column) + '.txt', header=None, index=None) #Guardar archivo de txt
    return df_sales_orders

def format_date(format):

    current_day = datetime.datetime.now()
    time_stamp = datetime.date.strftime(current_day, '%m-%d-%Y %H:%M:%S')
    default_date = datetime.date.today()
    formatted_date = datetime.date.strftime(current_day, "%m/%d/%Y")
    filedate = formatted_date.replace('/','')
    month_day = datetime.date.strftime(current_day, '%m/%d')
    month_name_day =datetime.date.strftime(current_day,'%b %d')
    #datetime.datetime.now()

    #Dates Format
        # 1.- format date mm-dd-yyyy hh:mm:ss:ffffff
        # 2.- format date mm/dd/yyyy
        # 3.- format date mmddyyyy
        # 4.- format date mm/dd
        # 5.- format date mm-dd-yyyy

    if format == 1:                
        return time_stamp
    elif format == 2:
        return formatted_date
    elif format == 3:
        return filedate
    elif format == 4:
        return month_day
    elif format == 5:
        return default_date
    elif format == 6:
        return month_name_day

def base_sku_column(df):

    for i in range(0,len(df.index)):

        material = df['MATERIAL'][i]

        if material.find('FG') > 0:
            df.at[i,'BASE SKU'] = material[:material.find('FG')]
        else:
            df.at[i,'BASE SKU'] = material
        
    return(df)

def project(file):

    #Parameters 
    # file = Destination file

    wo_types = pd.read_excel(share_path()+'\Master Template\Material Master - WO Types.xlsx', sheet_name='WO TYPES')

    file = file.merge(wo_types[['WO TYPE','COMPLEXITY']], on='WO TYPE', how='left')

    for i in range(0,len(file.index)):

        base_sku = file['MATERIAL'][i]
        complexity = file['COMPLEXITY'][i]

        if complexity == 'HPSD' and base_sku.find('FG') > 0:
            file.loc[i,'PROJECT'] = 'HPSD CTO'
        elif complexity == 'HPSD':
            file.loc[i,'PROJECT'] = 'HPSD BTO'
        elif complexity == 'VALIDAR' and base_sku[6:7] == 'R':
            file.loc[i,'PROJECT'] = 'REMAN TRADE'
        elif complexity == 'VALIDAR':
            file.loc[i,'PROJECT'] = 'DIRTY ORDER'
        else:
            file.loc[i,'PROJECT'] = complexity

    drop_list_of_columns(['COMPLEXITY'],file)
    
    return(file)

def family(file):

    sku_summary = pd.read_excel(share_path()+'\Master Template\Material Master - WO Types.xlsx', sheet_name='Material Master')
    file = file.merge(sku_summary[['BASE SKU','FAMILY']], on='BASE SKU', how='left')
    file['FAMILY'] = file['FAMILY'].fillna('FAMILY NOT FOUND')

    return file

def clean_source():
    log_file_route = path()+'\Files'
    for i in os.listdir(log_file_route):
        os.remove(path()+'\Files\\' + i)

def primary_key(df):
    
    #CREATE PRIMARY KEY
    #Find WO's and concatenate PO + ITEM + BASE SKU ON MISSING WO's

    for i in range(0,len(df.index)):

        work_order_key = df['WORK ORDER'][i]
        second_key = str(df['PO'][i]) + str(df['ITEM'][i]) + str(df['BASE SKU'][i])

        if work_order_key != work_order_key:
            df.loc[i,'PRIMARY KEY'] = second_key
        else:
            df.loc[i,'PRIMARY KEY'] = work_order_key
    
    df = df[ ['PRIMARY KEY'] + [ col for col in df.columns if col != 'PRIMARY KEY' ] ]
    df['PRIMARY KEY'] = df['PRIMARY KEY'].astype(str).str.replace('.0', '', regex=False)

    return df

def dates_operations(operation,days):

    current_day = datetime.datetime.now()

    if operation == 'sum':

        current_day = datetime.date.today()
        end_date = current_day + datetime.timedelta(days=+days)

        return end_date

    if operation == 'less':
        
        current_day = datetime.date.today()
        end_date = current_day + datetime.timedelta(days=-days)

        return end_date



def week_day():

    current_day = datetime.datetime.now()
    week_day = calendar.day_name[current_day.weekday()]

    return week_day

def dailys(df):
    
    #BACKLOG_COLUMN
    #column to create buckets for new orders(curren day), new orders(previous day), new orders (weekends) and Backlog for aged orders

    for i in range(0,len(df.index)):

        a = (df['SO DATE'][i]).date()

        # 11/29/2021 -> change value 4 to 3 in monday condition

        if a == format_date(5):
            df.loc[i,'BACKLOG']  = datetime.date.strftime(format_date(5),'%b %d')
        elif previous_labor_day() <= a <= dates_operations('less',1):
            df.loc[i,'BACKLOG'] = datetime.date.strftime(previous_labor_day(),'%b %d')
        else:
            df.loc[i,'BACKLOG'] = 'BACKLOG'

    
    #COMPLEXITY CATEGORY
    #PPS, SERVERS Y RACKS
    for i in range(0,len(df.index)):

        bts_reman = df['SHIP TO'][i]
        dirty_orders = df['PROJECT'][i]
        complexity = df['PROJECT'][i]
        reman_trade = df['FAMILY'][i]
        racks = df['FAMILY'][i]

        if 'DO NOT SHIP' in bts_reman:
            df.loc[i,'COMPLEXITY CATEGORY']  = 'BTS REMAN'
        elif 'DIRTY ORDER' in dirty_orders:
            df.loc[i,'COMPLEXITY CATEGORY']  = 'DIRTY ORDER'
        elif 'RACK' in racks:
            df.loc[i,'COMPLEXITY CATEGORY']  = 'RACKS'
        elif 'PPS' in complexity:
            df.loc[i,'COMPLEXITY CATEGORY']  = 'PPS'
        elif 'CTO' in complexity or 'BTO' in complexity:
            df.loc[i,'COMPLEXITY CATEGORY']  = 'SERVERS'
        elif 'OPTION' in reman_trade or 'BUY' in reman_trade:
            df.loc[i,'COMPLEXITY CATEGORY']  = 'PPS'
        elif 'REMAN TRADE' in complexity:
            df.loc[i,'COMPLEXITY CATEGORY']  = 'SERVERS'
    
    #COMPLEXITY
    #PPS, BTO, SIMPLE CTO, COMPLEX CTO, BLADES Y HPSD's

    for i in range(0,len(df.index)):

        bts_reman = df['PROJECT'][i]
        dirty_orders = df['PROJECT'][i]
        complexity = df['PROJECT'][i]
        fmx_family = df['FAMILY'][i]
        racks = df['FAMILY'][i]
        
        if 'DO NOT SHIP' in bts_reman:
            df.loc[i,'COMPLEXITY CATEGORY']  = 'BTS REMAN'
        elif 'DIRTY ORDER' in dirty_orders:
            df.loc[i,'COMPLEXITY']  = 'DIRTY ORDER'
        elif 'RACK' in racks:
            df.loc[i,'COMPLEXITY']  = 'RACKS'
        elif 'BL' == fmx_family[:2] and (('PPS' in complexity) == False):
            df.loc[i,'COMPLEXITY']  = 'BLADES'
        elif 'PPS' in complexity:
            df.loc[i,'COMPLEXITY']  = 'PPS'
        elif 'BTO' in complexity:
            df.loc[i,'COMPLEXITY']  = 'BTO'
        elif 'HPSD' in complexity:
            df.loc[i,'COMPLEXITY']  = 'HPSD'
        elif 'sCTO' in complexity:
            df.loc[i,'COMPLEXITY']  = 'SIMPLE CTO'
        elif 'cCTO' in complexity:
            df.loc[i,'COMPLEXITY']  = 'COMPLEX CTO'
        elif 'OPTION' in fmx_family or 'BUY' in fmx_family:
            df.loc[i,'COMPLEXITY']  = 'PPS'
        elif 'REMAN TRADE' in complexity:
            df.loc[i,'COMPLEXITY']  = 'BTO'

    return df

def complexities(df):

    for i in range(0,len(df.index)):

        project = df['PROJECT'][i]
        family = df['FAMILY'][i]
        material = df['MATERIAL']
        
        if 'DO NOT SHIP' in family:
            df.loc[i,'COMPLEXITY']  = 'BTS REMAN'
        elif 'DIRTY ORDER' in project or ('FG' in material and 'BTO' in project):
            df.loc[i,'COMPLEXITY']  = 'DIRTY ORDER'
        elif 'RACK' in family:
            df.loc[i,'COMPLEXITY']  = 'RACKS'
        elif 'PPS' in project:
            df.loc[i,'COMPLEXITY']  = 'PPS'
        elif 'BTO' in project:
            df.loc[i,'COMPLEXITY']  = 'BTO'
        elif 'cCTO' in project:
            df.loc[i,'COMPLEXITY']  = 'COMPLEX CTO'
        elif 'CTO' in project:
            df.loc[i,'COMPLEXITY']  = 'CTO'
        else:
            df.loc[i,'COMPLEXITY']  = project

    return df

def path(): #Current project path delimited by '\'

    path = str(Path(__file__).parent.parent)
    return path

def path_home(): #Root user path delimited by '\'

    home = str(Path.home())
    return home

def windows_path(): #Current project path delimited by '\\'

    path = str(Path(__file__).parent.parent).replace('\\','\\\\')
    return path

def windows_path_home(): #Root user path delimited by '\\'

    home = str(Path.home()).replace('\\','\\\\')
    return home

def root_path(jumps_back):

    root = str(Path(__file__).parents[jumps_back])

    return root

def delete_local_files(): #Delete file from 'Files' folder for specific project

    log_file_route = path()+'\Files'
    for i in os.listdir(log_file_route): 
        if (i != 'Shippeable_'+format_date(3)+'.xlsx') & (i != 'Master_columns.txt') & (i != 'Summary_columns.txt') & (i != 'Ship_columns.txt') & (i != 'RAWDATA.xlsx') & (i != 'Shippeable_'+format_date(3)+'(CA).xlsx'):
            print("Removed: "+i)
            os.remove(path()+'\Files\\' + i)

def previous_labor_day():
    current_day = datetime.date.today()
    holidays=txt_array('holidays.txt')
    final_date = current_day + datetime.timedelta(days=-1)

    if calendar.day_name[final_date.weekday()] == 'Saturday':
        final_date = final_date + datetime.timedelta(days=-1)
    elif calendar.day_name[final_date.weekday()] == 'Sunday':
        final_date = final_date + datetime.timedelta(days=-2) 
    while final_date.strftime('%m/%d/%Y') in holidays:
        final_date = final_date + datetime.timedelta(days=-1)
        if calendar.day_name[final_date.weekday()] == 'Saturday':
            final_date = final_date + datetime.timedelta(days=-1)
        elif calendar.day_name[final_date.weekday()] == 'Sunday':
            final_date = final_date + datetime.timedelta(days=-2)

    return final_date


def sap_decoding_zsd6_files(flag,file_route):

    if flag == 'zsd6':

        df =  pd.read_csv(file_route, skiprows=[0,1], sep='\\t', thousands=',' , engine='python', encoding='ISO-8859-1')

        df = df.dropna(axis=1, how='all')

        df.rename(columns={'TYPE.1': 'WO TYPE', 'COUN' : 'COUNTRY'}, inplace=True)
        df.columns = df.columns.str.lstrip()
        df = df[txt_array('zsd6_columns.txt')]

        if df["TYPE"].iloc[len(df.index)-1] == 'Job finished!':

            df=df.drop(df.index[len(df.index)-1:len(df.index)])

        return df

    elif flag == 'zsd6a':


        df =  pd.read_csv(file_route, skiprows=[0,1], sep='\\t', thousands=',' , engine='python', encoding='ISO-8859-1')

        df = df.dropna(axis=1, how='all')
        df.columns = df.columns.str.lstrip()
        df.rename(columns={'OPEN': 'OPEN QTY', 'CO' : 'COUNTRY','TYPE' : 'WO TYPE','ACK' : 'RE-ACK'}, inplace=True)
        df = df[txt_array('zsd6a_columns.txt')]

        if df["SO DATE"].iloc[len(df.index)-1] == 'Job finished!':

            df=df.drop(df.index[len(df.index)-1:len(df.index)])

        return df
    
    else:

        return False

def sap_decoding_coois():

    print()


def primary_key_by_so(df):
    
    #CREATE SO ID
    #Find WO's and concatenate SO + ITEM + BASE SKU ON MISSING WO's and SO QTY for reman orders

    for i in range(0,len(df.index)):

        try:

            deletion_flag = df['DELETION FLAG'][i]

        except Exception as e:
            
            deletion_flag = True
        
        work_order_key = df['WORK ORDER'][i]
        second_key = str(df['SO'][i]) + str(df['ITEM'][i]) + str(df['BASE SKU'][i])
        reman_id = str(df['SO'][i]) + str(df['ITEM'][i]) + str(df['BASE SKU'][i])+str(df['SO QTY'][i])

        if deletion_flag == True:

            if df['BASE SKU'][i][6:7] == 'R' and (work_order_key != work_order_key or len(str(work_order_key)) < 8):
                df.loc[i,'SO ID'] = reman_id
            elif work_order_key != work_order_key or len(str(work_order_key)) < 8:
                df.loc[i,'SO ID'] = second_key
            else:
                df.loc[i,'SO ID'] = work_order_key

        else:

            if df['BASE SKU'][i][6:7] == 'R' and deletion_flag == 'X':
                df.loc[i,'SO ID'] = reman_id
            elif work_order_key != work_order_key or len(str(work_order_key)) < 8:
                df.loc[i,'SO ID'] = second_key
            else:
                df.loc[i,'SO ID'] = work_order_key
    
    df = df[ ['SO ID'] + [ col for col in df.columns if col != 'SO ID' ] ]
    df['SO ID'] = df['SO ID'].astype(str).str.replace('.0', '', regex=False)

    return df

def coois():
    
    convert_xlsx('coois.xls')

    coois =  pd.read_excel(path()+'\Files\coois.xlsx', skiprows=[0,1,2,4])
    coois = coois.loc[:, ~coois.columns.str.contains('^Unnamed')]
    coois.drop(coois.tail(2).index,inplace=True) # drop last n rows
    coois.columns = txt_array('coois_default.txt')

    for i in range(0,len(coois.index)):

        collective_flag = coois['COLLECTIVE'][i]
        nested_id = coois['NESTED ID'][i]

        if collective_flag != collective_flag:
            coois.loc[i,'HEADERS'] = 'HEADER'
        elif 'X' in collective_flag and nested_id == 0:
            coois.loc[i,'HEADERS'] = 'NESTED'
        elif 'X' in collective_flag and nested_id > 0:
            coois.loc[i,'HEADERS'] = 'HEADER'
        else:
            print('NA')

    coois = coois[txt_array('coois_format.txt')]
    coois = primary_key_by_so(base_sku_column(coois))

    return coois

def hold_tool_format(df):

    df.rename(columns={'ID': 'ORIGINAL ID', 'Hold Reason': 'ORIGINAL Hold Reason'}, inplace=True)

    for i in range(0,len(df.index)):
        
        reference = df['Reference'][i]
        work_order = df['ORIGINAL ID'][i]

        if len(reference) >= 8:
            df.loc[i,'ID'] = reference.lstrip('0')
        else:
            try:
                df.loc[i,'ID'] = work_order.lstrip('0')
            except:
                df.loc[i,'ID'] = work_order

        hold_reason = df['ORIGINAL Hold Reason'][i]

        if 'Hold by 850 sERP' in hold_reason:
            df.loc[i,'Hold Reason'] = 'Hold by 850 sERP'
        else:
            df.loc[i,'Hold Reason'] = hold_reason

    non_wos = df[~df['ID'].str.isnumeric()]
    df = df[df['ID'].str.isnumeric()]
    df['ID'] = df['ID'].astype(np.int64)
    df = pd.concat([df,non_wos])

    df = df[txt_array('hold_tool_columns.txt')+['ORIGINAL ID','ORIGINAL Hold Reason']]

    return df


def get_time():

    time_stamp = datetime.datetime.strptime(format_date(1),'%m-%d-%Y %H:%M:%S')

    return time_stamp

#Upgrading column based in another df and keep same position with new values
def upgrade_column(df,second_df,id,column, column_position):

    """
    Upgrading column based in another df and keep same position with new values
    :param dataframe df: main Dataframe
    :param dataframe second_df: second datafreme with updated values
    :param str id: id to do merge
    :param str column: Column who will be updated
    :param int column_position: final column with specific or initial position
    :return: input dataframe with column already updated
   """
    df = df.merge(second_df[[id]+[column]], on=id, how='left')
    t_cols = df.pop(column+'_y')
    df.insert(column_position,t_cols.name,t_cols)
    df = drop_list_of_columns([column+'_x'],df)
    df.rename(columns={column+'_y':column+''}, inplace=True)

    df[column].fillna('NA', inplace = True)

    return df

def work_days(init_date,add_days,holidays):

    final_date = init_date + datetime.timedelta(days=+add_days)

    if calendar.day_name[final_date.weekday()] == 'Saturday':
        final_date = final_date + datetime.timedelta(days=+2)
    elif calendar.day_name[final_date.weekday()] == 'Sunday':
        final_date = final_date + datetime.timedelta(days=+1)
    while str(final_date) in holidays:
        final_date = final_date + datetime.timedelta(days=+1)
        if calendar.day_name[final_date.weekday()] == 'Saturday':
            final_date = final_date + datetime.timedelta(days=+2)
        elif calendar.day_name[final_date.weekday()] == 'Sunday':
            final_date = final_date + datetime.timedelta(days=+1)

    return final_date


def cygnus_request(wos,report):

    subprocess.call('sh bash_scripts/request_wip.sh '+wos+' '+report)   

    data = open(path()+'\json\\cygnus_files.json','r') #read json file downloaded
    json_array = json.load(data)
    jsonf = json.dumps(json_array[1]) #get inormation to dataframe
    df = pd.read_json(jsonf)

    return(df)

def cyg_cookie():
    
    #Login to CyGNUS and save cooke with credentials
    subprocess.call('sh bash_scripts/Login.sh')


def download_cygnus_files(df,column_list,column_name,array_range,sign_concat,report):

    try:
        df=df.str.replace("\.0$", "",regex=True)
    except Exception as e:
        print('Error: '+str(e))
    
    first = 0
    last = array_range
    sub_value = array_range
    batch = 0
    cyg_cookie()
    while sub_value == array_range:

        df1 = df.iloc[first:last]      
        
        sub_value = len(df1.axes[0])

        first = last
        last = last + sub_value 
        df1=[str(int) for int in df1]
        cyg_input = sign_concat.join(df1)

        if batch==0:
            final_df=cygnus_request(cyg_input,report)
        else:
            df_cyg=cygnus_request(cyg_input,report)

            frames = [final_df, df_cyg]

            final_df = pd.concat(frames)
        batch+=1

    final_df=final_df[column_list]
    final_df.columns=column_name
    final_df.reset_index(drop=True,inplace=True)

    return final_df

def wo_status(df,array_range,sign_concat,report):

    try:
        df=df.str.replace("\.0$", "",regex=True)
    except Exception as e:
        print('Error: '+str(e))
    
    first = 0
    last = array_range
    sub_value = array_range
    batch = 0
    cyg_cookie()
    while sub_value == array_range:

        df1 = df.iloc[first:last]      
        
        sub_value = len(df1.axes[0])

        first = last
        last = last + sub_value 
        df1=[str(int) for int in df1]
        cyg_input = sign_concat.join(df1)

        if batch==0:
            final_df=cygnus_request(cyg_input,report)
        else:
            df_cyg=cygnus_request(cyg_input,report)

            frames = [final_df, df_cyg]

            final_df = pd.concat(frames)
        batch+=1

    df_wo_status = final_df

    df_wo_status = df_wo_status[['item7','item15']]
    df_wo_status.columns = ['WORK ORDER', 'PLANNED DATE']

    return df_wo_status

def get_ratio(param_1,param_2):

    result = SM(None, param_1, param_2).ratio()

    return result

def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print('\n')

def pct_next_labor_day(date):
    
    """
    Checks value and determine if is a labor day or not comparing to 
    an array with holidays too
    :param datetime date: value to evaluate
    :return input date updated 
    """

    days=0
    hours=0
    final_date = date + datetime.timedelta(days)
    if date.day_name() == 'Saturday':
        final_date = final_date + datetime.timedelta(days=+2)
        hours = hours + 48 + 6
    elif date.day_name() == 'Sunday':
        final_date = final_date + datetime.timedelta(days=+1)
        hours = hours + 24 + 6
    while final_date.strftime("%m/%d/%Y") in txt_array('holidays.txt'):
        final_date = final_date + datetime.timedelta(days=+1)
        hours = hours + 24
        if final_date.day_name() == 'Saturday':
            final_date = final_date + datetime.timedelta(days=+2)
            hours = hours + 48 + 6
        elif final_date.day_name() == 'Sunday':
            final_date = final_date + datetime.timedelta(days=+1)
            hours = hours + 24 + 6

    #return final_date,hours (Adding total hours)

    return final_date

def previous_labor_day_to_today():

    commit_goal = (format_date(5) - previous_labor_day()).days

    return commit_goal

def api_request(column,po_list,Trantype,report,signal):

    subprocess.call('sh API_Connection/Request.sh '+str(column)+' '+str(po_list)+' '+str(Trantype)+' '+str(report)+' '+str(signal))

    try:    

        with open(path()+'\Json_Files\Cygnus_API.json', 'r') as f:
            data = json.load(f)

        df = pd.DataFrame(json.loads(pd.DataFrame([data])['JSONResponse'][0]))

        return df

    except:

        df = pd.DataFrame()

        return df

def signals(df ,column, trant_type, report, signal):

    """
    :param dataframe df: main Dataframe
    :param str column: column name to use
    :param str trant_type: Api's name
    :param str report: SHORT or EXTENDED depends the parameters quantity (2 or 3)
    :param int signal: 3rd parameter (optional)
    :return: input dataframe updated
    """
    
    first = 0
    last = 500
    sub_value = 500
    batch = 0

    while sub_value == 500:

        df1 = df[column].iloc[first:last]

        sub_value = len(df1.axes[0])

        first = last
        last = last + sub_value
        df1=[str(int) for int in df1]
        cyg_input = ",".join(df1)

        print(cyg_input)

        if batch==0:

            final_df=api_request(column,cyg_input, trant_type, report, signal)

        else:

            df_cyg=api_request(column,cyg_input, trant_type, report, signal)

            if df_cyg.empty == False :

                frames = [final_df, df_cyg]
                final_df = pd.concat(frames)
            
        batch+=1

    try:

        final_df.reset_index(drop=True,inplace=True)
        final_df.to_excel(path()+'\Files\\'+str(trant_type)+'.xlsx', index=False)

        return final_df

    except:

        return False

def datetime_convertion(df,column):

    df[column] = df[column].astype(str).str.replace("\.0$", "",regex=True)

    return pd.to_datetime(df[column])

def fill_holds(df):

    hpe_Holds_s4 = pd.read_excel(share_path()+'\Master_Analysis\PO_VIEWER.xlsx', usecols=['WORK ORDER','HPE RESTRICTIONS'])
    hpe_Holds_fusion = pd.read_excel(path()+'\Files\860_Holds.xlsx', usecols=['PO','HPE RESTRICTIONS'])
    hold_tool_cygnus = pd.read_excel(path()+'\Files\hold_tool_report.xlsx', usecols=['ID','HOLD TYPE'])

    df['WORK ORDER'] = df['WORK ORDER'].astype(str).str.replace('.0', '', regex=False)
    hpe_Holds_s4['WORK ORDER'] = hpe_Holds_s4['WORK ORDER'].astype(str).str.replace('.0', '', regex=False)
    hold_tool_cygnus['ID'] = hold_tool_cygnus['ID'].astype(str).str.replace('.0', '', regex=False)

    hold_tool_cygnus = hold_tool_cygnus.rename({'ID': 'WORK ORDER', 'HOLD TYPE': 'INTERNAL HOLDS'}, axis=1)

    df['PO'] = df['PO'].astype(str) 
    df_fusion = df[df['PO'].str.contains('52C')]
    df = df[~df['PO'].str.contains('52C')]

    hpe_Holds_s4['WORK ORDER'] = hpe_Holds_s4['WORK ORDER'].astype(str).str.replace('.0', '', regex=False)
    df['WORK ORDER'] = df['WORK ORDER'].astype(str).str.replace('.0', '', regex=False)

    df = df.merge(hpe_Holds_s4,on='WORK ORDER', how='left').drop_duplicates().reset_index(drop=True)
    df_fusion = df_fusion.merge(hpe_Holds_fusion,on='PO', how='left').drop_duplicates().reset_index(drop=True)
    df = pd.concat([df,df_fusion])

    df = df.merge(hold_tool_cygnus,on='WORK ORDER', how='left').drop_duplicates().reset_index(drop=True)

    df_temp = df[df['INTERNAL HOLDS'].isnull()]
    df = df[~df['INTERNAL HOLDS'].isnull()]
    df_temp = drop_list_of_columns(['INTERNAL HOLDS'],df_temp)
    hold_tool_cygnus = hold_tool_cygnus.rename({'WORK ORDER': 'PO'}, axis=1)
    df_temp = df_temp.merge(hold_tool_cygnus,on='PO', how='left').drop_duplicates().reset_index(drop=True)

    df = pd.concat([df,df_temp]).reset_index(drop=True)

    df = df.drop_duplicates(subset='SO ID', keep='first')
    df.fillna('NA',inplace=True)

    df.to_excel(path()+'\Files\\Fill_holds.xlsx',index = False)

    return df

def current_date():

    dt = datetime.datetime.strptime(str(dates_operations('less',0)), '%Y-%m-%d')

    return dt

def rdd_validation(df):
    
    df['ITEM RDD'] = pd.to_datetime(df['ITEM RDD'])
    df.fillna('NA', inplace=True)

    df_temp = df[df['SHIP TYPE'].str.contains('SC')]
    df = df[~df['SHIP TYPE'].str.contains('SC')]
    #Align Max RDD
    df_max_RDD = df_temp.sort_values('ITEM RDD', ascending=False).drop_duplicates(subset='PO',keep='first').reset_index(drop=True)
    df_temp = upgrade_column(df_temp,df_max_RDD,'PO','ITEM RDD',5)

    df = pd.concat([df,df_temp])
    
    return df

def cookie_cygnus():

    #Login to CyGNUS and save cooke with credentials
    subprocess.call('sh bash_scripts/Login.sh')

def txt_array_2d(z_file):

    with open(share_path()+'\Files_Format\\'+z_file) as textFile:

        lines = [line.split() for line in textFile]

    return lines

def week_day():    
    
    current_day = datetime.datetime.now()    
    week_day = calendar.day_name[current_day.weekday()]   

    return week_day

def previous_master_share():
    
    server = 'https://fiicorp.sharepoint.com'
    filename = 'Previous_Master'
    file_directory = path()+'\Files'

    site = 'https://fiicorp.sharepoint.com/:x:/r/sites/CABGL10/Departments/Order%20Management/01%20Master%20Consolidado/Master%20Final/Master%20'+previous_labor_day().strftime('%m%d%Y')+'.xlsx'
    s = sharepy.connect(server,txt_array('Credentials.txt')[2],txt_array('Credentials.txt')[3])

    s.getfile_sharepy_filename(site,filename,file_directory)


def get_SOC_SAB():

    flat_arr = np.reshape(txt_array_2d('SOC_SAB.txt'), -1, order='F')
    SOC_array = flat_arr[:len(flat_arr)//2]
    SAB_array = flat_arr[len(flat_arr)//2:]

    for x in SOC_array:
        x = pd.to_datetime(x)
        position = 0
        if (x.month == current_date().month) & (x.year == current_date().year):
            SOC_date = x
            break
        position += 1

    SAB_date = pd.to_datetime(SAB_array[position])

    return SOC_date,SAB_date


def possible_cases(df,case):

    df.reset_index(drop = True)
    
    subgroup = df[df['BUCKET'].str.contains(case) == True]

    if len(subgroup) == len(df):
        df['CASE'] = case +' - LINKED TO: FGI'

def priority_bucket(df):

    priority = [['SHORT TBC',1],['SHORT',2],['SHORT SOC',3],['SHORT SAB',4],['CTB',5],['KITTING',6],['WIP',7],['PACKING',8]]
    order_bucket = pd.DataFrame(priority, columns=['ID', 'PRIORITY'])

    df['ID'] = np.where(df['BUCKET'].str.contains('SHORT'),np.where(df['BUCKET'].str.contains('SOC'),'SHORT SOC',
                                np.where(df['BUCKET'].str.contains('SAB'),'SHORT SAB',
                                np.where(df['BUCKET'].str.contains('TBC'),'SHORT TBC','SHORT'))),df['BUCKET'])

    df['BUCKET'] = np.where(df['BUCKET'].str.contains('SHORT'),np.where(df['BUCKET'].str.contains('SOC'),'SHORT SOC',
                                np.where(df['BUCKET'].str.contains('SAB'),'SHORT SAB',
                                np.where(df['BUCKET'].str.contains('TBC'),'SHORT TBC','SHORT ('+df['RECOVERY DAYS']+')'))),df['BUCKET'])

    case_assignment_temp = df.merge(order_bucket,on = 'ID', how = 'left')
    case_assignment_temp = case_assignment_temp[['PO','BUCKET','PRIORITY']].sort_values(by='PRIORITY').drop_duplicates(subset='PO',keep='first').reset_index(drop = True)
    case_assignment_temp.rename(columns={'BUCKET':'FINAL STATUS'},inplace = True)

    df = df.merge(case_assignment_temp[['PO','FINAL STATUS']],on = 'PO',how = 'left')
    df.drop(columns=['BUCKET','RECOVERY DAYS','ID'],inplace = True)
    
    return df

def assing_buckets(df,column_name,reference_column):

    df.fillna('NA',inplace = True)

    bins = [0,5]
    for i in range(0,len(df.index)):

        if i % 10 == 0 and i > 1:

            bins = bins + [i]

    df[column_name] = pd.cut(df[reference_column],bins).astype(str)

    array = [['\.0$',''],['(',''],[',',' to'],[']','']]

    for i in array:

        df[column_name] = df[column_name].str.replace(i[0],i[1], regex = True)

    return df

def zpp9_format():

    df =  pd.read_csv(path()+'\Files\zpp9.xls', skiprows=[0,1], sep='\\t', thousands=',' , engine='python', encoding='ISO-8859-1')

    return df