#!/bin/bash

usage() { printf "Usage: %s -p <port_to_use> [-d] [-f]\nUse -d to enable debug\nUse -f to force server restart\n" "$0" 1>&2; exit 1; }

debug=""
force=""

while getopts ":p:df" o; do
    case "${o}" in
        p)
            port=${OPTARG}
            ;;
        d)
            debug="DEBUG"
            ;;
        f)
            force="yes"
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${port}" ]; then
    usage
fi

server_pid=$(pgrep -f holepunch)
if [ -z "${server_pid}" ]; then
  # Server is not running
  pip install -r requirements.txt
  nohup python3 main_holepunch.py "$port" >/dev/null 2>&1 &
  printf "Rabid Hole Punch server started on port %s\n" "$port"
else
  # Server is running
  if [ -z "$force" ]; then
    kill "${server_pid}"
    pip install -r requirements.txt
    nohup python3 main_holepunch.py "$port" $debug >/dev/null 2>&1 &
    printf "Rabid Hole Punch server started on port %s\n" "$port"
  else
    printf "Rabid Hole Punch server is already running"
  fi
fi
