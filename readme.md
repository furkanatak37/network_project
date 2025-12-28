# Micro CDN - Simple File Distribution System

This project is a simple Micro-CDN implementation written in Python.
It simulates how a Content Delivery Network works using sockets.

Components:
- Index Server
- Content Servers (multiple)
- Monitor / Health Server
- Client

All communication is done using TCP and UDP sockets.
The system runs on localhost and is intended for educational testing.

--------------------------------------------------
Requirements
--------------------------------------------------

- Python 3.8 or newer
- No external libraries are required
- Works on Linux, macOS, and Windows

--------------------------------------------------
Project Files
--------------------------------------------------

- index_server.py
  Keeps track of content servers and which files they host.
  Handles client file lookup requests.

- content_server.py
  Hosts files and sends them to clients over TCP.
  Sends heartbeat messages to the monitor over UDP.

- monitor.py
  Receives heartbeats from content servers.
  Detects server failures and notifies the index server.

- client.py
  Requests a file from the index server.
  Downloads the file from the selected content server.

--------------------------------------------------
Default Ports
--------------------------------------------------

Index Server:
- TCP 5000

Monitor Server:
- UDP 6000
- TCP 6001

Content Servers:
- TCP port is provided as an argument
- UDP port is TCP port + 1

--------------------------------------------------
How to Run the CDN (Step by Step)
--------------------------------------------------

1) Start the Monitor Server

Open a terminal and run:
python monitor.py

You should see:
Monitor UDP listening: 6000
Monitor TCP listening: 6001

--------------------------------------------------

2) Start the Index Server

Open a new terminal and run:
python index_server.py

You should see:
Index Server listening: 5000
Index -> Monitor connected

--------------------------------------------------

3) Prepare Content Server Files

Create one or more folders, for example:
server1_files/
server2_files/

Put some test files inside them, for example:
test.txt
hello.bin

--------------------------------------------------

4) Start Content Servers

Open new terminals for each content server.

Example for server 1:
python content_server.py server1 7001 server1_files

Example for server 2:
python content_server.py server2 7101 server2_files

Each content server will:
- Register itself with the Index Server
- Send its file list
- Start sending heartbeats to the Monitor

--------------------------------------------------

5) Run the Client

Open another terminal and run:
python client.py test.txt

If the file exists on any live content server:
- The client will contact the Index Server
- Connect to the Content Server
- Download and save the file locally

If the file does not exist:
- An error message is printed

--------------------------------------------------
How to Test Failure Handling
--------------------------------------------------

1) Start all servers as described above
2) Run the client and download a file successfully
3) Kill one content server (Ctrl+C)
4) Wait around 8 seconds
5) The Monitor will mark the server as DEAD
6) The Index Server will stop using that server
7) Run the client again and observe behavior

--------------------------------------------------
Notes
--------------------------------------------------

- All messages are simple text-based protocol messages
- Content Servers support multiple clients using threads
- This project is for learning purposes and not production use
