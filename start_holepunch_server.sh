#!/bin/bash

usage() { printf "Usage: %s -p <port_to_use> [-d] [-f]\nUse -d to enable debug\nUse -f to force server restart" "$0" 1>&2; exit 1; }

debug=""
force=false

while getopts ":p:df" o; do
    case "${o}" in
        p)
            port=${OPTARG}
            ;;
        d)
            debug="DEBUG"
            ;;
        f)
            force=true
            ;;
        *)
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${p}" ]; then
    echo "caca"
    usage
fi

server_pid=$(pgrep "main_holepunch")
if [ -z "${server_pid}" ]; then
  # Server is not running
  pip install -r requirements.txt
  nohup python3 main_holepunch.py "$port" >/dev/null 2>&1 &
  printf "Rabid Hole Punch server started on port %s" "$port"
else
  pip install -r requirements.txt
  if [ $force ]; then
    pip install -r requirements.txt
    nohup python3 main_holepunch.py "$port" $debug >/dev/null 2>&1 &
    printf "Rabid Hole Punch server started on port %s" "$port"
  else
    printf "Rabid Hole Punch server is already running"
  fi
fi
