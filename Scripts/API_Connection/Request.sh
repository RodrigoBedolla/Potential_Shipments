if [[ $4 == "SHORT" ]]
then

    sh API_Connection/S_report.sh $1 $2 $3> ../Json_Files/Cygnus_API.json;
elif [[ $4 == "EXTENDED" ]]
then
    sh API_Connection/L_report.sh $1 $2 $3 $5 > ../Json_Files/Cygnus_API.json;
fi