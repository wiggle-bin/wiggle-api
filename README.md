# WiggleApi

Control the [WiggleBin](https://github.com/wiggle-bin/wiggle-bin) via the API. Wiggle-api allows you do things like retrieve sensor data from the WiggleBin.

## Installing for development

### Running with Docker compose

Install Docker on your Raspberry Pi and run

```
docker-compose up
```

### Install as a local Pip package

```
pip3 install -e .
wiggle_api
```

### Running with venv

Create an environment

```bash
python3 -m venv .venv
```

Start environment

```bash
source .venv/bin/activate
```

Install packages

```bash
pip install -r requirements.txt
```

Start the Flask server

```bash
flask -app src/wiggle_api run --debug
```

## Install WiggleApi service

In the terminal run `wiggle-api-install`. This will install and start a service which runs `wiggle-api` on boot.

```
wiggle-api-install
```


You can check the status with:

```
systemctl --user status wiggle-api.service
```

To stop the service run:

```
systemctl --user stop wiggle-api.service
```

To start the service run:

```
systemctl --user start wiggle-api.service
```

Watching output of the service:

```
journalctl --user-unit=wiggle-api.service -f
```