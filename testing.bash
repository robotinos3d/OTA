#!/bin/bash
mkdir ./dir1

echo "file11" > ./dir1/file11.txt
echo "file12" > ./dir1/file12.txt
echo "file13" >  ./dir1/file13.txt

mkdir ./dir1/dir2

echo "file21" >  ./dir1/dir2/file21.txt
echo "file22" >  ./dir1/dir2/file22.txt
echo "file23" >  ./dir1/dir2/file23.txt


mkdir ./dir1/dir2/dir3

echo "file31" >  ./dir1/dir2/dir3/file31.txt
echo "file32" >  ./dir1/dir2/dir3/file32.txt
echo "file33" >  ./dir1/dir2/dir3/file33.txt

mkdir ./dir1/dir2/dir3/dir4

echo "file41" >  ./dir1/dir2/dir3/dir4/file41.txt
echo "file42" >  ./dir1/dir2/dir3/dir4/file42.txt
echo "file43" >  ./dir1/dir2/dir3/dir4/file43.txt

mv ./app ./tmp_app_name

mv ./dir1 ./app

./setup.bash

read -p "Presione <Enter> para terminar el test y regresar todo a su estado normal"

rm ./app -R

mv ./tmp_app_name ./app

./setup.bash

