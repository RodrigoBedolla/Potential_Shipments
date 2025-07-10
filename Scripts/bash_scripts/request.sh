
if [[ $3 == "HOLD_TOOL" ]] 
then
    
    sh bash_scripts/hold_tool_report.sh $1 $2 > ../Json_Files/Cygnus_Files.json;

elif [[ $3 == "860_PRIORITY_CODES" ]] 
then

    sh bash_scripts/860_priority_codes.sh $1 $2> ../Json_Files/Cygnus_Files.json;

elif [[ $1 == "SHIP_HISTORY" ]] 
then

    sh bash_scripts/ship_history.sh $2> ../Json_Files/Cygnus_Files.json;
    
elif [[ $2 == "PRD_SUMMARY" ]] 
then
    sh bash_scripts/prd_summary.sh "$1" "$3" | tee ../Json_Files/Cygnus_Files.json;
fi