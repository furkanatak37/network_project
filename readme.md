PROJECT TITLE
  Micro-CDN / File Distribution System

PROJECT OVERVIEW
  This project implements a simplified Content Delivery Network (Micro-CDN).
  Clients request files from an Index Server, which tracks available Content Servers.
  Files are transferred directly from Content Servers to Clients using TCP.
  A Monitor Server tracks server health using UDP heartbeats and informs the Index Server when failures occur.

  The system demonstrates socket programming with TCP and UDP, concurrency, basic protocol design, and failure handling in a distributed system.

SYSTEM COMPONENTS

Index Server:

  The Index Server acts as a tracker.
  It maintains a mapping of file names to Content Servers and handles client lookup requests.
  It also updates server availability based on notifications from the Monitor Server.

Content Server:

  Content Servers host files and serve them to clients over TCP.
  They register themselves with the Index Server and periodically send heartbeat messages to the Monitor Server using UDP.
  Multiple Content Servers can run simultaneously.

Monitor / Health Server: 

  The Monitor Server tracks which Content Servers are alive.
  It receives heartbeat messages over UDP and detects server failures based on missed heartbeats.
  It notifies the Index Server when a Content Server is considered dead.

Client Program:

  The Client requests a file from the Index Server and, if available, downloads it from the appropriate Content Server.

REQUIREMENTS

  Python 3.8 or later

  Standard Python libraries only (socket, threading, time, os, sys)

  No external dependencies

DEFAULT PORT CONFIGURATION

Index Server

  TCP: 5000

Monitor Server

  UDP: 6000

  TCP: 6001

Content Server

  TCP: configurable (example: 7001, 7101)

  UDP: TCP port + 1

  All components may run on localhost for testing.

HOW TO RUN

  Start the Monitor Server
  Run the following command in a terminal:
  python monitor.py

  Start the Index Server
  Run the following command in a terminal:
  python index_server.py

  Start Content Servers
  At least two Content Servers must be started.
  Each Content Server must have its own file directory.

  Example:
  python content_server.py server1 7001 files1/
  python content_server.py server2 7101 files2/

  Run the Client
  Run the client to download a file:
  python client.py <file_name>

  The downloaded file will be saved in the client’s current directory.

COMMAND LINE ARGUMENTS

  Content Server
  python content_server.py <server_id> <tcp_port> <files_directory>

  Client
  python client.py <file_name>

PROTOCOL SUMMARY

  All messages are ASCII text terminated by newline characters.

TCP is used for:

  Client to Index Server communication

  Client to Content Server file transfer

  Index Server to Monitor communication

UDP is used for:

  Content Server heartbeat messages to the Monitor

  ERROR HANDLING AND ROBUSTNESS

  Invalid commands return an error message.

  Requests for non-existent files return ERROR FILE_NOT_FOUND.

  Client disconnections are handled.

  Content Server failures are detected automatically via missed heartbeats.

  The Index Server avoids routing clients to servers marked as DEAD.

TESTING

  The system was tested using multiple concurrent clients, multiple Content Servers, and simulated server failures.
  The Monitor successfully detects failed servers, and the Index Server stops routing requests to them.

NOTES

  Raw sockets are used; no HTTP libraries or frameworks are involved.

  Concurrency is implemented using threads.

  The system can be extended with caching, replication, or chunked file transfer.