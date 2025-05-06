#!/bin/bash

echo "Running in production mode..."
if [ ! -f docker-compose-production.yml ]; then
  echo "docker-compose-production.yml not found. Please ensure you are in the correct directory."
  exit 1
fi

mkdir -p ~/kkook-app
cd ~/kkook-app

echo "Current directory: $(pwd)"

sudo docker compose -f docker-compose-production.yml down
sudo docker compose --env-files /tmp/.env.production -f docker-compose-production.yml up -d

echo "Production environment is up and running."
