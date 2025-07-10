# Author: Rodrigo Bedolla Fuerte
# Department: Order management
# Bedolla Fuerte, R. (Dec 15, 2021). Email_Alerts (version No 1.1 | last update(Dec 15, 2021)). Cd. Juarez: Foxconn eCMMS S.A. DE C.V. V1.1

from My_Book import txt_array,format_date,path
import win32com.client as win32

def send_mail_alert(recipient_email, subject, next_try,df):
    
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = recipient_email
    mail.Subject = subject
    mail.HTMLBody = """<html>
    <font face="Calibri">
    <style>
                    table{
                        border-collapse: collapse;
                        margin: 10px 0;
                        font-size: 0.9em;
                        font-family: sans-serif;
                        min-width: 400px;
                        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                        }
                        thead{
                        background-color: #163A5D;
                        color: #ffffff;
                        text-align: left;
                        }
                        th,td{
                        padding: 0px 20px;
                        }
                        tr {
                        border-bottom: 1px solid #dddddd;
                        }

                        tbody tr:nth-of-type(even) {
                        background-color: #f3f3f3;
                        }

                        tbody tr:last-of-type {
                        border-bottom: 1px solid #163A5D;
                        }
                        tbody tr.active-row {
                        font-weight: bold;
                        color: #163A5D;
                }
                </style>
    <body>Buen dia Team!,<br><br>
            
            Execution Error: """+next_try+"""<br><br><b>Error:</b>
            <br><br>

            """+df.to_html(classes="df", index=False)+""" 

            <br><br>
            Saludos/Regards!<br>
            BI Team<br>
            <b>OM</b></font>
	    </body>
    </html>
    """
    mail.Send()