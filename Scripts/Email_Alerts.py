# Author: Rodrigo Bedolla Fuerte
# Department: Order management
# Bedolla Fuerte, R. (Dec 15, 2021). Email_Alerts (version No 1.1 | last update(Dec 15, 2021)). Cd. Juarez: Foxconn eCMMS S.A. DE C.V. V1.1

import smtplib
from email.message import EmailMessage
import ssl
from My_Book import txt_array


def send_mail_alert(recipient_email, subject, next_try, df):

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = txt_array('Credentials.txt')[2]
    msg['To'] = recipient_email

    msg.set_content('<b>Buen dia Team!</b><br><br>Execution Error: '+next_try+'<br><br><b>Error:</b><br><br>'+'''
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
                '''+df.to_html(classes="df", index=False)+'<br><br><b>Saludos!<br>Rodrigo Bedolla<br>OM.</b>', subtype='html')


    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    connection = smtplib.SMTP('SMTP.Office365.com', 587)
    connection.ehlo()
    connection.starttls(context=context)
    connection.ehlo()
    connection.login(txt_array('Credentials.txt')[2], txt_array('Credentials.txt')[3])
    connection.send_message(msg)