import os
import sys

SCRIPT_NAME = 'wiggle-api'
SERVICE_FILE = f"{SCRIPT_NAME}.service"
SERVICE_DESCRIPTION = 'WiggleApi service'

def install():
    # Construct the path to the virtual environment
    python_path = sys.executable
    venv_path = os.path.dirname(python_path)
    script_path = os.path.dirname(os.path.abspath(__file__))

    # Define the content of the service file
    service_content = f"""[Unit]
    Description={SERVICE_DESCRIPTION}
    After=network.target

    [Service]
    WorkingDirectory={script_path}
    ExecStart={python_path} {script_path}/main.py
    Environment="PATH={venv_path}:{os.environ['PATH']}"

    [Install]
    WantedBy=default.target
    """

    # Write the content to the service file
    service_file_path = os.path.expanduser(f"~/.config/systemd/user/{SERVICE_FILE}")
    os.makedirs(os.path.dirname(service_file_path), exist_ok=True)
    with open(service_file_path, 'w') as f:
        f.write(service_content)

    os.system(f"systemctl --user enable {SERVICE_FILE}")
    os.system(f"systemctl --user start {SERVICE_FILE}")