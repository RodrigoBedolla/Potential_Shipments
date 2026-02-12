
curl -b bash_scripts/cookie.txt 'https://10.19.17.100/CyGNUS/srvcygnus' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Connection: close' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -H 'From-Submit: true' \
  -H 'Origin: https://10.19.17.100' \
  -H 'Referer: https://10.19.17.100/CyGNUS/' \
  -d 'data=[{"param":"strHoldType","val":"ALL"},
            {"param":"strHoldStatus","val":"1"},
            {"param":"dtini","val":"'$1'"},
            {"param":"dtfin","val":"'$2'"},
            {"param":"strMasterTrantype","val":"HoldToolM"},
            {"param":"strTrantype","val":"HoldToolReport"},
            {"param":"environment","val":"CyGNUS"},
            {"param":"strClient","val":"HPE"},
            {"param":"strUserName","val":""}]' \