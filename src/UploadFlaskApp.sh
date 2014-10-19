#!/bin/bash

# Prepare for upload

# Tar all the *.py files in dir `flask` to deploy/flaskapp.tar
mkdir -p deploy
tar -cf deploy/flaskapp.tar flask/*.py
gzip deploy/flaskapp.tar


# Upload zipped build file to server
USER=ubuntu
HOST=quizas.me
APPDIR="~/flask-app/"
scp deploy/flaskapp.tar.gz $USER@$HOST:$APPDIR/latest/flaskapp.tar.gz
ssh $USER@$HOST -C "$APPDIR/UpdateFlask.sh"


# Tidy up local working environment
rm deploy/flaskapp.tar.gz
