import os
import json
import time
from models import FileInfo

# Ensure uploads directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# File to store file information
FILE_INFO_PATH = 'file_info.json'

def load_file_info():
    """Load file information from JSON file"""
    try:
        with open(FILE_INFO_PATH, 'r') as f:
            data = json.load(f)
            return {filename: FileInfo(**info) for filename, info in data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_file_info(file_info):
    """Save file information to JSON file"""
    data = {filename: info.to_dict() for filename, info in file_info.items()}
    with open(FILE_INFO_PATH, 'w') as f:
        json.dump(data, f)

def list_files():
    """List all files in the upload directory with their information"""
    file_info = load_file_info()
    files = []
    
    # Check if files in the directory match our records
    for filename in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            
            # If file exists in our records, use that info
            if filename in file_info:
                info = file_info[filename]
                files.append({
                    'filename': filename,
                    'size': info.size,
                    'upload_time': info.upload_time,
                    'download_count': info.download_count,
                    'size_formatted': format_size(info.size)
                })
            else:
                # If not, create new record
                current_time = time.time()
                file_info[filename] = FileInfo(
                    filename=filename,
                    size=size,
                    upload_time=current_time
                )
                files.append({
                    'filename': filename,
                    'size': size,
                    'upload_time': current_time,
                    'download_count': 0,
                    'size_formatted': format_size(size)
                })
    
    # Save updated file info
    save_file_info(file_info)
    
    # Sort files by upload time (newest first)
    files.sort(key=lambda x: x['upload_time'], reverse=True)
    
    return files

def register_file_upload(filename, size):
    """Register a file upload in the file information"""
    file_info = load_file_info()
    
    # Add or update file information
    file_info[filename] = FileInfo(
        filename=filename,
        size=size,
        upload_time=time.time(),
        download_count=file_info.get(filename, FileInfo(filename, 0, 0)).download_count
    )
    
    save_file_info(file_info)

def register_file_download(filename):
    """Register a file download in the file information"""
    file_info = load_file_info()
    
    # Increment download count if file exists
    if filename in file_info:
        file_info[filename].download_count += 1
        save_file_info(file_info)

def delete_file(filename):
    """Delete a file from the upload directory and file information"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
            # Remove from file information
            file_info = load_file_info()
            if filename in file_info:
                del file_info[filename]
                save_file_info(file_info)
            
            return True
        return False
    except Exception:
        return False

def format_size(size_bytes):
    """Format size in bytes to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
