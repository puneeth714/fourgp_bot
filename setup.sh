required_packages=(gcc g++ make python3.8 python3.8-pip python3.8-dev libblas-dev liblapack-dev pybind11 rust setuptools_rust openssl libssl-dev libjpeg  )
pip_packages=(numpy matplotlib scikit-learn pandas scipy cython)

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

# Function to install a packages
InstallPackage() {
    # TODO: Check distribution and install appropriate packages
    linux_distro=$(cat /etc/os-release | grep "^ID=" | cut -d '=' -f 2)
    if [[ $linux_distro == "ubuntu" ]]; then
        sudo apt-get install $1
    fi
}


# Install required packages
echo "Installing required packages"
InstallPackage ${required_packages[@]}
post_operations "Required packages"


# Create python3.8 virtual environment
echo "Creating python3.8 virtual environment in python3.8-env folder"
python3 -m venv python3-env
source python3.8-env/bin/activate
echo "Virtual environment created.."

# Install python libraries
echo "Installing required python libraries..."
pip3 install ${pip_packages[@]}


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
    if [ ! -f /tmp/$source_file ]; then # CHeck if source file is already present
        echo "$source_file is not present in /tmp, downloading it"
        wget $source -O /tmp/$source_file   # Download source file
    else
        echo "$source_file already exists. Using it"
    fi
    
    echo "Extracting $source_file into $extract_dir"
    tar -xzf /tmp/$source_file  # Extract source file
    cd $extract_dir 
    
    ./configure && make -j$(nproc)
    post_operations "TA_Lib"   
    sudo make install   # Install TA_Lib into system, need root access!!
    post_operations "TA_Lib system"
    
    cd .. && rm -rf $extract_dir # Remove build directory
    unset source source_file extract_dir     # Delete uneeded variables
else
    echo "ta-lib is already installed. Continuing with installation"
fi



# install all packages in requirements.txt
pip install -r requirements.txt
post_operations "requirements"


echo "All required packages are installed successfully!!!"
