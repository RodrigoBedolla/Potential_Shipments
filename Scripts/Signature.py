# Author: Ana Barraza Reyes
# Department: Order management
# Client: -
# Ana Barraza, R. (Junio 16, 2025). Signature (version No 2.5 | last update by Ana Barraza (Junio 18, 2025)). Cd. Juarez: Foxconn eCMMS S.A. DE C.V. V1.1


from My_Book import share_path

def get_html_signature(name, mail,phone_extension):
    html_signature = fr"""
    <html>
    <head>
    <meta http-equiv=Content-Type content="text/html; charset=windows-1252">
    </head>
    <body lang=EN-US link=blue vlink="#954F72" style='word-wrap:break-word'>
    <div>
        <p class=MsoNormal><b><span style='font-size:12.0pt;font-family:"Microsoft YaHei",sans-serif'>{name}</span></b><br>
        <span style='font-size:9.5pt;font-family:"Arial",sans-serif'>Order Management | eCMMS</span><br>
        <span style='font-size:9.5pt;font-family:"Arial",sans-serif'>Foxconn Industrial Internet</span><br>
        <b>O</b>&nbsp;&nbsp;+ 656.649.9999 &nbsp;&nbsp;&nbsp; EXT:{phone_extension}<br>
        <a href="mailto:{mail}">{mail}</a> | Boulevard Oscar Flores San 8951,<br>
        Puente Alto, 32690 Cd. Juárez, Chihuahua México
        <br>
            <img src="{share_path()}\\Signatures\\Logos\\image001.png" width="95" height="31">
        </p>
    </div>
    </body>
    </html>
    """
    return html_signature

