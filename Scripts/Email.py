
from My_Book import txt_array,format_date,path
import win32com.client as win32

def send_email(recipient_email,cc_recipient_email,subject,df):

    shippeable = path()+"\Files\\Shippable_"+format_date(3)+".xlsx"

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = recipient_email
    mail.CC = cc_recipient_email
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
    <body>Buen dia Team,<br><br>
            
            Adjunto Shippable """+format_date(4)+""" File.
            <br><br>

            """+df.to_html(classes="df", index=False)+""" 

            <br><br>
            Saludos/Regards!<br>
            Erik Carbajal<br>
            <b>OM</b></font>
	    </body>
    </html>
    """
    mail.Attachments.Add(Source=shippeable)    
    mail.Send()