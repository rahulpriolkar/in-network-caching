sudo apt update

sudo apt install python3-matplotlib
sudo apt install python3-numpy

sudo apt install git

mkdir project
cd project/

git clone https://github.com/jafingerhut/p4-guide.git

./p4-guide/bin/install-p4dev-v6.sh |& tee log.txt

git clone https://github.com/p4lang/tutorials.git

cd ~
mv ./netcache ./project/tutorials/exercises
mv ./simple_switch ./project/tutorials/simple_switch


