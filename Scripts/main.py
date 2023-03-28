# Author: Erik Carbajal Ruiz
# Department: Order management
# Bedolla Fuerte, R. (July 09, 2022). Potential Shipments version No 1.0. Cd. Juarez: Foxconn eCMMS S.A. DE C.V. V1.0

import schedule
import time
from Shippable_complete import *
from Execution_log import *
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
        Execution_log(start,'SUCCESS','')
    
    error_count = 0

    schedule.clear()
    job()  

def job():

    global error_count

    try:

        if error_count == 0:
            """
            schedule.every().day.at("05:55").do(main)
            schedule.every().day.at("07:25").do(main)
            schedule.every().day.at("15:25").do(main)
            schedule.every().day.at("23:55").do(main)
            """
            schedule.every().day.at("05:55").do(main)
            schedule.every().day.at("07:25").do(main)
            schedule.every().day.at("08:00").do(main)
            schedule.every().day.at("09:00").do(main)
            schedule.every().day.at("11:00").do(main)
            schedule.every().day.at("12:00").do(main)
            schedule.every().day.at("13:00").do(main)
            schedule.every().day.at("14:00").do(main)
            schedule.every().day.at("15:00").do(main)
            schedule.every().day.at("15:25").do(main)
            schedule.every().day.at("16:00").do(main)
            schedule.every().day.at("17:00").do(main)
            schedule.every().day.at("18:00").do(main)
            schedule.every().day.at("19:00").do(main)
            schedule.every().day.at("20:00").do(main)
            schedule.every().day.at("21:00").do(main)
            schedule.every().day.at("22:00").do(main)
            schedule.every().day.at("23:58").do(main)

        elif error_count <= 5:

            schedule.every(5).minutes.do(main)

        else:

            schedule.every(30).minutes.do(main) 

        while True:

            schedule.run_pending()
            time.sleep(1)

    except Exception as error:

        df_table = Execution_log(start,'FAIL',error)

        df_table = df_table[['SCRIPT NAME','START', 'FINISH','EXECUTION TIME','PASS/FAIL','FAILURE DESCRIPTION']]

        error_count = error_count + 1

        if error_count <= 5:

            if error_count == 1:

                send_mail_alert('rodrigo.bedolla@fii-na.com', 'POTENTIAL SHIPMENTS '+ str(format_date(2)) +' ERROR' , 'Proximo intento en 5 min | numero de intento: '+str(error_count), df_table)

            else:

                send_mail_alert('rodrigo.bedolla@fii-na.com', 'POTENTIAL SHIPMENTS '+ str(format_date(2)) +' ERROR' , 'Proximo intento en 5 min | numero de intento: '+str(error_count), df_table)

        elif error_count <= 10:

            send_mail_alert('rodrigo.bedolla@fii-na.com', 'POTENTIAL SHIPMENTS '+ str(format_date(2)) +' ERROR' , 'Proximo intento en 30 min | numero de intento: '+str(error_count), df_table)
        
        else:

            send_mail_alert('rodrigo.bedolla@fii-na.com', 'POTENTIAL SHIPMENTS '+ str(format_date(2)) +' CRITICAL ERROR' , 'Ultimo intento | numero de intento: '+str(error_count), df_table)

        if error_count <= 10:

            schedule.clear()
            job()  
job()