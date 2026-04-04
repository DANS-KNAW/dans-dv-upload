import json
import logging
import os
import requests

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

def upload_file_to_s3(dataverse_url, api_key, state, state_file_path, file_path, progress_callback=None):
    """Uploads the file to the provided S3 URL(s)."""
    logging.info("Uploading file to S3.")
    upload_urls = state['upload_urls']
    file_size = state['file_size']

    if 'url' in upload_urls:  # Single-part upload
        logging.debug("Single-part upload URL: {}".format(upload_urls['url']))
        
        class ProgressReader:
            def __init__(self, file, callback):
                self.file = file
                self.callback = callback
                self.total = file_size
                self.current = 0

            def read(self, size=-1):
                data = self.file.read(size)
                self.current += len(data)
                if self.callback:
                    self.callback(self.current, self.total)
                return data

            def __len__(self):
                return self.total

        with open(file_path, 'rb') as file:
            headers = {'x-amz-tagging': 'dv-state=temp'}
            data = ProgressReader(file, progress_callback) if progress_callback else file
            response = requests.put(upload_urls['url'], data=data, headers=headers)
            response.raise_for_status()
    elif 'urls' in upload_urls:  # Multi-part upload
        etags = state.get('etags', {})
        part_size = upload_urls['partSize']
        
        # Initial progress update
        if progress_callback:
            # Calculate already uploaded size
            already_uploaded = len(etags) * part_size
            # Multi-part might have last part smaller, but for progress bar it's close enough 
            # or we can be more precise if we want.
            progress_callback(already_uploaded, file_size)

        with open(file_path, 'rb') as file:
            items = list(upload_urls['urls'].items())
            total_parts = len(items)
            for part_number, url in items:
                if part_number in etags:
                    logging.info("Part {} already uploaded, skipping.".format(part_number))
                    continue

                logging.debug("Uploading part {} of {} to URL: {}".format(part_number, total_parts, url))
                offset = (int(part_number) - 1) * part_size
                file.seek(offset)
                part_data = file.read(part_size)
                response = requests.put(url, data=part_data)
                response.raise_for_status()
                etags[part_number] = response.headers['ETag']
                state['etags'] = etags
                write_state(state_file_path, state)
                
                if progress_callback:
                    # Current progress is number of completed parts * part_size
                    # but we should not exceed file_size
                    current_progress = min(int(part_number) * part_size, file_size)
                    progress_callback(current_progress, file_size)

        logging.info("Calling COMPLETE on multi-part upload.")
        complete_url = "{}{}".format(dataverse_url, upload_urls['complete'])
        headers = {'X-Dataverse-key': api_key}
        requests.put(complete_url, json=etags, headers=headers).raise_for_status()
    logging.info("File uploaded to S3 successfully.")
