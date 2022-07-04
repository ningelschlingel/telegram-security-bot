#!/bin/bash

#: - Get location of this file (https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

###### +++++++++++++++++++++++++++++++++++ ######
###### +++ Install python requirements +++ ######
###### +++++++++++++++++++++++++++++++++++ ######

install_req () { # To be run without sudo, pass SCRIPT_DIR as #1 parameter

    echo "Installing virtualenv ..."
    #: - Installing virtualenv
    python3 -m pip install virtualenv

    #: - Create and activate venv
    #: - ${1} referring to arg #1
    echo "Creating virtual environment ${1}/venv ..."
    python3 -m virtualenv "${1}/venv"
    source "${1}/venv/bin/activate"

    #: - Install python requirements
    echo "Installing python dependencies ..."
    python3 -m pip install -r "${1}/requirements.txt"

    #: - Deactivate venv
    deactivate

}

export -f install_req

#: - Run function as logged in user
su "$(logname)" -c "install_req ${SCRIPT_DIR}"

###### ++++++++++++++++++++++++++++++ ######
###### +++ Configure app service  +++ ######
###### ++++++++++++++++++++++++++++++ ######

echo "Preparing app service ..."

sed -i -e "s#{directory}#$SCRIPT_DIR#g" "${SCRIPT_DIR}/app.service"

echo "Copying service ..."
#: [sudo]
#: - Copy service file to systemd
cp "${SCRIPT_DIR}/app.service" "/lib/systemd/system"

echo "Update services ..."
#: [sudo]
#: - Reload to get access to new configuratons
systemctl daemon-reload

echo "Enable app service ..."
#: [sudo]
#: - Enable app service to start automatically after reboot
systemctl enable app.service

echo "Start app service ..."
#: [sudo]
#: - Start app service now without reboot
systemctl start app.service

echo "DONE"