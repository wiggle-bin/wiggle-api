from datetime import datetime, timedelta
import glob
import json
import os
import io
from pathlib import Path
import zipfile
from flask import Flask, Response, jsonify, Response, send_from_directory, request
import csv

BASE_FOLDER = Path.home() / "WiggleBin"
IMG_FOLDER = f"{BASE_FOLDER}/pictures"
VID_FOLDER = f"{BASE_FOLDER}/videos"
VID_FOLDER_HOURLY = f"{VID_FOLDER}/hourly"
VID_FOLDER_DAILY = f"{VID_FOLDER}/daily"
VID_FOLDER_WEEKLY = f"{VID_FOLDER}/weekly"
ZIP_FOLDER = f"{BASE_FOLDER}/zips"
ZIP_FOLDER_HOURLY = f"{ZIP_FOLDER}/hourly"
ZIP_FOLDER_DAILY = f"{ZIP_FOLDER}/daily"
ZIP_FOLDER_WEEKLY = f"{ZIP_FOLDER}/weekly"
DATA_FOLDER = BASE_FOLDER / "sensor-data"
BME_FILE = DATA_FOLDER / "bme680.csv"
TEMPERATURE_FILE = DATA_FOLDER / "temperature.csv"
IMAGE_DATA = DATA_FOLDER / "image-data.csv"
WIGGLE_GATE_FILE = DATA_FOLDER / "wiggle-gate.csv"
SOIL_TEMPERATURE_FILE = DATA_FOLDER / "temperature.json"

def list_files(folder, path, extension):
    out = []
    for fileName in sorted(os.listdir(folder)):
        name, ext = os.path.splitext(fileName)
        if ext == extension:
            out.append({"name": name, "path": f'http://{request.host}' + path + fileName})
    return out

def get_latest_file(dir):
    files = os.listdir(dir)
    files.sort()
    return os.path.join(dir, files[-1])


