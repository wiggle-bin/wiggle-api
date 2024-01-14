# WiggleApi

Control the [WiggleR](https://github.com/wiggle-bin/wiggle-r) via the API. Wiggle-api allows you do things like retrieve sensor data from the WiggleR.

## Running

Without Docker:
```
flask --app src/wiggle_api run --debug
```

With docker-compose:
```
docker-compose up
```

As a Pip package
```
pip3 install -e .
wiggle_api
```