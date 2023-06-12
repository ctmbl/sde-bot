#!/bin/sh

PATH=$(/usr/bin/getconf PATH || /bin/kill $$)
NAME="sde-bot"

RED=$(tput setaf 1)
NORMAL=$(tput sgr0)


# TODO: don't run the command if there is nothinf to stop
OLD_CONT_ID=$(docker ps --all --quiet --filter name=${NAME} --format="{{.ID}}")
docker kill $OLD_CONT_ID
docker container rm $OLD_CONT_ID

docker build -t ${NAME} .
docker run --interactive --tty --detach\
    --name ${NAME} \
    ${NAME}:latest