def zipfiles(filenames, name):
    zip_subdir = "./"
    zip_io = io.BytesIO()

    with zipfile.ZipFile(
        zip_io, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as temp_zip:
        for fpath in filenames:
            _, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            temp_zip.write(fpath, zip_path)

    zip_io.seek(0)

    response = Response(zip_io, mimetype="application/x-zip-compressed")
    response.headers["Content-Disposition"] = f"attachment; filename={name}.zip"
    return response


def read_last_json_item(file_path):
    try:
        with open(file_path, 'r') as file:
            items = json.load(file)
            return items[-1]
    except FileNotFoundError:
        return {"error": "File not found"}

def read_last_row(file_path):
    try:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            last_row = None
            for row in reader:
                last_row = row
        return last_row
    except FileNotFoundError:
        return {"error": "File not found"}

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    @app.route('/download-zip/<filename>')
    def download_zip(filename):
        return send_from_directory(ZIP_FOLDER, filename, as_attachment=True)
    
    @app.route('/data/', methods=['GET'])
    def list_data():
        return jsonify(list_files(DATA_FOLDER, "/data/", ".csv"))

    @app.route('/data/<filename>', methods=['GET'])
    def download_file(filename):
        return send_from_directory(DATA_FOLDER, filename, as_attachment=True)

    # a simple page that says hello
    @app.route("/")
    def hello():
        return jsonify({"worm": "Hello!"})

    # Latest data from sensors
    @app.route("/sensors/")
    def sensors():
        data = {
            "environment": read_last_row(BME_FILE),
            "temperature": read_last_json_item(SOIL_TEMPERATURE_FILE),
            "image": read_last_row(IMAGE_DATA),
        }
        return jsonify(data)

    # BME sensor environment data
    @app.route("/sensors/bme")
    def environment():
        data = []
        try:
            with open(BME_FILE, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            return jsonify({"error": "File not found"})
        return jsonify(data)

    # Soil temperature sensor environment data
    @app.route("/sensors/soil-temperature")
    def soil_temperature():
        try:
            with open(SOIL_TEMPERATURE_FILE, 'r') as file:
                data = json.load(file)
                return jsonify(data)
        except FileNotFoundError:
            return {"error": "File not found"}

    # WiggleGate sensor
    @app.route("/sensors/wiggle-gate")
    def gate():
        data = []
        try:
            with open(WIGGLE_GATE_FILE, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            return jsonify({"error": "File not found"})
        return jsonify(data)

    # a simple page that says hello
    @app.route("/images")
    def images():
        files = list_files(IMG_FOLDER, "/image/", ".jpg")
        return jsonify(files)

    @app.route("/image/<filename>")
    def image(filename):
        return send_from_directory(IMG_FOLDER, filename)

    @app.route("/videos/daily", methods=["GET"])
    def daily_videos():
        return jsonify(list_files(VID_FOLDER_DAILY, "/videos/daily/", ".mp4"))

    @app.route("/videos/hourly", methods=["GET"])
    def hourly_videos():
        return jsonify(list_files(VID_FOLDER_HOURLY, "/videos/hourly/", ".mp4"))

    @app.route("/videos/weekly", methods=["GET"])
    def weekly_videos():
        return jsonify(list_files(VID_FOLDER_WEEKLY, "/videos/weekly/", ".mp4"))
    
    @app.route("/videos/<string:subFolder>/<string:file>", methods=["GET"])
    def get_video(subFolder, file):
        return send_from_directory(f"{VID_FOLDER}/{subFolder}", file)

    @app.route("/zips/hourly", methods=["GET"])
    def hourly_zips():
        return jsonify(list_files(ZIP_FOLDER_HOURLY, "/zips/hourly/", ".zip"))

    @app.route("/zips/daily", methods=["GET"])
    def daily_zips():
        return jsonify(list_files(ZIP_FOLDER_DAILY, "/zips/daily/", ".zip"))

    @app.route("/zips/weekly", methods=["GET"])
    def weekly_zips():
        return jsonify(list_files(ZIP_FOLDER_WEEKLY, "/zips/weekly/", ".zip"))

    @app.route("/zips/<string:subFolder>/<string:file>", methods=["GET"])
    def get_zip(subFolder, file):
        return send_from_directory(f"{ZIP_FOLDER}/{subFolder}", file)

    @app.route("/images/zip/stream/<string:date>", methods=["GET"])
    def zip_stream(date):
        filenames = glob.glob(str(Path(__file__).parent / f"{IMG_FOLDER}/{date}*.jpg"))
        print(filenames)
        return zipfiles(filenames, date)

    @app.route("/images/zip/yesterday", methods=["GET"])
    def zip_yesterday():
        yesterday = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
        os.system(f"zip -j {ZIP_FOLDER}/{yesterday} {IMG_FOLDER}/{yesterday}*.jpg")
        return {"name": yesterday, "path": f"/zip/{yesterday}.zip"}

    @app.route("/images/zip/<string:date>", methods=["GET"])
    def zip_based_on_date(date):
        os.system(f"zip -j {ZIP_FOLDER}/{date} {IMG_FOLDER}/{date}*.jpg")
        return {"name": date, "path": f"/zip/{date}.zip"}

    @app.route("/camera/picture", methods=["GET"])
    def take_picture():
        now = datetime.now()
        fileName = now.strftime("%Y-%m-%d-%H-%M")
        filePath = f"{IMG_FOLDER}/{fileName}.jpg"
        os.system(
            f"libcamera-jpeg --width 1024 --height 768 --nopreview -t 1 -o {filePath}"
        )
        return {"picture": f"image/{fileName}.jpg"}

    @app.route("/light/on/<float:intensity>", methods=["GET"])
    def light(intensity=1): ...

    @app.route("/light/off", methods=["GET"])
    def lightOff(): ...

    @app.route("/timelapse/yesterday", methods=["GET"])
    def timelapse_yesterday():
        yesterday = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
        os.system(
            f'ffmpeg -framerate 30 -pattern_type glob -i "{IMG_FOLDER}/{yesterday}*.jpg" -s:v 1440x1080 -c:v libx264 -crf 17 -pix_fmt yuv420p {VID_FOLDER}/{yesterday}.mp4'
        )
        return jsonify({"name": yesterday, "path": f"/video/{yesterday}.mp4"})

    @app.route("/timelapse/date/<string:date>", methods=["GET"])
    def timelapse_date(date):
        os.system(
            f'ffmpeg -framerate 30 -pattern_type glob -i "{IMG_FOLDER}/{date}*.jpg" -s:v 1440x1080 -c:v libx264 -crf 17 -pix_fmt yuv420p {VID_FOLDER}/{date}.mp4'
        )
        return jsonify({"name": date, "path": f"/video/{date}.mp4"})

    return app
