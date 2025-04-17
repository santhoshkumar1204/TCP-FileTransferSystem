import os
import json
import time
import logging
from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver
import file_manager
from models import NetworkStats, ConnectionInfo

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure uploads directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global network statistics object
network_stats = NetworkStats.load()

class FileTransferProtocol(LineReceiver):
    """Protocol for handling file transfers over TCP"""
    
    def __init__(self):
        self.client_id = None
        self.ip_address = None
        self.mode = None
        self.filename = None
        self.filesize = 0
        self.received_size = 0
        self.file_handle = None
        self.start_time = None
        self.connection_info = None
    
    def connectionMade(self):
        """Called when a connection is established"""
        self.client_id = str(id(self))
        self.ip_address = self.transport.getPeer().host
        
        # Update network statistics
        global network_stats
        network_stats.total_connections += 1
        network_stats.active_connections += 1
        
        # Create connection info and add to history
        self.connection_info = ConnectionInfo(
            client_id=self.client_id,
            ip_address=self.ip_address,
            connection_time=time.time()
        )
        network_stats.connection_history.append(self.connection_info)
        network_stats.save()
        
        logger.info(f"Connection established with {self.ip_address}")
        self.sendLine(b"CONNECTED")
    
    def connectionLost(self, reason):
        """Called when the connection is lost"""
        global network_stats
        network_stats.active_connections -= 1
        
        # Update connection info
        if self.connection_info:
            self.connection_info.active = False
        
        network_stats.save()
        
        # Close any open file handle
        if self.file_handle:
            self.file_handle.close()
            
        logger.info(f"Connection lost with {self.ip_address}: {reason}")
    
    def lineReceived(self, line):
        """Process a line of text from the client"""
        try:
            command = line.decode('utf-8').strip()
            
            if command.startswith("UPLOAD"):
                # Format: UPLOAD filename filesize
                parts = command.split(' ', 2)
                if len(parts) == 3:
                    self.mode = "UPLOAD"
                    self.filename = parts[1]
                    self.filesize = int(parts[2])
                    self.received_size = 0
                    
                    # Open file for writing
                    safe_filename = os.path.basename(self.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
                    self.file_handle = open(file_path, 'wb')
                    
                    # Start binary mode to receive file data
                    self.setRawMode()
                    
                    # Record start time for transfer rate calculation
                    self.start_time = time.time()
                    
                    logger.info(f"Starting upload of {self.filename} ({self.filesize} bytes)")
                    self.sendLine(b"READY")
                else:
                    self.sendLine(b"ERROR Invalid UPLOAD command format")
                    
            elif command.startswith("DOWNLOAD"):
                # Format: DOWNLOAD filename
                parts = command.split(' ', 1)
                if len(parts) == 2:
                    filename = parts[1]
                    safe_filename = os.path.basename(filename)
                    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
                    
                    if os.path.exists(file_path):
                        filesize = os.path.getsize(file_path)
                        self.sendLine(f"FILEINFO {filename} {filesize}".encode('utf-8'))
                        
                        # Start sending the file
                        with open(file_path, 'rb') as f:
                            data = f.read()
                            self.transport.write(data)
                            
                        # Register download in stats
                        file_manager.register_file_download(filename)
                        
                        # Update connection stats
                        if self.connection_info:
                            self.connection_info.bytes_downloaded += filesize
                            
                        # Update global stats
                        global network_stats
                        network_stats.total_bytes_downloaded += filesize
                        network_stats.save()
                        
                        logger.info(f"Sent file {filename} ({filesize} bytes)")
                    else:
                        self.sendLine(b"ERROR File not found")
                else:
                    self.sendLine(b"ERROR Invalid DOWNLOAD command format")
                    
            elif command == "LIST":
                # Send list of available files
                files = file_manager.list_files()
                self.sendLine(f"FILELIST {json.dumps(files)}".encode('utf-8'))
                
            elif command == "STATS":
                # Send network statistics
                stats = network_stats.to_dict()
                self.sendLine(f"STATS {json.dumps(stats)}".encode('utf-8'))
                
            else:
                self.sendLine(b"ERROR Unknown command")
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.sendLine(f"ERROR {str(e)}".encode('utf-8'))
    
    def rawDataReceived(self, data):
        """Handle raw binary data for file uploads"""
        if self.mode == "UPLOAD":
            self.file_handle.write(data)
            self.received_size += len(data)
            
            # Update connection stats
            if self.connection_info:
                self.connection_info.bytes_uploaded += len(data)
            
            # Update global stats
            global network_stats
            network_stats.total_bytes_uploaded += len(data)
            
            # Check if file is complete
            if self.received_size >= self.filesize:
                self.file_handle.close()
                self.file_handle = None
                
                # Calculate upload rate
                duration = time.time() - self.start_time
                if duration > 0:
                    upload_rate = self.filesize / duration
                    network_stats.upload_rate = (network_stats.upload_rate + upload_rate) / 2
                
                # Register file upload
                file_manager.register_file_upload(self.filename, self.filesize)
                
                # Save stats
                network_stats.save()
                
                # Return to line mode
                self.setLineMode()
                
                logger.info(f"Upload complete: {self.filename} ({self.filesize} bytes)")
                self.sendLine(b"UPLOAD_COMPLETE")
                
                # Reset state
                self.mode = None
                self.filename = None
                self.filesize = 0
                self.received_size = 0
                self.start_time = None

class FileTransferFactory(protocol.Factory):
    """Factory for creating FileTransferProtocol instances"""
    
    def buildProtocol(self, addr):
        return FileTransferProtocol()

def start_twisted_server():
    """Start the Twisted server on a specified port"""
    logger.info("Starting Twisted TCP server on port 8000")
    reactor.listenTCP(8000, FileTransferFactory(), interface='0.0.0.0')
    reactor.run(installSignalHandlers=0)  # Don't install signal handlers to avoid conflicts with Flask

if __name__ == "__main__":
    # If run directly, start the Twisted server
    start_twisted_server()
