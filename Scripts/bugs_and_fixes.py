from My_Book import *

def partial_shipments(master,ship_status):

    wo_1 = ship_status.loc[ship_status['PRIMARY KEY'] == '141173653', 'DN QTY'].iloc[0]
    wo_2 = ship_status.loc[ship_status['PRIMARY KEY'] == '141173652', 'DN QTY'].iloc[0]

    master.loc[master['PRIMARY KEY'] == '141173653', 'OPEN QTY'] = wo_1
    master.loc[master['PRIMARY KEY'] == '141173652', 'OPEN QTY'] = wo_2
    ship_status.to_excel(path()+r'\Files\Revision.xlsx')
    return master