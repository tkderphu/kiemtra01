#! /bin/bash

git clone https://github.com/tkderphu/kiemtra01 test

cd test

docker compose down
docker compose up --build
docker compose up -d