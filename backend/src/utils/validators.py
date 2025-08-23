import os
from flask import current_app
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """Check if file has allowed extension."""
    allowed_ext = current_app.config.get('ALLOWED_EXT', '.pdf')
    return '.' in filename and filename.lower().endswith(allowed_ext.lower())

def validate_file_size(file):
    """Check if file size is within limits."""
    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 25 * 1024 * 1024)
    
    # Get file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer
    
    return size <= max_size

def generate_safe_filename(filename):
    """Generate a safe filename for storage."""
    import uuid
    
    # Get file extension
    ext = os.path.splitext(filename)[1]
    
    # Generate UUID-based filename
    safe_name = f"{uuid.uuid4().hex}{ext}"
    
    return safe_name

def validate_upload_request(request):
    """Validate file upload request."""
    errors = []
    
    if 'file' not in request.files:
        errors.append('No file provided')
        return errors
    
    file = request.files['file']
    
    if file.filename == '':
        errors.append('No file selected')
        return errors
    
    if not allowed_file(file.filename):
        allowed_ext = current_app.config.get('ALLOWED_EXT', '.pdf')
        errors.append(f'Only {allowed_ext} files are allowed')
    
    if not validate_file_size(file):
        max_mb = current_app.config.get('MAX_UPLOAD_MB', 25)
        errors.append(f'File size must be less than {max_mb}MB')
    
    return errors