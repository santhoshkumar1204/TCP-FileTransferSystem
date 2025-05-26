# TCP File Transfer and Network Monitoring System

This is a software project developed as part of a networking mini project. It implements a real-time file transfer and monitoring system using TCP sockets, Twisted (Python), and Flask for the web interface.

## About the Project

The application allows users to upload, download, and manage files over TCP using a web-based interface. It provides real-time statistics like active connections and data throughput using Twisted's event-driven architecture. This system is suitable for LAN-based environments, especially in educational or lightweight enterprise use cases.

The architecture is modular, separating file management, TCP communication, web interface, and monitoring into distinct components for scalability and maintainability.

## Technologies Used

- *Python* with:
  - *Twisted* for asynchronous TCP socket communication
  - *Flask* for web interface
- *HTML/CSS* for frontend
- *Sockets & TCP/IP* for communication
- *JSON* for file metadata persistence

## How to Run

### Prerequisites

- Python 3.x installed
- Required libraries installed:
  bash
  pip install flask twisted
  

### Steps to Run

1. Clone or download this repository.
2. Open a terminal and navigate to the server directory.
3. Start the server by running the main Python script:
   bash
   python main.py
   
4. Open your browser and go to:
   
   http://localhost:5000
   
5. Use the web interface to upload files, view statistics, and monitor transfers.
6. To test file transfer from the client, run the client script in a separate terminal:
   bash
   python file_client.py
   

> Ensure both client and server are connected to the same network or update the IP/port configurations accordingly.

## Features

- Upload and download files via TCP
- Real-time network statistics (active connections, transfer rates)
- Lightweight web interface for users
- Concurrent connection handling using Twisted
- File metadata storage in JSON for easy access

