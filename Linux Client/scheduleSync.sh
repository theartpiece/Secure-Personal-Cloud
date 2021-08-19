#! /bin/bash

echo -n "Enter how often would you like to sync(mins): "
read min

if ! [[ "$min" =~ ^[0-9]+$ ]]; then
    echo "Sorry integers only"
    exit 1
else
    min="/$min"
    echo "*$min * * * * /usr/bin/sync.sh" | crontab -
fi

#echo  "Enter at what time during the dat would you like to sync."
#echo -n "hour: "
#read hr
#echo -n "min: "
#read min

#"visite:\"$site\""
#crontab -l | echo "* * * * *  /usr/bin/sync.sh" > EDITOR=cat crontab -e

#(crontab -l && echo "* * * * *  /usr/bin/sync.sh") | crontab -


