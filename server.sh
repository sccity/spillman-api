#!/bin/bash

docker_compose="docker-compose -f docker-compose.yml"

[ -f config/dev/settings.yaml ] || { echo "Missing dev settings.yaml file. Exiting."; exit 1; }
[ -f config/prod/settings.yaml ] || { echo "Missing prod settings.yaml file. Exiting."; exit 1; }
[ -f config/nginx/spillman-api-dev.conf ] || { echo "Missing spillman-api-dev.conf file. Exiting."; exit 1; }
[ -f config/nginx/spillman-api-prod.conf ] || { echo "Missing spillman-api-prod.conf file. Exiting."; exit 1; }

if [[ $1 = "start" ]]; then
  echo "Starting Spillman API..."
	$docker_compose up -d
elif [[ $1 = "stop" ]]; then
	echo "Stopping Spillman API..."
	$docker_compose stop
elif [[ $1 = "restart" ]]; then
	echo "Restarting Spillman API..."
  $docker_compose down
  $docker_compose start
elif [[ $1 = "down" ]]; then
	echo "Tearing Down Spillman API..."
	$docker_compose down
elif [[ $1 = "rebuild" ]]; then
	echo "Rebuilding Spillman API..."
	$docker_compose down --remove-orphans
	$docker_compose build --no-cache
elif [[ $1 = "update" ]]; then
	echo "Updating Spillman API..."
	$docker_compose down --remove-orphans
	git pull origin prod
elif [[ $1 = "shell" ]]; then
	echo "Entering Spillman API Shell..."
	docker exec -it spillman-api sh
else
	echo "Unkown or missing command..."
fi