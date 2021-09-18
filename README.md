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

You can implement a client for this server in any game engine of your choice, [but you have one already available for the Godot game engine here](https://gitlab.com/RabidTunes/rabid-hole-punch-godot)

In case you want to implement your own client, here is the workflow and the UDP packets you have to send to the server in order to the hole punch process to work:

### 1 (Host) - Create session request - h:<sessionname>:<playername>:<maxplayers>:<sessionpassword>

Session name must have between 1-10 alphanumeric characters
Player name must have between 1-12 alphanumeric characters
Max players must be a number between 2 and 12
Session password must have between 1-12 alphanumeric characters. This part is optional

Examples:
`h:NiceRoom:SuperPlayer:4:Pass`
`h:NiceRoom:SuperPlayer:4` (no password)

After sending this, if the session was created, the server will respond with the following udp message `i:SuperPlayer`. It is the info prefix `i` followed by the current list of players (currently just one)

### 1 (Client) - Connect to session request - c:<sessionname>:<playername>:<sessionpassword>

Session name must have between 1-10 alphanumeric characters
Player name must have between 1-12 alphanumeric characters
Session password must have between 1-12 alphanumeric characters. This part is optional

Examples:
`c:NiceRoom:CoolPlayer:Pass`
`c:NiceRoom:CoolPlayer`

After sending this, if the session exists and has enough room for you, the server will respond with the following udp message `i:SuperPlayer:CoolPlayer`. It is the info prefix `i` followed by the current list of players


### 2 (Everybody) - Ping request - p:<sessionname>:<playername>

After creating/connecting to the session, you have to send regularly some pings, otherwise the server will kick you out. Sending one ping at least each second will suffice in most cases.

Examples:
`p:NiceRoom:SuperPlayer`
`p:NiceRoom:CoolPlayer`

### 3 (Host) - Start Session - s:<sessionname>:<playername>

When enough players have connected, as host you can send this message so the server will answer with the IPs and ports of all peers. Sending this message will make the server start sending the start message to all peers. The start message changes depending on the receiver, for example, if a session has 3 players, SuperPlayer, CoolPlayer and NicePlayer:
- SuperPlayer will receive this message: `s:<SuperPlayerPort>:CoolPlayer:<CoolPlayerIP>:<CoolPlayerPort>;NicePlayer:<NicePlayerIP>:<NicePlayerPort>`
- CoolPlayer will receive this message: `s:<CoolPlayerPort>:SuperPlayer:<SuperPlayerIP>:<SuperPlayerPort>;NicePlayer:<NicePlayerIP>:<NicePlayerPort>`
- NicePlayer will receive this message: `s:<NicePlayerPort>:SuperPlayer:<SuperPlayerIP>:<SuperPlayerPort>;CoolPlayer:<CoolPlayerIP>:<CoolPlayerPort>`

If a non-host player receives this message, it is safe to assume that the first player that receives in this message is the host. Both CoolPlayer and NicePlayer received 'SuperPlayer' as first player in the list, so they will assume that's the host.

### 4 (Everybody) - Confirm Start Session info received - y:<sessionname>:<playername>

After receiveing the list of players message, it is nice to send a confirmation to let the server know that we received the info, so it stops sending us the start session message. It is not only to save resources, but to prevent it to spam our ports.

Example:
`y:NiceRoom:SuperPlayer`

### Optional message in session (Host) - Kick player from session - k:<sessionname>:<player-name-to-kick>

If you are the host you can kick a player by sending this message to the server. In the current version this won't prevent the player to re-enter the session, unfortunately.
Example:
`k:NiceRoom:CoolPlayer`

### Optional message in session (Everybody) - Exit session - x:<sessionname>:<playername>

You can send this message in any given time inside a session that has not started yet to exit that session.
Example:
`x:NiceRoom:NicePlayer`

### Error codes
- Error 1 (WORK IN PROGRESS)
