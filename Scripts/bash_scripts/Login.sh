usr="erikruiz"
pass="Magaly2508"

curl -s -c bash_scripts/cookie.txt 'http://10.19.17.100/CyGNUS/' > bash_scripts/home.txt

curl -s -X POST 'http://10.19.17.100/API/CyGNUS/authentication' \
    -H 'Connection: close' \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://10.19.17.100' \
    -H 'Referer: https://10.19.17.100/CyGNUS/login.jsp' \
    -H 'client_name: HPE' \
    -d '{"userName":"'$usr'","password":"'$pass'","authType":"standard","email":""}' > bash_scripts/auth_result.json

py bash_scripts/read_json.py
data_raw=$(cat data_raw.txt)

curl -s -b bash_scripts/cookie.txt 'http://10.19.17.100/CyGNUS/srvLogin?' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.9,es-MX;q=0.8,es;q=0.7' \
  -H 'Connection: close' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -H 'Origin: http://10.19.17.100' \
  -H 'Referer: http://10.19.17.100/CyGNUS/login.jsp' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  --cookie-jar bash_scripts/cookie.txt \
  --data-raw "$data_raw" \
  --compressed > bash_scripts/login_output.json