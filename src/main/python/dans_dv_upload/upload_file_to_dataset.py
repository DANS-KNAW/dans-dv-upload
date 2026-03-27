#!/usr/bin/env python3
import argparse
import hashlib
import json
import logging
import mimetypes
import os
import requests
import shutil
import yaml

from logging import config as logconfig

example_config = """
dataverse:
  url: changeme
  api_key: changeme

logging:
  version: 1
  root:
    handlers:
      - console
      - file
    level: DEBUG
  handlers:
    console:
      formatter: std_out
      class: logging.StreamHandler
      level: DEBUG
    file:
      class: logging.FileHandler
      filename: upload-file-to-dataset-config.log
      level: DEBUG
  formatters:
    std_out:
      format: "%(asctime)s : %(levelname)s : %(funcName)s : %(message)s"
      datefmt: "%Y-%m-%d %I:%M:%S"
"""


def ensure_configuration_file_exists():
    home_config_path = os.path.expanduser('~/.upload-file-to-dataset.yml')
    cwd_config_path = './upload-file-to-dataset.yml'
    if os.path.exists(home_config_path):
        config_path = home_config_path
    elif os.path.exists(cwd_config_path):
        config_path = cwd_config_path
    else:
        # Create a sample config file if it doesn't exist
        with open(cwd_config_path, 'w') as file:
            file.write(example_config)
        config_path = cwd_config_path
        print("Configuration file created at: {}. Please, review and edit and then try again.".format(config_path))
        exit(1)

def read_config():
    home_config_path = os.path.expanduser('~/.upload-file-to-dataset.yml')
    cwd_config_path = './upload-file-to-dataset.yml'

    if os.path.exists(home_config_path):
        config_path = home_config_path
    elif os.path.exists(cwd_config_path):
        config_path = cwd_config_path
    else:
        raise FileNotFoundError("Configuration file not found. Please create a configuration file at either {} or {}".format(home_config_path, cwd_config_path))

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def get_upload_urls(dataverse_url, api_key, doi, file_size):
    """Requests upload URLs from the Dataverse API."""
    logging.info("Requesting upload URLs from Dataverse.")
    headers = {'X-Dataverse-key': api_key}
    params = {'persistentId': doi, 'size': file_size}
    response = requests.get("{}/api/datasets/:persistentId/uploadurls".format(dataverse_url), headers=headers, params=params)
    response.raise_for_status()
    logging.info("Received upload URLs from Dataverse.")
    return response.json()['data']


def write_state(state_file_path, state):
    """Writes the upload state to a file."""
    temp_file_path = state_file_path + ".temp"
    with open(temp_file_path, 'w') as file:
        json.dump(state, file, indent=4)
    os.replace(temp_file_path, state_file_path)


def load_state(state_file_path):
    """Loads the upload state from a file."""
    with open(state_file_path, 'r') as file:
        return json.load(file)


def upload_file_to_s3(dataverse_url, api_key, state, state_file_path, file_path):
    """Uploads the file to the provided S3 URL(s)."""
    logging.info("Uploading file to S3.")
    upload_urls = state['upload_urls']
    if 'url' in upload_urls:  # Single-part upload
        logging.debug("Single-part upload URL: {}".format(upload_urls['url']))
        with open(file_path, 'rb') as file:
            headers = {'x-amz-tagging': 'dv-state=temp'}
            response = requests.put(upload_urls['url'], data=file, headers=headers)
            response.raise_for_status()
    elif 'urls' in upload_urls:  # Multi-part upload
        etags = state.get('etags', {})
        part_size = upload_urls['partSize']
        file_size = state['file_size']
        with open(file_path, 'rb') as file:
            items = upload_urls['urls'].items()
            for part_number, url in items:
                if part_number in etags:
                    logging.info("Part {} already uploaded, skipping.".format(part_number))
                    continue

                logging.debug("Uploading part {} of {} to URL: {}".format(part_number, len(items), url))
                offset = (int(part_number) - 1) * part_size
                file.seek(offset)
                part_data = file.read(part_size)
                response = requests.put(url, data=part_data)
                response.raise_for_status()
                etags[part_number] = response.headers['ETag']
                state['etags'] = etags
                write_state(state_file_path, state)

        logging.info("Calling COMPLETE on multi-part upload.")
        complete_url = "{}{}".format(dataverse_url, upload_urls['complete'])
        headers = {'X-Dataverse-key': api_key}
        requests.put(complete_url, json=etags, headers=headers).raise_for_status()
    logging.info("File uploaded to S3 successfully.")


