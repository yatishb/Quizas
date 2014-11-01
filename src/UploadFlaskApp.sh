#!/bin/bash

# Prepare for upload

# Tar all the *.py files in dir `flask` to deploy/flaskapp.tar
DEPLOYDIR=deploy
mkdir -p $DEPLOYDIR
tar -cf $DEPLOYDIR/flaskapp.tar startserver.py \
                            flaskapp/*.py \
                            flaskapp/**/*.py \
                            flaskapp/templates/*.html
gzip $DEPLOYDIR/flaskapp.tar


# Upload zipped build file to server
USER=ubuntu
HOST=quizas.me
APPDIR="~/flask-app/"
scp $DEPLOYDIR/flaskapp.tar.gz $USER@$HOST:$APPDIR/latest/flaskapp.tar.gz
ssh $USER@$HOST -C "$APPDIR/UpdateFlask.sh"


# Tidy up local working environment
rm $DEPLOYDIR/flaskapp.tar.gz
