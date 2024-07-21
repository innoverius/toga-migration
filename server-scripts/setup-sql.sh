#!/bin/bash

set -e
SCRIPT=$(basename "$0")

Help() {
  echo
  echo "$SCRIPT"
  echo
  echo "Description: Set up Firebird"
  echo "Syntax: $SCRIPT [-p|help]"
  echo "Example: $SCRIPT -p secret"
  echo "Options:"
  echo "    -p      Database password"
  echo "    help    Instructions to use $SCRIPT"
  echo
}

if [[ $1 == 'help' ]]; then
    Help
    exit
fi

while getopts ":p:" opt;
do
  case $opt in
    p) PASSWORD="$OPTARG";;
    \?) echo "Invalid option -$OPTARG" >&2
    Help
    exit;;
  esac
done

[[ -z "$PASSWORD" ]] && { echo "Please define password with parameter -p" ; exit 1; }



