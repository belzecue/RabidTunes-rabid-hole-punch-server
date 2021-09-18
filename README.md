# Rabid Hole Punch Server

HolePunch Server that allows peer to peer communication via UDP Hole Punching between devices that are behind NAT

## Requirements

- A public accessible machine with a udp port open
- Python3 installed
- Twisted installed. With Python3 installed you can run `pip install twisted` to do this


## Instructions

Clone this repository to any folder of your choice and run the following command. 
- python3.9 is the Python version recommended, but if you have an earlier 3.x version that should work too
- Replace <port> with a port of your choice (must be the same as the port opened)

```
python3.9 main.py <port>
```

Server will start running in the port specified

If some weird behaviour is happening and you want to print more information to debug, you can run the server using

```
python3.9 main.py <port> DEBUG
```

And it will print more information

The server will generate log files with the name `rabid-hole-punch.log`
