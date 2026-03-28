import hashlib
import mimetypes

def detect_mime_type(file_path):
    """Detects the MIME type of the given file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'  # Default MIME type
    return mime_type

def calculate_checksum(file_path):
    """Calculates the SHA-1 checksum of the given file."""
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as file:
        chunk = file.read(8192)
        while chunk:
            sha1.update(chunk)
            chunk = file.read(8192)
    return sha1.hexdigest()
