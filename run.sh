#!/bin/sh

PATH=$(/usr/bin/getconf PATH || /bin/kill $$)
NAME="sde-bot"

RED=$(tput setaf 1)
NORMAL=$(tput sgr0)


# TODO: don't run the command if there is nothinf to stop
docker stop $(docker ps --all --quiet --filter ancestor=${NAME} --format="{{.ID}}")

docker build -t ${NAME} .
docker run --rm --interactive --tty --detach\
    --name ${NAME} \
    ${NAME}:latest

