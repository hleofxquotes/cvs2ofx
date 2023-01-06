#!/bin/sh

mkdir -p input
mkdir -p output
cp data/example1.csv input/ofx.csv

docker run \
  -v "$PWD/input:/app/input" \
  -v "$PWD/output:/app/output"  \
  --user $(id -u):$(id -g) \
  python-docker \
  --input /app/input/ofx.csv \
  --output /app/output/ofx.ofx \
  -a 123456789
