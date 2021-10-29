#!/bin/bash

server_pid=$(pgrep -f main_holepunch)
if [ -z "${server_pid}" ]; then
  # Server is not running
  printf "Rabid Hole Punch server is not running\n"
else
  # Server is running
  kill $((server_pid))
  echo "Terminated previous instance of Rabid Hole Punch server"
fi
