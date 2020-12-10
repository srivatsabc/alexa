#!/bin/sh
# Author - Srivatsa

git_repo=$1
cd ${git_repo}

git add .
git commit -m "`date`"
git push
exit 0