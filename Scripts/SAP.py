# Author: Rodrigo Bedolla Fuerte
# Department: Order management
# Bedolla Fuerte, R. (Aug 28, 2021). Ship status (version No 1.1 | last update(Dec 06, 2021)). Cd. Juarez: Foxconn eCMMS S.A. DE C.V. V1.1

# Importing the Libraries
import win32com.client
import sys
import subprocess
import time
import subprocess
from My_Book import txt_array, path

# This function will Login to SAP from the SAP Logon window
def saplogin(file_flag):

    try:

        sap_path = r"C:/Program Files (x86)/SAP/FrontEnd/SAPgui/saplogon.exe"
        subprocess.Popen(sap_path)
        time.sleep(5)

        SapGuiAuto = win32com.client.GetObject('SAPGUI')
        if not type(SapGuiAuto) == win32com.client.CDispatch:
            return

        application = SapGuiAuto.GetScriptingEngine
        if not type(application) == win32com.client.CDispatch:
            SapGuiAuto = None
            return

        #SAP PRODUCTION
        connection = application.OpenConnection("[A1] PA PRD-PRI  (H249)", True)

        if not type(connection) == win32com.client.CDispatch:
            application = None
            SapGuiAuto = None
            return

        session = connection.Children(0)
        if not type(session) == win32com.client.CDispatch:
            connection = None
            application = None
            SapGuiAuto = None
            return

        session.findById("wnd[0]").maximize
        
        #Login PRD
        session.findById("wnd[0]/usr/txtRSYST-MANDT").text = txt_array('SAP_Credentials.txt')[0]
        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = txt_array('SAP_Credentials.txt')[1]
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = txt_array('SAP_Credentials.txt')[2]

        session.findById("wnd[0]").sendVKey(0)

        if session.Children.Count > 1:
         session.findById("wnd[1]/usr/radMULTI_LOGON_OPT2").select()
         session.findById("wnd[1]/usr/radMULTI_LOGON_OPT2").setFocus()
         session.findById("wnd[1]/tbar[0]/btn[0]").press()

        #Download ZSD5 File
        if file_flag == 1:

         session.findById("wnd[0]/tbar[0]/okcd").text = "/NZSD5"
         session.findById("wnd[0]").sendVKey(0)
         session.findById("wnd[0]/usr/radR3").select()
         session.findById("wnd[0]/usr/ctxtP_WERKS").text = "S315"
         session.findById("wnd[0]/usr/radR3").setFocus()
         session.findById("wnd[0]/usr/btn%_P_PO_%_APP_%-VALU_PUSH").press()
         session.findById("wnd[1]/tbar[0]/btn[23]").press()
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\PO.txt'
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").caretPosition = 49
         session.findById("wnd[2]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/tbar[0]/btn[8]").press()
         session.findById("wnd[0]/tbar[1]/btn[8]").press()
         session.findById("wnd[0]/tbar[0]/okcd").text = "%PC"
         session.findById("wnd[0]").sendVKey(0)
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").select()
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").setFocus()
         session.findById("wnd[1]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\zsd5.xls'
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").caretPosition = 50
         session.findById("wnd[1]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/tbar[0]/btn[0]").press()
         #close session SAP
         session.findById("wnd[0]").close()
         session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        #End ZSD5 File

        elif file_flag == 2:
         session.findById("wnd[0]/tbar[0]/okcd").text = "/nzsd6"
         session.findById("wnd[0]").sendVKey(0)
         session.findById("wnd[0]/usr/chkR1").selected = 0
         session.findById("wnd[0]/usr/radR4").select()
         session.findById("wnd[0]/usr/ctxtP_WERKS").text = "S315"
         session.findById("wnd[0]/usr/radR4").setFocus()
         session.findById("wnd[0]/usr/btn%_S_SO_%_APP_%-VALU_PUSH").press()
         session.findById("wnd[1]/tbar[0]/btn[23]").press()
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\SO.txt'
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").caretPosition = 49
         session.findById("wnd[2]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/tbar[0]/btn[8]").press()
         session.findById("wnd[0]/tbar[1]/btn[8]").press()
         session.findById("wnd[0]/tbar[0]/okcd").text = "%pc"
         session.findById("wnd[0]").sendVKey(0)
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").select()
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").setFocus()
         session.findById("wnd[1]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\zsd6.xls'
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").caretPosition = 50
         session.findById("wnd[1]").sendVKey(0)
         session.findById("wnd[1]/tbar[0]/btn[0]").press()
         session.findById("wnd[0]/tbar[0]/okcd").text = "/nzsd6a"
         session.findById("wnd[0]").sendVKey(0)
         session.findById("wnd[0]/usr/chkR1").selected = 0
         session.findById("wnd[0]/usr/ctxtP_WERKS").text = "S315"
         session.findById("wnd[0]/usr/ctxtS_SO-LOW").setFocus()
         session.findById("wnd[0]/usr/ctxtS_SO-LOW").caretPosition = 0
         session.findById("wnd[0]/usr/btn%_S_SO_%_APP_%-VALU_PUSH").press()
         session.findById("wnd[1]/tbar[0]/btn[23]").press()
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\SO.txt'
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").caretPosition = 49
         session.findById("wnd[2]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/tbar[0]/btn[8]").press()
         session.findById("wnd[0]").sendVKey(8)
         session.findById("wnd[0]/tbar[0]/okcd").text = "%pc"
         session.findById("wnd[0]").sendVKey(0)
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").select()
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").setFocus()
         session.findById("wnd[1]").sendVKey(0)
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\zsd6a.xls'
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").caretPosition = 51
         session.findById("wnd[1]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/tbar[0]/btn[0]").press()

         #close session SAP
         session.findById("wnd[0]").close()
         session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        
        elif file_flag == 3:

         session.findById("wnd[0]/tbar[0]/okcd").text = "/ncoois"
         session.findById("wnd[0]").sendVKey(0)
         session.findById("wnd[0]/usr/ssub%_SUBSCREEN_TOPBLOCK:PPIO_ENTRY:1100/ctxtPPIO_ENTRY_SC1100-ALV_VARIANT").text = "/OM"
         session.findById("wnd[0]/usr/ssub%_SUBSCREEN_TOPBLOCK:PPIO_ENTRY:1100/ctxtPPIO_ENTRY_SC1100-ALV_VARIANT").setFocus()
         session.findById("wnd[0]/usr/ssub%_SUBSCREEN_TOPBLOCK:PPIO_ENTRY:1100/ctxtPPIO_ENTRY_SC1100-ALV_VARIANT").caretPosition = 3
         session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSEL_00/ssub%_SUBSCREEN_SELBLOCK:PPIO_ENTRY:1200/btn%_S_KDAUF_%_APP_%-VALU_PUSH").press()
         session.findById("wnd[1]/tbar[0]/btn[23]").press()
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\SO.txt'
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").caretPosition = 72
         session.findById("wnd[2]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/tbar[0]/btn[8]").press()
         session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSEL_00/ssub%_SUBSCREEN_SELBLOCK:PPIO_ENTRY:1200/chkP_LOEKZ").selected = -1
         session.findById("wnd[0]/usr/tabsTABSTRIP_SELBLOCK/tabpSEL_00/ssub%_SUBSCREEN_SELBLOCK:PPIO_ENTRY:1200/chkP_LOEKZ").setFocus()
         session.findById("wnd[0]/tbar[1]/btn[8]").press()
         session.findById("wnd[0]/usr/cntlGRID_0100/shellcont/shell").pressToolbarContextButton("&EXPORT")
         session.findById("wnd[0]/usr/cntlGRID_0100/shellcont/shell").selectContextMenuItem("&PC")
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").select()
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").setFocus()
         session.findById("wnd[1]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\coois.xls'
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").caretPosition = 75
         session.findById("wnd[1]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/tbar[0]/btn[0]").press()

         #close session SAP
         session.findById("wnd[0]").close()
         session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()

        elif file_flag == 4:

         session.findById("wnd[0]/tbar[0]/okcd").text = "/NZPP9"
         session.findById("wnd[0]").sendVKey(0)
         session.findById("wnd[0]/usr/ctxtSP$00003-LOW").text = "S315"
         session.findById("wnd[0]/usr/btn%_SP$00001_%_APP_%-VALU_PUSH").press()
         session.findById("wnd[1]/tbar[0]/btn[23]").press()
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\ID.txt'
         session.findById("wnd[2]/usr/ctxtRLGRAP-FILENAME").caretPosition = 75
         session.findById("wnd[2]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/tbar[0]/btn[8]").press()
         session.findById("wnd[0]/tbar[1]/btn[8]").press()
         session.findById("wnd[0]/tbar[1]/btn[45]").press()
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").select()
         session.findById("wnd[1]/usr/sub:SAPLSPO5:0101/radSPOPLI-SELFLAG[1,0]").setFocus()
         session.findById("wnd[1]/tbar[0]/btn[0]").press()
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").text = path()+'\Files\zpp9.xls'
         session.findById("wnd[1]/usr/ctxtRLGRAP-FILENAME").caretPosition = 80
         session.findById("wnd[1]/tbar[0]/btn[0]").press()

         #close session SAP
         session.findById("wnd[0]").close()
         session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        
    except Exception as e:
        
        sap_error = str(sys.exc_info()[0])
        print('Error: '+sap_error+' | '+str(e))
    
    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None

#saplogin() #ejecutar sap