# Rabid Hole Punch Server

Python Server that allows peer to peer communication via UDP Hole Punching between devices that are behind NAT

## Requirements

- A public accessible machine with a udp port open
- Python3 installed
- Twisted installed. With Python3 installed you can run the command `pip install twisted` to do this


## Run instructions

Clone this repository to any folder of your choice and run the following command. 

```
python3 main.py <port>
```
Notes:
- Python 3.9 is the Python version recommended, but if you have an earlier 3.x version that should work too
- Replace <port> with a port of your choice (must be the same as the port opened for the machine)

Server will start running in the port specified

If some weird behaviour is happening and you want to print more information to debug, you can run the server using

```
python3 main.py <port> DEBUG
```

And it will print more information

The server will generate log files with the name `rabid-hole-punch.log`

## Usage (WORK IN PROGRESS)

This server will start listening in the UDP port of your choice and it will wait for requests to arrive

You can implement a client for this server in any game engine of your choice, but you have one already available for the Godot game engine here

In case you want to implement your own client, here are the different requests you can send to this server

### Req1 (example, fill more)

### Error codes
- Error 1
