# python-srFile

Transport directory or file to other computer within the same local network.

## client

client side is located at client-send/client.py, it's used to send file or directory.

For example: `python client.py path/to/send/directory ip:port`

## server

server side is located at server-recv/server.py, it's used to recv file or directory from client and keep it in local file system.

Server side command example: python server.py path/to/keep/file/directory