def detect_mime_type(file_path):
    """Detects the MIME type of the given file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'  # Default MIME type
    return mime_type


def calculate_checksum(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as file:
        chunk = file.read(8192)
        while chunk:
            sha1.update(chunk)
            chunk = file.read(8192)
    return sha1.hexdigest()


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


def main():
    ensure_configuration_file_exists()
    config = read_config()
    logconfig.dictConfig(config['logging'])

    parser = argparse.ArgumentParser(description="Upload a file to a Dataverse dataset.")
    parser.add_argument("doi", help="DOI of the dataset")
    parser.add_argument("file", help="Path to the file to upload")
    parser.add_argument("--directory-label", help="Directory label for the file in the dataset")
    parser.add_argument("--resume", action="store_true", help="Resume a previously started upload")
    parser.add_argument("--skip-checksum-on-resume", action="store_true", help="Skip SHA-1 checksum verification when resuming")
    parser.add_argument("--keep-upload-state", action="store_true", help="Keep the state file after a successful upload")
    args = parser.parse_args()

    dataverse_url = config['dataverse']['url']
    api_key = config['dataverse']['api_key']
    file_path = args.file
    doi = args.doi

    if not os.path.exists(file_path):
        logging.error("File not found: {}".format(file_path))
        raise FileNotFoundError("File not found: {}".format(file_path))

    state_file_path = os.path.basename(file_path) + "-upload-state.json"

    if os.path.exists(state_file_path) and not args.resume:
        logging.error("Upload state file already exists: {}. Either delete it or specify --resume to continue the upload.".format(state_file_path))
        exit(1)

    if args.resume and not os.path.exists(state_file_path):
        logging.error("Upload state file not found: {}".format(state_file_path))
        exit(1)

    if args.resume:
        logging.info("Resuming upload from {}...".format(state_file_path))
        state = load_state(state_file_path)
        if state['file'] != os.path.abspath(file_path):
            logging.error("File in upload state ({}) does not match file specified on command line ({})".format(state['file'], os.path.abspath(file_path)))
            exit(1)
        if state['file_size'] != os.path.getsize(file_path):
            logging.error("File size in upload state does not match actual file size")
            exit(1)
        if not args.skip_checksum_on_resume:
            sha1_checksum = calculate_checksum(file_path)
            if sha1_checksum != state['sha1_checksum']:
                logging.error("SHA-1 checksum in upload state does not match actual file checksum")
                exit(1)
    else:
        logging.info("Starting file upload process.")
        file_size = os.path.getsize(file_path)
        sha1_checksum = calculate_checksum(file_path)
        state = {
            'file': os.path.abspath(file_path),
            'file_size': file_size,
            'sha1_checksum': sha1_checksum,
            'etags': {},
            'upload_urls': None
        }

    if state['upload_urls'] is None:
        upload_urls = get_upload_urls(dataverse_url, api_key, doi, state['file_size'])
        state['upload_urls'] = upload_urls
        write_state(state_file_path, state)

    upload_file_to_s3(dataverse_url, api_key, state, state_file_path, file_path)
    register_file(dataverse_url, api_key, doi, file_path, args.directory_label, state['upload_urls']['storageIdentifier'], state['sha1_checksum'])

    if not args.keep_upload_state:
        os.remove(state_file_path)
        logging.info("Upload state file {} deleted".format(state_file_path))

    logging.info("File upload process completed successfully.")


if __name__ == "__main__":
    main()
