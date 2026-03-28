import os
import yaml

EXAMPLE_CONFIG = """
dataverses:
  - name: test_archaeology
    label: Data Station Archaeology (Test)
    url: changeme
    api_key: changeme
  - name: test_ssh
    label: Data Station SSH (Test)
    url: changeme
    api_key: changeme
    
default_dataverse: test_archaeology    

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
            file.write(EXAMPLE_CONFIG)
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
