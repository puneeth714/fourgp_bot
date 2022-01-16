
# Function to check if installation succeeded
post_operations() 
{
    if [[ $? -eq 0 ]]; then
        echo "$1 installed successfully"
    else
        echo "$1 installation failed, Do you want to continue? (y/n)"
        read -r answer
        if [[ $answer =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo "Continuing with installation"
        else
            echo "Exiting"
            exit 1
        fi
    fi
}

# install cypthon
pip3 install cython
post_operations "cython"


# install talib from sources https://github.com/mrjbq7/ta-lib.git
# check if gcc is present
if [ -z "$(which gcc)" ]; then
    echo "gcc is not present, please install it"
    exit 1
fi

# Check if TA_Lib-0.4.24.tar.gz is present in /tmp
if [ ! -f /tmp/TA_Lib-0.4.24.tar.gz ]; then
    echo "TA_Lib-0.4.24.tar.gz is not present in /tmp, downloading it"
    wget https://github.com/mrjbq7/ta-lib/archive/refs/heads/master.zip -O /tmp/TA_Lib_master.zip
fi

unzip /tmp/TA_Lib_master.zip
cd ta-lib-master

python setup.py install
post_operations "ta-lib"


cd ..
rm -rf ta-lib-master
# install requirements.txt
pip3 install -r requirements.txt
post_operations "requirements.txt"