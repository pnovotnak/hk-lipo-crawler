#! /bin/bash

#
#   This script installs *everything required for operation* where possible
#  Including libraries, and system dependencies
#

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function debian_linux() {
    echo '
!
!   You need to enter your password! What you type won\'t be shown
!'
    sudo apt-get update
    sudo apt-get install -qy python-pip python-dev build-essential
    sudo pip install --upgrade pip
    sudo pip install --upgrade virtualenv
}

function osx() {
    # Check and install pip if it's not here already
    if hash pip 2>/dev/null; then
        sudo pip install virtualenv
    else
        # Check if Homebrew is installed, otherwise install it now
        if hash brew 2>/dev/null; then
            brew install pip
        else
            ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
            brew install pip
        fi
    fi
}

if ! hash virtualenv 2>/dev/null; then
    # Check for lsb_release binary, which would indicate a linux system
    if hash lsb_release 2>/dev/null; then
        if [ "$(lsb_release -i | cut -d: -f2 | tr -d '\t' | tr -d ' ')" == *"Debian Ubuntu"* ]; then
            debian_linux
        else
            echo "I don't know how to install myself on your system. Best of luck!"
        fi
    else
        osx
    fi
fi

cd "$DIR"
virtualenv env
source env/bin/activate
pip install -r requirements.txt
