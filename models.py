import json
import time
from dataclasses import dataclass, asdict

@dataclass
class FileInfo:
    """Data class to store file information"""
    filename: str
    size: int
    upload_time: float
    download_count: int = 0
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class ConnectionInfo:
    """Data class to store connection information"""
    client_id: str
    ip_address: str
    connection_time: float
    bytes_uploaded: int = 0
    bytes_downloaded: int = 0
    active: bool = True
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class NetworkStats:
    """Data class to store network statistics"""
    total_connections: int = 0
    active_connections: int = 0
    total_bytes_uploaded: int = 0
    total_bytes_downloaded: int = 0
    upload_rate: float = 0  # bytes per second
    download_rate: float = 0  # bytes per second
    connection_history: list = None
    
    def __post_init__(self):
        if self.connection_history is None:
            self.connection_history = []
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['connection_history'] = [conn.to_dict() for conn in self.connection_history]
        return data
    
    def save(self):
        """Save network statistics to JSON file"""
        with open('network_stats.json', 'w') as f:
            json.dump(self.to_dict(), f)
    
    @classmethod
    def load(cls):
        """Load network statistics from JSON file"""
        try:
            with open('network_stats.json', 'r') as f:
                data = json.load(f)
                stats = cls(
                    total_connections=data.get('total_connections', 0),
                    active_connections=data.get('active_connections', 0),
                    total_bytes_uploaded=data.get('total_bytes_uploaded', 0),
                    total_bytes_downloaded=data.get('total_bytes_downloaded', 0),
                    upload_rate=data.get('upload_rate', 0),
                    download_rate=data.get('download_rate', 0)
                )
                
                # Load connection history
                history = []
                for conn_data in data.get('connection_history', []):
                    history.append(ConnectionInfo(
                        client_id=conn_data.get('client_id', ''),
                        ip_address=conn_data.get('ip_address', ''),
                        connection_time=conn_data.get('connection_time', time.time()),
                        bytes_uploaded=conn_data.get('bytes_uploaded', 0),
                        bytes_downloaded=conn_data.get('bytes_downloaded', 0),
                        active=conn_data.get('active', False)
                    ))
                stats.connection_history = history
                return stats
        except (FileNotFoundError, json.JSONDecodeError):
            # Return new instance if file doesn't exist or is invalid
            return cls()
