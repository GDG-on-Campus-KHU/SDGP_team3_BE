#! /bin/bash
# This script is used to run a PostgreSQL container for test database migrations and running.
# It will create a new PostgreSQL container.
# Usage: migrations/run_docker_postgres.sh

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker could not be found. Please install Docker to run this script."
    exit
fi
# Check if Docker is running
if ! docker info &> /dev/null
then
    echo "Docker is not running. Please start Docker to run this script."
    exit
fi
# Check if the container is already running
if [ "$(docker ps -q -f name=postgres-test)" ]; then
    echo "Container is already running. Please stop it before running this script."
    exit
fi
# Remove if the container exists
if [ "$(docker ps -aq -f status=exited -f name=postgres-test)" ]; then
    docker rm postgres-test
    echo "Container already exists. It has been removed."
    exit
fi
# Check if the image exists
if [ "$(docker images -q postgres:17.4 2> /dev/null)" == "" ]; then
    echo "Image does not exist. Please pull the image before running this script."
    exit
fi

# Run the PostgreSQL container
docker run --name postgres-test \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=1234 \
    -e POSTGRES_DB=postgres \
    -p 5432:5432 \
    -v postgres-test-volume:/var/lib/postgresql/data \
    --memory=1g \
    -d \
    postgres:17.4
