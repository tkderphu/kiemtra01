#! /bin/bash

git clone 

cd test

docker-compose down
docker-compose up --build
docker-compose up -d