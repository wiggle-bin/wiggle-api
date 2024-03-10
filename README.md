# WiggleApi

Control the [WiggleR](https://github.com/wiggle-bin/wiggle-r) via the API. Wiggle-api allows you do things like retrieve sensor data from the WiggleR.

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