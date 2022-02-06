
# Function to check if installation succeeded
post_operations()
{
    if [[ $? -eq 0 ]]; then     # If last command was successful
        echo "$1 installed successfully"
    else    # If last command returned non zero value
        read -p "$1 installation failed, Do you want to continue? (y/n)" answer
        if [[ $answer =~ ^([yY][eE][sS]|[yY])$ ]]; then # If user pressed y or Y
            echo "Continuing with installation"
        else
            echo "Exiting"  # If user pressed n or N...
            exit 1
        fi
    fi
}

# install cython
if [[ -z "$(pip show cython)" ]]; then  # If cython is not installed
    echo "Installing cython"
    pip install cython  # Install cython
    post_operations "cython"    # Check if installation succeeded
else
    echo "cython already installed"
fi


# check if gcc is present
if [ -z "$(which gcc)" ]; then
    echo "gcc is not present, please install it"
    exit 2
fi

# Check if "ta-lib-config" is present in PATH
if [ -z "$(which ta-lib-config)" ]; then
    echo "ta-lib is not installed. Do you wanted to install it? (y/n)"
    read -r answer
    # If answer is no then exit
    if [[ $answer =~ ^([nN][oO]|[nN])$ ]]; then
        echo "ta-lib is not installed. Exiting"
        exit 3
    fi
    
    source="http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz"
    source_file=$(basename $source)
    extract_dir="ta-lib"
    
    echo "Using $source_file as source file"
    # Check if ta-lib-0.4.0-src.tar.gz is present in /tmp
    if [ ! -f /tmp/$source_file ]; then
        echo "$source_file is not present in /tmp, downloading it"
        wget $source -O /tmp/$source_file   # Download source file
    else
        echo "$source_file already exists. Using it"
    fi
    
    echo "Extracting $source_file into $extract_dir"
    tar -xzf /tmp/$source_file  # Extract source file
    cd $extract_dir # Change directory to ta-lib
    
    # Install TA_Lib
    ./configure
    make    # build ta-lib
    post_operations "TA_Lib"   
    
    
    sudo make install   # Install TA_Lib into system, need root access!!
    post_operations "TA_Lib system"
    
    cd ..
    rm -rf $extract_dir # Remove build directory
else
    echo "ta-lib is already installed. Continuing with installation"
fi



# install all packages in requirements.txt
pip install -r requirements.txt
post_operations "requirements"


echo "All required packages are installed successfully!!!"
