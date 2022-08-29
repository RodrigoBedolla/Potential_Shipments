curl -X POST 'http://10.19.17.100/API/CyGNUS/OMDATA_API' \
    -H 'Connection: close' \
    -H 'Content-Type: application/json' \
    -d '{"'$1'": "'$2'", "strTrantype": "'$3'", "_strType": "'$4'"}' \
