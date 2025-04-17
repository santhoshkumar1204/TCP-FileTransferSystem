import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
import file_manager
from twisted_server import start_twisted_server
import threading

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Start Twisted server in a separate thread
twisted_thread = threading.Thread(target=start_twisted_server)
twisted_thread.daemon = True
twisted_thread.start()

@app.route('/')
def home():
    """Render the home page"""
    return render_template('home.html')

@app.route('/upload')
def index():
    """Render the upload page with file upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload via web interface"""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        file_size = os.path.getsize(file_path)  # Get the size from the saved file
        file_manager.register_file_upload(filename, file_size)
        flash(f'File {filename} uploaded successfully')
        return redirect(url_for('file_manager_page'))
    
    return redirect(url_for('index'))

@app.route('/file_manager')
def file_manager_page():
    """Render the file manager page"""
    return render_template('file_manager.html')

@app.route('/api/files', methods=['GET'])
def get_files():
    """API endpoint to get list of files"""
    files = file_manager.list_files()
    return jsonify(files)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Handle file download"""
    file_manager.register_file_download(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """API endpoint to delete a file"""
    success = file_manager.delete_file(filename)
    if success:
        return jsonify({'status': 'success', 'message': f'File {filename} deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'File not found or could not be deleted'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
