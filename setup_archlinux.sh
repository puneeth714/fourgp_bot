#!/bin/bash

# Check if the distro is not ArchLinux
if [[ ! -f /etc/arch-release ]]; then
    echo "This script is only for ArchLinux"
    exit 1
fi


declare no_env=0
declare env_dir="python3-env"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -n|--no-env)
            no_env=1
            shift
        ;;
        -d|--env-dir)
            env_dir="$2"
            shift
            shift
        ;;
        
        -h|--help)
            echo "Usage: $0 [OPTION]..."
            echo "Install required packages and python libraries"
            echo "  -n, --no-env    Do not create virtual environment"
            echo "  -d, --env-dir   Specify virtual environment directory"
            echo "  -h, --help      Print this help"
            exit 0
        ;;
        *)
            echo "Unknown option $key"
            exit 1
        ;;
    esac
done

# Install python3, pip, numpy matplotlib scikit-learn pandas scipy cython
sudo pacman -Sy
sudo pacman -S --needed --noconfirm python3 python-{pip,numpy,matplotlib,scikit-learn,pandas,scipy} git
sudo pip install cython

if [[ $no_env -eq 0 ]]; then
    echo "Creating virtual environment in $env_dir"
    python3 -m venv $env_dir
    source $env_dir/bin/activate
elif [[ $no_env -eq 1 ]]; then
    echo "No virtual environment created"
fi

unset no_env env_dir


# Install ta-lib
# Clone ta-lib aur package
git clone https://aur.archlinux.org/ta-lib.git
cd ta-lib
makepkg -si
cd ..
rm -rf ta-lib


# install all packages in requirements.txt
pip install -r requirements.txt
echo "All required packages are installed successfully!!!"