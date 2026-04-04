import os
import shutil
import sys
import textwrap
import yaml


def ensure_configuration_file_exists():
    home_config_path = os.path.expanduser('~/.dv-upload.yml')
    if os.path.exists(home_config_path):
        return

    example_config = textwrap.dedent("""
        dataverses:
          - name: archaeology
            label: Data Station Archaeology
            url: https://archaeology.datastations.nl
            api_key: changeme
          - name: ssh
            label: Data Station SSH
            url: https://ssh.datastations.nl
            api_key: changeme
          - name: lifesciences
            label: Data Station Life Sciences
            url: https://lifesciences.datastations.nl
            api_key: changeme
          - name: phystechsciences
            label: Data Station Phys-Tech Sciences
            url: https://phys-techsciences.datastations.nl
            api_key: changeme
          - name: dataversenl
            label: DataverseNL
            url: https://dataverse.nl
            api_key: changeme
        
        default_dataverse: archaeology
        
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
              filename: ~/dv-upload.log
              level: DEBUG
          formatters:
            std_out:
              format: "%(asctime)s : %(levelname)s : %(funcName)s : %(message)s"
              datefmt: "%Y-%m-%d %I:%M:%S"
""")
    with open(home_config_path, 'w') as f:
        f.write(example_config)

def read_config():
    config_path = os.path.expanduser('~/.dv-upload.yml')

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
