#!/bin/bash

#: - Get location of this file (https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

###### ++++++++++++++++++++++++++++++ ######
###### +++ Configure app service  +++ ######
###### ++++++++++++++++++++++++++++++ ######

echo "${SCRIPT_DIR}"

sed -i -e "s#{directory}#$SCRIPT_DIR#g" "${SCRIPT_DIR}/app.service"

echo "DONE"