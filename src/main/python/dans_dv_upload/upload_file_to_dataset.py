#!/usr/bin/env python3
import argparse
import logging
import os
import sys
from logging import config as logconfig

from .config import read_config, ensure_configuration_file_exists
from .dataverse import get_upload_urls, register_file
from .gui import combined_gui_dialog
from .s3_upload import upload_file_to_s3, load_state, write_state
from .util import calculate_checksum


def get_args():
    parser = argparse.ArgumentParser(description="Upload a file to a Dataverse dataset.")
    parser.add_argument("doi", nargs="?", help="DOI of the dataset")
    parser.add_argument("file", nargs="?", help="Path to the file to upload")
    parser.add_argument("--directory-label", help="Directory label for the file in the dataset")
    parser.add_argument("--resume", action="store_true", help="Resume a previously started upload")
    parser.add_argument("--skip-checksum-on-resume", action="store_true", help="Skip SHA-1 checksum verification when resuming")
    parser.add_argument("--keep-upload-state", action="store_true", help="Keep the state file after a successful upload")
    parser.add_argument("--gui", action="store_true", help="Force GUI mode (show file dialog and DOI prompt)")
    return parser, parser.parse_known_args()

def handle_ui_cli_logic(parser, args):
    if args.gui:
        file_path, doi = combined_gui_dialog()
        
        if file_path is None or doi is None:
            print("Required information missing or GUI not available. Exiting.")
            sys.exit(0)
            
        args.file = file_path
        args.doi = doi
    else:
        if not args.doi or not args.file:
            parser.print_usage()
            print("\nBoth DOI and file must be specified in CLI mode.")
            sys.exit(2)
    return args

def main():
    ensure_configuration_file_exists()
    config = read_config()
    logconfig.dictConfig(config['logging'])

    parser, (args, unknown) = get_args()
    args = handle_ui_cli_logic(parser, args)

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
