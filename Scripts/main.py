# Author: Erik Carbajal Ruiz
# Department: Order management
# Bedolla Fuerte, R. (July 09, 2022). Potential Shipments version No 1.0. Cd. Juarez: Foxconn eCMMS S.A. DE C.V. V1.0

import schedule
import time
from Shippable import *
from Execution_log import Execution_log
from Email_Alerts import *

flag = 0
error_count = 0
start = 0

def main():

    global start
    global error_count

    start = get_time()
    
    if week_day() not in txt_array('Weekend_Execution.txt'):

        Shippable_complete()
        Execution_log(start,'SUCCESS','','-')
    
    error_count = 0

    schedule.clear()
    job()  

def job():

    global error_count

    try:

        if error_count == 0:
            
            schedule.every().hour.at(":55").do(main)
            schedule.every().day.at("07:26").do(main)
            schedule.every().day.at("08:26").do(main)
            schedule.every().day.at("09:26").do(main)
            schedule.every().day.at("10:26").do(main)
            schedule.every().day.at("11:26").do(main)

        elif error_count <= 5:

            schedule.every(5).minutes.do(main)

        else:

            schedule.every(30).minutes.do(main) 

        while True:

            schedule.run_pending()
            time.sleep(1)

    except Exception as error:

        df_table = Execution_log(start,'FAIL',error,'-')

        df_table = df_table[['SCRIPT NAME','START', 'FINISH','EXECUTION TIME','PASS/FAIL','FAILURE DESCRIPTION']]

        error_count = error_count + 1

        bi_team = 'rodrigo.bedolla@fii-na.com ; erik.carbajalr@fii-na.com ; bryan.rodriguez@fii-na.com'
        error_subject = 'POTENTIAL SHIPMENTS '+ str(format_date(2))

        if error_count <= 5:

            if error_count == 1:

                send_mail_alert(bi_team, error_subject+' ERROR' , 'Proximo intento en 5 min | numero de intento: '+str(error_count), df_table)

            else:

                send_mail_alert(bi_team, error_subject+' ERROR' , 'Proximo intento en 5 min | numero de intento: '+str(error_count), df_table)

        elif error_count <= 10:

            send_mail_alert(bi_team, error_subject+' ERROR' , 'Proximo intento en 30 min | numero de intento: '+str(error_count), df_table)
        
        else:

            send_mail_alert(bi_team, error_subject+' CRITICAL ERROR' , 'Ultimo intento | numero de intento: '+str(error_count), df_table)

        if error_count <= 10:

            schedule.clear()
            job()  
job()