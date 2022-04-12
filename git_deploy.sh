#!/bin/bash

sudo -E pkill -f runserver

cd ~/flexibility_platform/git/flexibility_platform/

echo previous runserver killed : ok
cd ~/flexibility_platform/flexibility_platform/

#dir="$1"

#echo $dir

repo_url=$(git config --get remote.origin.url)

echo "****************************************************************************"
echo "Updating Repo: $dir with url: $repo_url"
echo "Starting pull in $PWD"
(git checkout master)
(git pull)


echo pull : ok

echo runserver killed : ok


pip3 install -r requirements.txt
echo dependences from requirements installed: ok

python3 manage.py runserver 0.0.0.0:9001 &

exit
