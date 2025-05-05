#!/bin/bash

echo "[TEST] Running in test mode..."
if [ ! -f docker-compose-test.yml ]; then
  echo "docker-compose-test.yml not found. Please ensure you are in the correct directory."
  exit 1
fi

if [ ! -f .env.test ]; then
  echo "[NO_ENV_ERROR] .env.test not found. Please ensure you are in the correct directory."
  exit 1
fi

echo "Current directory: $(pwd)"
docker compose --env-file .env.test -f docker-compose-test.yml up -d
