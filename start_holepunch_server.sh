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

debug_text=""
if [ -n "${debug}" ]; then
  debug_text="with debug enabled"
fi

server_pid=$(pgrep -f main_holepunch)
if [ -z "${server_pid}" ]; then
  # Server is not running
  pip install -r requirements.txt
  nohup python3 main_holepunch.py "$port" $debug >/dev/null 2>&1 &
  printf "Rabid Hole Punch server started ${debug_text} on port %s\n" "$port"
else
  # Server is running
  if [ -n "${force}" ]; then
    kill $((server_pid))
    echo "Terminated previous instance of Rabid Hole Punch server"
    pip install -r requirements.txt
    nohup python3 main_holepunch.py "$port" $debug >/dev/null 2>&1 &
    printf "Rabid Hole Punch server started ${debug_text} on port %s\n" "$port"
  else
    printf "Rabid Hole Punch server is already running\n"
  fi
fi
