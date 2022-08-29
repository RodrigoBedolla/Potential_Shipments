
if [[ $3 == "HOLD_TOOL" ]] 
then
    
    sh bash_scripts/hold_tool_report.sh $1 $2 > ../Json_Files/cygnus_files.json;

elif [[ $3 == "860_PRIORITY_CODES" ]] 
then

    sh bash_scripts/860_priority_codes.sh $1 $2> ../Json_Files/cygnus_files.json;

fi