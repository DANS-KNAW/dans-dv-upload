import json
import logging
import os
import requests
from .util import detect_mime_type

def get_upload_urls(dataverse_url, api_key, doi, file_size):
    """Requests upload URLs from the Dataverse API."""
    logging.info("Requesting upload URLs from Dataverse.")
    headers = {'X-Dataverse-key': api_key}
    params = {'persistentId': doi, 'size': file_size}
    response = requests.get("{}/api/datasets/:persistentId/uploadurls".format(dataverse_url), headers=headers, params=params)
    response.raise_for_status()
    logging.info("Received upload URLs from Dataverse.")
    return response.json()['data']

def register_file(dataverse_url, api_key, doi, file_path, directory_label, storage_identifier, sha1_checksum):
    """Registers the uploaded file in the Dataverse dataset."""
    logging.info("Registering file in Dataverse dataset.")
    headers = {'X-Dataverse-key': api_key}
    file_name = os.path.basename(file_path)
    mime_type = detect_mime_type(file_path)
    json_data = {
        'description': '',
        'label': file_name,
        'directoryLabel': directory_label,
        'storageIdentifier': storage_identifier,
        'fileName': file_name,
        'mimeType': mime_type,
        'checksum': {
            '@type': 'SHA-1',
            '@value': sha1_checksum
        }
    }
    logging.debug("JSON data for registration: {}".format(json_data))
    response = requests.post(
        "{}/api/datasets/:persistentId/add".format(dataverse_url),
        headers=headers,
        params={'persistentId': doi},
        files={'jsonData': (None, json.dumps(json_data), 'application/json')})
    logging.debug(response.text)

    response.raise_for_status()
    logging.info("File registered in Dataverse dataset successfully with MIME type: {}.".format(mime_type))
