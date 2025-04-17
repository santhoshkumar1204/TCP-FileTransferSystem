/**
 * JavaScript file for the file manager page
 */

// DOM elements
const fileListElement = document.getElementById('fileList');
const noFilesElement = document.getElementById('noFiles');
const refreshBtn = document.getElementById('refreshBtn');
const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
const deleteFileNameElement = document.getElementById('deleteFileName');
const confirmDeleteBtn = document.getElementById('confirmDelete');

// Current file being considered for deletion
let currentFileToDelete = null;

// Load files from the server
async function loadFiles() {
    // Show loading indicator
    fileListElement.innerHTML = `
        <tr>
            <td colspan="5" class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </td>
        </tr>
    `;
    
    const files = await fetchData('/api/files');
    
    if (!files || files.length === 0) {
        fileListElement.innerHTML = '';
        noFilesElement.classList.remove('d-none');
        return;
    }
    
    // Hide the "no files" message
    noFilesElement.classList.add('d-none');
    
    // Build the table rows
    let tableHtml = '';
    files.forEach(file => {
        tableHtml += `
            <tr class="file-item">
                <td style="padding-left: 1.25rem;">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-file me-3 text-primary"></i>
                        <span>${file.filename}</span>
                    </div>
                </td>
                <td>${file.size_formatted}</td>
                <td>${formatDate(file.upload_time)}</td>
                <td>
                    <span class="badge bg-info rounded-pill">${file.download_count}</span>
                </td>
                <td class="text-end" style="padding-right: 1.25rem;">
                    <a href="/download/${file.filename}" class="btn btn-sm btn-outline-primary action-btn" title="Download File">
                        <i class="fas fa-download"></i>
                    </a>
                    <button class="btn btn-sm btn-outline-danger action-btn delete-btn" data-filename="${file.filename}" title="Delete File">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    fileListElement.innerHTML = tableHtml;
    
    // Add event listeners to delete buttons
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const filename = this.getAttribute('data-filename');
            showDeleteConfirmation(filename);
        });
    });
}

// Show delete confirmation modal
function showDeleteConfirmation(filename) {
    currentFileToDelete = filename;
    deleteFileNameElement.textContent = filename;
    deleteModal.show();
}

// Delete a file
async function deleteFile(filename) {
    try {
        const response = await fetch(`/api/delete/${filename}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Show success message
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show';
        successDiv.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>${result.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(successDiv, container.firstChild);
        
        // Reload files
        loadFiles();
        
    } catch (error) {
        console.error('Error deleting file:', error);
        showError(`Failed to delete file: ${error.message}`);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load files when page loads
    loadFiles();
    
    // Refresh button click
    refreshBtn.addEventListener('click', loadFiles);
    
    // Confirm delete button click
    confirmDeleteBtn.addEventListener('click', function() {
        if (currentFileToDelete) {
            deleteFile(currentFileToDelete);
            deleteModal.hide();
            currentFileToDelete = null;
        }
    });
});
