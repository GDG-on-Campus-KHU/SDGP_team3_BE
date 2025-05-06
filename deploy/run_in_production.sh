#!/bin/bash

echo "Running in production mode..."
if [ ! -f docker-compose-production.yml ]; then
  echo "docker-compose-production.yml not found. Please ensure you are in the correct directory."
  exit 1
fi

mkdir -p ~/kkook-app
cd ~/kkook-app

echo "Current directory: $(pwd)"

# parsing command line arguments
if [ $# -gt 0 ]; then
  echo "Using environment variables passed as arguments..."
  ENV_VARS=""
  for VAR in "$@"; do
    ENV_VARS="$ENV_VARS -e $VAR"
  done

  sudo docker compose -f docker-compose-production.yml down
  sudo docker compose $ENV_VARS -f docker-compose-production.yml up -d
else
  echo "No environment variables provided, using .env.production file..."
  exit 1
fi

echo "Production environment is up and running."
