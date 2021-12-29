#!/bin/bash
#
# setup project. make python venv, replace project name, author etc.

set -eu

VENV_DIR=.venv
DEFAULT_PROJECT_NAME=poetry-sample
DEFAULT_PROJECT_VERSION=0.1.0
DEFAULT_PROJECT_AUTHOR_NAME=___REPLACE-AUTHOR-NAME___
DEFAULT_PROJECT_COPYRIGHT_YEAR=$(date '+%Y')
DEFAULT_PROJECT_COPYRIGHT_NAME=___REPLACE-AUTHOR-NAME___

print_msg () {
  echo "### $1"
}

err() {
  echo "### [$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

replace_txt () {
  for file in $(grep -rl $1 | grep -v .pyc | grep -v .venv | grep -e .py -e .rst -e .md -e .toml); do
    echo "replace $1 -> $2 at ${file}"
    sed -i -e "s/$1/$2/g" ${file}
  done
}

# check requirements
if ! command -v poetry &> /dev/null
then
  print_msg "poetry could not be found. please install before exec this script"
  exit
fi
if ! command -v python3 &> /dev/null
then
  print_msg "python3 could not be found. please install before exec this script"
  exit
fi

cd $(dirname $0)
print_msg "please input project infomation."
echo "What's project name? (default: ${DEFAULT_PROJECT_NAME})"
read project_name
project_name="${project_name:=${DEFAULT_PROJECT_NAME}}"

print_msg "What's project version? (default: ${DEFAULT_PROJECT_VERSION})"
read project_version
project_version="${project_version:=${DEFAULT_PROJECT_VERSION}}"

print_msg "What's project author's name? (default: ${DEFAULT_PROJECT_AUTHOR_NAME})"
read project_author_name
project_author_name="${project_author_name:=${DEFAULT_PROJECT_AUTHOR_NAME}}"

print_msg "What's project copyright year? (default: ${DEFAULT_PROJECT_COPYRIGHT_YEAR})"
read project_copyright_year
project_copyright_year="${project_copyright_year:=${DEFAULT_PROJECT_COPYRIGHT_YEAR}}"

print_msg "What's project copyright name? (default: ${DEFAULT_PROJECT_COPYRIGHT_NAME})"
read project_copyright_name
project_copyright_name="${project_copyright_name:=${DEFAULT_PROJECT_COPYRIGHT_NAME}}"

print_msg "replace project infomation"
replace_txt ___REPLACE-PROJECT-NAME___ ${project_name}
replace_txt ___REPLACE-PROJECT-VERSION___ ${project_version}
replace_txt ___REPLACE-PROJECT-AUTHOR-NAME___ ${project_author_name}
replace_txt ___REPLACE-PROJECT-COPYRIGHT-YEAR___ ${project_copyright_year}
replace_txt ___REPLACE-PROJECT-COPYRIGHT-NAME___ ${project_copyright_name}

rm -rf ${VENV_DIR}
python3 -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate

poetry install --no-dev

print_msg "setup is done! venv dir is ${VENV_DIR} ."
print_msg "if you need develop libs. exec bellow comands."
print_msg "########################################################"
print_msg "source ${VENV_DIR}/bin/activate"
print_msg "poetry install"