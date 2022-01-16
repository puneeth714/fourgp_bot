# install cypthon
pip3 install cython
# install talib from sources https://github.com/mrjbq7/ta-lib.git
# check if gcc is present
if [ -z "$(which gcc)" ]; then
    echo "gcc is not present, please install it"
    exit 1
fi
git clone https://github.com/mrjbq7/ta-lib.git
cd ta-lib
python setup.py install
cd ..
rm -rf ta-lib
# install requirements.txt
pip3 install -r requirements.txt